from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
import textwrap

app = FastAPI()

class TextRequest(BaseModel):
    text: str

def call_openrouter(messages):
    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",  # Required for free usage
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": messages
    }

    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

@app.post("/summarize")

def summarize(request: TextRequest):
    try:
        #breaking the long texts into chunks to summarize each section
        chunks = textwrap.wrap(request.text, width=1500, break_long_words=False, replace_whitespace=False)

        summaries = []
        for chunk in chunks:
            msg = [
                {"role": "system", "content": "Summarize the following text clearly and concisely."},
                {"role": "user", "content": chunk}
            ]
            summaries.append(call_openrouter(msg))

        if len(summaries) == 1:
            return {"summary": summaries[0]}

        combined_summary_text = "\n\n".join(summaries)
        final_msg = [
            {"role": "system", "content": "Summarize these points into a clear, concise summary of the original full text."},
            {"role": "user", "content": combined_summary_text}
        ]
        
        final_summary = call_openrouter(final_msg)
        return {"summary": final_summary}

    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {str(e)}"}

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
