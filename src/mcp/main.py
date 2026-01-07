from src.ai_model.model_stub import LightweightLLM
from src.integrations.git_service_mock import MockGitService
from src.mcp.mcp_client import MCPOrchestrator


def main() -> None:
    """Entry point for the public demo."""
    model = LightweightLLM()
    git_service = MockGitService()
    orchestrator = MCPOrchestrator()

    prompt = "Summarize today's UI tasks and create an issue."
    resp = orchestrator.run(prompt, model.generate, git_service)
    print(resp.message)


if __name__ == "__main__":
    main()