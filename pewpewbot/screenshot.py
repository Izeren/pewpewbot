import asyncio
import logging
from copy import deepcopy

import structlog
from arsenic import browsers, keys, services, start_session, stop_session
from arsenic.session import Session
from structlog.types import WrappedLogger

from pewpewbot.state import State

# Fix long values in log for screenshot method
class DictTrimmerProcessor:
    def __init__(self, max_chars=25) -> None:
        self.max_chars = max_chars
        self.block_length = max_chars // 2 - 1

    def __call__(self, logger: WrappedLogger, method_name: str, event_dict: dict):
        """Processor to trim long fields in dicts
        Description: https://www.structlog.org/en/stable/processors.html
        """
        for field in event_dict:
            if isinstance(event_dict[field], dict):
                val = deepcopy(event_dict[field]) # Copy so that original event_dict is not changed
                for key in val:
                    if isinstance(val[key], str) and len(val[key]) > self.max_chars:
                        val[key] = f"{val[key][:self.block_length]}...{val[key][-self.block_length:]}"
                event_dict[field] = val
        return event_dict


def fix_arsenic_log():
    processors = structlog.get_config().get("processors", [])
    processors.insert(0, DictTrimmerProcessor())
    structlog.configure(processors=processors)

class Screenshoter:
    def __init__(
        self, url=None, height=1000, width=1000, file_name="screenshot.png", loop=None
    ):
        fix_arsenic_log()
        self.url = url
        self.height = height
        self.width = width
        self.file_name = file_name
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        service = services.Chromedriver()
        browser = browsers.Chrome(
            **{
                "goog:chromeOptions": {
                    "args": ["--headless", "--no-sandbox", "--disable-dev-shm-usage", "--incognito"],
                    "w3c": True,
                }
            }
        )
        self.session: Session = loop.run_until_complete(start_session(service, browser))

    async def sync_with_state(self, state: State):
        # Update URL
        if state.screenshot_url is not None and state.screenshot_url != self.url:
            self.url = state.screenshot_url
            await self.session.get(self.url)
            if "docs.google.com" in self.url:
                await self.hide_topbar_gdocs()
            logging.info(f"Updated url to {self.url}")

        # Update page size
        if (
            state.screenshot_width != self.width
            or state.screenshot_height != self.height
        ):
            self.width = state.screenshot_width
            self.height = state.screenshot_height
            await self.session.set_window_size(self.width, self.height)
            logging.info(f"Updated window size to {self.width}x{self.height}")

    async def hide_topbar_gdocs(self):
        elem = await self.session.get_element("body")
        await elem.send_keys(f"{keys.CONTROL}{keys.SHIFT}F")

    async def update_screenshot(self, state):
        logging.info(f"Updating screenshot...")
        await self.sync_with_state(state)
        if self.url is None:
            logging.info(f"URL not set.")
            return
        image_bytes = await self.session.get_screenshot()
        with open(self.file_name, "wb") as f:
            f.write(image_bytes.read())

    def __del__(self):
        try:
            logging.info("Shutting down browser session...")
            self.loop.run_until_complete(stop_session(self.session))
        except AttributeError:  # if session does not exist, do nothing
            pass
