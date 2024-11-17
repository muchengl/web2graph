import json
import uuid
from pathlib import Path
from typing import TextIO

import yaml
from PIL.Image import Image
from loguru import logger

from browser.browser_env import PlaywrightBrowserEnv
from fsm.abs import GraphState
from project.checkpoint_config import CheckpointConfig
from web_parser.omni_parser import WebSOM


class WebState(GraphState):

    def __init__(self,
                 state_name: str,
                 state_info: str,
                 web_image: Image,
                 som: WebSOM,
                 browse_env: PlaywrightBrowserEnv,
                 url=''):

        self.browse_env = browse_env
        self.uuid = str(uuid.uuid1())

        # origin image of website
        self.web_image = web_image

        # processed image & info
        self.som = som
        self.som_image = som.processed_image
        self.label_coordinates = som.label_coordinates
        self.parsed_content = som.parsed_content

        self.url = url

        super().__init__(state_name, state_info)


    def generate_id(self) -> str:
        return self.uuid

    def to_prompt(self):
        return self._to_openai_prompt()

    def _to_openai_prompt(self) -> list[dict]:
        pass
        # prompts = []
        #
        # prompts.append({
        #     "type": "text",
        #     "text": "Webpage State:\n"
        # })
        #
        # prompts.append({
        #     "type": "text",
        #     "text": self.observation['observation']['text']
        # })
        #
        # if self.image is not None:
        #     prompts.append({
        #         "type": "text",
        #         "text": "Webpage Screenshot:\n"
        #     })
        #
        #     prompts.append({
        #         "type": "image_url",
        #         "image_url": {
        #             "url": pil_to_b64(self.image)
        #         },
        #     })
        #
        #
        # return prompts

    def do_checkpoint(self,
                      cfg: CheckpointConfig,
                      state_file: TextIO,
                      static_path: Path):
        logger.info(f"do state point: {self.id}")

        image_path = None
        som_path = None
        if self.web_image:
            image_path = static_path / f"{self.id}_1.png"
            self.web_image.save(image_path)

        if self.som_image:
            som_path = static_path / f"{self.id}_2.png"
            self.som_image.save(som_path)

        state_data = {
            self.id: {
                "id": self.id,
                "uuid": self.uuid,
                "name": self.state_name,
                "info": self.state_info,
                "image_path": str(image_path),
                "som_path": str(som_path),
                "label_coordinates": json.dumps(self.label_coordinates),
                "parsed_content": json.dumps(self.parsed_content),
                "url": self.url,
                "merge_into": self.merge_into.id if self.merge_into is not None else ''
            }
        }
        yaml.dump(state_data, state_file, default_flow_style=False)
