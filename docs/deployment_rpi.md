# Raspberry Pi + Qwen3-0.6B Setup Notes

These notes describe the private local setup with real GitLab access and Qwen3-0.6B served by `llama.cpp`.

## Clone and Install

```bash
git clone https://github.com/wenhangong/mcp-qwen3-rpi-gitlab-assistant.git
cd mcp-qwen3-rpi-gitlab-assistant

python3 -m venv mcp_venv
source mcp_venv/bin/activate
python -m pip install -r requirements.txt
```

## Environment Variables

Keep secrets outside the repository, for example in `~/.secrets`:

```bash
export ASSISTANT_MODE="local"
export GITLAB_TOKEN="<paste your GitLab personal access token>"
export GITLAB_BASE_URL="https://gitlab.com"
export QWEN_API_URL="http://127.0.0.1:9000/v1/chat/completions"
export QWEN_MODEL_NAME="qwen3-0.6b"
```

Load the file before starting the backend:

```bash
chmod 600 ~/.secrets
source ~/.secrets
```

If you update the token or change token scopes, reload the file and restart the backend:

```bash
source ~/.secrets
pkill -f "src.web.server"
python -m src.web.server
```

## Start the Local Model Server

Example `llama.cpp` command:

```bash
~/llama.cpp/build/bin/llama-server \
  -m ~/models/qwen3-0_6b-q4_k_m.gguf \
  -c 1024 \
  --port 9000 \
  --host 0.0.0.0
```

Keep this running in a separate terminal.

## Start the Web Backend

```bash
cd ~/mcp-qwen3-rpi-gitlab-assistant
source mcp_venv/bin/activate
source ~/.secrets
python -m src.web.server
```

Open `http://<raspberry-pi-ip>:7000` from a browser on the same network.

## Public Demo Mode

For a safe demo without Qwen or GitLab:

```bash
ASSISTANT_MODE=demo python -m src.web.server
```
