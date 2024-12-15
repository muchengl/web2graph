
# agent.py
import ast
import re
import sys
import threading
from time import sleep

from PIL.Image import Image
from PyQt6.QtWidgets import QApplication
from loguru import logger
import os
import openai

from runtime.llm import invoke_llm_by_chat, global_token_usage
from runtime.runtime import BasicRuntime
from utils.image_util import pil_image_to_base64
from utils.print_util import pretty_print


class BasicAgent:
    """
    Force the Agent to execute tasks according to the FSM. Cannot execute tasks outside the FSM.
    """

    def __init__(self, fsm_path: str, task: str):

        self.task = task

        self.runtime = BasicRuntime(fsm_path)

        self.conversation_history = []
        self.system_prompt = """
You are a website agent. You will be given a task, screenshots of the current web page, and the Action Space of the current web page. 
You need to generate actions based on this information and complete the task step by step.

Available Actions:
- CLICK ID
- TYPE ID CONTENT


You can take actions in the following format:
ACTION_TYPE ID [ACTION_CONTENT]

Example 01:
    Website Current Action Space:
    [0] Button: Login/Register 
    [1] Button: Post
    [3] Input Box: Search
    [4] Button: Search
    
    Task: I need to register a new account
    
    Expected Output: CLICK 0
    
Example 02:
    Website Current Action Space:
    [0] Button: Login/Register 
    [1] Button: Post
    [3] Input Box: Search
    [4] Button: Search
    
    Task: I need to post an ad to recruit workers
    
    Expected Output: CLICK 1
    
Example 03:
    Website Current Action Space:
    [0] Button: Login/Register 
    [1] Button: Post
    [3] Input Box: Search
    [4] Button: Search
    
    Task: I need to find a job as a software development engineer
    
    Expected Output: TYPE 3 [software development engineer]
        
    After input, move to the new state. Website Current Action Space:
    [0] Button: Login/Register 
    [1] Button: Post
    [3] Input Box: Search
    [4] Button: Search
    
    Task: I need to find a job as a software development engineer
    
    Expected Output: CLICK 4
    
Example 04:
    Website Current Action Space:
    [0] Button: Login/Register 
    [1] Button: Post
    [3] Input Box: Search
    [4] Button: Search
    
    Task: I need to register a new account
    
    Output: CLICK 5
    This is an error case, there is no action 5 in the action space. This will cause the execution to fail.
        
Note that this is not a fixed step, you need to understand it according to the task.

Note, To ensure success: 
    1. Respond only with actions, and do not include any additional text.
    2. Respond only one action at a time
    3. You must select an action from Action Space List, otherwise the execution will fail

"""

        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })



    def construct_prompt(self, state_info, action_space, raw_img, label_img: Image):
        # label_img.show()

        label_img_base64 = pil_image_to_base64(label_img)
        raw_img_base64 = pil_image_to_base64(raw_img)

        current_state_prompt = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Current State Description: {state_info}",
                },
                {
                    "type": "text",
                    "text": f"Action Space, You must select an action from this space\n: {action_space}",
                },

                # Action Space of current state
                {
                    "type": "text",
                    "text": "Below is the Labeled-Image of the current state:\n\n",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{label_img_base64}",
                    },
                },


                # Realtime Screenshot
                {
                    "type": "text",
                    "text": "Below is the Screenshot of current website\n\n",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{raw_img_base64}",
                    },
                },
            ]
        }


        return current_state_prompt


    def get_llm_response(self):

        state_info, action_space, raw_img, label_img = self.runtime.get_state_obs_space()

        prompt = self.construct_prompt(state_info, action_space, raw_img, label_img)
        self.conversation_history.append(prompt)

        # debug
        # pretty_print(self.conversation_history)

        # self.conversation_history.append({
        #     "role": "user",
        #     "content": self.task
        # })

        current_user_task = {
            "role": "user",
            "content": self.task
        }

        conversation = self.conversation_history + [prompt, current_user_task]

        # assistant_reply = invoke_llm_by_chat(self.conversation_history)
        assistant_reply = invoke_llm_by_chat(conversation)

        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_reply
        })

        logger.info(f"LLM response: {assistant_reply}")


        return assistant_reply


    def parse_actions(self, assistant_reply):
        actions = []
        lines = assistant_reply.strip().split('\n')
        for line in lines:
            # if line.startswith("Action:"):
            #     logger.info(f"Action: {line}")
            #     action_line = line[len("Action:"):].strip()
            #     actions.append(action_line)
            #     # print(f"{action_line}")

            actions.append(line.strip())

        return actions


    def execute_action(self, action_str: str) -> str:
        logger.info(f"Prepare to Execute Action: {action_str}")

        # self.runtime.fsm.current_state.som_image.show()
        # input("Press Enter to continue...")

        # sleep(1)

        result = self.runtime.take_action(action_str)


    def run(self):
        print("Agent is running.......\n")

        while True:
            print("\n====================================================\n")

            assistant_reply = self.get_llm_response()
            if "QUIT" in assistant_reply:
                break

            logger.info(f"Assistant:\n{assistant_reply}\n")

            actions = self.parse_actions(assistant_reply)

            for action in actions:

                output = self.execute_action(action)

                # todo: add output into prompt

                # if output != "":
                #     self.conversation_history.append({
                #         "role": "user",
                #         "content": output
                #     })
                # else:
                #     self.conversation_history.append({
                #         "role": "user",
                #         "content": "Action Executed"
                #     })

            # input("Press Enter to continue...")
            # sleep(1)
            logger.info(f"prompt_tokens: {global_token_usage["prompt_tokens"]}")
            logger.info(f"completion_tokens: {global_token_usage["completion_tokens"]}")
            logger.info(f"total_tokens: {global_token_usage["total_tokens"]}")




# def run_agent_in_background(agent):
#     """
#     Run the agent's main logic in a separate thread.
#     """
#     def agent_logic():
#         agent.run()
#     threading.Thread(target=agent_logic, daemon=True).start()

if __name__ == "__main__":
    # app = QApplication(sys.argv)

    fsm_path = '/Users/lhz/Desktop/craigslist_graph'

    print("You can use this AI assistant to help you complete website tasks,")
    print()
    prompt = input("What do you want to do today? \n")

    # prompt = 'I need to register a craigslist account.'
    # prompt = 'Help me post an ad for recruiting a software development engineer'

    agent = BasicAgent(fsm_path, prompt)
    agent.run()

    # run_agent_in_background(agent)
    # sys.exit(app.exec())