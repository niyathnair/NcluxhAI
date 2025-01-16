from typing import Dict, Any

def get_agent_config(ai_model: str = "gpt-4") -> Dict[str, Any]:
    """Get agent configuration based on AI model."""
    return {
        'model': ai_model,
        'config_list': [{'model': ai_model}]
    }

# Default config
AGENT_CONFIG = get_agent_config()