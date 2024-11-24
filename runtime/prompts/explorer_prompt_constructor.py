from typing import Any

from agent.web_action import WebAction
from agent.web_state import WebState
from prompts.prompt_constructor import PromptConstructor
from prompts.warehouse.action_examples import ActionExamples
from prompts.warehouse.basic_explorer import BasicExplorer
from prompts.warehouse.string_block import StringBlock
from prompts.warehouse.target_element_block import TargetElementBlock
from prompts.warehouse.web_fsm_block import WebStateToPromptBlock, WebActionToPromptBlock


class ExplorerPromptConstructor(PromptConstructor):

    def __init__(self):
        super().__init__()

        p_basic_explorer = BasicExplorer()
        self.prompt_block_stack.append(p_basic_explorer)

        s = StringBlock("Example:")
        self.prompt_block_stack.append(s)

        p_action_examples = ActionExamples()
        self.prompt_block_stack.append(p_action_examples)

    def get_prompt(self,
                   previous_state: WebState = None,
                   action: WebAction = None,
                   current_state: WebState = None,
                   target: str = "") -> list[dict[str, Any]]:

        if previous_state is not None:
            s1 = WebStateToPromptBlock(previous_state)
            self.prompt_block_stack.append(StringBlock("previous_state"))
            self.prompt_block_cache.append(s1)

        if action is not None:
            a = WebActionToPromptBlock(action)
            self.prompt_block_cache.append(a)

        if current_state is not None:
            s2 = WebStateToPromptBlock(current_state)
            self.prompt_block_stack.append(StringBlock("current_state"))
            self.prompt_block_cache.append(s2)

        if target:
            target_block = TargetElementBlock(target)
            self.prompt_block_stack.append(StringBlock("\n"))
            self.prompt_block_cache.append(target_block)

        base_prompt = self.construct_prompt()

        return base_prompt

    # def get_prompt(self,
    #                previous_state: WebState=None,
    #                action: WebAction=None,
    #                current_state: WebState=None,
    #                target: str="") -> list[dict[str, Any]]:
    #
    #     s1 = WebStateToPromptBlock(previous_state)
    #     a = WebActionToPromptBlock(action)
    #     s2 = WebStateToPromptBlock(current_state)
    #
    #     target = TargetElementBlock(target)
    #
    #     self.prompt_block_stack.append(StringBlock("previous_state"))
    #     self.prompt_block_cache.append(s1)
    #
    #     self.prompt_block_cache.append(a)
    #
    #     self.prompt_block_stack.append(StringBlock("current_state"))
    #     self.prompt_block_cache.append(s2)
    #
    #     self.prompt_block_stack.append(StringBlock("\n"))
    #     self.prompt_block_cache.append(target)
    #
    #     base_prompt = self.construct_prompt()
    #
    #     return base_prompt





