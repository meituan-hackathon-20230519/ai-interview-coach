import asyncio
import logging
import sys
import uuid
from queue import Queue, Empty

import gradio as gr
from anyio import start_blocking_portal

from ai_interview_coach.jd import PM_JD, RD_JD
from coach import InterviewCoach, Resume
from speech import SpeechService
from util.commons import evaluation_generator
from utils import StreamingCallbackHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_global_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_global_exception
interview_coach = InterviewCoach()
speech_service = SpeechService()


def upload_resume(current_tab, self_intro, experience, resume):
    resume.self_intro = self_intro
    resume.experience = experience
    return gr.Tabs.update(selected=(current_tab + 1) % 4), resume


def add_text(history, text):
    history = history + [(text, None)]
    return history, ""


def start_talking(history):
    q = Queue()
    job_done = object()
    history = history + [("", None)]

    async def task():
        try:
            await speech_service.speech_to_text(StreamingCallbackHandler(q))
        except Exception:
            logger.exception("Error in STT")
        q.put(job_done)

    with start_blocking_portal() as portal:
        portal.start_task_soon(task)
        content = ""
        while True:
            try:
                next_token = q.get(timeout=30)
            except Empty:
                break
            if next_token is job_done:
                yield history
                break
            content += next_token
            history[-1] = (content, None)
            yield history


def bot(history, resume, stage, session_id):
    q = Queue()
    job_done = object()
    next_stage = stage

    async def task():
        nonlocal next_stage
        try:
            next_stage, output = await interview_coach.agenerate_output(history, resume, stage, session_id,
                                                                        StreamingCallbackHandler(q))
        except Exception:
            logger.exception("Error in bot")
            output = ""
        speech_service.text_to_speech(output)
        q.put(job_done)

    with start_blocking_portal() as portal:
        portal.start_task_soon(task)
        content = ""
        while True:
            try:
                next_token = q.get(timeout=100)
            except Empty:
                break
            if next_token is job_done:
                yield history, next_stage
                break
            content += next_token
            history[-1][1] = content
            yield history, next_stage


def generate_evaluation(history, resume, session_id):
    q = Queue()
    job_done = object()

    async def task():
        try:
            await evaluation_generator.arun(None, session_id, history, StreamingCallbackHandler(q))
        except Exception:
            logger.exception("Error in generate_evaluation")
        # speech_service.text_to_speech(output)
        q.put(job_done)

    with start_blocking_portal() as portal:
        portal.start_task_soon(task)
        content = "## 面试评价\n"
        while True:
            try:
                next_token = q.get(timeout=100)
            except Empty:
                break
            if next_token is job_done:
                break
            content += next_token
            yield content


with gr.Blocks() as demo:
    resume_state = gr.State(Resume())
    session = gr.State(str(uuid.uuid4()))

    gr.HTML("<div><img src='file/logo.png' width='120' style='display:inline-block;vertical-align:middle;'>"
            "<h1 style='display:inline-block;vertical-align:middle;padding-left:1rem;font-size:2rem'>AI 聘</h1></div>")
    with gr.Tabs() as tabs:
        def next_tab(current_tab):
            return gr.Tabs.update(selected=(current_tab + 1) % 4)


        def select_jd(current_tab, selection):
            if selection == "产品":
                return next_tab(current_tab)
            else:
                return gr.Tabs.update(selected=current_tab)


        with gr.Tab("选择JD", id=0):
            jd_radio = gr.Radio(["产品", "研发"], label="岗位", info="请选择你要面试的岗位").style(item_container=False)
            with gr.Row():
                with gr.Column(scale=0.01, min_width=0):
                    pass
                with gr.Column(scale=0.47):
                    gr.Markdown(PM_JD)
                with gr.Column(scale=0.04, min_width=0):
                    pass
                with gr.Column(scale=0.47):
                    gr.Markdown(RD_JD)
                with gr.Column(scale=0.01, min_width=0):
                    pass
            with gr.Row():
                with gr.Column(scale=0.4, min_width=0):
                    num0 = gr.Number(value=0, visible=False)
                with gr.Column(scale=0.2, min_width=0):
                    gr.Button("下一步").click(select_jd, [num0, jd_radio], tabs)
        with gr.Tab("上传简历", id=1):
            self_intro_txt = gr.Textbox(label="自我介绍", lines=8)
            exp_txt = gr.Textbox(label="项目经历", lines=10)
            with gr.Row():
                with gr.Column(scale=0.4, min_width=0):
                    num1 = gr.Number(value=1, visible=False)
                with gr.Column(scale=0.2, min_width=0):
                    gr.Button("上传").click(
                        upload_resume, [num1, self_intro_txt, exp_txt, resume_state], [tabs, resume_state]
                    )
        with gr.Tab("模拟面试", id=2):
            stage_state = gr.State((0, 0))
            chatbot = gr.Chatbot([[None, "你好，我是面试官，请介绍一下你自己。"]], elem_id="chatbot")
            with gr.Row():
                with gr.Column(scale=0.8):
                    txt = gr.Textbox(
                        show_label=False,
                        placeholder="请在此输入",
                    ).style(container=False)
                    txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
                        bot, [chatbot, resume_state, stage_state, session], [chatbot, stage_state]
                    )
                with gr.Column(scale=0.2, min_width=0):
                    mic = gr.Button("🎙").click(start_talking, [chatbot], [chatbot]).then(
                        bot, [chatbot, resume_state, stage_state, session], [chatbot, stage_state]
                    )
            with gr.Row():
                with gr.Column(scale=0.4, min_width=0):
                    num2 = gr.Number(value=2, visible=False)
                with gr.Column(scale=0.2, min_width=0):
                    gr.Button("下一步").click(next_tab, num2, tabs)
        with gr.Tab("面试评价", id=3):
            evaluation_txt = gr.Markdown(
                "## 面试评价\n暂无，请点击生成"
            )
            gr.Button("获取面评").click(generate_evaluation, [chatbot, resume_state, session], evaluation_txt)

if __name__ == "__main__":
    demo.queue().launch()
