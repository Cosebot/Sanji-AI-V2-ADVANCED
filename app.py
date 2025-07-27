from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import uvicorn

# === Setup ===
app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

# === ChatBot ===
chatbot = ChatBot(
    "ASH-1",
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri=f"sqlite:///{BASE_DIR}/ASH-1.sqlite3"
)

# === Trainer ===
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train(str(BASE_DIR / "ash_corpus.yaml"))

# === HTML Response ===
@app.get("/", response_class=HTMLResponse)
async def get_page(request: Request):
    return HTMLResponse(content=html_code, status_code=200)

class ChatMessage(BaseModel):
    message: str

@app.post("/chat")
async def chat(msg: ChatMessage):
    reply = chatbot.get_response(msg.message)
    return JSONResponse(content={"response": str(reply)})

html_code = """
<!DOCTYPE html>
<html>
<head>
    <title>ASH-1 ChatBot</title>
    <style>
        body {
            background: #111;
            font-family: Arial;
            color: #eee;
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 30px;
        }
        #chat-box {
            width: 90%%;
            max-width: 600px;
            height: 400px;
            border: 1px solid #333;
            background: #1a1a1a;
            padding: 10px;
            overflow-y: scroll;
            margin-bottom: 20px;
            border-radius: 8px;
        }
        .user { color: #00ffff; }
        .bot { color: #ffcc00; }
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
        }
        #send-btn {
            padding: 10px;
            background: #00ffff;
            border: none;
            color: #000;
            border-radius: 0 8px 8px 0;
            font-weight: bold;
            cursor: pointer;
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