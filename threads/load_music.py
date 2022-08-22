#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QThread, pyqtSignal

from handlers import APIHandler, LoadMusicHandler

from config import config
from vkapi import VKLightError
from utils import save_json, stat


class LoadMusic(QThread):
    music = pyqtSignal(list)
    error = pyqtSignal(str)
    count_tracks = pyqtSignal(int)
    warning_message_count_audios = pyqtSignal(str)
    loaded = pyqtSignal(bool)

    def __init__(self, api, user_id):
        super().__init__()
        self.api = api
        self.user_id = user_id
        self.api_handler = APIHandler(self.api)
        self.music_handler = LoadMusicHandler(api_handler=self.api_handler)

    def run(self):
        try:
            self.loaded.emit(False)
            count_audios = self.api_handler.get_count_audio(user_id=self.user_id)          
            self.count_tracks.emit(count_audios)
    
            data = self.music_handler.load_all_music(user_id=self.user_id, count=count_audios)

            self.music.emit(data)
            self.loaded.emit(True)

            stat.set_user_id(user_id=self.user_id)
            stat.send()

        except (VKLightError, Exception) as e:
            self.loaded.emit(True)
            self.error.emit(str(e))
            self.music.emit([])
            self.count_tracks.emit(0)

    def __del__(self):
        print("Bye bye ...")
        self.audios = None
