# src/web/server.py

from __future__ import annotations

import os
import requests
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.ai_model.qwen_client import call_qwen_chat

# ----------------- FastAPI app & static frontend -----------------

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent          # = src/web
FRONTEND_DIR = BASE_DIR / "static"                  # = src/web/static

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# ----------------- Helper: GitLab API Fetcher -----------------
# Added directly here to solve the "hallucination" issue immediately.
# Make sure to set your actual GitLab URL and Token below!

GITLAB_URL = os.getenv("GITLAB_URL", "https://gitlab.com")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "YOUR_GITLAB_TOKEN_HERE") 

def get_enhanced_gitlab_summary() -> str:
    """
    Fetches detailed project info: counts, oldest, newest, creators, and file trees.
    Returns a summarized string formatted for the 0.6B LLM so it doesn't have to guess.
    """
    if GITLAB_TOKEN == "YOUR_GITLAB_TOKEN_HERE":
        return "System Warning: GITLAB_TOKEN is not configured in the backend."

    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    
    try:
        # 1. Fetch projects (membership=true ensures we only get user's relevant projects)
        resp = requests.get(f"{GITLAB_URL}/api/v4/projects?membership=true&simple=false", headers=headers, timeout=10)
        resp.raise_for_status()
        projects = resp.json()
        
        if not projects:
            return "No GitLab projects found for this user."

        # 2. Sort by creation date (created_at is ISO 8601 format)
        projects_sorted = sorted(projects, key=lambda x: x.get('created_at', ''))
        
        total_count = len(projects_sorted)
        oldest = projects_sorted[0]
        newest = projects_sorted[-1]

        # 3. Build the factual summary string for the LLM
        summary_lines = [
            f"Total projects: {total_count}",
            f"Oldest project: '{oldest.get('name')}' created on {oldest.get('created_at')}",
            f"Newest project: '{newest.get('name')}' created on {newest.get('created_at')}",
            "\nDetailed Project List:"
        ]

        # LIMIT: Only process the first 5 projects to avoid blowing up the 0.6B context window
        for p in projects_sorted[:5]:
            project_id = p.get('id')
            name = p.get('name')
            creator = p.get('namespace', {}).get('name', 'Unknown')
            
            # Fetch file tree for each project
            tree_resp = requests.get(f"{GITLAB_URL}/api/v4/projects/{project_id}/repository/tree", headers=headers, timeout=5)
            
            if tree_resp.status_code == 200:
                files_data = tree_resp.json()
                file_names = [item['name'] for item in files_data]
                file_count = len(file_names)
                
                # Limit file display to avoid massive prompts
                files_str = ", ".join(file_names[:10])
                if file_count > 10:
                    files_str += f" (...and {file_count - 10} more)"
            else:
                file_count = 0
                files_str = "Could not read files (empty repo or lack of permissions)"

            summary_lines.append(
                f"- Project '{name}' (Created by {creator}): Contains {file_count} root files/folders. Files: {files_str}."
            )

        if total_count > 5:
            summary_lines.append(f"\n* Note to AI: Only the first 5 projects are shown to save memory.")

        return "\n".join(summary_lines)

    except Exception as e:
        return f"Failed to fetch detailed GitLab data: {str(e)}"


# ----------------- Request / Response models -----------------

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    # The frontend now sends the previous messages here
    history: List[ChatMessage] = [] 

class ChatResponse(BaseModel):
    reply: str
    used_gitlab: bool = False


# ----------------- Front page: return index.html -----------------

@app.get("/")
async def index() -> FileResponse:
    """Return the HTML UI."""
    return FileResponse(FRONTEND_DIR / "index.html")


# ----------------- Chat endpoint -----------------

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """
    Main entry for browser chat. Now supports history injection and detailed GitLab facts.
    """
    user_msg = req.message.strip()
    if not user_msg:
        return ChatResponse(reply="Please type something first.", used_gitlab=False)

    text_lower = user_msg.lower()

    # Simple keyword trigger
    ask_gitlab = (
        "gitlab" in text_lower
        or "project" in text_lower
        or "projects" in text_lower
        or "项目" in user_msg
        or "merge" in text_lower
        or "commit" in text_lower
    )

    # Prepare the array of messages we will send to Qwen
    messages_for_qwen = []

    if ask_gitlab:
        # ---- branch 1: call enhanced GitLab REST API ----
        gitlab_data_str = get_enhanced_gitlab_summary()

        # The system prompt now forces the model to look at the exact text we injected
        system_prompt = (
            "You are an internal assistant for GitLab usage. "
            "Answer the user's questions based ONLY on the provided GitLab facts below. "
            "Do not invent or guess file numbers or names. Keep answers short, clear, and friendly.\n\n"
            f"### GITLAB FACTS ###\n{gitlab_data_str}\n####################"
        )
        
        messages_for_qwen.append({"role": "system", "content": system_prompt})
        used_gitlab = True

    else:
        
        system_prompt = (
            "You are a small local Qwen3-0.6B model running on a Raspberry Pi. "
            "Answer in a clear and short way. Be helpful and polite."
        )
        messages_for_qwen.append({"role": "system", "content": system_prompt})
        used_gitlab = False

    # Inject the conversation history from the frontend
    for msg in req.history:
        messages_for_qwen.append({"role": msg.role, "content": msg.content})

    # Finally, add the user's newest message
    messages_for_qwen.append({"role": "user", "content": user_msg})

    # Send the whole package to the model
    try:
        qwen_reply = call_qwen_chat(messages_for_qwen)
        reply_text = qwen_reply or "Model processed the request but returned an empty response."
    except Exception as e:
        reply_text = f"Error communicating with local Qwen model: {str(e)}"

    return ChatResponse(reply=reply_text, used_gitlab=used_gitlab)


# ----------------- Local run entry -----------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.web.server:app",
        host="0.0.0.0",
        port=7000,
        reload=False,
    )