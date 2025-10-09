# src/memory_store.py
import os
from langchain.memory import ConversationBufferMemory
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

def init_memory(chroma_persist_dir="chroma_store"):
    # Conversation buffer for short-term
    buffer = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Vectorstore for long-term memory (requires embeddings)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # fallback: no embeddings available; return only buffer
        return {"buffer": buffer, "vectorstore": None}
    embeddings = OpenAIEmbeddings(openai_api_key=api_key)
    vect = Chroma(persist_directory=chroma_persist_dir, embedding_function=embeddings)
    return {"buffer": buffer, "vectorstore": vect}

