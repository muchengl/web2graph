import json
import uuid
from pathlib import Path
from typing import TextIO

import yaml
from PIL.Image import Image
from loguru import logger

from browser_env import StateInfo, Trajectory, ScriptBrowserEnv
from browser_env.utils import pil_to_b64
from fsm import GraphState
from checkpoint.checkpoint_config import CheckpointConfig


class WebState(GraphState):

    def __init__(self,
                 state_name: str,
                 state_info: str,
                 observation: StateInfo,
                 browse_env: ScriptBrowserEnv,
                 image: Image = None,
                 trajectory: Trajectory = None,
                 metadata: dict = None):

        # WebArena State raw info
        self._observation = observation
        self.image = image

        # Raw Info
        ## e.g meta_data = {"action_history": ["None"]}
        self.metadata = metadata if metadata is not None else {}
        self.trajectory = trajectory

        self.browse_env = browse_env

        self.uuid = str(uuid.uuid1())

        super().__init__(state_name, state_info)

    @property
    def observation(self):
        if self._observation is None and self.browse_env is not None:
            # self._observation = self.browse_env.observation_space
            # state_info = {"observation": self.browse_env.observation_space}
            state_info = {"observation": self.browse_env._get_obs()}
            self._observation = state_info
        return self._observation

    @observation.setter
    def observation(self, value):
        self._observation = value

    def generate_id(self) -> str:
        action_history = self.metadata.get("action_history", None)
        if action_history is None:
            logger.info("action_history is None")
            return str(hash(self.observation['observation']['text']))+"_"+self.uuid

        # Otherwise, use action_history to generate the hash
        return str(hash(tuple(action_history)))+"_"+str(hash(self.observation['observation']['text']))

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
            "text": "Webpage State:\n"
        })

        prompts.append({
            "type": "text",
            "text": self.observation['observation']['text']
        })

        if self.image is not None:
            prompts.append({
                "type": "text",
                "text": "Webpage Screenshot:\n"
            })

            prompts.append({
                "type": "image_url",
                "image_url": {
                    "url": pil_to_b64(self.image)
                },
            })


        return prompts

    def do_checkpoint(self,
                      cfg: CheckpointConfig,
                      state_file: TextIO,
                      static_path: Path):
        logger.info(f"do state point: {self.id}")

        # Generate the image path and save the image if available
        image_path = None
        if self.image:
            image_path = static_path / f"{self.id}.png"
            self.image.save(image_path)

        # Convert the state to a dictionary and write it to the file
        state_data = {
            self.id: {
                "id": self.id,
                "name": self.state_name,
                "info": self.state_info,
                "metadata": self.metadata,
                # "observation": self.observation,
                # "trajectory": json.dumps(self.trajectory),
                "image_path": str(image_path) if image_path else None,
                "uuid": self.uuid,
            }
        }
        yaml.dump(state_data, state_file, default_flow_style=False)
