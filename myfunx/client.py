#!/bin/env python3

__all__ = ()

import time
import asyncio
from typing import (Any,
                    Union,
                    Literal,
                    Optional,)
import aiotgm
from . import logger
from aiotgm.types import *
from .json_manager import JsonManager

def parse_list(val: list) -> list[list[int]]:
    '''
    Used in the method clean_up_chat()
    to parse the list of mids in a
    nested of 100 for each sublist.
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
    '''
    Main class to communicate with the `Telegram Bot API <https://core.telegram.org/bots/api>`_.

    :param token: Api token obtained from `@BotFather <https://t.me/botfather>`_.
    :type token: :obj:`str`
    :param parse_mode: Select a default `parse mode <https://core.telegram.org/bots/api#formatting-options>`_ option (it can be overwritten in the methods).
    :type parse_mode: :obj:`str`, optional
    :param protect_content: Pass :obj:`True` to use the protect content option by default (it can be overwritten in the methods).
    :type protect_content: :obj:`bool`, optional
    :param proxy: Pass a proxy string to be used in the http requests.
    :type proxy: :obj:`str`, optional
    :param debug: Pass :obj:`True` for some debug information.
    :type debug: :obj:`bool`, optional
    :param deep_debug: Pass :obj:`True` for more debug information about http requests.
    :type deep_debug: :obj:`bool`, optional
    :param tracker: A :obj:`~myfunx.JsonManager` instance to track the messages.
    :type tracker: :obj:`~myfunx.JsonManager`, optional
    '''
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
               "'tracker' must be None or JsonManager,"
               f' got {tracker.__class__.__name__}.'
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

    @property
    def tracker(self) -> Optional[JsonManager]:
        return self._tracker

    def track_message(self, msg: Message, /) -> Optional[dict[str, Any]]:
        '''
        Client method to save in a json in the *traker* updates the following values:
        "message_id",
        "username" or first_name",
        "datetime".
        '''
        # Check if type is Message
        from datetime import datetime
        if not isinstance(msg, Message):
            raise TypeError(
                f'Expected Message in track_message(), got {msg.__class__.__name__}.'
            )
        # Check if file is ok
        data = self.tracker.check(msg.chat.id)
        # Add message_id
        data['mid'] += [msg.message_id]
        # Add username or first_name
        if msg.from_user:
            username = msg.from_user.username
            data['usr'] = username if username else msg.from_user.first_name
        else:
            data['usr'] = msg.chat.id
        # Add Unix-time
        if data['time'] is None:
            data['time'] = msg.date
        # Add datetime
        if data['datetime'] is None:
            data['datetime'] = str(datetime.now())
        return data


    async def send_message(self, chat_id: int | str, text: str, message_thread_id: int | None = None, parse_mode: str | None = None, entities: list[MessageEntity] | None = None, link_preview_options: LinkPreviewOptions | None = None, disable_notification: bool | None = None, protect_content: bool | None = None, reply_parameters: ReplyParameters | None = None, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None, track: bool = True) -> Message:
        '''
        :rtype: :obj:`~aiotgm.types.Message`
        '''
        msg = await super().send_message(chat_id, text, message_thread_id, parse_mode, entities, link_preview_options, disable_notification, protect_content, reply_parameters, reply_markup)
        if track and self.tracker:
            self.track_message(msg)
        return msg

    async def send_document(self, chat_id: int | str, document: InputFile | str, message_thread_id: int | None = None, thumbnail: InputFile | str | None = None, caption: str | None = None, parse_mode: str | None = None, caption_entities: list[MessageEntity] | None = None, disable_content_type_detection: bool | None = None, disable_notification: bool | None = None, protect_content: bool | None = None, reply_parameters: ReplyParameters | None = None, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None, track: bool = True) -> Message:
        '''
        :rtype: :obj:`~aiotgm.types.Message`
        '''
        msg = await super().send_document(chat_id, document, message_thread_id, thumbnail, caption, parse_mode, caption_entities, disable_content_type_detection, disable_notification, protect_content, reply_parameters, reply_markup)
        if track and self.tracker:
            self.track_message(msg)
        return msg

    async def send_video(self, chat_id: int | str, video: InputFile | str, message_thread_id: int | None = None, duration: int | None = None, width: int | None = None, height: int | None = None, thumbnail: InputFile | str | None = None, caption: str | None = None, parse_mode: str | None = None, caption_entities: list[MessageEntity] | None = None, has_spoiler: bool | None = None, supports_streaming: bool | None = None, disable_notification: bool | None = None, protect_content: bool | None = None, reply_parameters: ReplyParameters | None = None, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None, track: bool = True) -> Message:
        '''
        :rtype: :obj:`~aiotgm.types.Message`
        '''
        msg = await super().send_video(chat_id, video, message_thread_id, duration, width, height, thumbnail, caption, parse_mode, caption_entities, has_spoiler, supports_streaming, disable_notification, protect_content, reply_parameters, reply_markup)
        if track and self.tracker:
            self.track_message(msg)
        return msg

    async def send_photo(self, chat_id: int | str, photo: InputFile | str, message_thread_id: int | None = None, caption: str | None = None, parse_mode: str | None = None, caption_entities: list[MessageEntity] | None = None, has_spoiler: bool | None = None, disable_notification: bool | None = None, protect_content: bool | None = None, reply_parameters: ReplyParameters | None = None, reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None, track: bool = True) -> Message:
        '''
        :rtype: :obj:`~aiotgm.types.Message`
        '''
        msg = await super().send_photo(chat_id, photo, message_thread_id, caption, parse_mode, caption_entities, has_spoiler, disable_notification, protect_content, reply_parameters, reply_markup)
        if track and self.tracker:
            self.track_message(msg)
        return msg

    async def check_mids(self, target_id: Union[int, str], /, delay: float = 3600 * 3) -> None:
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
                    await self.send_message(target_id, text)
                diff_time = time.time() - start_time
                await asyncio.sleep(delay - diff_time)

        except:
            logger.info('Client method check_mids() was interrupted.')
            raise

    async def clean_up_chat(
        self,
        chat_id: Union[int, str]
    ) -> Literal[True]:
        data = self.tracker.get(chat_id)
        messages_history = data['mid']
        old_time = data['time']
        old_datetime = data['datetime']
        old_query = data['query']
        messages_to_delete = parse_list(messages_history)
        data.update({'mid': [], 'time': None, 'datetime': None, 'query': None})
        try:
            for messages_list in messages_to_delete:
                await self.delete_messages(chat_id, messages_list)
                if len(messages_to_delete) > 1:
                    messages_history = [x for x in messages_history if x not in messages_list]
                    await asyncio.sleep(1)
        except:
            restored_data = self.tracker.get(chat_id)
            restored_data['mid'] += messages_history
            restored_data['time'] = old_time
            restored_data['datetime'] = old_datetime
            restored_data['query'] = old_query
            self.tracker.updates[chat_id] = restored_data
            self.tracker.push_updates()
            logger.warning(
                f"{chat_id}'s chat cleanup was"
                ' interrupted. Json was restored.'
            )
            raise
        else:
            return True
