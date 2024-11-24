from abc import ABC, abstractmethod


class PromptBlock(ABC):

    @abstractmethod
    def get_prompt(self):
        pass