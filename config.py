#!/usr/bin/python3
# -*- coding: utf-8 -*-

from os.path import abspath, dirname


class MetaSingleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=MetaSingleton):
    ApplicationName = "VKMusicDownloader"
    ApplicationVersion = "1.1.17"
    ApplicationBranch = "Public Pre-Release"
    Description = "Кроссплатформенный клиент для массового скачивания музыки из ВКонтакте."

    ApplicationFullName = f"{ApplicationName} {ApplicationVersion} {ApplicationBranch}"

    IconPath = dirname(abspath(__file__)) + "/assets/icon/vk_downloader_icon.png"
    IconPathV2 = dirname(abspath(__file__)) +  "/assets/icon/downloader_icon.png"
    IconPathV3 = dirname(abspath(__file__)) +  "/assets/icon/downloader.png"

    AuthFile = dirname(abspath(__file__)) + "/DATA"

    License = "https://github.com/dreamerbruh420/VKMusicDownloader/blob/master/LICENSE"
    SourceCode = "https://github.com/dreamerbruh420/VKMusicDownloader"

    UseAnalytics = True


config = Config()
