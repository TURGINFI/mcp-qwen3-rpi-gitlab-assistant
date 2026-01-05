from dataclasses import dataclass

@dataclass
class LLMResult:
    text: str

class LightweightLLM:
    """
    Public demo: stubbed inference.
    In a private/local setup, this can be connected to an actual model runtime
    (e.g., running inference on Raspberry Pi).
    """
    def generate(self, prompt: str) -> LLMResult:
        # Stubbed response for demo purposes
        return LLMResult(text=f"[stubbed-llm] Received prompt: {prompt}")
