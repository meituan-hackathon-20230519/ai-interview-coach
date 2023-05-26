import asyncio
import logging
import os
import time

import azure.cognitiveservices.speech as speechsdk

from utils import StreamingCallbackHandler

logger = logging.getLogger(__name__)


class SpeechService:
    def __init__(self):
        self.tts_config = speechsdk.SpeechConfig(
            subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION')
        )
        self.tts_config.speech_synthesis_voice_name = 'zh-CN-liaoning-XiaobeiNeural'
        self.audio_out_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

        self.stt_config = speechsdk.SpeechConfig(
            subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION')
        )
        self.stt_config.speech_recognition_language = "zh-CN"
        self.audio_in_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.user_map = {}

    def text_to_speech(self, text: str) -> None:
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.tts_config, audio_config=self.audio_out_config)

        speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f"Speech synthesized for text [{text}]")
        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            logger.info(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error and cancellation_details.error_details:
                logger.info(f"Error details: {cancellation_details.error_details}")

    async def speech_to_text(self, callback: StreamingCallbackHandler) -> None:
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.stt_config, audio_config=self.audio_in_config)
        done = False
        last_spoken = 0

        def stop_cb(evt):
            logger.info(f"CLOSING on {evt}")
            speech_recognizer.stop_continuous_recognition()
            nonlocal done
            done = True

        def recognizing_cb(evt):
            nonlocal last_spoken
            last_spoken = time.time()
            logger.info(f"RECOGNIZING: {evt}")

        def recognized_cb(evt):
            nonlocal last_spoken
            last_spoken = time.time()
            logger.info(f"RECOGNIZED: {evt}")
            asyncio.run(callback.on_new_token(evt.result.text))

        speech_recognizer.recognizing.connect(recognizing_cb)
        speech_recognizer.recognized.connect(recognized_cb)
        speech_recognizer.session_started.connect(lambda evt: logger.info(f"SESSION STARTED: {evt}"))
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)

        speech_recognizer.start_continuous_recognition()
        last_spoken = time.time()
        while not done:
            await asyncio.sleep(.5)
            if time.time() - last_spoken > 2:
                print("No speech detected for 2 seconds. Stopping recognition.")
                speech_recognizer.stop_continuous_recognition_async()
                break
