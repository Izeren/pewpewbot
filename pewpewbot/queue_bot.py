import asyncio
import logging
import typing
from asyncio.base_events import _format_handle
from dataclasses import dataclass

import aiohttp
from aiogram import Bot, types
from aiogram.types import base
from aiogram.utils.exceptions import RetryAfter

from pewpewbot.utils import split_text

@dataclass
class FutureCall:
    """Represents function call with args and result future to put in queue"""
    result: asyncio.Future
    func: typing.Union[typing.Callable, typing.Coroutine]
    args: typing.List[typing.Any]
    kwargs: typing.Dict[str, typing.Any]

    def __post_init__(self):
        # Remove service locals
        self.kwargs = {k: v for k, v in self.kwargs.items() if not k.startswith("_")}
        # If method is bound, remove self from kwargs
        if hasattr(self.func, '__self__') and "self" in self.kwargs:
            del self.kwargs["self"]


class QueueBot(Bot):
    """aiogram bot that handles messages via queue, handles Too Many Requests error and pagination"""

    def __init__(
        self,
        token: base.String,
        loop: typing.Optional[
            typing.Union[asyncio.BaseEventLoop, asyncio.AbstractEventLoop]
        ] = None,
        connections_limit: typing.Optional[base.Integer] = None,
        proxy: typing.Optional[base.String] = None,
        proxy_auth: typing.Optional[aiohttp.BasicAuth] = None,
        validate_token: typing.Optional[base.Boolean] = True,
        parse_mode: typing.Optional[base.String] = None,
        timeout: typing.Optional[
            typing.Union[base.Integer, base.Float, aiohttp.ClientTimeout]
        ] = None,
    ):
        if loop is None:
            loop = asyncio.get_event_loop()
        self.queue = asyncio.Queue()
        loop.create_task(self.process_queue())
        super().__init__(
            token,
            loop=loop,
            connections_limit=connections_limit,
            proxy=proxy,
            proxy_auth=proxy_auth,
            validate_token=validate_token,
            parse_mode=parse_mode,
            timeout=timeout,
        )

    async def send_message(
        self,
        chat_id: typing.Union[base.Integer, base.String],
        text: base.String,
        parse_mode: typing.Union[base.String, None] = None,
        disable_web_page_preview: typing.Union[base.Boolean, None] = None,
        disable_notification: typing.Union[base.Boolean, None] = None,
        reply_to_message_id: typing.Union[base.Integer, None] = None,
        reply_markup: typing.Union[
            types.InlineKeyboardMarkup,
            types.ReplyKeyboardMarkup,
            types.ReplyKeyboardRemove,
            types.ForceReply,
            None,
        ] = None,
    ) -> typing.List[typing.Awaitable[types.Message]]:
        """Splits message, puts in the queue, returns list of Future of sent messages"""
        all_args = locals()
        fut_list = []
        for chunk in split_text(text):
            fut = self._main_loop.create_future()
            call = FutureCall(result=fut, func=super().send_message, args=(), kwargs={**all_args, 'text': chunk})
            await self.queue.put(call)
            fut_list.append(fut)
        return fut

    async def process_call(self, fcall: FutureCall):
        result = fcall.func(*fcall.args, **fcall.kwargs)
        if asyncio.iscoroutine(result):
            result = await result
        fcall.result.set_result(result)
    
    async def process_queue(self):
        while True:
            fcall: FutureCall = await self.queue.get()
            try:
                await self.process_call(fcall)
            except RetryAfter as exc:
                logging.warning(f"Hit rate limits, waiting {exc.timeout} seconds")
                await asyncio.sleep(exc.timeout + 1)
                # Send popped message again
                await self.process_call(fcall)
            except Exception as exc:
                logging.error(exc_info=exc)
                fcall.result.set_exception(exc)
            finally:
                self.queue.task_done()
