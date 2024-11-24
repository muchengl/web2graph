from prompts.abs.string_prompt_block import StringPromptBlock


class StringBlock(StringPromptBlock):

    def __init__(self, s: str):
        self.s = s


    def get_prompt(self) -> str:
        return self.s