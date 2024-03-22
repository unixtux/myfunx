#!/bin/env python3

__all__ = ()

import time
import asyncio
from typing import (Any,
                    Union,
                    Literal,
                    Optional,)
import aiotgm
from aiotgm.types import *
from . import logger, my_id
from .json_manager import JsonManager, logger

def parse_list(val: list) -> list[list]:
    '''
    Used in the method clean_up_chat()
    to parse the list of mids.
    '''
    n = 100
    res = []
    while True:
        nest = val[n-100:n]
        res.append(sorted(nest))
        if len(val) <= n:
            return res
        else:
            n += 100


class Client(aiotgm.Client):

    def __init__(
        self,
        token: str,
        *,
        parse_mode: Optional[str] = None,
        protect_content: Optional[bool] = None,
        proxy: Optional[str] = None,
        debug: Optional[bool] = None,
        deep_debug: Optional[bool] = None,
        tracker: Optional[JsonManager] = None
    ):
        if not isinstance(tracker, (JsonManager, type(None))):
            raise TypeError(
               "'tracker' must be None or a JsonManager"
               f' instance, got {tracker.__class__.__name__}.'
            )
        self._tracker = tracker

        super().__init__(
            token,
            parse_mode=parse_mode,
            protect_content=protect_content,
            proxy=proxy,
            debug=debug,
            deep_debug=deep_debug
        )

    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        message_thread_id: int | None = None,
        parse_mode: str | None = None,
        entities: list[MessageEntity] | None = None,
        link_preview_options: LinkPreviewOptions | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_parameters: ReplyParameters | None = None,
        reply_markup: REPLY_MARKUP_TYPES | None = None,
        track: bool = True
    ) -> Message:
        msg = await super().send_message(chat_id, text, message_thread_id, parse_mode, entities, link_preview_options, disable_notification, protect_content, reply_parameters, reply_markup)
        if track and self.tracker:
            self.track_message(msg)
        return msg

    async def send_document(
        self,
        chat_id: int | str,
        document: InputFile | str,
        message_thread_id: int | None = None,
        thumbnail: InputFile | str | None = None,
        caption: str | None = None,
        parse_mode: str | None = None,
        caption_entities: list[MessageEntity] | None = None,
        disable_content_type_detection: bool | None = None,
        disable_notification: bool | None = None,
        protect_content: bool | None = None,
        reply_parameters: ReplyParameters | None = None,
        reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None,
        track: bool = True
    ) -> Message:
        msg = await super().send_document(chat_id, document, message_thread_id, thumbnail, caption, parse_mode, caption_entities, disable_content_type_detection, disable_notification, protect_content, reply_parameters, reply_markup)
        if track and self.tracker:
            self.track_message(msg)
        return msg

    @property
    def tracker(self) -> Optional[JsonManager]:
        return self._tracker

    def track_message(self, msg: Message, /) -> Optional[dict[str, Any]]:
        if not isinstance(msg, Message):
            raise TypeError(
                f'Expected Message in track_message(), got {msg.__class__.__name__}.'
            )
        if msg.chat.type != 'private':
            return
        data = self.tracker.check(msg.chat.id)
        data['mid'] += [msg.message_id]
        if data['time'] is None:
            data['time'] = msg.date
        return data

    async def check_mids(self, hours_to_sleep: int = 3) -> None:
        try:
            while True:
                start_time = time.time()
                users = self.tracker.merge()
                text = str()
                for chat_id in users:
                    data = users[chat_id]
                    if data['time']:
                        user = data['usr']
                        first_log = data['time']
                        remaining_hours = 48 - (round((start_time-first_log) / 3600))
                        if remaining_hours <= 12:
                            if remaining_hours > 2 or remaining_hours < 0:
                                text += f'{remaining_hours} hours'
                            else:
                                remaining_minutes = 2880 - (round((start_time-first_log) / 60))
                                text += f'{remaining_minutes} minutes'
                            text += f" to clean {user}'s chat 📝️\n"
                if text:
                    await self.send_message(my_id, text)
                diff_time = time.time() - start_time
                await asyncio.sleep(3600 * hours_to_sleep - diff_time)

        except:
            logger.info('Client method check_mids() was interrupted.')
            raise

    async def clean_up_chat(
        self,
        chat_id: Union[int, str]
    ) -> Literal[True]:
        data = self.tracker.get(chat_id)
        messages_history = data['mid']
        messages_to_delete = parse_list(messages_history)
        data.update({'mid': [], 'time': None, 'query': None})
        try:
            for messages_list in messages_to_delete:
                await self.delete_messages(chat_id, messages_list)
                if len(messages_to_delete) > 1:
                    messages_history = [x for x in messages_history if x not in messages_list]
                    await asyncio.sleep(1)
        except:
            restored_data = self.tracker.get(chat_id)
            restored_data['mid'] += messages_history
            self.tracker.updates[chat_id] = restored_data
            self.tracker.push_updates()
            logger.warning(
                f"{chat_id}'s chat cleanup was"
                ' interrupted. Json was restored.'
            )
            raise
        else:
            return True
