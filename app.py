from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from pathlib import Path
import uvicorn

# === Setup ===
app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR))

# === ChatBot Setup ===

chatbot = ChatBot(
    "ASH-1",
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///main/ASH-1.sqlite3'  # Path relative to current script
)

# === Routes ===
@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    return HTMLResponse(content=html_code, status_code=200)

class ChatMessage(BaseModel):
    message: str

@app.post("/chat")
async def get_response(msg: ChatMessage):
    response = chatbot.get_response(msg.message)
    return JSONResponse(content={"response": str(response)})

# === HTML + CSS + JS ===
html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>ASH-1 ChatBot</title>
    <style>
        body {
            background: #1a1a1a;
            font-family: Arial, sans-serif;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 30px;
        }
        h1 {
            color: #00ffcc;
        }
        #chat-box {
            width: 90%%;
            max-width: 600px;
            height: 400px;
            border: 1px solid #444;
            background: #111;
            padding: 10px;
            overflow-y: scroll;
            margin-bottom: 20px;
            border-radius: 8px;
        }
        .user {
            color: #00ffcc;
        }
        .bot {
            color: #ffcc00;
        }
        #chat-form {
            width: 90%%;
            max-width: 600px;
            display: flex;
        }
        #msg-input {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 8px 0 0 8px;
            outline: none;
        }
        #send-btn {
            padding: 10px 20px;
            background: #00ffcc;
            border: none;
            color: #000;
            font-weight: bold;
            cursor: pointer;
            border-radius: 0 8px 8px 0;
        }
    </style>
</head>
<body>
    <h1>ASH-1 ChatBot</h1>
    <div id="chat-box"></div>
    <form id="chat-form" onsubmit="return sendMessage(event)">
        <input type="text" id="msg-input" placeholder="Type your message..." required />
        <button id="send-btn">Send</button>
    </form>

    <script>
        async function sendMessage(event) {
            event.preventDefault();
            const input = document.getElementById("msg-input");
            const msg = input.value;
            const chatBox = document.getElementById("chat-box");

            chatBox.innerHTML += `<div class="user"><strong>You:</strong> ${msg}</div>`;
            input.value = "";

            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ message: msg })
            });

            const data = await response.json();
            chatBox.innerHTML += `<div class="bot"><strong>ASH-1:</strong> ${data.response}</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

# === Run Server ===
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)