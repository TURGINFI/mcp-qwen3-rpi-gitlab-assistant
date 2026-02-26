# src/web/server.py

from __future__ import annotations

from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.ai_model.qwen_client import call_qwen_chat
from src.integrations.gitlab_client import list_gitlab_projects_via_rest


# ----------------- FastAPI app & static frontend -----------------

app = FastAPI()

# This file is src/web/server.py
BASE_DIR = Path(__file__).resolve().parent          # = src/web
FRONTEND_DIR = BASE_DIR / "static"                  # = src/web/static

# /static/... -> serve files from src/web/static/...
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ----------------- Request / Response models -----------------


class ChatRequest(BaseModel):
    # Browser sends this JSON: { "message": "..." }
    message: str


class ChatResponse(BaseModel):
    # Backend returns this JSON: { "reply": "...", "used_gitlab": true/false }
    reply: str
    used_gitlab: bool = False


# ----------------- Front page: return index.html -----------------


@app.get("/")
async def index() -> FileResponse:
    """Return the HTML UI (new nice page)."""
    return FileResponse(FRONTEND_DIR / "index.html")


# ----------------- Chat endpoint: simple keyword routing -----------------


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """
    Main entry for browser chat.

    Very simple logic:
    - If user message looks like asking GitLab projects, we call GitLab REST
      and then ask Qwen to summarize.
    - Otherwise, just normal Qwen chat.
    """
    user_msg = req.message.strip()
    if not user_msg:
        return ChatResponse(reply="Please type something first.", used_gitlab=False)

    text_lower = user_msg.lower()

    # Very naive keyword check. For real project you can design better intent logic.
    ask_gitlab = (
        "gitlab" in text_lower
        or "project" in text_lower
        or "projects" in text_lower
        or "项目" in user_msg  # user maybe type Chinese
    )

    if ask_gitlab:
        # ---- branch 1: call GitLab REST API ----
        try:
            projects: List[str] = list_gitlab_projects_via_rest()
        except Exception as e:  # noqa: BLE001
            # If GitLab request fails, we still give friendly answer
            return ChatResponse(
                reply=f"I tried to call GitLab API but got error: {e}",
                used_gitlab=True,
            )

        if not projects:
            reply_text = "I did not find any GitLab projects for this user."
        else:
            project_list_str = "\n".join(f"- {name}" for name in projects)

            system_prompt = (
                "You are an internal assistant for GitLab usage. "
                "User will ask about their GitLab projects. "
                "You receive a list of project names. "
                "You answer shortly and friendly, tell how many projects and list names. "
                "If user message is Chinese, you can answer in Chinese."
            )

            qwen_reply = call_qwen_chat(
                [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": (
                            f"User question: {user_msg}\n\n"
                            f"Here are the GitLab projects:\n{project_list_str}"
                        ),
                    },
                ]
            )
            reply_text = (
                qwen_reply
                or "GitLab projects fetched, but model did not return content."
            )

        return ChatResponse(reply=reply_text, used_gitlab=True)

    # ---- branch 2: normal small-talk Qwen chat ----
    system_prompt = (
        "You are a small local Qwen3-0.6B model running on a Raspberry Pi. "
        "Answer in a clear and short way. If user writes in Chinese, reply in Chinese."
    )
    qwen_reply = call_qwen_chat(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg},
        ]
    )

    return ChatResponse(reply=qwen_reply, used_gitlab=False)


# ----------------- Local run entry -----------------

if __name__ == "__main__":
    import uvicorn

    # host=0.0.0.0 so you can open page from Windows browser in same LAN
    uvicorn.run(
        "src.web.server:app",
        host="0.0.0.0",
        port=7000,
        reload=False,
    )