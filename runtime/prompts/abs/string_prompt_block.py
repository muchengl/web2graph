from abc import ABC, abstractmethod

from prompts.abs.prompt_block import PromptBlock


class StringPromptBlock(PromptBlock):

    @abstractmethod
    def get_prompt(self) -> str:
        pass