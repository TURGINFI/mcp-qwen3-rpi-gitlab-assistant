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


To run the private Raspberry Pi setup, you need to:

1. Obtain the Qwen3-0.6B weights from the official Qwen distribution
   channels (e.g. Hugging Face or other providers), following their license.
2. Convert or download a quantized GGUF file, such as  
   `qwen3-0_6b-q4_k_m.gguf`.
3. Place the file under a local `models/` directory (not committed to Git),
   and point `llama.cpp` to it, for example:

   ```bash
   ./bin/llama-server \
     -m ../models/qwen3-0_6b-q4_k_m.gguf \
     -c 1024 \
     --port 9000




## Model Weights (not included in this repo)

This project was tested with the **Qwen3-0.6B** model.
The base weights were obtained from the official Qwen repository on Hugging Face (`Qwen/Qwen3-0.6B`), and then converted/downloaded as a quantized GGUF file (e.g. `qwen3-0_6b-q4_k_m.gguf`) for use with `llama.cpp`.

Since the model has not been fine-tuned for this specific project, its performance in user-facing interactions is still quite limited.

Model weights are **not** included in this repository and must be
downloaded separately from the official sources, following the Qwen license.



This project includes a minimal CI pipeline (GitHub Actions) to ensure
the core demo runs successfully in a clean environment.