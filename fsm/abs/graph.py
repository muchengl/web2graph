from abc import ABC, abstractmethod

# from fsm import GraphState
from project.checkpoint_config import CheckpointConfig


class Graph(ABC):
    def __init__(self, root_state):
        """
        Initialize the graph with a root node.
        """
        self.root_state = root_state
        self.current_state  = root_state
        self.visited = set()
        self.stack = [root_state]

        # Mark the root state as visited
        if root_state is not None:
            self.visited.add(root_state.id)

        # from -> to, [[from, to],[from, to],[from, to]]
        self.edges = []

    @abstractmethod
    def move_to_next_state(self):
       pass

    @abstractmethod
    def move_back(self):
       pass

    @abstractmethod
    def reset(self):
       pass

    @abstractmethod
    def has_next_state(self):
        pass

    @abstractmethod
    def do_checkpoint(self, cfg: CheckpointConfig):
        pass

    @abstractmethod
    def load_checkpoint(self, cfg: CheckpointConfig):
        pass


class FSMGraph(Graph):
    def __init__(self, root_state):
        super().__init__(root_state)


    def move_to_next_state(self):
        """
        Move to the next unvisited state based on the current state's 'to_action' list.
        This method will iterate over the available actions and transition to the first unvisited state.
        """
        if self.current_state is None:
            return None

        for action in self.current_state.to_action:
            # Check the next state of each action
            for next_state in action.to_state:
                if next_state.id not in self.visited:
                    self.visited.add(next_state.id)
                    self.stack.append(next_state)
                    self.current_state = next_state
                    return self.current_state

        return None

    def move_back(self):
        """
        Move back to the previous state by popping the stack.
        If the stack is not empty, we backtrack to the previous state.
        """
        if len(self.stack) > 1:
            self.stack.pop()
            self.current_state = self.stack[-1]
            return self.current_state
        return None

    def reset(self):
        """
        Reset the traversal by clearing the visited states and setting
        the current state back to the root state.
        """
        self.visited.clear()
        self.stack = [self.root_state]
        self.current_state = self.root_state
        self.visited.add(self.root_state.id)

    def has_next_state(self):
        """
        Check if the current state has any unvisited next states.
        """
        for action in self.current_state.to_action:
            for next_state in action.to_state:
                if next_state.id not in self.visited:
                    return True
        return False

    @abstractmethod
    def do_checkpoint(self, cfg: CheckpointConfig):
        pass


