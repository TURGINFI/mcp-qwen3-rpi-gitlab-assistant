# MCP-Style Qwen3 GitLab Assistant on Raspberry Pi

This project is a proof-of-concept **on-premise AI assistant** that runs a quantized Qwen3-0.6B model on a **Raspberry Pi 5** using `llama.cpp`, and connects it to GitLab through an **MCP-style architecture**.

The goal is to explore how small organisations can use LLMs **inside their own network** without sending source code or NDA-protected data to external cloud services.

> In my original setup, I deployed and ran Qwen3-0.6B on a Raspberry Pi 5 using `llama.cpp` (inference only, no training).  
> This public repository contains a privacy-safe version with stubs and mocks for demonstration.

---

## What This Project Demonstrates

- **Local LLM inference on low-resource hardware**
  - Qwen3-0.6B (quantized GGUF) running on Raspberry Pi 5 (8 GB) via `llama.cpp`.
  - CPU-only inference, suitable for small offices or student projects without GPUs.

- **MCP-style architecture**
  - Clear separation between three layers:
    - `src/ai_model/` – AI model interface  
      (stubbed in the public repo; real setup talks to the local Qwen HTTP server).
    - `src/integrations/` – integration with Git services  
      (mocked in the public repo; real setup used the GitLab REST API).
    - `src/mcp/` – orchestration layer that routes user requests to the model and tools.

- **Git service integration**
  - Public version includes a **mock Git service** that simulates listing repositories and creating issues.
  - On Raspberry Pi, the backend calls the **GitLab REST API** to:
    - list all accessible projects,
    - fetch basic project metadata,
    - answer questions like “show me all my GitLab projects”.

- **Browser-based internal chat UI**
  - A small frontend served by FastAPI (`src/web/server.py`) provides a web chat console.
  - User types questions like “How many GitLab projects do I have?” and the backend:
    1. Calls GitLab (if needed),
    2. Sends the result into Qwen3-0.6B,
    3. Returns a friendly natural-language answer.

- **Privacy-first design**
  - No model weights or GitLab tokens are committed to the repository.
  - Real integrations use environment variables (`GITLAB_TOKEN`, optional `GITLAB_BASE_URL`) on the Raspberry Pi.
  - All inference happens on-device; prompts and code never leave the local network.

---

## Model Weights (not included in this repo)

- This project was tested with the **Qwen3-0.6B** model.
- The base weights were obtained from the official Qwen repository on Hugging Face  
  (`Qwen/Qwen3-0.6B`), and then converted/downloaded as a quantized GGUF file  
  (for example: `qwen3-0_6b-q4_k_m.gguf`) for use with `llama.cpp`.
- The model has **not** been fine-tuned for this specific project, so its performance in
  user-facing interactions is intentionally limited.
- Model weights are **not** included in this repository and must be downloaded separately
  from the official sources, following the Qwen license.

This project also includes a minimal CI pipeline (GitHub Actions) to ensure the core demo
runs successfully in a clean environment.

---

## High-Level Architecture

```text
[Browser UI]
   ↓  HTTP (port 7000)
FastAPI backend (src/web/server.py)
   ↓
MCP-style Orchestrator (src/mcp/mcp_client.py)
   ↓                 ↓
AI Model Interface   Git Service Integration
(src/ai_model/)      (src/integrations/)

[Private Raspberry Pi setup]
   ↓
llama.cpp HTTP server  →  Qwen3-0_6b-q4_k_m.gguf (local model file)
GitLab REST API        →  using GITLAB_TOKEN / GITLAB_BASE_URL
```

---

## Screenshots (optional)

You can insert screenshots here, for example:

```markdown
![Chat UI running on Raspberry Pi](docs/screenshot-chat-ui.png)
```

---

## 1. Running the Public Demo (no secrets, no real GitLab)

This mode is designed for GitHub and classroom demos.
It uses stubbed model logic and a mock Git service – **no tokens and no real repositories**.

### Requirements

* Python 3.10+ (tested with 3.11)
* `git`

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-name>/MCP-QWEN3-RPi-GitLab-Assistant.git
cd MCP-QWEN3-RPi-GitLab-Assistant

# 2. Create and activate virtual environment
python -m venv mcp_venv
source mcp_venv/bin/activate    # Windows: mcp_venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the web backend (mock mode)
python -m src.web.server
```

Then open in your browser:

* [http://localhost:7000](http://localhost:7000) (if running on your laptop), or
* <http://<raspberry-pi-ip>:7000> (if running on the Pi).

In this mode:

* Qwen3 and GitLab are **not required**.
* Responses are generated from simple stubs so the UI and flow can be demonstrated safely.

---

## 2. Full Private Setup on Raspberry Pi (Qwen3 + GitLab)

This is the **real** internal setup used on my Raspberry Pi 5.

### 2.1 Prepare the repository and Python environment

On the Raspberry Pi:

```bash
git clone https://github.com/<your-name>/MCP-QWEN3-RPi-GitLab-Assistant.git
cd MCP-QWEN3-RPi-GitLab-Assistant

python -m venv mcp_venv
source mcp_venv/bin/activate
pip install -r requirements.txt
```

### 2.2 Prepare Qwen3-0.6B with `llama.cpp`

1. Download the original Qwen3-0.6B weights from the official Qwen distribution
   (e.g. Hugging Face `Qwen/Qwen3-0.6B`), following their license.

2. Convert or download a quantized GGUF file, such as:

   ```text
   qwen3-0_6b-q4_k_m.gguf
   ```

3. Place the file under a local `models/` directory (this directory is **not** in git):

   ```bash
   mkdir -p ~/models
   mv qwen3-0_6b-q4_k_m.gguf ~/models/
   ```

4. Build `llama.cpp` on the Pi and start the HTTP server, for example:

   ```bash (sometimes it is better to use absolute path to start the HTTP server)
   ~/llama.cpp/build/bin/llama-server -m ~/llama.cpp/models/qwen3-0_6b-q4_k_m.gguf -c 1024 --port 9000 --host 0.0.0.0
   ```

   Keep this process running in its own terminal window.

### 2.3 Configure GitLab token (environment only)

Create a small secrets file in your home directory **outside the repo**:

```bash
nano ~/.secrets
```

Example content (replace with your real values):

```bash
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"
export GITLAB_BASE_URL="https://gitlab.com"   # or your self-hosted URL
```

Then lock down the file and load it from your shell:

```bash
chmod 600 ~/.secrets

# Add this line once to the end of ~/.bashrc
echo 'source ~/.secrets' >> ~/.bashrc

# Reload current shell session
source ~/.bashrc
```
**Note that once the token is modified based on the change of the token's scope, these command must be executed"
source ~/.secrets
pkill -f "src.web.server" 
python -m src.web.server


**Important security note**

* `~/.secrets` and `~/.bashrc` are in your home directory, not in the project folder,
  so they are **not** tracked by git.
* Never write `GITLAB_TOKEN` or other secrets into the repository,
  and never commit any `.env`, `config.yaml`, or log files that contain tokens.

### 2.4 Start the MCP-style backend

Back in the project directory on the Pi:

```bash
cd ~/MCP-QWEN3-RPi-GitLab-Assistant
source mcp_venv/bin/activate
python -m src.web.server
```

By default this runs FastAPI on **port 7000**, listening on `0.0.0.0`.

### 2.5 Open the chat UI

From a browser on the Raspberry Pi, or from another machine in the same network:


```text
http://<raspberry-pi-ip>:7000
```

Now you can ask questions like:

* “How many GitLab projects do I have?”
* “Show me all project names.”
* “Tell me who is in charge of the projects.”
![alt text](image.png) 

The flow is:

1. Browser → sends your question to `/chat` on the FastAPI backend.
2. Backend → decides whether this is a GitLab question.
3. If yes, it calls GitLab REST API using `GITLAB_TOKEN`, then passes the result into Qwen.
4. Qwen3-0.6B generates a short answer, which is sent back to the browser.

---

## 3. What Needs to Be Running?

When you interact with GitLab through the model, you **only** need:

1. **Qwen HTTP server** (via `llama.cpp`)

   * Listens on `http://127.0.0.1:9000/v1/chat/completions`
   * Uses the local `qwen3-0_6b-q4_k_m.gguf` file.

2. **FastAPI backend** (`python -m src.web.server`)

   * Listens on `http://0.0.0.0:7000`
   * Serves the HTML/JS frontend and handles all Qwen + GitLab integration.
![alt text](image-1.png)
You do **not** need to run any extra Python scripts like experimental
`qwen_gitlab_demo.py` during the demo; those are kept locally and are ignored by git.

GitLab itself runs as usual (cloud GitLab or self-hosted).
All requests go from the Raspberry Pi backend → GitLab API over HTTPS.

---

## 4. Security & Privacy Notes

* GitLab access uses a **personal access token** stored in shell environment variables.
* No tokens, secrets, or model weights are included in this public repository.
* The recommended flow is:

  * keep secrets in `~/.secrets`,
  * `source ~/.secrets` from `~/.bashrc`,
  * never commit those files.
* All AI inference happens on the Raspberry Pi; prompts and repository metadata
  stay inside your network.

---

## 5. Tooling & AI Assistance

* Backend: Python, FastAPI, `requests`
* Frontend: Plain HTML + CSS + vanilla JS (served as static files)
* Local model runtime: `llama.cpp` on Raspberry Pi
* Git service: GitLab REST API
* CI: GitHub Actions (basic “can this run in a clean environment” check)

Part of the documentation, UI text, and scaffolding code was written with the help of AI
tools (for example ChatGPT).
All code, configuration, and deployment steps were reviewed and tested by me on my own
Raspberry Pi 5.