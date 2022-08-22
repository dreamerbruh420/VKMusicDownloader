#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
from math import ceil

from .api_handlers import APIHandler, APIConstants
from models import Audio


class LoadMusicHandler:
    """Класс, реализующий логику загрузки списка музыки"""

    def __init__(self, api_handler: APIHandler):
        self.api_handler = api_handler

    def load_all_music(self, user_id, count=None) -> list:
        try:
            response = []
            if count > APIConstants.count_audios:
                for i in range(ceil(count / APIConstants.count_audios)):
                    response.extend(
                        self.api_handler.get_audio(
                            user_id=user_id, 
                            offset=APIConstants.count_audios * i
                        )['response']['items']
                    )

                    if i != 0 and i % 10 == 0:
                        time.sleep(5)
            else:
                response = self.api_handler.get_audio(user_id=user_id)['response']['items']
            
            return [Audio(audio) for audio in response]

        except Exception as e:
            raise e
