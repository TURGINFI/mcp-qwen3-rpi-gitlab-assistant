# Local Qwen3 GitLab Assistant on Raspberry Pi

A privacy-focused AI assistant prototype that runs Qwen3-0.6B locally on a Raspberry Pi 5 with `llama.cpp` and integrates with GitLab through a small MCP-style orchestration architecture.

This repository uses an **MCP-style / MCP-inspired architecture**: it separates model access, GitLab integration, and request orchestration. It is not a full implementation of the official Model Context Protocol specification.

**Key technologies:** Python, FastAPI, Qwen3-0.6B, `llama.cpp`, Raspberry Pi 5, GitLab REST API, GitHub Actions.

**Key idea:** keep prompts and repository metadata inside a local environment instead of sending them to a cloud LLM API. The public repository includes a safe demo mode that does not require model weights, a running Qwen server, or GitLab credentials.

![Chat UI showing the GitLab assistant](docs/images/chat-ui.png)

## What This Project Demonstrates

- A browser chat UI served by FastAPI.
- A local model client for a `llama.cpp` OpenAI-compatible chat endpoint.
- A GitLab REST API integration that reads projects using `GITLAB_TOKEN` and `GITLAB_BASE_URL`.
- A public demo mode using deterministic stub responses and mock GitLab data.
- A simplified custom orchestration layer in `src/mcp/` that demonstrates MCP-style flow without claiming official MCP protocol support.
- A minimal GitHub Actions workflow that compiles the Python source and imports core modules.

## Repository

```bash
git clone https://github.com/wenhangong/mcp-qwen3-rpi-gitlab-assistant.git
cd mcp-qwen3-rpi-gitlab-assistant
```

## Current Implementation

The web application path is:

```text
Browser UI
  -> FastAPI backend (src/web/server.py)
  -> simple request routing
  -> optional GitLab REST summary fetcher
  -> model backend
       - demo mode: deterministic local stub
       - local mode: llama.cpp HTTP server running Qwen3-0.6B
```

The standalone orchestration demo is:

```text
src/mcp/main.py
  -> MCPOrchestrator (src/mcp/mcp_client.py)
  -> LightweightLLM stub
  -> MockGitService
```

The `src/mcp/` package is intentionally small. It shows the project structure and routing idea, while the production-like web flow currently lives in `src/web/server.py`.

## Screenshots

![Chat UI with GitLab project summary](docs/images/chat-ui.png)

![Raspberry Pi runtime terminals](docs/images/raspberry-pi-runtime.png)

## 1. Public Demo Mode

Use this mode for GitHub review, portfolio demos, and local smoke testing. It does not call GitLab and does not require Qwen or `llama.cpp`.

### Requirements

- Python 3.10+ (tested with Python 3.11 in CI)
- `git`

### Run

```bash
git clone https://github.com/wenhangong/mcp-qwen3-rpi-gitlab-assistant.git
cd mcp-qwen3-rpi-gitlab-assistant

python3 -m venv mcp_venv
source mcp_venv/bin/activate
python -m pip install -r requirements.txt

ASSISTANT_MODE=demo python -m src.web.server
```

Then open:

- <http://localhost:7000> when running locally
- `http://<raspberry-pi-ip>:7000` when running on a Raspberry Pi

In demo mode, GitLab-related questions are answered from mock project data and general questions use a deterministic stub response.

You can also run the small CLI orchestration demo:

```bash
python -m src.mcp.main
```

## 2. Private Raspberry Pi Setup

This mode uses a local Qwen3-0.6B model server and real GitLab API calls.

### Prepare Python

```bash
git clone https://github.com/wenhangong/mcp-qwen3-rpi-gitlab-assistant.git
cd mcp-qwen3-rpi-gitlab-assistant

python3 -m venv mcp_venv
source mcp_venv/bin/activate
python -m pip install -r requirements.txt
```

### Prepare Qwen3-0.6B with llama.cpp

1. Download Qwen3-0.6B from the official Qwen distribution, such as Hugging Face `Qwen/Qwen3-0.6B`, following the model license.
2. Convert or download a quantized GGUF file, for example `qwen3-0_6b-q4_k_m.gguf`.
3. Store model files outside git, for example under `~/models/`.
4. Build `llama.cpp` on the Raspberry Pi and start the HTTP server:

```bash
~/llama.cpp/build/bin/llama-server \
  -m ~/models/qwen3-0_6b-q4_k_m.gguf \
  -c 1024 \
  --port 9000 \
  --host 0.0.0.0
```

Keep that process running in a separate terminal.

### Configure GitLab and Runtime Environment

Store secrets outside the repository, for example in `~/.secrets`:

```bash
export ASSISTANT_MODE="local"
export GITLAB_TOKEN="<paste your GitLab personal access token>"
export GITLAB_BASE_URL="https://gitlab.com"
export QWEN_API_URL="http://127.0.0.1:9000/v1/chat/completions"
export QWEN_MODEL_NAME="qwen3-0.6b"
```

Then protect and load the file:

```bash
chmod 600 ~/.secrets
echo 'source ~/.secrets' >> ~/.bashrc
source ~/.secrets
```

If you change the token or its scopes later, reload the environment and restart the backend:

```bash
source ~/.secrets
pkill -f "src.web.server"
python -m src.web.server
```

### Start the Web Backend

```bash
cd ~/mcp-qwen3-rpi-gitlab-assistant
source mcp_venv/bin/activate
source ~/.secrets
python -m src.web.server
```

By default, FastAPI listens on `0.0.0.0:7000`.

Open:

```text
http://<raspberry-pi-ip>:7000
```

Example questions:

- "How many GitLab projects do I have?"
- "Show me all project names."
- "Which repositories were created most recently?"

When a question looks GitLab-related, the backend fetches project metadata through the GitLab REST API, injects a factual summary into the prompt, and sends that prompt to the local Qwen endpoint.

## Model Weights

Model weights are not included in this repository.

The project was tested with Qwen3-0.6B as a quantized GGUF model served by `llama.cpp`. The model was used for local inference only and was not fine-tuned for this project.

## Security and Privacy

- No GitLab tokens, model weights, or private GitLab data are committed.
- Secrets are read from environment variables.
- `GITLAB_TOKEN` is required only for real GitLab mode.
- `GITLAB_BASE_URL` defaults to `https://gitlab.com` and can point to a self-hosted GitLab instance.
- `.gitignore` excludes common local env files, virtual environments, local model directories, and model weight file extensions.
- Tokens are never sent to the browser. Browser requests go to the local FastAPI backend.

## Validation

The repository includes a minimal CI workflow in `.github/workflows/ci.yml`:

```bash
python -m compileall -q src
python -c "import importlib; [importlib.import_module(m) for m in ['src.web.server', 'src.ai_model.qwen_client', 'src.integrations.gitlab_client', 'src.mcp.mcp_client', 'src.mcp.main']]"
```

For a local public demo smoke test:

```bash
ASSISTANT_MODE=demo python -m src.web.server
```

Then open <http://localhost:7000> and ask a GitLab-related question. The response should clearly say it is using mock GitLab data.

## Tooling and AI Assistance

Parts of the documentation, UI text, and scaffolding were written with AI assistance. The repository keeps the implementation and setup notes explicit so reviewers can verify what is running in demo mode and what is required for private local mode.
