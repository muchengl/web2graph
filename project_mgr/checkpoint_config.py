
class CheckpointConfig:
    def __init__(self,
                 path: str,
                 main_file: str,
                 edge_file,
                 state_file,
                 action_file,
                 static_path,
                 metadata_path):
        self.path = path

        self.history = "history"
        self.current = "current"

        self.current_path = path + "/" + self.current
        self.history_path = path + "/" + self.history

        self.edge_file = edge_file
        self.state_file = state_file
        self.action_file = action_file
        self.static_path = static_path

        # store huge date
        self.metadate_path = metadata_path

        self.main_file = main_file