import json
import uuid
from pathlib import Path
from typing import TextIO, Any

import numpy as np
import torch
import yaml
from PIL import Image
from loguru import logger

from browser.browser_env import PlaywrightBrowserEnv
from fsm.abs import GraphState
from project.checkpoint_config import CheckpointConfig
from web_parser.omni_parser import WebSOM
from web_parser.utils import annotate_processed_data


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


    def update_som(self, labels: list[dict[str, Any]]):
        """
        :param labels:
        :return:
        """

        new_label_coordinates = {}
        new_parsed_content = []
        for label in labels:
            new_label_coordinates[label['id']] = label['coordinates']
            new_parsed_content.append(label['metadata'])

        self.label_coordinates = new_label_coordinates
        self.parsed_content = new_parsed_content
        self.som.label_coordinates = new_label_coordinates
        self.som.parsed_content = new_parsed_content

        # generate new som image
        self.annotate_image()


    def annotate_image(self):
        # Load image
        image_source = np.array(self.web_image)

        # Prepare data for annotation
        boxes = torch.tensor([self.label_coordinates[key] for key in self.label_coordinates])  # Example bounding boxes
        boxes[:, 2] = boxes[:, 0] + boxes[:, 2]  # x2 = x + w
        boxes[:, 3] = boxes[:, 1] + boxes[:, 3]


        logits = torch.ones(len(self.label_coordinates))  # Dummy logits

        phrases = list(self.parsed_content)

        text_scale = 0.4

        # Call the annotate function
        annotated_image, label_coordinates = annotate_processed_data(
            image_source=image_source,
            boxes=boxes,
            logits=logits,
            phrases=phrases,
            text_scale=text_scale
        )

        pil_image = Image.fromarray(annotated_image)
        pil_image.show()

        self.som_image = pil_image
        self.som.processed_image = pil_image

        print(f"Annotated image and Save")


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
