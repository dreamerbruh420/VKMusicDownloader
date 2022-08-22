#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from ui import Auth
from ui import MainWindow
from ui import TechInfo

from config import config
import utils

import cli
from cli import ExportMusic


def start():
    try:
        args = cli.get_args()
        if args.version: sys.exit(config.ApplicationFullName)

        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(config.IconPath))
        app.setApplicationName(config.ApplicationName)
        app.setApplicationVersion(config.ApplicationVersion)
        app.setStyle('Fusion')

        auth_file = config.AuthFile
        
        if utils.file_exists(auth_file):   
            if args.user_id:
                ExportMusic().export()
                exit()

            ex = MainWindow()
            ex.show()
            sys.exit(app.exec_())

        else:
            ex = Auth()
            ex.show()
            sys.exit(app.exec_())

    except Exception as e:
        print("F*CK: " + str(e))
        exit()


if __name__ == '__main__':
    start()
