# main_UI.py
import os
import uuid
import gradio as gr
from pyngrok import ngrok

# Import the main agent orchestrator function from our core package
from core.orchestrator import agent

def chat(message, history, session_id):
    """
    Cleans incoming user text inputs and routes them along with the 
    isolated user session ID down into the core orchestrator pipeline.
    """
    # 1. Prevent empty strings or input network stutter duplicates from mobile browsers
    clean_message = message.strip()
    if not clean_message:
        return "Please ask a question about the McDonald's India menu!"

    # 2. Prevent general conversational goodbyes from triggering RAG hallucinations
    if any(word in clean_message.lower() for word in ["bye", "k bye", "goodbye", "exit"]):
        return "Thank you for visiting McDonald’s India! Have a wonderful day ahead! 🍔"
        
    # 3. Pass clean_message as the 1st argument and session_id as the 2nd argument
    response = agent(clean_message, session_id)
    return response

# We use gr.Blocks to cleanly introduce isolated user session tracking variables
with gr.Blocks() as demo:
    # Generates a unique string hash token per fresh browser tab instance
    session_state = gr.State(lambda: uuid.uuid4().hex)
    
    gr.ChatInterface(
        fn=chat,
        title="🍔 McDonald's India AI Assistant",
        description="Ask me about nutrition, menu items, and recommendations!",
        examples=[
            ["Which burger has lowest calories?"],
            ["Tell me about McVeggie Burger"],
            ["Healthy breakfast options under 200 calories?"],
            ["How many items are in McCafe?"]
        ],
        additional_inputs=[session_state] # Maps session_id securely as the 3rd argument to chat()
    )

# 1. Force kill any old dangling ngrok proxy processes running in the background
ngrok.kill()

# 2. Authenticate using the token stored securely in your .env file
NGROK_TOKEN = os.environ.get("NGROK_AUTH_TOKEN")
if not NGROK_TOKEN:
    print("⚠️ Warning: NGROK_AUTH_TOKEN not found in .env file!")
else:
    ngrok.set_auth_token(NGROK_TOKEN)

# 3. Configure designated interface networking port
TARGET_PORT = 7860 

# 4. Open the secure public HTTPS tunnel link mapping (bind_tls=True enforces HTTPS)
public_url = ngrok.connect(TARGET_PORT, bind_tls=True)
print(f"\n🚀 SECURE PUBLIC TUNNEL ACTIVE! Share this link with your friends:\n👉 {public_url.public_url}\n")

# 5. Launch the local Gradio server locked onto the target port configuration
demo.launch(share=False, server_port=TARGET_PORT)
