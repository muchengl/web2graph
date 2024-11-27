import os

from PIL import Image

from utils.image_util import pil_image_to_base64
from runtime.prompts.abs.openai_prompt_block import OpenAIPromptBlock


class ActionExamples(OpenAIPromptBlock):

    def get_prompt(self) -> list[dict]:

        examples: list[dict] = []

        self.example_01(examples)

        return examples

    def example_01(self, examples: list[dict]):

        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)

        page_screenshot_img_01 = Image.open(f"{current_dir}/../fsm_examples/e0.png")
        page_screenshot_img_02 = Image.open(f"{current_dir}/../fsm_examples/e1.png")

        examples.append(
            {
                "type": "text",
                "text": "IMAGES: (1) current page screenshot",
            }
        )

        examples.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": pil_image_to_base64(page_screenshot_img_01)
                },
            }
        )

        examples.append(
            {
                "type": "text",
                "text": "IMAGES: (2) page after take action: type [5] [blue kayak] ",
            }
        )

        examples.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": pil_image_to_base64(page_screenshot_img_02)
                },
            }
        )

