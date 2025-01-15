from core.logger import LOGGER
import yaml
from pathlib import Path

PROMPTS_DIR = "core/prompts/templates"


class PromptManager:
    _instance = None

    def __new__(cls, prompts_dir: str = PROMPTS_DIR):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.prompts_dir = Path(prompts_dir)
            cls._instance.prompts = cls._instance._load_prompts()
        return cls._instance

    def _load_prompts(self):
        if not hasattr(self, "prompts"):
            prompts = {}
            for file in self.prompts_dir.glob("*.yaml"):
                LOGGER.debug(f"Loading prompts from file: {file}")
                with open(file, "r") as f:
                    file_prompts = yaml.safe_load(f)
                    LOGGER.debug(
                        f"Prompts found in {file}: {list(file_prompts.keys())}"
                    )
                    prompts.update(file_prompts)
            LOGGER.info("Prompt templates loaded successfully")
            return prompts
        return self.prompts

    def get_prompt(self, key: str, **kwargs):
        prompt_data = self.prompts.get(key)
        if prompt_data is None:
            raise KeyError(f"Prompt '{key}' not found")

        template = prompt_data["template"]
        variables = prompt_data["variables"].copy()
        variables.update(kwargs)

        return template.format(**variables)


# Create a single instance to be used throughout the application
prompt_manager = PromptManager()
