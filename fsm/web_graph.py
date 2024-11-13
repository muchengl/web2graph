import json
from collections import deque
from pathlib import Path
from typing import TextIO, Any

import yaml
from PIL import Image
from loguru import logger

from browser.actions import Action, ActionType, ClickAction, TypeAction
from browser.browser_env import PlaywrightBrowserEnv
from fsm.web_action import WebAction
from fsm.web_state import WebState
from project.checkpoint_config import CheckpointConfig
from fsm.abs.graph import FSMGraph
from utils.graph import VGraph
from web_parser.omni_parser import WebSOM
import networkx as nx


class WebGraph(FSMGraph):
    def __init__(self,
                 root_state: WebState = None,
                 browse_env: PlaywrightBrowserEnv = None):
        self.browse_env = browse_env
        self.v_graph = VGraph()

        super().__init__(root_state)


    def move_to_state(self, target_state: WebState):
        # reset browse_env


        # move to target state

        pass


    def show(self):

        for edge in self.edges:
            old_state: WebState = edge[0]
            action: WebAction = edge[1]
            new_state: WebState = edge[2]

            self.v_graph.add_node_pair(
                                old_state.id,
                                action.id,
                                old_state.state_name,
                                action.action_name,
                                'green',
                                'yellow')

            self.v_graph.add_node_pair(
                                action.id,
                                new_state.id,
                                action.action_name,
                                new_state.state_name,
                                'yellow',
                                'green')

        self.v_graph.visualize_graph_plotly()


    def insert_node(self,
                    action_name:str,
                    action_info: str,
                    action: Action,
                    state_name:str,
                    state_info:str,
                    web_image: Image.Image,
                    som: WebSOM):

        logger.info("Inserting and move")

        new_web_action = WebAction(
            action_name=action_name,
            action_info=action_info,
            action=action,
            browse_env=self.browse_env,
        )

        new_web_state = WebState(
            state_name=state_name,
            state_info=state_info,
            web_image=web_image,
            som=som,
            browse_env=self.browse_env,
        )

        old_state = self.current_state
        self.current_state = new_web_state

        self._add_state_to_graph(old_state, new_web_action, new_web_state)




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

        #
        # Load states
        logger.info("Load states")
        states: dict[Any, WebState] = self._load_state(state_file_path)


        #
        # Load actions
        logger.info("Load actions")
        actions: dict[Any, WebAction] = self._load_actions(action_file_path)


        #
        # Load edges and reconstruct connections
        logger.info("Load edges and reconstruct connections")
        self._load_edges(edge_file_path, states, actions)


        # Set root state, current state, and restore visited and stack attributes
        self.root_state = states[root_state_id]
        self.current_state = states[current_state_id]
        self.visited = set(visited_ids)
        self.stack = [states[state_id] for state_id in stack_ids]

        logger.info("Checkpoint loaded successfully.")


    def _load_state(self, state_file_path):
        states: dict[Any, WebState] = {}
        with open(state_file_path, "r") as state_file:

            state_data = yaml.safe_load(state_file)

            for state_id, state_info in state_data.items():

                id = state_info["id"]
                state_name = state_info["name"]
                state_info_text = state_info["info"]
                uuid = state_info.get("uuid", None)

                image_path = state_info.get("image_path", None)
                som_path = state_info.get("som_path", None)

                label_coordinates = state_info.get("label_coordinates", None)
                parsed_content = state_info.get("parsed_content", None)


                # Load image if path is provided
                web_image = None
                som_image = None
                if image_path:
                    web_image = Image.open(image_path)

                if som_path:
                    som_image = Image.open(som_path)

                label_coordinates_ = json.loads(label_coordinates)
                parsed_content_ = json.loads(parsed_content)


                # Reconstruct state object
                som = WebSOM(
                    som_image,
                    label_coordinates_,
                    parsed_content_,
                )
                state = WebState(
                    state_name,
                    state_info_text,
                    web_image,
                    som,
                    self.browse_env
                )
                state.id = id
                state.uuid = uuid
                states[state_id] = state

                logger.info(f"load state: {state_id}")

                print(state)

        return states


    def _load_actions(self, action_file_path):
        actions: dict[Any, WebAction] = {}
        with open(action_file_path, "r") as action_file:

            action_data = yaml.safe_load(action_file)
            if action_data is None:
                return

            for action_id, action_info in action_data.items():

                action_name = action_info["name"]
                action_info_text = action_info["info"]
                uuid = action_info["uuid"]
                action_type = action_info["action_type"]
                action_content = action_info["action_content"]
                action_target_id = action_info["action_target_id"]

                action: Action = None
                if ActionType[action_type] == ActionType['CLICK']:
                    action: Action = ClickAction(
                        None,
                        None,
                        action_target_id,
                        action_content,
                        ActionType[action_type]
                    )
                elif ActionType[action_type] == ActionType['TYPE']:
                    action: Action = TypeAction(
                        None,
                        None,
                        action_target_id,
                        action_content,
                        ActionType[action_type]
                    )


                # Reconstruct action object
                web_action = WebAction(
                    action_name,
                    action_info_text,
                    action,
                    self.browse_env
                )
                web_action.id = action_id
                web_action.uuid = uuid
                actions[action_id] = web_action

                logger.info(f"load action: {action_id}")
                print(action)

        return actions


    def _load_edges(self, edge_file_path, states, actions):

        with open(edge_file_path, "r") as edge_file:

            edge_data = yaml.safe_load(edge_file)
            if edge_data is None:
                return

            for edge_id, edge_info in edge_data.items():

                from_state_id = edge_info["from_state"]
                to_state_id = edge_info["to_state"]
                action_id = edge_info["action"]

                # Establish the action and state transitions
                from_state = states[from_state_id]
                to_state = states[to_state_id]
                mid_action = actions[action_id]

                self._add_state_to_graph(from_state, mid_action, to_state)

                # if mid_action not in from_state.to_action:
                #     from_state.to_action.append(mid_action)
                #
                # if from_state not in mid_action.from_state:
                #     mid_action.from_state.append(from_state)
                #
                # if to_state not in mid_action.to_state:
                #     mid_action.to_state.append(to_state)
                #
                #     # Action based on previous State
                #     mid_action.action.web_som = from_state.som
                #     mid_action.action.web_image = from_state.web_image
                #
                # if mid_action not in to_state.from_action:
                #     to_state.from_action.append(mid_action)


    def _add_state_to_graph(self, old_state, new_web_action, new_web_state):
        old_state.to_action.append(new_web_action)
        new_web_action.to_state.append(new_web_state)

        new_web_action.from_state.append(old_state)
        new_web_state.from_action.append(new_web_action)

        # graph
        self.edges.append([old_state, new_web_action, new_web_state])

