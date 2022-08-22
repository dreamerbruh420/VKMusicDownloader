#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import datetime
import json

import socket
import requests
import wget

from config import config


def fix_filename(filename) -> str:
    if len(filename) >= 128:
        return re.sub(r'[\\/:*?\"<>|\n\r\xa0]', "", filename[0:126])
    else:
        return re.sub(r'[\\/:*?\"<>|\n\r\xa0]', "", filename)


def file_exists(path) -> bool:
    try:
        return os.path.exists(path)
    except OSError:
        return False


def get_path(self, flags, _object):
    if flags:
        path = _object.getExistingDirectory(
            self,
            "Выберите папку для скачивания",
            "",
            _object.ShowDirsOnly
        )

        return path if path != "" else os.getcwd()
    else:
        return os.getcwd()


def check_connection(url):
    try:
        requests.head(url, timeout=5)
    except Exception:
        return False

    return True


def get_internal_ip():
    try:
        return socket.gethostbyname(socket.getfqdn())
    except Exception:
        return None


def get_external_ip():
    try:
        return bytes(
            requests.get("http://ident.me/", timeout=5).content
        ).decode("utf-8")

    except Exception:
        return None


def get_network_info():
    return requests.get("http://ipinfo.io", timeout=5).json()


def unix_time_stamp_convert(time) -> str:
    return datetime.datetime.fromtimestamp(int(time)
                                           ).strftime("%d.%m.%Y %H:%M:%S")


def time_duration(time) -> str:
    return str(datetime.timedelta(seconds=int(time)))


def get_current_datetime() -> str:
    return datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")


def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return json.loads(file.read())


def downloads_files_in_wget(url, filename, progress):
    wget.download(url, out=filename, bar=progress)


def get_user_agent(usage_application_name) -> str:
    if usage_application_name:
        return f'VKAndroidApp/6.45-8597 (Android 12; SDK 31; arm64-v8a;' \
               f'{config.ApplicationName} {config.ApplicationVersion}; ru; 1920x1080)'
    else:
        return 'VKAndroidApp/6.45-8597 (Android 12; SDK 31; arm64-v8a; Unknown; ru; 1920x1080)'


def get_mp3_url(url) -> str:
    if '.mp3' in url:
        return url

    return url
