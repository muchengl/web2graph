from prompts.abs.string_prompt_block import StringPromptBlock


class TargetElementBlock(StringPromptBlock):

    def __init__(self, target_element: str):
        self.target_element = target_element


    def get_prompt(self) -> str:
        return "You need to based on the current state, explore: "+self.target_element