#!/usr/bin/python3
# -*- coding: utf-8 -*-

import platform
import json
import requests

from base64 import urlsafe_b64decode as dec
from config import config


ENDPOINT_URL = dec(b'aHR0cHM6Ly9pbW1lbnNlLXNob3JlLTUxODIxLmhlcm9rdWFwcC5jb20vYXBpL3NlbmRTdGF0aXN0aWM=').decode("utf-8")
DONT_SENDING_STATS = not config.UseAnalytics

stats_data = dict(
    platform=dict(
        system=platform.system(),
        machine=platform.machine(),
        node=platform.node(),
        version=platform.version()
    ),
    app_meta=dict(
        name=config.ApplicationName,
        version=config.ApplicationVersion,
        branch=config.ApplicationBranch
    ),
    python=dict(
        build=platform.python_build(),
        compiler=platform.python_compiler(),
        implementation=platform.python_implementation(),
        version=platform.python_version(),
        exec=platform.sys.executable
    )
)


class Statistic:

    def __init__(self, can_sending_data):
        self.stats_data = stats_data
        self.is_sended = can_sending_data
        self.headers = {
            'user-agent': f'{config.ApplicationName}/{config.ApplicationVersion}',
            'content-type': 'application/json'
        }

    def send(self):
        if not self.is_sended:
            self.is_sended = True
            try:
                requests.post(
                    ENDPOINT_URL,
                    data=json.dumps(self.stats_data),
                    timeout=10,
                    headers=self.headers
                )

            except Exception as _:
                return
        else:
            return

    def set_user_id(self, user_id=None) -> dict:
        return self.stats_data.update(dict(user_id=user_id)) if not self.is_sended else ...


stat = Statistic(DONT_SENDING_STATS)

__all__ = ['stat']
