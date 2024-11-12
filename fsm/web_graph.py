import json
from pathlib import Path
from typing import TextIO, Any

import yaml
from PIL import Image
from loguru import logger

from browser.actions import Action, ActionType
from browser.browser_env import PlaywrightBrowserEnv
from fsm.web_action import WebAction
from fsm.web_state import WebState
from project_mgr.checkpoint_config import CheckpointConfig
from fsm.abs.graph import FSMGraph


class WebGraph(FSMGraph):
    def __init__(self,
                 root_state: WebState = None,
                 browse_env: PlaywrightBrowserEnv = None):

        self.browse_env = browse_env

        super().__init__(root_state)


    def do_checkpoint(self, cfg: CheckpointConfig):

        # Create the directories if they do not exist
        base_path = Path(cfg.current_path)
        main_file_path =  base_path / cfg.main_file
        static_path = base_path / cfg.static_path
        edge_file_path = base_path / cfg.edge_file
        state_file_path = base_path / cfg.state_file
        action_file_path = base_path / cfg.action_file

        static_path.mkdir(parents=True, exist_ok=True)

        self.check_point_visited = set()
        self.edge_id = 0

        # Open files for edges, states, and actions
        with open(main_file_path, "a+") as main_file, \
                open(edge_file_path, "a+") as edge_file, \
                open(state_file_path, "a+") as state_file, \
                open(action_file_path, "a+") as action_file:

            self._graph_checkpoint(main_file, cfg)
            self._traverse_graph_checkpoint(self.root_state, edge_file, state_file, action_file, cfg, static_path)

    def _graph_checkpoint(self, main_file: TextIO, cfg: CheckpointConfig):
        # logger.info("")
        _visited = []
        _stack = []

        for v in self.visited:
            _visited.append(v)

        for s in self.stack:
            _stack.append(s.id)

        main = {
            "root_state": self.root_state.id,
            "current_state": self.current_state.id,
            "visited": _visited,
            "stack":_stack
        }
        logger.debug(f"main: {main}")
        yaml.dump(main, main_file, default_flow_style=False)


    def _traverse_graph_checkpoint(self,
                                 current_state: WebState,
                                 edge_file: TextIO,
                                 state_file: TextIO,
                                 action_file: TextIO,
                                 cfg: CheckpointConfig,
                                 static_path: Path):
        # If the state has already been visited, skip it
        if current_state.generate_id() in self.check_point_visited:
            return

        # Mark the current state as visited
        self.check_point_visited.add(current_state.generate_id())

        # Log the current state
        current_state.do_checkpoint(cfg, state_file, static_path)

        # Traverse all actions from the current state
        to_action: list[WebAction] = current_state.to_action
        for action in to_action:
            # Log the action
            action.do_checkpoint(cfg, action_file)

            # Traverse each possible next state for this action
            for next_state in action.to_state:
                # Log the edge between the current state and the next state
                edge_data = {str(self.edge_id): {
                    "from_state": current_state.id,
                    "to_state": next_state.id,
                    "action": action.id
                }}
                yaml.dump(edge_data, edge_file, default_flow_style=False)
                self.edge_id += 1

                # Recursively visit the next state
                self._traverse_graph_checkpoint(next_state, edge_file, state_file, action_file, cfg, static_path)


    def load_checkpoint(self, cfg: CheckpointConfig):

        # Define paths to checkpoint files
        base_path = Path(cfg.current_path)
        main_file_path = base_path / cfg.main_file
        state_file_path = base_path / cfg.state_file
        action_file_path = base_path / cfg.action_file
        edge_file_path = base_path / cfg.edge_file

        # Load main graph structure
        with open(main_file_path, "r") as main_file:
            main_data = yaml.safe_load(main_file)
            root_state_id = main_data["root_state"]
            current_state_id = main_data["current_state"]
            visited_ids = set(main_data["visited"])
            stack_ids = main_data["stack"]

        # Load states
        states: dict[Any, WebState] = {}
        with open(state_file_path, "r") as state_file:

            state_data = yaml.safe_load(state_file)

            for state_id, state_info in state_data.items():

                id = state_id["id"]
                state_name = state_info["name"]
                state_info_text = state_info["info"]
                uuid = state_info.get("uuid", None)
                image_path = state_info.get("image_path", None)
                som_path = state_info.get("som_path", None)
                ocr_result = state_info.get("ocr_result", None)
                parsed_content = state_info.get("parsed_content", None)


                # Load image if path is provided
                web_image = None
                som_image = None
                if image_path:
                    web_image = Image.open(image_path)

                if som_path:
                    som_image = Image.open(som_path)

                ocr_result_ = json.loads(ocr_result)
                parsed_content_ = json.loads(parsed_content)


                # Reconstruct state object
                state = WebState(
                    state_name,
                    state_info_text,
                    web_image,
                    som_image,
                    ocr_result_,
                    parsed_content_,
                    self.browse_env
                )
                state.id = state_id
                state.uuid = uuid
                states[state_id] = state

                logger.info(f"load state: {state_id}")

                print(state)

        # Load actions
        actions: dict[Any, WebAction] = {}
        with open(action_file_path, "r") as action_file:

            action_data = yaml.safe_load(action_file)

            for action_id, action_info in action_data.items():

                action_name = action_info["name"]
                action_info_text = action_info["info"]
                uuid = action_info["uuid"]
                action_type = action_info["action_type"]
                action_content = action_info["action_content"]
                action_target_id = action_info["action_target_id"]


                action: Action = Action(
                    ActionType[action_type],
                    action_target_id,
                    action_content
                )


                # Reconstruct action object
                web_action = WebAction(
                    action_name,
                    action_info_text,
                    action,
                    self.browse_env
                )
                action.id = action_id  # Set action id explicitly
                action.uuid = uuid
                actions[action_id] = web_action

                logger.info(f"load action: {action_id}")
                print(action)


        # Load edges and reconstruct connections
        with open(edge_file_path, "r") as edge_file:

            edge_data = yaml.safe_load(edge_file)

            for edge_id, edge_info in edge_data.items():

                from_state_id = edge_info["from_state"]
                to_state_id = edge_info["to_state"]
                action_id = edge_info["action"]


                # Establish the action and state transitions
                from_state = states[from_state_id]
                to_state = states[to_state_id]
                mid_action = actions[action_id]

                if action not in from_state.to_action:
                    from_state.to_action.append(action)

                if to_state not in mid_action.to_state:
                    mid_action.to_state.append(to_state)


        # Set root state, current state, and restore visited and stack attributes
        self.root_state = states[root_state_id]
        self.current_state = states[current_state_id]
        self.visited = set(visited_ids)
        self.stack = [states[state_id] for state_id in stack_ids]

        logger.info("Checkpoint loaded successfully.")
