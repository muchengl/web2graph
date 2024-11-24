from abc import abstractmethod

from agent.web_action import WebAction
from agent.web_state import WebState
from prompts.abs.fsm_prompt_block import StateToPromptBlock, ActionToPromptBlock


class WebStateToPromptBlock(StateToPromptBlock):

    def __init__(self, state: WebState):
        super().__init__(state)

    def get_prompt(self) -> list[dict]:
        return self.state.to_prompt()


class WebActionToPromptBlock(ActionToPromptBlock):

    def __init__(self, action: WebAction):
        super().__init__(action)

    def get_prompt(self) -> list[dict]:
        return self.state.to_prompt()