import asyncio
import logging
import autogen
from core.config.agent import get_agent_config
from core.prompts.manager import prompt_manager



class BaseAgent:
    def __init__(self, agent_name: str, system_prompt_key: str, ai_model: str = "gpt-4"):
        self.loop = asyncio.get_event_loop()
        try:
            system_message = prompt_manager.get_prompt(system_prompt_key)
        except KeyError:
            logging.error(
                f"Error: '{system_prompt_key}' prompt not found. Please check your YAML files in the prompts directory."
            )
            raise
        agent_config = get_agent_config(ai_model)
        self.agent = autogen.AssistantAgent(
            name=agent_name,
            llm_config={"config_list": agent_config["config_list"]},
            system_message=system_message,
        )
        self.user_proxy = autogen.UserProxyAgent(
            name="UserProxy", human_input_mode="NEVER", max_consecutive_auto_reply=0
        )

    def send_message(self, prompt: str) -> str:
        """Send a message to the agent and retrieve the response."""
        self.user_proxy.initiate_chat(self.agent, message=prompt)
        response = self.user_proxy.last_message()["content"]
        return response

    