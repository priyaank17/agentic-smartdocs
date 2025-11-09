"""Utilities for loading Paligemma on vLLM."""

from typing import Optional

from vllm import LLM, SamplingParams

from src.config.settings import get_settings

settings = get_settings()


class PaligemmaModel:
    def __init__(self) -> None:
        tensor_parallel = int(settings.paligemma_lora_path is not None) or 1
        self.llm = LLM(
            model=settings.paligemma_model_name,
            enable_lora=(settings.paligemma_lora_path is not None),
            lora_modules=[settings.paligemma_lora_path] if settings.paligemma_lora_path else None,
            tensor_parallel_size=tensor_parallel,
        )
        self.sampling = SamplingParams(temperature=0.0, max_tokens=2048)

    def generate(self, prompt: str) -> str:
        outputs = self.llm.generate(prompt, self.sampling)
        return outputs[0].outputs[0].text


model_singleton: Optional[PaligemmaModel] = None


def get_model() -> PaligemmaModel:
    global model_singleton
    if model_singleton is None:
        model_singleton = PaligemmaModel()
    return model_singleton
