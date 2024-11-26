import asyncio
import json
import uuid, io
from enum import Enum
from abc import ABC, abstractmethod
from time import sleep

from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal
from loguru import logger
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright


class BrowserEnv(ABC):

    @abstractmethod
    def start_browser(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_current_url(self):
        pass

    @abstractmethod
    def navigate_to(self, url: str):
        pass

    @abstractmethod
    def click_at_position(self, x: int, y: int):
        pass

    @abstractmethod
    def input_at_position(self, x: int, y: int, text: str):
        pass

    @abstractmethod
    def take_full_screenshot(self):
        pass

    @abstractmethod
    def start_browser_sync(self):
        pass

    @abstractmethod
    def navigate_to_sync(self, url: str):
        pass

    @abstractmethod
    def click_at_position_sync(self, x: int, y: int):
        pass

    @abstractmethod
    def input_at_position_sync(self, x: int, y: int, text: str):
        pass

    @abstractmethod
    def take_full_screenshot_sync(self):
        pass



class PlaywrightBrowserEnv(BrowserEnv):
    def __init__(self, context="", headless=True):
        self.browser = None
        self.page = None
        self.headless = headless


        # webarena setup
        if context != "":
            self.storage_state = json.loads(context)
        else:
            self.storage_state = None
        # self.cookies_list = self.context.get("cookies", [])

    async def start_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1024})

    async def navigate_to(self, url: str):
        await self.page.goto(url)

    def start_browser_sync(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)


        if self.storage_state != None:
            context = self.browser.new_context(
                storage_state=self.storage_state,
            )
            cookies = context.cookies()
            logger.info(f"added cookies_list: {cookies}")

        self.page = self.browser.new_page()
        self.page.set_viewport_size({"width": 1024, "height": 768})


    def navigate_to_sync(self, url: str):
        self.page.goto(url)

        # login reddit (for webarena only)
        # logger.info("webarena login!")
        # if 'http://ec2-3-129-227-13.us-east-2.compute.amazonaws.com:9999' in url:
        #     logger.info("webarena reddit login!")
        #     self.page.goto(f"{url}/login")
        #     sleep(2)
        #     # self.page.get_by_label("Username").fill('testuser')
        #     self.page.get_by_label("Username").fill('MarvelsGrantMan136')
        #     sleep(2)
        #     self.page.get_by_label("Password").fill('test1234')
        #     sleep(2)
        #     self.page.get_by_role("button", name="Log in").click()
        #     sleep(2)
        #     self.page.goto(url)

        sleep(3)

    async def click_at_position(self, x: int, y: int):
        await self.page.mouse.click(x, y)

    def click_at_position_sync(self, x: int, y: int):

        if y >= 768:
            logger.info(f"out of view size, update window size: h={y}")
            self.page.set_viewport_size({"width": 1024, "height": y+100})
            sleep(1)

        self.page.mouse.click(x, y)
        sleep(3)

        self.page.set_viewport_size({"width": 1024, "height": 768})


    async def input_at_position(self, x: int, y: int, text: str):
        await self.page.mouse.click(x, y)
        await self.page.keyboard.type(text)

    def input_at_position_sync(self, x: int, y: int, text: str):
        if y >= 768:
            logger.info(f"out of view size, update window size: h={y}")
            self.page.set_viewport_size({"width": 1024, "height": y+100})
            sleep(1)

        self.page.mouse.click(x, y)
        self.page.keyboard.type(text)
        sleep(3)

        self.page.set_viewport_size({"width": 1024, "height": 768})

    async def take_full_screenshot(self):
        pass

    def take_full_screenshot_sync(self):
        screenshot_data = self.page.screenshot(full_page=True)  # This returns bytes data directly

        pil_image = Image.open(io.BytesIO(screenshot_data))

        return pil_image

    async def get_current_url(self) -> str:
        return self.page.url

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()



class BrowserStartThread(QThread):
    started_signal = pyqtSignal()

    def __init__(self, wrapper: PlaywrightBrowserEnv):
        super().__init__()
        self.wrapper = wrapper

    def run(self):
        asyncio.run(self.wrapper.start_browser())
        self.started_signal.emit()

class NavigateThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, wrapper: PlaywrightBrowserEnv, url: str):
        super().__init__()
        self.wrapper = wrapper
        self.url = url

    def run(self):
        asyncio.run(self.wrapper.navigate_to(self.url))
        self.finished_signal.emit()

class ClickThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, wrapper: PlaywrightBrowserEnv, x: int, y: int):
        super().__init__()
        self.wrapper = wrapper
        self.x = x
        self.y = y

    def run(self):
        asyncio.run(self.wrapper.click_at_position(self.x, self.y))
        self.finished_signal.emit()

class InputThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, wrapper: PlaywrightBrowserEnv, x: int, y: int, text: str):
        super().__init__()
        self.wrapper = wrapper
        self.x = x
        self.y = y
        self.text = text

    def run(self):
        asyncio.run(self.wrapper.input_at_position(self.x, self.y, self.text))
        self.finished_signal.emit()

class ScreenshotThread(QThread):
    finished_signal = pyqtSignal(str)

    def __init__(self, wrapper: PlaywrightBrowserEnv, path: str = "screenshot.png"):
        super().__init__()
        self.wrapper = wrapper
        self.path = path

    def run(self):
        # asyncio.run(self.wrapper.take_full_screenshot(self.path))

        self.wrapper.take_full_screenshot_sync(self.path)

        self.finished_signal.emit(self.path)

class GetUrlThread(QThread):
    url_signal = pyqtSignal(str)

    def __init__(self, wrapper: PlaywrightBrowserEnv):
        super().__init__()
        self.wrapper = wrapper

    def run(self):
        current_url = asyncio.run(self.wrapper.get_current_url())
        self.url_signal.emit(current_url)

