#!/usr/bin/python3
# -*- coding: utf-8 -*-

import utils
from PyQt5.QtCore import QThread, pyqtSignal


class NetworkInfo(QThread):

    internal_ip = pyqtSignal(str)
    external_ip = pyqtSignal(str)
    hostname = pyqtSignal(str)
    location = pyqtSignal(str)
    api = pyqtSignal(str)
    oauth = pyqtSignal(str)

    def __init__(self, host_api, host_oauth):
        super().__init__()
        self.host_api = host_api
        self.host_oauth = host_oauth

    def run(self):
        try:
            self.internal_ip.emit(utils.get_internal_ip())
            data = utils.get_network_info()
            loc = f"{data['country']}, {data['region']}, {data['city']}"
            self.external_ip.emit(data['ip'])
            if 'hostname' in data:
                self.hostname.emit(data['hostname'])
            self.location.emit(loc)

        except Exception as e:
            print(e)
            self.internal_ip.emit(utils.get_internal_ip())
            self.external_ip.emit(None)
            self.hostname.emit(None)
            self.location.emit(None)

        if utils.check_connection(self.host_api):
            status = f"Хост: [{self.host_api}] - Доступен"
            self.api.emit(status)
        else:
            status = f"Хост: [{self.host_api}] - Недоступен"
            self.api.emit(status)

        if utils.check_connection(self.host_oauth):
            status = f"Хост: [{self.host_oauth}] - Доступен"
            self.oauth.emit(status)
        else:
            status = f"Хост: [{self.host_oauth}] - Недоступен"
            self.oauth.emit(status)

    def __del__(self):
        print("Never Say Goodbye")
