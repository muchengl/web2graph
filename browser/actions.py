from enum import Enum
from abc import ABC, abstractmethod

from PIL import Image
from loguru import logger

from browser.browser_env import BrowserEnv, PlaywrightBrowserEnv
from web_parser.omni_parser import WebSOM


action_types  = [
    'CLICK',
    'TYPE',
    "MOVE"
]

class ActionType(Enum):
    CLICK = action_types[0]
    TYPE = action_types[1]
    MOVE = action_types[2]


class Action(ABC):
    def __init__(self,
                 action_type: ActionType,
                 action_target_id: int,
                 action_content: str='',
                 web_image: Image.Image=None,
                 web_som: WebSOM=None):

        self.web_image = web_image
        self.web_som = web_som
        self.type = action_type
        self.action_content = action_content
        self.action_target_id = action_target_id

    @abstractmethod
    def execute(self, browser_env: BrowserEnv):
        pass


class ClickAction(Action):

    def __init__(self,
                 web_image: Image.Image,
                 web_som: WebSOM,
                 action_target_id: int,
                 action_content: str='',
                 action_type: ActionType=ActionType.CLICK):

        super().__init__(action_type, action_target_id, action_content, web_image, web_som)


    def execute(self, browser_env: BrowserEnv):

        logger.info(f"CLICK: {self.action_target_id}")

        width, height = self.web_som.processed_image.size

        id = int(self.action_target_id)

        position = self.web_som.ocr_result[1][id]

        avg_x = int((position[0] + position[2]) / 2)
        avg_y = int((position[1] + position[3]) / 2)

        browser_env.click_at_position_sync(avg_x, avg_y)


class TypeAction(Action):

    def __init__(self,
                 web_image: Image.Image,
                 web_som: WebSOM,
                 action_target_id: int,
                 action_content: str='', # click som id
                 action_type: ActionType=ActionType.CLICK):

        super().__init__(action_type, action_target_id, action_content, web_image, web_som)


    def execute(self, browser_env: BrowserEnv):

        logger.info(f"TYPE: {self.action_target_id}, {self.action_content}")

        width, height = self.web_som.processed_image.size

        id = int(self.action_target_id)

        position = self.web_som.ocr_result[1][id]

        avg_x = int((position[0] + position[2]) / 2)
        avg_y = int((position[1] + position[3]) / 2)

        browser_env.input_at_position_sync(avg_x, avg_y, self.action_content)
