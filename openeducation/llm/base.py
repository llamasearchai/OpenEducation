class LLM:
    def answer(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError

    def structured(self, prompt: str, schema: dict) -> dict:
        raise NotImplementedError
