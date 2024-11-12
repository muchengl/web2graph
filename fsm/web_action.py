import json
import uuid
from typing import TextIO

import yaml

from browser.actions import Action
from browser.browser_env import PlaywrightBrowserEnv
from fsm.abs import GraphAction
from project_mgr.checkpoint_config import CheckpointConfig

from loguru import logger

class WebAction(GraphAction):

    def __init__(self,
                 action_name: str,
                 action_info: str,
                 action: Action,
                 browse_env: PlaywrightBrowserEnv):
        self.action = action
        self.browse_env = browse_env
        self.uuid = str(uuid.uuid1())
        super().__init__(action_name, action_info)

    def generate_id(self) -> str:
        return self.uuid

    def to_prompt(self):
        return self._to_openai_prompt()

    def _to_openai_prompt(self) -> list[dict]:
        # prompts = []
        #
        # prompts.append({
        #     "type": "text",
        #     "text": f"Action: {action2str(self.action, 'som')}"
        # })
        #
        # return prompts

        pass

    def do_checkpoint(self,
                      cfg: CheckpointConfig,
                      action_file: TextIO):
        logger.info(f"do action check point: {self.id}")

        action_data = {self.generate_id(): {
            "id": self.generate_id(),
            "name": self.action_name,
            "info": self.action_info,
            "uuid": str(self.uuid),
            "action_type": self.action.type,
            "action_content": self.action.action_content,
            "action_target_id": self.action.action_target_id,
        }}
        yaml.dump(action_data, action_file, default_flow_style=False)
