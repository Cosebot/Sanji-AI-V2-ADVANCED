from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import uvicorn

# === Sanji Brain ===
from info_module import info_pipeline

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

# === HTML Page Content ===
from sanji_ui import chat_html  # assuming you've moved the big HTML string to `sanji_ui.py`

@app.get("/", response_class=HTMLResponse)
async def get_page(request: Request):
    return HTMLResponse(content=chat_html, status_code=200)

# === Models ===
class ChatMessage(BaseModel):
    message: str

class InfoQuery(BaseModel):
    query: str

# === Chat Endpoint ===
@app.post("/chat")
async def chat(msg: ChatMessage):
    reply = chatbot.get_response(msg.message)
    return JSONResponse(content={"response": str(reply)})

# === Info Search Endpoint ===
@app.post("/ask")
async def ask_info(q: InfoQuery):
    result = info_pipeline(q.query)
    return JSONResponse(content={
        "response": result["answer"],
        "sources": result["sources"]
    })

html_code = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Sanji AI - Chat</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bitcount+Grid+Single:wght@100..900&display=swap" rel="stylesheet">
  <style>
    :root {
      --title-bg: #800020;
      --bg: #880808;
      --ai-bubble: #191970;
      --user-bubble: #A42A04;
      --input-bg: #A52A2A;
      --btn-bg: #1434A4;
      --text-color: white;
    }
    body {
      margin: 0;
      padding: 0;
      font-family: 'Bitcount Grid Single', sans-serif;
      background-color: var(--bg);
      color: var(--text-color);
      display: flex;
      flex-direction: column;
      height: 100vh;
      overflow: auto;
    }
    .title-box {
      background-color: var(--title-bg);
      text-align: center;
      padding: 10px;
      font-size: 1.4rem;
      font-weight: bold;
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    #transitionText {
      transition: opacity 1s ease-in-out;
    }
    #settings-btn {
      background: none;
      border: none;
      font-size: 1.4rem;
      color: white;
      cursor: pointer;
    }
    #settings-menu {
      display: none;
      position: absolute;
      top: 60px;
      right: 10px;
      background-color: #222;
      padding: 10px;
      border-radius: 10px;
      z-index: 999;
    }
    .chat-container {
      flex: 1;
      height: calc(100vh - 120px);
      padding: 10px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .chat-bubble {
      max-width: 80%;
      padding: 10px;
      border-radius: 10px;
      word-wrap: break-word;
    }
    .ai-bubble {
      background-color: var(--ai-bubble);
      align-self: flex-start;
    }
    .user-bubble {
      background-color: var(--user-bubble);
      align-self: flex-end;
    }
    .input-container {
      display: flex;
      padding: 10px;
      background-color: var(--input-bg);
      gap: 5px;
      position: fixed;
      bottom: 0;
      width: 100%;
      box-sizing: border-box;
    }
    input[type="text"] {
      flex: 1;
      padding: 10px;
      border: none;
      border-radius: 5px;
      font-family: 'Bitcount Grid Single', sans-serif;
    }
    button {
      padding: 10px;
      border: none;
      background-color: var(--btn-bg);
      color: white;
      border-radius: 5px;
      font-size: 1.1rem;
      font-family: 'Bitcount Grid Single', sans-serif;
    }
    body.desktop .chat-container {
      font-size: 1.2rem;
      padding: 20px;
    }
    body.desktop input[type="text"], body.desktop button {
      font-size: 1.2rem;
    }
  </style>
</head>
<body>
  <div class="title-box">
    <span id="transitionText">Sanji AI</span>
    <button id="settings-btn">⚙️</button>
  </div>
  <div id="settings-menu">
    <button id="theme-btn">🎨 Theme</button><br><br>
    <button id="mode-switch-btn">🖥️ Switch to Desktop Mode</button>
  </div>
  <div class="chat-container" id="chat-container">
    <div class="chat-bubble ai-bubble">Hello! I’m Sanji AI</div>
    <div class="chat-bubble user-bubble">Yo!</div>
  </div>
  <div class="input-container">
    <input type="text" id="user-input" placeholder="Say something..." />
    <button id="send-btn">➤</button>
  </div>
  <script>
  window.onload = function () {
    const themes = [
      { name: "Spiderman", title: "#800020", bg: "#880808", ai: "#191970", user: "#A42A04", input: "#A52A2A", btn: "#1434A4" },
      { name: "Real Madrid", title: "#EDEADE", bg: "#87CEEB", ai: "#D22B2B", user: "#5D3FD3", input: "#FFD5EE", btn: "#FFAA33" },
      { name: "Zoro", title: "#097969", bg: "#50C878", ai: "#E4D00A", user: "#00A36C", input: "#0BDA51", btn: "#5D3FD3" },
      { name: "Cars", title: "#A7C7E7", bg: "#C2B280", ai: "#4682B4", user: "#D2042D", input: "#FF2400", btn: "#FDDA0D" },
      { name: "GTA SA", title: "#1B2121", bg: "#FFAC1C", ai: "#9F2B68", user: "#009E60", input: "#93C572", btn: "#E5E4E2" },
      { name: "Squid Game", title: "#36454F", bg: "#800020", ai: "#DC143C", user: "#478778", input: "#2AAA8A", btn: "#355E3B" }
    ];
    let currentTheme = 0;

    const themeBtn = document.getElementById("theme-btn");
    const sendBtn = document.getElementById("send-btn");
    const settingsBtn = document.getElementById("settings-btn");
    const settingsMenu = document.getElementById("settings-menu");
    const modeBtn = document.getElementById("mode-switch-btn");

    settingsBtn.addEventListener("click", () => {
      settingsMenu.style.display = settingsMenu.style.display === "none" ? "block" : "none";
    });

    modeBtn.addEventListener("click", () => {
      document.body.classList.toggle("desktop");
      modeBtn.textContent = document.body.classList.contains("desktop") ? "📱 Switch to Mobile Mode" : "🖥️ Switch to Desktop Mode";
    });

    themeBtn.addEventListener("click", () => {
      currentTheme = (currentTheme + 1) % themes.length;
      const theme = themes[currentTheme];
      document.documentElement.style.setProperty("--title-bg", theme.title);
      document.documentElement.style.setProperty("--bg", theme.bg);
      document.documentElement.style.setProperty("--ai-bubble", theme.ai);
      document.documentElement.style.setProperty("--user-bubble", theme.user);
      document.documentElement.style.setProperty("--input-bg", theme.input);
      document.documentElement.style.setProperty("--btn-bg", theme.btn);
    });

    const titleText = document.getElementById("transitionText");
    let toggle = true;
    setInterval(() => {
      titleText.style.opacity = 0;
      setTimeout(() => {
        titleText.textContent = toggle ? "Making your day better" : "Sanji AI";
        titleText.style.opacity = 1;
        toggle = !toggle;
      }, 500);
    }, 5000);

    const chatContainer = document.getElementById("chat-container");
    const userInput = document.getElementById("user-input");

    function scrollToBottom() {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    sendBtn.addEventListener("click", () => {
      const msg = userInput.value.trim();
      if (msg === "") return;

      const userBubble = document.createElement("div");
      userBubble.className = "chat-bubble user-bubble";
      userBubble.textContent = msg;
      chatContainer.appendChild(userBubble);
      scrollToBottom();

      fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: msg })
      })
      .then(res => res.json())
      .then(data => {
        const aiBubble = document.createElement("div");
        aiBubble.className = "chat-bubble ai-bubble";
        aiBubble.innerHTML = data.response;
        chatContainer.appendChild(aiBubble);
        scrollToBottom();
      });

      userInput.value = "";
    });

    userInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") sendBtn.click();
    });

    setTimeout(scrollToBottom, 100);
  };
  </script>
</body>
</html>
'''

# === Run Server ===
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)