from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import uvicorn

from info_module import info_pipeline
from sanji_ui import chat_html

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent

# === ChatBot Setup ===
chatbot = ChatBot(
    "ASH-1",
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri=f"sqlite:///{BASE_DIR}/ASH-1.sqlite3"
)

# === Train ChatBot with Corpus ===
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train(str(BASE_DIR / "ash_corpus.yaml"))

# === Models ===
class ChatMessage(BaseModel):
    message: str

class InfoQuery(BaseModel):
    query: str

# === Routes ===
@app.get("/", response_class=HTMLResponse)
async def get_page(request: Request):
    return HTMLResponse(content=chat_html, status_code=200)

@app.post("/chat")
async def chat(msg: ChatMessage):
    reply = chatbot.get_response(msg.message)
    return JSONResponse(content={"response": str(reply)})

@app.post("/ask")
async def ask_info(q: InfoQuery):
    result = info_pipeline(q.query)
    return JSONResponse(content={
        "response": result["answer"],
        "sources": result["sources"]
    })

# === Run App ===
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)