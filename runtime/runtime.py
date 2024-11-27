from PIL.Image import Image
from loguru import logger

from browser.actions import ClickAction, TypeAction
from browser.browser_env import PlaywrightBrowserEnv
from fsm import WebState, WebAction
from project.manager import ProjectManager
from project.metadata import ProjectMetadata


class BasicRuntime:

    def __init__(self, fsm_path):
        # fsm_path = '/Users/lhz/Desktop/REDDIT'
        # fsm_path = '/Users/lhz/Desktop/craigslist_graph'

        metadata: ProjectMetadata = ProjectMetadata(fsm_path)

        browser = PlaywrightBrowserEnv(headless=False)
        self.browser = browser
        self.browser.start_browser_sync()

        self.proj_manager = ProjectManager(metadata, self.browser)
        self.proj_manager.load_project()

        # init browser environment
        self.proj_manager.fsm_graph.current_state = self.proj_manager.fsm_graph.root_state
        self.browser.navigate_to_sync(self.proj_manager.url)

        self.fsm = self.proj_manager.fsm_graph



    def get_state_obs_space(self) -> [str, str, Image, Image]:
        """
        :return: state metadata, action_space, current screenshot, screenshot with label
        """

        screenshot = self.browser.take_full_screenshot_sync() # real time screenshot

        current_state: WebState = self.fsm.current_state

        action_space = ""

        to_actions: list[WebAction] =  current_state.to_action
        for action in to_actions:
            a_id = action.action.action_target_id
            a_name = action.action_name
            a_info = action.action_info
            action_space += f"[{a_id}] {a_name}, {a_info}\n"

        logger.info(f"\naction_space:\n{action_space}")

        return current_state.state_name, action_space, screenshot, current_state.som_image



    def take_action(self, action_str: str):
        """
        Keep sync between Browser and FSM

        :param action_str:
        :return:
        """

        err = ""
        current_state: WebState = self.fsm.current_state

        action_str = action_str.replace("[","")
        action_str = action_str.replace("]", "")
        action = action_str.split(" ")

        try:
            if action[0] == "CLICK":
                id = action[1]
                logger.info(f"Runtime, CLICK: {id}")

                # move to next state in FSM
                if self._move_to_next_state(id) is False:
                    err = f"Failed to move {id} to next state"

                # take action
                action = ClickAction(
                    current_state.web_image,
                    current_state.som,
                    int(id),
                    ''
                )
                action.execute(self.browser)

            elif action[0] == "TYPE":
                id = action[1]
                content = ""

                for idx in range(2, len(action)):
                    content += action[idx]+" "

                logger.info(f"Runtime, TYPE: {id}, {content}")

                # move to next state in FSM
                if self._move_to_next_state(id) is False:
                    err = f"Failed to move {id} to next state"

                # take action
                action = TypeAction(
                    current_state.web_image,
                    current_state.som,
                    int(id),
                    content
                )
                action.execute(self.browser)

            elif action[0] == "QUIT":
                return "QUIT"
            else:
                err = f"Unknown action: {action_str}"

        except Exception as e:
            err = f"Error executing action '{action_str}': {e}"

        if err!="":
            logger.error(err)
        return err


    def _move_to_next_state(self, aid):
        current_state: WebState = self.fsm.current_state
        aid = int(aid)
        for act in current_state.to_action:
            if act.action.action_target_id == aid:
                self.fsm.current_state = act.to_state[0]
                return True

        return False


if __name__ == '__main__':
    main = BasicRuntime()