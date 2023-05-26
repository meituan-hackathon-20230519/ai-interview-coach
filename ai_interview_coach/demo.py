import logging
import sys
from queue import Queue, Empty

import gradio as gr
from anyio import start_blocking_portal

from ai_interview_coach.jd import PM_JD, RD_JD
from coach import InterviewCoach, Resume
from stage import INTERVIEW_STAGES
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


def upload_resume(current_tab, self_intro, experience, resume):
    resume.self_intro = self_intro
    resume.experience = experience
    return gr.Tabs.update(selected=(current_tab + 1) % 4), resume


def add_text(history, text):
    history = history + [(text, None)]
    return history, ""


def bot(history, resume, stage):
    q = Queue()
    job_done = object()
    next_stage = stage

    async def task():
        nonlocal next_stage
        try:
            next_stage = await interview_coach.agenerate_output(history, resume, stage, StreamingCallbackHandler(q))
        except Exception:
            logger.exception("Error in bot")
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
                yield history, next_stage
                break
            content += next_token
            history[-1][1] = content
            yield history, next_stage


with gr.Blocks() as demo:
    resume_state = gr.State(Resume())

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
            stage_state = gr.State(INTERVIEW_STAGES[0])
            chatbot = gr.Chatbot([[None, "你好，我是面试官，请介绍一下你自己。"]], elem_id="chatbot")
            with gr.Row():
                with gr.Column(scale=0.8):
                    txt = gr.Textbox(
                        show_label=False,
                        placeholder="请在此输入",
                    ).style(container=False)
                    txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
                        bot, [chatbot, resume_state, stage_state], [chatbot, stage_state]
                    )
                with gr.Column(scale=0.2, min_width=0):
                    # TODO How to handle audio https://github.com/gradio-app/gradio/blob/main/demo/stream_audio/run.py
                    btn = gr.Audio(label="语音", min_width=50, source="microphone", type="filepath", streaming=True)
            with gr.Row():
                with gr.Column(scale=0.4, min_width=0):
                    num2 = gr.Number(value=2, visible=False)
                with gr.Column(scale=0.2, min_width=0):
                    gr.Button("获取面评").click(next_tab, num2, tabs)
        with gr.Tab("面试评价", id=3):
            gr.HTML(
                "<h1>兴哥说</h1>"
                "<section>面试评价：牛逼</section>"
            )

if __name__ == "__main__":
    demo.queue().launch()
