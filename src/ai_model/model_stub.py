# src/ai_model/model_stub.py

class LightweightLLM:
    """A tiny stub model for public demo / CI."""
    def generate(self, prompt: str) -> str:
        return f"[stub] You said: {prompt}"