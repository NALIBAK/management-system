import requests as http_requests
from app.db import query

def get_selected_model():
    """Fetch the selected model from the llm_config table."""
    config = query("SELECT selected_model FROM llm_config LIMIT 1", fetchone=True)
    return config["selected_model"] if config else "gemma3:1b"

def safe_ping_model(model_name):
    """Verify if the model is actually pulled in Ollama."""
    try:
        resp = http_requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            return model_name in models
        return False
    except:
        return False

def call_ollama_ai(system_prompt, messages, model=None):
    """
    Call Ollama with resource protection and safe ping.
    - num_ctx hard-capped to 4096.
    - history capped to last 5 messages.
    """
    if not model:
        model = get_selected_model()

    # Safe Ping
    if not safe_ping_model(model):
        try:
            available_resp = http_requests.get("http://localhost:11434/api/tags", timeout=5)
            available = [m["name"] for m in available_resp.json().get("models", [])]
            return f"❌ Model '{model}' is not found in your Ollama installation. Available models: {', '.join(available)}"
        except:
            return f"❌ Model '{model}' is not found and Ollama appears to be offline."

    # Resource Protection: History Limit
    history = messages[-5:] if len(messages) > 5 else messages

    try:
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": system_prompt}] + history,
            "stream": False,
            "options": {
                "num_ctx": 4096
            }
        }
        resp = http_requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except Exception as e:
        return f"Ollama Error: {str(e)}"
