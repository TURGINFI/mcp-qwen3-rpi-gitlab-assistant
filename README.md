# MCP-Style Qwen3 GitLab Assistant on Raspberry Pi

This project is a proof-of-concept **on-premise AI assistant** that runs a quantized Qwen3-0.6B model on a **Raspberry Pi 5** using `llama.cpp`, and connects it to GitLab via an **MCP-style architecture**.

The goal is to explore how small organisations can use LLMs **inside their own network** without sending source code or NDA-protected data to external cloud services.

> In my original setup, I deployed and ran Qwen3-0.6B on a Raspberry Pi 5 using `llama.cpp` (inference only, no training).  
> This public repository contains a privacy-safe version with stubs and mocks for demonstration.

---

## What This Project Demonstrates

- **Local LLM inference on low-resource hardware**
  - Qwen3-0.6B (quantized GGUF) running on a Raspberry Pi 5 (8 GB) via `llama.cpp`.
  - CPU-only inference, suitable for small offices or student projects without GPUs.

- **MCP-style architecture**
  - Clear separation between:
    - `ai_model/` – AI model interface (stubbed in public repo; real setup talks to the local Qwen server),
    - `integrations/` – integration with Git services (mocked here; real setup used GitLab),
    - `mcp/` – orchestration layer that routes user requests to the model and tools.

- **Git service integration**
  - Public version includes a **mock Git service** that simulates listing repositories and creating issues.
  - In the private Raspberry Pi setup, this layer called the GitLab REST API and an MCP server to:
    - list all accessible projects,
    - fetch recent merge requests,
    - answer questions like “show me all my GitLab projects”.

- **Privacy-first design**
  - No model weights or GitLab tokens are committed to the repository.
  - Real integrations use environment variables (`GITLAB_TOKEN`, `GITLAB_BASE_URL`) on the Raspberry Pi.
  - All inference happens on-device; prompts and code never leave the local network.

---

## High-Level Architecture

```text
User CLI
   ↓
MCP Orchestrator (src/mcp/mcp_client.py, main.py)
   ↓                 ↓
AI Model Interface   Git Service Integration
(src/ai_model/)      (src/integrations/)

[Private Raspberry Pi setup]
   ↓
llama.cpp HTTP server → Qwen3-0_6b-q4_k_m.gguf (local model file)
GitLab REST API (via gitlab_mcp_server.py)
