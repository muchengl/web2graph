import logging
from abc import ABC, abstractmethod
from typing import Any


from runtime.prompts.abs.openai_prompt_block import OpenAIPromptBlock
from runtime.prompts.abs.prompt_block import PromptBlock
from runtime.prompts.abs.string_prompt_block import StringPromptBlock

logger = logging.getLogger(__name__)

class PromptConstructor(ABC):

    def __init__(self):
        """
        prompt_block_stack: Stores predefined long-term prompts

        prompt_block_cache: Stores short-term prompts for one time construct_prompt

        """
        self.prompt_block_stack: list[PromptBlock] = []
        self.prompt_block_cache: list[PromptBlock] = []

    def construct_prompt(self) -> list[dict[str, Any]]:

        final_prompts = []

        for block in self.prompt_block_stack:
            self._construct(final_prompts, block)

        for block in self.prompt_block_cache:
            self._construct(final_prompts, block)
        self.prompt_block_cache.clear()

        return final_prompts

    def _construct(self, final_prompts: list, block: PromptBlock):
        prompt = block.get_prompt()
        if prompt is None:
            logger.warning(f"empty prompt block: {str(block)}")
            return

        # print("===============================")
        # self.pretty_print(prompt)

        if isinstance(block, StringPromptBlock):
            final_prompts.append({
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            })

        elif isinstance(block, OpenAIPromptBlock):
            # logger("openai prompt")
            final_prompts.append({
                "role": "system",
                "content": prompt,
            })


    def pretty_print(self, data, indent=0):
        spacer = " " * indent
        if isinstance(data, dict):
            print(f"{spacer}{{")
            for key, value in data.items():
                print(f"{spacer}  '{key}': ", end="")
                if isinstance(value, (dict, list)):
                    print()
                    self.pretty_print(value, indent + 4)
                elif isinstance(value, str) and value.startswith("data:image/png;base64"):
                    print(f"'{value[:50]}...[base64 data truncated]'")
                else:
                    print(repr(value))
            print(f"{spacer}}}")
        elif isinstance(data, list):
            print(f"{spacer}[")
            for item in data:
                if isinstance(item, (dict, list)):
                    self.pretty_print(item, indent + 4)
                elif isinstance(item, str) and item.startswith("data:image/png;base64"):
                    print(f"{spacer}  '{item[:50]}...[base64 data truncated]'")
                else:
                    print(f"{spacer}  {repr(item)}")
            print(f"{spacer}]")
        else:
            print(f"{spacer}{repr(data)}")