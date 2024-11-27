
from abc import ABC, abstractmethod

from fsm.abs import GraphState, GraphAction
from runtime.prompts.abs.openai_prompt_block import OpenAIPromptBlock


class StateToPromptBlock(OpenAIPromptBlock):
    """
    StateToPromptBlock:
    Turn FSM State to prompt block
    """

    def __init__(self, state: GraphState):
        self.state = state

    @abstractmethod
    def get_prompt(self) -> list[dict]:
        pass


class ActionToPromptBlock(OpenAIPromptBlock):
    """
    ActionToPromptBlock:
    Turn FSM Action to prompt block
    """
    def __init__(self, state: GraphAction):
        self.state = state

    @abstractmethod
    def get_prompt(self) -> list[dict]:
        pass