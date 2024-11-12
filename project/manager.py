import os

import yaml
from PIL.Image import Image

from browser.browser_env import PlaywrightBrowserEnv
from fsm import WebGraph, WebState
from fsm.abs.graph import FSMGraph
from project.checkpoint_config import CheckpointConfig
from project.metadata import ProjectMetadata


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


    def save_project(self):
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
                som_image: Image,
                ocr_result,
                parsed_content) -> 'ProjectManager':

    if os.path.exists(metadata.path) is not True:
        os.makedirs(metadata.path)

    root_state = WebState(
        state_name="root",
        state_info="home page",
        web_image=web_image,
        som_image=som_image,
        ocr_result=ocr_result,
        parsed_content=parsed_content,
        browse_env=browse_env
    )

    fsm_graph = WebGraph(root_state=root_state, browse_env=browse_env)

    mgr = ProjectManager(
        metadata=metadata,
        browse_env=browse_env,
    )
    mgr.fsm_graph = fsm_graph

    return mgr

