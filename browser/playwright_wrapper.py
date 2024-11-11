import asyncio

from PyQt6.QtCore import QThread, pyqtSignal
from playwright.async_api import async_playwright

class PlaywrightWrapper:
    def __init__(self, headless=True):
        self.browser = None
        self.page = None
        self.headless = headless

    async def start_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()

    async def navigate_to(self, url: str):
        await self.page.goto(url)

    async def click_at_position(self, x: int, y: int):
        await self.page.mouse.click(x, y)

    async def input_at_position(self, x: int, y: int, text: str):
        await self.page.mouse.click(x, y)
        await self.page.keyboard.type(text)

    async def take_full_screenshot(self, path: str = "screenshot.png"):
        await self.page.screenshot(path=path, full_page=True)

    async def get_current_url(self) -> str:
        return self.page.url

    async def close(self):
        await self.browser.close()
        await self.playwright.stop()



class BrowserStartThread(QThread):
    started_signal = pyqtSignal()

    def __init__(self, wrapper: PlaywrightWrapper):
        super().__init__()
        self.wrapper = wrapper

    def run(self):
        asyncio.run(self.wrapper.start_browser())
        self.started_signal.emit()

class NavigateThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, wrapper: PlaywrightWrapper, url: str):
        super().__init__()
        self.wrapper = wrapper
        self.url = url

    def run(self):
        asyncio.run(self.wrapper.navigate_to(self.url))
        self.finished_signal.emit()

class ClickThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, wrapper: PlaywrightWrapper, x: int, y: int):
        super().__init__()
        self.wrapper = wrapper
        self.x = x
        self.y = y

    def run(self):
        asyncio.run(self.wrapper.click_at_position(self.x, self.y))
        self.finished_signal.emit()

class InputThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, wrapper: PlaywrightWrapper, x: int, y: int, text: str):
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

    def __init__(self, wrapper: PlaywrightWrapper, path: str = "screenshot.png"):
        super().__init__()
        self.wrapper = wrapper
        self.path = path

    def run(self):
        asyncio.run(self.wrapper.take_full_screenshot(self.path))
        self.finished_signal.emit(self.path)

class GetUrlThread(QThread):
    url_signal = pyqtSignal(str)

    def __init__(self, wrapper: PlaywrightWrapper):
        super().__init__()
        self.wrapper = wrapper

    def run(self):
        current_url = asyncio.run(self.wrapper.get_current_url())
        self.url_signal.emit(current_url)

