from abc import ABC, abstractmethod

from project.checkpoint_config import CheckpointConfig


# from fsm import GraphState


class GraphAction(ABC):

    def __init__(self,
                 action_name:str,
                 action_info:str):

        self.id = self.generate_id()

        self.action_name = action_name
        self.action_info = action_info

        # Graph
        self.from_state: list['GraphState'] = []
        self.to_state: list['GraphState'] = []

        from fsm import GraphState

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