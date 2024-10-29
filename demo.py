import re
import gradio as gr
import os, json
from typing import TypedDict, Literal
from core.chat import ChatService
from pathlib import Path
CACHED = Path(__file__).parent.joinpath('cached')
class MessageData(TypedDict, total=False):
    role: Literal["user", "assistant"]
    content: str

def create_user(user_id):
    if not os.path.exists(os.path.join(CACHED,str(user_id)+'.json')):
        with open(os.path.join(CACHED,str(user_id)+'.json'),'w') as f:
            pass
    return 1

class Playground:
    def __init__(self):
        self.chat_history = []
        self.context_str = ""
        
        # self.clean_history()


    def clean_history(self):
        """ 清空历史信息
        """
        self.chat_history.clear()
        self.context_str = ""


def submit(query_str , playground:Playground, chat_bot, user_id):
    with open(os.path.join(CACHED,str(user_id)+'.json'),'r') as f:
        data = f.read().strip()
        if data:
            history = json.loads(data)
        else:
            history = []
    service = ChatService()
    ans = service.get_answer(str(user_id), chat_history=history[-40:], question=query_str)
    print(query_str)
    print(ans)
    history.append(f"用户：{query_str}")
    history.append(f"助理：{ans}")
    # print(history)
    with open(os.path.join(CACHED,str(user_id)+'.json'),'w') as f:
        json.dump(history,f,ensure_ascii=False,indent=4)
    chat_bot.append((query_str, ans))
    query_str = ""
    return query_str , chat_bot


def clear_user_input():
    return gr.update(value='')

def reset_state(playground, chat_bot):
    playground.clean_history()
    chat_bot = []
    return chat_bot


with gr.Blocks() as demo:
    playground = gr.State(value=Playground())
    gr.Markdown("# 养老知识库")
    with gr.Column():
        chat_bot = gr.Chatbot(value= [] , height=1000)
        user_prompt = gr.Textbox(label="USER", placeholder="Enter reference here.", lines=5)
        user_id = gr.Textbox(label="USER_ID", placeholder="Set a user id here", lines=1)
        with gr.Row():
            submit_button = gr.Button(value="Submit", variant="primary")
            clear_result_button = gr.Button("Clear History")
            create_button = gr.Button("创建用户")

        
    submit_button.click(
        submit, inputs=[user_prompt , playground, chat_bot,user_id ], outputs= [user_prompt, chat_bot]
    )
    submit_button.click(
        clear_user_input, [], [user_prompt]
    )
    create_button.click(create_user,[user_id],[])
    clear_result_button.click(reset_state, inputs=[playground, chat_bot], outputs=[chat_bot], show_progress=True)

if __name__ == "__main__":
    gr.close_all()
    # demo.launch(server_port=40075, share=True, show_api=False)
    demo.launch(server_port=40051, share=True, show_api=False,root_path="/e_care")