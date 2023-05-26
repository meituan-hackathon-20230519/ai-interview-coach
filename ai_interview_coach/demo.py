import gradio as gr


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
    gr.HTML("<div><img src='file/logo.png' width='120' style='display:inline-block;vertical-align:middle;'>"
            "<h1 style='display:inline-block;vertical-align:middle;padding-left:1rem;font-size:2rem'>AI 聘</h1></div>")
    with gr.Tabs() as tabs:
        def next_tab(current_tab):
            return gr.Tabs.update(selected=(current_tab + 1) % 4)

        with gr.Tab("选择JD", id=0):
            gr.Radio(["产品", "研发"], label="岗位", info="请选择你要面试的岗位").style(item_container=False)
            with gr.Row():
                with gr.Column(scale=0.5):
                    gr.Markdown(
                        '''
                        ## 产品
                        * 0-3年经验
                        * ...
                        '''
                    )
                with gr.Column(scale=0.5):
                    gr.Markdown(
                        '''
                        ## 研发
                        * 0-3年经验
                        * ...
                        '''
                    )
            with gr.Row():
                with gr.Column(scale=0.4, min_width=0):
                    num0 = gr.Number(value=0, visible=False)
                with gr.Column(scale=0.2, min_width=0):
                    gr.Button("下一步").click(next_tab, num0, tabs)
        with gr.Tab("上传简历", id=1):
            gr.Textbox(label="教育经历")
            gr.Textbox(label="工作经历")
            with gr.Row():
                with gr.Column(scale=0.4, min_width=0):
                    num1 = gr.Number(value=1, visible=False)
                with gr.Column(scale=0.2, min_width=0):
                    gr.Button("上传").click(next_tab, num1, tabs)
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
