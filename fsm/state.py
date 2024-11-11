from abc import ABC, abstractmethod

from project_mgr.checkpoint_config import CheckpointConfig


class GraphState(ABC):

    def __init__(self,
                 state_name: str,
                 state_info: str):

        self.id = self.generate_id()

        self.state_name = state_name if state_name is not None else ""
        self.state_info = state_info if state_info is not None else ""

        # Graph
        self.from_action: list['GraphAction'] = []
        self.to_action: list['GraphAction'] = []

        from fsm.action import GraphAction


    @abstractmethod
    def generate_id(self):
        """
        user must implement this method to generate a unique id
        """
        pass

    @abstractmethod
    def to_prompt(self):
        pass

    @abstractmethod
    def do_checkpoint(self, cfg: CheckpointConfig):
        pass