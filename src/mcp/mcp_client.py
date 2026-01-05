from dataclasses import dataclass

@dataclass
class MCPResponse:
    message: str

class MCPOrchestrator:
    """
    Simplified orchestrator representing MCP-style flow:
    prompt -> model -> tool/integration.
    """
    def run(self, prompt: str, model_generate, git_service) -> MCPResponse:
        llm_result = model_generate(prompt)
        repos = git_service.list_repos()
        issue_url = git_service.create_issue(
            repo_name=repos[0].name,
            title="AI-generated summary",
            body=llm_result.text
        )
        return MCPResponse(message=f"Created issue (mock): {issue_url}")
