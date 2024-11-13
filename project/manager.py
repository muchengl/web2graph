import os
import shutil

import yaml
from PIL.Image import Image

from browser.browser_env import PlaywrightBrowserEnv
from fsm import WebGraph, WebState
from fsm.abs.graph import FSMGraph
from project.checkpoint_config import CheckpointConfig
from project.metadata import ProjectMetadata
from web_parser.omni_parser import WebSOM

# global_project_manager = None

class ProjectManager:

    def __init__(self,
                 metadata: ProjectMetadata,
                 browse_env: PlaywrightBrowserEnv):

        self.metadata = metadata

        self.path = metadata.path
        self.name = metadata.name
        self.url = metadata.url

        self.fsm_graph = WebGraph(browse_env=browse_env)

        self.checkpoint_base_path = self.path+'/checkpoints'
        self.checkpoint_config = CheckpointConfig(
            self.checkpoint_base_path,
            "main.yaml",
            "edge.yaml",
            "state.yaml",
            "action.yaml",
            "static",
            "metadata"
        )

        self.metadata_file = self.path + '/metadata.yaml'

        # global global_project_manager
        # global_project_manager = self


    def save_project(self):
        if os.path.exists(self.checkpoint_config.current_path):
            os.makedirs(self.checkpoint_config.history_path, exist_ok=True)

            # Find the latest history file index
            history_files = [
                f for f in os.listdir(self.checkpoint_config.history_path)
                if f.startswith("history_") and f[8:].isdigit()
            ]
            history_indices = sorted([int(f[8:]) for f in history_files])
            next_index = history_indices[-1] + 1 if history_indices else 1

            new_history_folder = os.path.join(
                self.checkpoint_config.history_path,
                f"history_{next_index}"
            )
            shutil.move(self.checkpoint_config.current_path, new_history_folder)


        self.fsm_graph.do_checkpoint(self.checkpoint_config)

        with open(self.metadata_file, "w") as metadata_file:
            project_metadata = {
                "name": self.name,
                "url": self.url,
                "path": self.path,
            }

            metadata_file.write(yaml.dump(project_metadata))

    def load_project(self):
        with open(self.metadata_file, "r") as metadata_file:
            state_data = yaml.safe_load(metadata_file)

            self.name = state_data['name']
            self.url = state_data['url']
            self.path = state_data['path']

            self.metadata.name = self.name
            self.metadata.url = self.url
            self.metadata.path = self.path

        self.fsm_graph.load_checkpoint(self.checkpoint_config)


def new_project(browse_env: PlaywrightBrowserEnv,
                metadata: ProjectMetadata,
                web_image: Image,
                som: WebSOM) -> 'ProjectManager':

    if os.path.exists(metadata.path) is not True:
        os.makedirs(metadata.path)


    root_state = WebState(
        state_name="root",
        state_info="home page",
        web_image=web_image,
        som=som,
        browse_env=browse_env,
        url=metadata.url
    )

    fsm_graph = WebGraph(root_state=root_state, browse_env=browse_env)

    mgr = ProjectManager(
        metadata=metadata,
        browse_env=browse_env,
    )
    mgr.fsm_graph = fsm_graph

    return mgr

