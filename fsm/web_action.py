import json
import uuid
from typing import TextIO

import yaml
# from browser_env import Action, action2str, ScriptBrowserEnv
from fsm import GraphAction
from project_mgr.checkpoint_config import CheckpointConfig

from loguru import logger

class WebAction(GraphAction):

    def __init__(self,
                 action_name: str,
                 action_info: str,
                 action: Action,
                 browse_env: ScriptBrowserEnv):

        self.action = action

        self.browse_env = browse_env

        self.uuid = str(uuid.uuid1())

        super().__init__(action_name, action_info)

    def generate_id(self) -> str:
       # return action2str(self.action, "som")
        return self.action['raw_prediction'].replace(" ","_")+"_"+str(self.uuid)

    def to_prompt(self):
        # if llm_config.provider is "opanai":
        #     return self._to_openai_prompt()
        #
        # else:
        #     # raise NotImplementedError("not opanai")
        #     return self._to_openai_prompt()
        return self._to_openai_prompt()

    def _to_openai_prompt(self) -> list[dict]:
        prompts = []

        prompts.append({
            "type": "text",
            "text": f"Action: {action2str(self.action, 'som')}"
        })

        return prompts

    def do_checkpoint(self,
                      cfg: CheckpointConfig,
                      action_file: TextIO):
        logger.info(f"do action check point: {self.id}")
        # action_file = cfg.action_file

        # Convert the action to a dictionary and write it to the file
        # aid = self.action['raw_prediction'].replace(" ","_")
        action_data = {self.generate_id(): {
            "id": self.generate_id(),
            "name": self.action_name,
            "info": self.action_info,
            "action_raw": self.action['raw_prediction'],
            "uuid": str(self.uuid),
        }}
        yaml.dump(action_data, action_file, default_flow_style=False)
