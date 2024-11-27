from typing import Any
import re

from fsm.web_action import WebAction
from fsm.web_state import WebState
from runtime.prompts.prompt_constructor import PromptConstructor
from runtime.prompts.warehouse.action_examples import ActionExamples
from runtime.prompts.warehouse.basic_explainer import BasicExplainer
from runtime.prompts.warehouse.web_fsm_block import WebStateToPromptBlock, WebActionToPromptBlock


class ExplainPromptConstructor(PromptConstructor):

    def __init__(self):
        super().__init__()

        p_basic_explainer = BasicExplainer()
        self.prompt_block_stack.append(p_basic_explainer)

        p_action_examples = ActionExamples()
        self.prompt_block_stack.append(p_action_examples)


    def get_prompt(self,
                   previous_state: WebState,
                   action: WebAction,
                   current_state: WebState) -> list[dict[str, Any]]:

        s1 = WebStateToPromptBlock(previous_state)
        a = WebActionToPromptBlock(action)
        s2 = WebStateToPromptBlock(current_state)

        self.prompt_block_cache.append(s1)
        self.prompt_block_cache.append(a)
        self.prompt_block_cache.append(s2)

        base_prompt = self.construct_prompt()

        return base_prompt

    import re

    def parse_explanation_string(self, input_string) -> dict | None:
        if "ACTION_EXPLANATION:" not in input_string or "STATE_EXPLANATION:" not in input_string:
            return None

        # Patterns to capture text following ACTION_EXPLANATION: and STATE_EXPLANATION:
        action_pattern = r"ACTION_EXPLANATION:\s*(.*?)(?:STATE_EXPLANATION:|$)"
        state_pattern = r"STATE_EXPLANATION:\s*(.*)"

        action_explanation = re.search(action_pattern, input_string, re.DOTALL)
        state_explanation = re.search(state_pattern, input_string, re.DOTALL)

        if action_explanation and state_explanation:
            return {
                "action_explanation": action_explanation.group(1).strip(),
                "state_explanation": state_explanation.group(1).strip()
            }
        else:
            return None

# import json
# import logging
# import re
# from pathlib import Path
# from typing import Any, TypedDict
#
# import yaml
# from PIL import Image
#
# from browser_env import Action, ActionParsingError, Trajectory, action2str
# from browser_env.utils import StateInfo, pil_to_b64, pil_to_vertex
# from llms import lm_config
# from llms.tokenizers import Tokenizer
# from llms.utils import APIInput
#
#
# logger = logging.getLogger(__name__)
#
# class FsmInstruction(TypedDict):
#     """Instruction for constructing prompt"""
#
#     intro: str
#     examples: list[tuple[str, str]]
#     template: str
#     meta_data: dict[str, Any]
#
#
# class FsmPromptConstructor:
#     """The agent will perform step-by-step reasoning before the answer"""
#
#     def __init__(
#         self,
#         instruction_path: str | Path,
#         lm_config: lm_config.LMConfig,
#         tokenizer: Tokenizer,
#     ):
#         # super().__init__(instruction_path, lm_config, tokenizer)
#         # self.answer_phrase = self.instruction["meta_data"]["answer_phrase"]
#
#         self.instruction_path = Path(instruction_path)
#         self.obs_modality = "text"
#         self.lm_config = lm_config
#
#         instruction = yaml.load(open(self.instruction_path), Loader=yaml.SafeLoader)
#         instruction["examples"] = [tuple(e) for e in instruction["examples"]]
#         self.instruction: FsmInstruction = instruction
#
#         self.tokenizer = tokenizer
#
#     def construct(
#             self,
#             trajectory: Trajectory,
#             page_screenshot_img: Image.Image,
#             images: list[Image.Image],
#             meta_data: dict[str, Any] = {}) -> APIInput:
#
#         intro = self.instruction["intro"]
#         examples = self.instruction["examples"]
#         template = self.instruction["template"]
#         keywords = self.instruction["meta_data"]["keywords"]
#
#         if len(trajectory) < 3:
#             return
#         new_state_info: StateInfo = trajectory[-1]
#         action: Action = trajectory[-2]
#         old_state_info: StateInfo = trajectory[-3]
#
#         old_obs = old_state_info["observation"][self.obs_modality]
#         new_obs = new_state_info["observation"][self.obs_modality]
#         action_str = action2str(action, "id_accessibility_tree")
#
#         max_obs_length = self.lm_config.gen_config["max_obs_length"]
#
#         old_obs = self.tokenizer.decode(self.tokenizer.encode(old_obs)[:max_obs_length])
#         new_obs = self.tokenizer.decode(self.tokenizer.encode(new_obs)[:max_obs_length])
#         action_str = self.tokenizer.decode(self.tokenizer.encode(action_str)[:max_obs_length])
#
#         logger.debug(f"{old_obs} \n{new_obs} \n{action_str}")
#
#         # page = new_state_info["info"]["page"]
#         # url = page.url
#         previous_action_str = meta_data["action_history"][-2]
#
#         current = template.format(
#             old_state_observation=old_obs,
#             new_state_observation=new_obs,
#             action=action_str,
#             # url=self.map_url_to_real(url),
#             previous_action=previous_action_str,
#         )
#         print(current)
#
#         # assert all([f"{{k}}" not in current for k in keywords])
#
#         prompt = self.get_lm_api_input(
#             intro, examples, current, page_screenshot_img, images
#         )
#
#         return prompt
#
#     def get_lm_api_input(
#         self,
#         intro: str,
#         examples: list[tuple[str, str]],
#         current: str,
#         page_screenshot_img: Image.Image,
#         images: list[Image.Image],
#     ) -> APIInput:
#
#         """
#         Message Stack:
#             Introduction,
#             Examples,
#             Current Page's Screenshot,
#             Other Images,
#             Current_prompt,
#         """
#
#         message: list[dict[str, str]] | str | list[str | Image.Image]
#
#         if "openai" not in self.lm_config.provider:
#             raise NotImplementedError(
#                 f"Provider {self.lm_config.provider} not implemented"
#             )
#         if self.lm_config.mode is not "chat":
#             raise NotImplementedError(
#                 f"{self.lm_config.mode} not implemented"
#             )
#
#         # Introduction
#         message = [
#             {
#                 "role": "system",
#                 "content": [
#                     {
#                         "type": "text",
#                         "text": intro}
#                 ],
#             }
#         ]
#
#         # Examples
#         # for k, v in examples:
#         #     pass
#
#         # Current Page
#         content = [
#             {
#                 "type": "text",
#                 "text": "IMAGES: (1) current page screenshot",
#             },
#             {
#                 "type": "image_url",
#                 "image_url": {"url": pil_to_b64(page_screenshot_img)},
#             },
#         ]
#
#
#         # for image_i, image in enumerate(images):
#         #     content.extend(
#         #         [
#         #             {
#         #                 "type": "text",
#         #                 "text": f"({image_i+2}) input image {image_i+1}",
#         #             },
#         #             {
#         #                 "type": "image_url",
#         #                 "image_url": {"url": pil_to_b64(image)},
#         #             },
#         #         ]
#         # )
#
#         current_prompt = current
#         content = [{"type": "text", "text": current_prompt}] + content
#
#         message.append({"role": "user", "content": content})
