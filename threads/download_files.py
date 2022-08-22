#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import utils
from PyQt5.QtCore import QThread, pyqtSignal


class DownloadsFile(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    progress_range = pyqtSignal(int)
    abort_download = pyqtSignal(str)
    loading_audio = pyqtSignal(str)
    unavailable_audio = pyqtSignal(str)
    message = pyqtSignal(int, int, int)
    content_restricted = pyqtSignal(int, str)

    def __init__(self, count_track, path, downloads_list=None, data=None):
        super().__init__()
        self.count_track: int = count_track
        self.downloads_list: list = downloads_list
        self.selected_audios: int = len(self.downloads_list)
        self.completed: int = 0
        self.current_track: str = ''
        self.data: list = data
        self.current_path: str = path

    def run(self):
        try:
            for item in self.downloads_list:
                self.current_track = str(self.data[item])
                filename = f"{self.current_path}/{self.data[item].get_filename()}"

                if self.data[item].url == "":
                    if self.data[item].content_restricted:
                        content_restricted = int(self.data[item].content_restricted)
                        self.content_restricted.emit(content_restricted, self.current_track)
                    else:
                        self.unavailable_audio.emit(self.current_track)

                else:
                    self.update_label(self.count_track, self.selected_audios, self.completed)
                    self.loading_audio.emit(self.current_track)

                    utils.downloads_files_in_wget(
                        self.data[item].get_url(),
                        filename,
                        self.update_progress
                    )

                    self.completed += 1
                    self.update_label(self.count_track, self.selected_audios, self.completed)

            self.finished.emit()
            self.loading_audio.emit('')

        except Exception as e:
            self.abort_download.emit(str(e))

    # Magic. Do not touch.
    def update_progress(self, current, total, wight=80):
        self.progress_range.emit(total)
        self.progress.emit(current)

    def update_label(self, count, selected, completed):
        self.message.emit(count, selected, completed)
