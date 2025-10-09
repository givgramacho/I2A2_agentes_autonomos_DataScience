# src/langsmith_setup.py
import os
from langsmith import Client

def get_langsmith_client():
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        return None
    client = Client(api_key=api_key)
    return client
