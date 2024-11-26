
# agent.py
import ast
import re

from loguru import logger
import os
import openai

from runtime.llm import invoke_llm_

logger.remove()
logger.add("log/run.log", rotation="10 MB", retention="10 days", compression="zip")

class Agent:
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """
You are a website agent. You will be given a task, screenshots of the current web page, and the action space of the current web page. 
You need to generate actions based on this information and complete the task step by step.

Available Actions:
- CLICK ID
- TYPE ID CONTENT
- QUIT 

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
        
Note that this is not a fixed step, you need to understand it according to the task.

Note, To ensure success: 
    1. Respond only with actions, and do not include any additional text.
    2. Respond only one action at a time
"""

        self.conversation_history.append({
            "role": "system",
            "content": self.system_prompt
        })


    def get_llm_response(self, prompt=""):

        # todo: 在fsm上行走，每一步都提供当前 image 和 action space

        if prompt != "":
            # Add the user's input to the conversation
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })

        # assistant_reply = invoke_local_llm(self.conversation_history)
        assistant_reply = invoke_llm_(self.conversation_history)

        # Update conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_reply
        })

        logger.info(f"LLM response: {assistant_reply}")

        return assistant_reply


    def parse_actions(self, assistant_reply):
        """
        Parses the assistant's reply to extract actions.
        Assumes each action is on a new line starting with 'Action:'.
        """
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

        # print(f"Execute action: {action_str}")
        logger.info(f"Execute action: {action_str}")

        err = ""

        action = action_str.split(" ")

        try:
            if action[0] == "CLICK":
                id = action[1]

                # self.conversation_history.append({
                #     "role": "system",
                #     "content": "..."
                # })

                # execute action


                # append history




            elif action[0] == "TYPE":
                id = action[1]
                content = action[2]



            elif action[0] == "QUIT":
                return "QUIT"


            else:
                err = f"Unknown action: {action_str}"

        except Exception as e:
            err = f"Error executing action '{action_str}': {e}"

        if err!="":
            logger.error(err)
        return err



    def run(self, prompt=""):
        print("Agent is running.\n")
        while True:
            print("\n====================================================\n")
            assistant_reply = self.get_llm_response(prompt)
            if "QUIT" in assistant_reply:
                break

            logger.info(f"Assistant:\n{assistant_reply}\n")

            actions = self.parse_actions(assistant_reply)

            for action in actions:

                output = self.execute_action(action)

                if output != "":
                    self.conversation_history.append({
                        "role": "user",
                        "content": output
                    })
                else:
                    self.conversation_history.append({
                        "role": "user",
                        "content": "Action Executed"
                    })


if __name__ == "__main__":
    agent = Agent()

    print("You can use this AI assistant to help you complete website tasks like:")
    print()
    prompt = input("What do you want to do today? \n")
    # prompt =''
    agent.run(prompt)