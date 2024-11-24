from browser.browser_env import PlaywrightBrowserEnv
from project.manager import ProjectManager
from project.metadata import ProjectMetadata


class Runtime:

    def __init__(self):
        fsm_path = '/Users/lhz/Desktop/REDDIT'

        metadata: ProjectMetadata = ProjectMetadata(fsm_path)

        browser_config_file = "../.auth/reddit_state.json"
        with open(browser_config_file, "r", encoding="utf-8") as file:
            content = file.read()

        browser = PlaywrightBrowserEnv(context=content, headless=False)
        self.browser = browser
        self.browser.start_browser_sync()

        fsm_manager = ProjectManager(metadata, self.browser)
        fsm_manager.load_project()

        # fsm_manager.fsm_graph.show()

    def plan(self):
        # 1. Planner


        # 2. Executor

        pass

    def execute(self):
        pass

        # 根据计划，生成执行内容


if __name__ == '__main__':
    main = Runtime()