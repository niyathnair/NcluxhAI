import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from core.logger import LOGGER
import yaml
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
        prompts = {}
        try:
            for file in self.prompts_dir.glob("*.yaml"):
                LOGGER.debug(f"Loading prompts from file: {file}")
                with open(file, "r") as f:
                    file_prompts = yaml.safe_load(f)
                    if file_prompts:  # Check if file is not empty
                        LOGGER.debug(f"Prompts found in {file}: {list(file_prompts.keys())}")
                        prompts.update(file_prompts)
                    else:
                        LOGGER.warning(f"No valid YAML content found in {file}")
            
            if not prompts:
                LOGGER.error("No prompts were loaded from any files")
                
            return prompts
            
        except Exception as e:
            LOGGER.error(f"Error loading prompts: {str(e)}")
            return {}  # Return empty dict instead of raising error

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
