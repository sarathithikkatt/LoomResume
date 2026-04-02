
class LLMService:
    async def generate(self, prompt: str, provider: str):
        if provider == "openai":
            return await self.openai_call(prompt)
        elif provider == "claude":
            return await self.claude_call(prompt)
        elif provider == "ollama":
            return await self.ollama_call(prompt)