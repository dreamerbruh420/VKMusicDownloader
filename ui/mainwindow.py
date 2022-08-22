#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

import utils
from config import config

from vkapi import VKLightOauth, VKLight, VKLightError, VKLightOauthError
from handlers import APIHandler, LoadMusicHandler

from threads import DownloadsFile, LoadMusic

from .window import auth
from .window import mainwindow
from .tech_info import TechInfo


from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, Qt


# Окно авторизации
class Auth(QtWidgets.QMainWindow, auth.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.window = None
        self.setupUi(self)
        self.setWindowIcon(QIcon(config.IconPath))
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.statusBar().showMessage("2fa is supported :)")
        self.pushButton.clicked.connect(self.go)
        self.pushButton.setShortcut("Return")
        self.oauth = VKLightOauth(dict())

    def go(self):
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()
        r = None
        self.statusBar().showMessage('Loading...')
        self.oauth = VKLightOauth(
            dict(
                login=login,
                password=password,
                proxy=self.action.isChecked()
            )
        )
        try:
            try:
                r = self.oauth.go()

            except VKLightOauthError as e:
                if 'need_validation' in e.error:
                    if 'ban_info' in dir(e):
                        return QMessageBox.critical(self, "F*CK", str(e))

                    code, ok = QInputDialog.getText(
                        self,
                        "Подтвердите номер",
                        "Мы отправили SMS с кодом на номер"
                    )

                    if ok:
                        self.oauth = VKLightOauth(
                            dict(
                                login=login,
                                password=password,
                                proxy=self.action.isChecked(),
                                code=code
                            )
                        )
                        r = self.oauth.go()
                else:
                    raise e

            except Exception as e:
                raise e

            self.statusBar().showMessage('Done!')

        except VKLightOauthError as e:

            if 'need_captcha' in e.error:
                return QMessageBox.critical(self, 'F*CK', 'F*CKING CAPTHA')
            else:
                return QMessageBox.critical(self, 'F*CK', str(e))

        except Exception as e:
            self.statusBar().showMessage('Login failed :(')
            QMessageBox.critical(self, "F*CK", str(e))

        else:

            access_token = r['access_token']
            user_id = r['user_id'] or ''

            api = VKLight(dict(
                    access_token=access_token,
                    proxy=self.action.isChecked()
                )
            )
            api_handler = APIHandler(api=api)
            
            self.statusBar().showMessage('Getting refresh_token')
            refresh_token = api_handler.refresh_token(
                access_token=access_token
            )['response']['token']

            data = {
                'access_token': access_token,
                'token': refresh_token,
                'user_id': user_id
            }
            utils.save_json(config.AuthFile, data)

            # Запуск главного окна
            self.window = MainWindow()
            self.hide()
            self.window.show()


class MainWindow(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.auth_window = None
        self.tech_info_window = None
        self.completed = 0

        self.setupUi(self)
        self.setWindowIcon(QIcon(config.IconPath))
        self.setWindowFlags(QtCore.Qt.Window)

        self.pushButton_2.clicked.connect(self.loads_list_music)
        self.pushButton.clicked.connect(self.download)
        self.pushButton.setCheckable(True)
        self.action.triggered.connect(self.about_message)
        self.action_2.setShortcut("Ctrl+Q")
        self.action_2.triggered.connect(self.logout)
        self.action_4.triggered.connect(self.tech_information)
        self.action_4.setShortcut("Ctrl+T")
        self.progressBar.setFormat("%p% (%v/%m)")
        
        self.PATH = os.getcwd()

        self.api = VKLight(dict())
        self.data = None
        self.lm = None
        self.th = None
        self.is_loaded = False
        self.getSelected = []
        self.downloads_list = []
        self.count_track = 0
        self.user_id = 0

    def loads_list_music(self):
        try:
            data_token = utils.read_json(config.AuthFile)
            access_token = data_token["access_token"]
            refresh_token = data_token["token"]
            self.user_id = data_token["user_id"]

            self.api = VKLight(dict(
                    access_token=refresh_token,
                    proxy=self.action_5.isChecked()
                )
            )

            self.lm = LoadMusic(self.api, self.user_id)

            self.lm.music.connect(self.fill_table)
            self.lm.error.connect(self.show_error)
            self.lm.count_tracks.connect(self.set_count)
            self.lm.warning_message_count_audios.connect(self.show_warning)
            self.lm.loaded.connect(self.pushButton_2.setEnabled)

            self.lm.start()
            self.is_loaded = True

        except (Exception, VKLightError)as ex:
            QMessageBox.critical(self, "F*CK", str(ex))

    def download(self, started):
        try:
            if not self.is_loaded:
                self.pushButton.setChecked(False)
                return QMessageBox.information(
                    self,
                    "Информация",
                    "Вы не загрузили список аудиозаписей"
                )

            self.downloads_list = [int(i.text(0)) - 1 for i in self.treeWidget.selectedItems()]

            if len(self.downloads_list) == 0:
                self.pushButton.setChecked(False)
                return QMessageBox.information(
                    self, "Информация", "Ничего не выбрано."
                )

            if started:

                self.PATH = utils.get_path(self,self.action_7.isChecked(), QFileDialog)
                self.label_2.setText("Путь для скачивания: " + self.PATH)
                self.pushButton.setText("Остановить")

                self.th = DownloadsFile(
                    self.count_track,
                    self.PATH,
                    self.downloads_list,
                    self.data
                )

                self.th.progress_range.connect(self.progress)
                self.th.progress.connect(self.progress_set_value)
                self.th.loading_audio.connect(self.loading_audio)
                self.th.message.connect(self.set_text)
                self.th.unavailable_audio.connect(self.unavailable_audio)
                self.th.content_restricted.connect(self.content_restricted)
                self.th.finished.connect(self.finished_loader)
                self.th.abort_download.connect(self.aborted_download)
                self.th.start()

            else:
                self.th.terminate()
                self.set_ui_default()
                QMessageBox.information(self, "Информация", "Загрузка остановлена.")
                del self.th

        except Exception as e:
            QMessageBox.critical(self, "F*CK", str(e))
            self.pushButton.setText("Скачать")

    def set_ui_default(self):
        self.downloads_list = []
        self.pushButton.setText("Скачать")
        self.pushButton.setChecked(False)
        self.progressBar.setValue(0)
        self.progressBar.setRange(0, 100)
        self.progressBar.setFormat("%p% (%v/%m)")
        self.label_3.setText("Загружается: ")
        self.label.setText(f"Всего аудиозаписей: {str(self.count_track)} Выбрано: 0 Загружено: 0")

    @pyqtSlot(list)
    def fill_table(self, data):
        self.data = data
        QtWidgets.QTreeWidget.clear(self.treeWidget)

        for i, audio in enumerate(data, 1):

            test = QtWidgets.QTreeWidgetItem(self.treeWidget)

            test.setText(0, str(i))
            test.setText(1, audio.artist)
            test.setText(2, audio.title)
            test.setText(3, utils.time_duration(audio.duration))
            test.setText(4, utils.unix_time_stamp_convert(audio.date))

            if audio.is_hq:
                if audio.is_explicit:
                    test.setText(5, "HQ (E)")
                else:
                    test.setText(5, "HQ")
            else:
                if audio.is_explicit:
                    test.setText(5, "E")

            if audio.url == "":
                test.setText(6, "Недоступно")

    @pyqtSlot(str)
    def show_error(self, error):
        QMessageBox.critical(self, "F*CK", f"{error}")

    @pyqtSlot(str)
    def show_warning(self, msg):
        QMessageBox.warning(self, "Внимание", msg)

    @pyqtSlot(int)
    def set_count(self, count=0, selected=0, completed=0):
        self.count_track = count
        self.set_text(count, selected, completed)

    @pyqtSlot(int, int, int)
    def set_text(self, count=0, selected=0, completed=0):
        self.label.setText(
            f"Всего аудиозаписей: {count}" +
            f" Выбрано: {selected}" +
            f" Загружено: {completed}"
        )

    @pyqtSlot()
    def finished_loader(self):
        QMessageBox.information(self, "Информация", "Аудиозаписи загружены")
        self.set_ui_default()

    @pyqtSlot(str)
    def aborted_download(self, err_msg):
        QMessageBox.critical(
            self,
            "F*CK", f"Загрузка прервана. Причина: {err_msg}"
        )
        self.set_ui_default()

    @pyqtSlot(str)
    def loading_audio(self, song_name):
        self.label_3.setText(
            f"Загружается: " + (f"{song_name[0:100]}..." if len(song_name) >= 100 else song_name)
        )

    @pyqtSlot(str)
    def unavailable_audio(self, song_name):
        QMessageBox.warning(
            self,
            "Внимание",
            f"Аудиозапись: {song_name} недоступна в вашем регионе"
        )

    @pyqtSlot(int, str)
    def content_restricted(self, id_restrict, song_name):
        message = f"Аудиозапись: {song_name} недоступна в вашем регионе"
        
        if id_restrict == 1:
            message = f"Аудиозапись: {song_name} недоступна по решению правообладателя"
        
        if id_restrict == 2:
            message = f"Аудиозапись: {song_name} недоступна в вашем регионе по решению правообладателя"
        
        if id_restrict == 5:
            message = f"Доступ к аудиозаписи: {song_name} вскоре будет открыт." + \
                      "\nВы сможете её послушать после официального релиза"

        QMessageBox.warning(self, "Внимание", message)

    @pyqtSlot(int)
    def progress(self, _range):
        self.progressBar.setFormat("%p% ( %v KB / %m KB )")
        self.progressBar.setRange(0, int(_range / 1024))

    @pyqtSlot(int)
    def progress_set_value(self, value):
        self.progressBar.setValue(int(value / 1024))

    def about_message(self):
        QMessageBox.about(
            self, "О программе",
            "<b>" + config.ApplicationName
            + "</b> - " + config.Description + "<br><br><b>Версия: </b>"
            + config.ApplicationVersion
            + "<br><b>Стадия: </b> "
            + config.ApplicationBranch
            + "<br><br>Данное ПО распространяется по лицензии "
            + "<a href=" + config.License + ">MIT</a>, исходный код доступен"
            + " на <a href=" + config.SourceCode + ">GitHub</a>"
        )

    def tech_information(self):
        self.tech_info_window = TechInfo(
            VKLight(dict(proxy=self.action_5.isChecked())).baseURL,
            VKLightOauth(dict(proxy=self.action_5.isChecked())).baseURL
        )

    def logout(self):
        reply = QMessageBox.question(
            self,
            "Выход из аккаунта", "Вы точно хотите выйти из аккаунта?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if utils.file_exists(config.AuthFile):
                os.remove(config.AuthFile)
            else:
                print("WTF?")

            if utils.file_exists("response.json"):
                os.remove("response.json")

            self.auth_window = Auth()
            self.auth_window.show()
            self.hide()
        else:
            pass
