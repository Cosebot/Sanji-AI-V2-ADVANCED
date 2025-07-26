from chatterbot import ChatBot

chatbot = ChatBot(
    "ASH-1",
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///main/ASH-1.sqlite3'  # Path relative to current script
)