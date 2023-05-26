import gradio as gr

from ai_interview_coach.jd import PM_JD, RD_JD


class Resume:
    def __init__(self, self_intro: str = "", experience: str = ""):
        self.self_intro = self_intro
        self.experience = experience


def upload_resume(current_tab, self_intro, experience, resume):
    resume.self_intro = self_intro
    resume.experience = experience
    return gr.Tabs.update(selected=(current_tab + 1) % 4), resume


def add_text(history, text):
    history = history + [(text, None)]
    return history, ""


def add_file(history, file):
    history = history + [((file.name,), None), (f"You uploaded {file.name}", None)]
    return history


def bot(history):
    response = "**That's cool!**"
    history[-1][1] = response
    return history


with gr.Blocks() as demo:
    resume_state = gr.State(Resume())

    gr.HTML("<div><img src='file/logo.png' width='120' style='display:inline-block;vertical-align:middle;'>"
            "<h1 style='display:inline-block;vertical-align:middle;padding-left:1rem;font-size:2rem'>AI 聘</h1></div>")
    with gr.Tabs() as tabs:
        def next_tab(current_tab):
            return gr.Tabs.update(selected=(current_tab + 1) % 4)

        with gr.Tab("选择JD", id=0):
            gr.Radio(["产品", "研发"], label="岗位", info="请选择你要面试的岗位").style(item_container=False)
            with gr.Row():
                with gr.Column(scale=0.5):
                    gr.Markdown(PM_JD)
                with gr.Column(scale=0.5):
                    gr.Markdown(RD_JD)
            with gr.Row():
                with gr.Column(scale=0.4, min_width=0):
                    num0 = gr.Number(value=0, visible=False)
                with gr.Column(scale=0.2, min_width=0):
                    gr.Button("下一步").click(next_tab, num0, tabs)
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
            chatbot = gr.Chatbot([[None, "你好，我是面试官，请介绍一下你自己。"]], elem_id="chatbot")
            with gr.Row():
                with gr.Column(scale=0.8):
                    txt = gr.Textbox(
                        show_label=False,
                        placeholder="请在此输入",
                    ).style(container=False)
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

    txt.submit(add_text, [chatbot, txt], [chatbot, txt]).then(
        bot, chatbot, chatbot
    )

if __name__ == "__main__":
    demo.launch()
