import sys, os
# Thêm src vào sys.path để import core
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import gradio as gr
from core import get_chat_response

# CSS custom cho Blocks
custom_css = """
#chatbot { 
    height: 500px; 
    overflow-y: auto; 
    background-color: #f9f9f9; 
    border-radius: 8px; 
    padding: 8px; 
}
#input-row { 
    margin-top: 10px; 
}
#txt { 
    flex: 1; 
}
#clear-btn { 
    margin-left: 8px; 
}
h1 {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #333;
}
"""

def respond(user_message, history):
    if history is None:
        history = []
    history.append(("Bạn", user_message))
    bot_reply = get_chat_response(user_message)
    history.append(("Hệ thống", bot_reply))
    return history, history

with gr.Blocks(title="Chatbot Text2SQL", css=custom_css) as demo:
    gr.Markdown("<h1 style='text-align: center;'>🤖 Chatbot Text2SQL</h1>")
    
    # Chat area
    chatbot = gr.Chatbot(elem_id="chatbot")
    state = gr.State([])

    # Input row: textbox + clear button
    with gr.Row(elem_id="input-row"):
        txt = gr.Textbox(
            placeholder="Nhập tin nhắn của bạn...",
            show_label=False,
            lines=1,
            elem_id="txt"
        )
        clear_btn = gr.Button("🗑 Xóa", elem_id="clear-btn", variant="secondary")

    # Hook submit và clear
    txt.submit(respond, [txt, state], [chatbot, state])
    clear_btn.click(lambda: ([], []), None, [chatbot, state])

if __name__ == "__main__":
    # Bạn có thể đổi share=True nếu muốn public link
    demo.launch()
