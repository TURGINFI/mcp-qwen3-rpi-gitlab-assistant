# Architecture Overview

This repository uses an MCP-style architecture: model access, GitLab integration, and orchestration are separated into small modules. It is a simplified custom design, not a full implementation of the official Model Context Protocol.

## Web Application Flow

```text
Browser UI
  -> FastAPI backend (src/web/server.py)
  -> request routing
  -> GitLab summary fetcher, when needed
  -> model backend
```

The web backend has two runtime modes:

- `ASSISTANT_MODE=demo`: uses deterministic stub responses and mock GitLab data.
- `ASSISTANT_MODE=local`: calls the local `llama.cpp` Qwen endpoint and, for GitLab-related questions, the GitLab REST API.

## Modules

### AI model module

`src/ai_model/` contains:

- `qwen_client.py`: calls a local OpenAI-compatible `llama.cpp` chat endpoint.
- `model_stub.py`: provides a deterministic stub for public demos and smoke tests.

### Integrations

`src/integrations/gitlab_client.py` contains:

- environment helpers for `GITLAB_TOKEN` and `GITLAB_BASE_URL`
- a small GitLab REST project-listing helper
- `MockGitService` for the standalone orchestration demo

### MCP-style module

`src/mcp/` contains a small orchestration demo:

- `mcp_client.py`: routes a prompt through a model function and Git service object.
- `main.py`: runs the demo with `LightweightLLM` and `MockGitService`.

This module demonstrates the architectural idea but does not implement the official MCP protocol.

### Web entry point

`src/web/server.py` serves the static frontend and implements the practical chat workflow used by the browser UI.
