from pydantic import BaseSettings

class ModelConfig(BaseSettings):
    primary_llm: str = "Llama-3"
    secondary_llm: str = "Mistral"
    task_specific_models: dict = {
        "task1": "ModelA",
        "task2": "ModelB"
    }

    class Config:
        env_file = ".env"
