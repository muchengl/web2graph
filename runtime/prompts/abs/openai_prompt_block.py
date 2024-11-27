from abc import ABC, abstractmethod

from runtime.prompts.abs.prompt_block import PromptBlock


class OpenAIPromptBlock(PromptBlock):

    @abstractmethod
    def get_prompt(self) -> list[dict]:
        """
        OpenAI API Style Prompt Content

        [{
            "type": "text",
            "text": $text
        },{
            "type": "image_url",
            "image_url": {
                        "url": $image
                    }
        }]

        """
        pass