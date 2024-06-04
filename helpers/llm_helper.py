import ollama
from config import Config

system_prompt = Config.SYSTEM_PROMPT

def chat(user_prompt, model, history):
    # Ajoute le message système une seule fois au début de l'historique
    messages = [{'role': 'assistant', 'content': system_prompt}] + history
    messages.append({'role': 'user', 'content': f"Model being used is {model}. {user_prompt}"})
    
    stream = ollama.chat(
        model=model,
        messages=messages,
        stream=True,
    )

    return stream

# handles stream response back from LLM
def stream_parser(stream):
    response_content = ""
    for chunk in stream:
        response_content += chunk['message']['content']
        yield response_content
