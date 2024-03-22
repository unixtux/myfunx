#!/bin/env python3

__all__= ()

import os
import re
import asyncio
from . import logger
import ujson as json
from typing import (Any,
                    Union,
                    Optional,)
BASE_DICT = {
    'usr': None,
    'mid': [],
    'time': None,
    'query': None
}
INT_PATTERN = re.compile(r'^(\-|\d){0,1}\d+$')
MERGE_PATTERN = re.compile(r'^(\-|\d){0,1}\d+\.json$')

def _json_format(chat_id: Union[str, int]) -> str:
    file_name = str(chat_id)
    if not file_name.endswith('.json'):
        return file_name + '.json'
    return file_name


class JsonManager:

    def __init__(
        self,
        main_dir: Optional[str],
        *,
        base_dict: Optional[dict[str, Any]]
    ):
        if not isinstance(main_dir, (str, type(None))):
            raise TypeError(
                "'main_dir' must be str, pass None"
                ' to use the current directory.'
            )
        if main_dir is not None and not os.path.isdir(main_dir):
            raise NotADirectoryError(
                "'main_dir' is not a directory, pass"
                ' None to use the current one.'
            )
        if not isinstance(base_dict, (dict, type(None))):
            raise TypeError(
                "'base_dict' must be dict or"
                f' None, got {base_dict.__class__.__name__}.'
            )

        if main_dir is None: main_dir = './'
        elif not main_dir.endswith('/'): main_dir += '/'

        self._main_dir = main_dir
        self._updates = {}

        if base_dict is None:
            base_dict = {}

        base_dict.update(BASE_DICT)
        self._base_dict = base_dict

    @property
    def main_dir(self) -> str:
        return self._main_dir

    @property
    def updates(self) -> dict[int, dict[str, Any]]:
        return self._updates

    @property
    def base_dict(self) -> dict[str, Any]:
        return self._base_dict.copy()


    def get(self, chat_id: int, /) -> dict[str, Any]:

        if INT_PATTERN.match(str(chat_id)):
            chat_id = int(chat_id)
        else:
            logger.warning(
                'integer conversion failed'
                f' for {chat_id!r} in get() method'
            )
        if chat_id in self.updates:
            logger.debug(f'Got {chat_id!r} from updates.')
        else:
            file_name = _json_format(chat_id)
            try:
                with open(self.main_dir + file_name) as r:
                    self.updates[chat_id] = json.loads(r.read())
            except FileNotFoundError:
                raise FileNotFoundError(
                    f'No such file {self.main_dir + file_name!r}.'
                    ' You should use the check() method before to'
                    ' call the get() to ensure the file exists.'
                )
            logger.debug(f'Got {chat_id!r} from file.')

        return self.updates[chat_id]


    def merge(self) -> dict[int, dict[str, Any]]:
        '''
        Useful for the bot Client to merge
        all the json in the updates dict,
        non-integer files will be skipped
        '''
        for file_name in os.listdir(self.main_dir):

            if MERGE_PATTERN.match(file_name):
                chat_id = file_name.replace('.json', str())
                self.get(chat_id)
            else:
                logger.warning(
                    f'Unexpected file {self.main_dir + file_name!r}'
                    ' in the merge() method, it was skipped.'
                )
        return self.updates


    def check(self, chat_id: int, /) -> dict[str, Any]:
        '''
        Useful for the bot Client, to ensure that the json keys exist.
        '''
        file_name = _json_format(chat_id)

        if (chat_id in self.updates
            or os.path.isfile(self.main_dir + file_name)):

            result = {}
            actual_dict = self.get(chat_id)
            for key, val in self.base_dict.items():

                if key in actual_dict:
                    val = actual_dict[key]

                result.update({key: val})
        else:
            result = self.base_dict

        self.updates[chat_id] = result

        return self.updates[chat_id]


    def push_updates(self) -> int:
        '''
        You need to call this method explicitly, to push the
        updates to files. Used in the method process_updates().
        '''

        for chat_id in self.updates:
            file_name = _json_format(chat_id)
            logger.debug(f'Pushing {chat_id!r} {self.updates[chat_id]!r}')

            with open(self.main_dir + file_name, 'w') as push_json:
                push_json.write(json.dumps(self.updates[chat_id], indent = 2))

        return len(self.updates)


    async def process_updates(self, delay: int = 15) -> None:
        '''
        Coroutine to process the updates and write them to files.
        '''
        try:
            while True:
                if self.updates:
                    self.push_updates()
                await asyncio.sleep(delay)
        except:
            pushed = self.push_updates()
            were = 'was' if pushed == 1 else 'were'
            s = str() if pushed == 1 else 's'
            logger.info(
                f'{pushed} json file{s} {were} saved.'
            )
            raise
