from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QTextEdit, QSizePolicy, QPushButton
from PyQt5.QtCore import QTimer, QThread, QObject, pyqtSignal, pyqtSlot, QStandardPaths, QEvent, Qt
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtGui import QPixmap, QTextCursor, QIcon, QFontMetrics
from PyQt5 import QtCore, QtWidgets

from pystray import MenuItem as item
import pystray
from PIL import Image

import sys
import configparser
import threading
import subprocess
import os
import time
import ctypes
from math import floor

# Добавляем директорию, где лежит program.py, в начало sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

import lockTest

import traceback
import getpass


def exception_hook(exctype, value, traceback_):
    print("Unhandled exception:", exctype, value)
    print(''.join(traceback.format_exception(exctype, value, traceback_)))

sys.excepthook = exception_hook

os.chdir(os.path.dirname(os.path.realpath(__file__)))

def nt_posix_run(program, arg=None):
    if os.name == 'posix':
        cmd = ["python", program]
    elif os.name == 'nt':
        cmd = ["pythonw", program]
    else:
        raise OSError(f"Unsupported OS: {os.name}")

    if arg is not None:
        cmd.append(str(arg))

    subprocess.Popen(cmd)


# --- ХЕЛПЕР ДЛЯ ПРИНУДИТЕЛЬНОЙ АКТИВАЦИИ ОКНА ---
def force_activate_window(window):
    """Принудительно выводит окно на передний план."""
    # Снимаем состояние свёрнутости, если оно есть
    window.setWindowState(window.windowState() & ~Qt.WindowMinimized)
    window.show()
    window.activateWindow()
    window.raise_()

    if os.name == 'nt':
        try:
            hwnd = int(window.winId())
            user32 = ctypes.windll.user32
            if user32.IsIconic(hwnd):
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
        except Exception:
            pass


# --- НАЧАЛО: Логика SingleInstance ---
class SingleInstanceManager:
    def __init__(self, app, server_name="lifepart_single_instance"):
        self.app = app
        self.main_window = None
        username = getpass.getuser()
        self.server_name = f"{server_name}_{username}"
        self.local_server = None
        self.socket = None

    def set_main_window(self, window):
        self.main_window = window

    def check_and_activate(self):
        self.socket = QLocalSocket()
        self.socket.connectToServer(self.server_name)

        if self.socket.waitForConnected(1000):
            print("Instance already running. Activating existing window...")
            self.socket.write(b"activate")
            self.socket.waitForBytesWritten(1000)
            self.socket.disconnectFromServer()
            if self.socket.state() != QLocalSocket.UnconnectedState:
                self.socket.waitForDisconnected(1000)
            return False
        else:
            print("No instance found. Starting new instance...")
            self._start_server()
            return True

    def _start_server(self):
        self.local_server = QLocalServer()
        QLocalServer.removeServer(self.server_name)
        if not self.local_server.listen(self.server_name):
            QLocalServer.removeServer(self.server_name)
            if not self.local_server.listen(self.server_name):
                print(f"Failed to start local server: {self.local_server.errorString()}")
                sys.exit(1)
        self.local_server.newConnection.connect(self._handle_new_connection)

    def _handle_new_connection(self):
        socket = self.local_server.nextPendingConnection()
        socket.readyRead.connect(lambda s=socket: self._read_message(s))

    def _read_message(self, socket):
        data = socket.readAll()
        if data == b"activate":
            if self.main_window:
                force_activate_window(self.main_window)
        socket.disconnectFromServer()


class Worker(QObject):
    finished = pyqtSignal()
    new_log_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def do_work(self):
        self.timer = QTimer()
        updFreq = config['settings']['update_frequency']
        print('updFreq = ' + updFreq)
        self.timer.start(int(updFreq))

        self.timer.timeout.connect(self.loopCheck)

    def loopCheck(self):
        global big_timer
        global small_timer

        global big_timer_start
        global small_timer_start

        global locked

        if lockTest.test():
            if not locked:
                self.report('blocked')
                big_timer_start = floor(time.time())
                small_timer_start = big_timer_start
            locked = True
        else:
            if locked:
                self.report('unblocked')

                big_timer_start = floor(time.time())
                small_timer_start = big_timer_start

                locked = False

            timestamp = floor(time.time())
            big_timer = timestamp - big_timer_start
            small_timer = timestamp - small_timer_start

            if small_timer > 300:
                self.report('passed', floor(big_timer/60))

                small_timer = 0
                small_timer_start = timestamp

                if big_timer >= 2700:
                    nt_posix_run("longBlink.pyw")

                    if big_timer < 3000:
                        self.report('recommend')

                        if os.name == 'posix':
                            self.report('posix hint')
                        elif os.name == 'nt':
                            self.report('nt hint')
                        else:
                            self.report('recommend at least')
                else:
                    nt_posix_run("shortBlink.pyw", (floor(big_timer/300)))

    def report(self, message='', data=None):
        match message:
            case 'blocked':
                text = '\nСессия заблокирована, сбрасываем время.'
            case 'unblocked':
                text = '\nСессия разблокирована, время пошло.'
            case 'passed':
                text = '\nПрошло ' + str(data) + ' минут.'
            case 'recommend':
                text = '\nПора сделать 15-минутный перерыв.'
            case 'recommend at least':
                text = '\nПора сделать хотя бы 15-минутный перерыв.'
            case 'posix hint':
                text = '\nЗаблокируйте сессию (через i3lock), это сбросит таймер в течение 5 минут)'
            case 'nt hint':
                text = '\n(Windows+L заблокирует сессию и сбросит таймер в течение 5 минут)'
            case _:
                text = '\nEmpty message!'
        self.new_log_message.emit(text)


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LifePart")
        print('test font-size == ' + config['settings']['font_size'])
        self.setStyleSheet('background-color: '
                           + config['settings']['background_color']
                           + '; color: '
                           + config['settings']['foreground_color']
                           + ';')
        self.setGeometry(0, 0, 460, 170)

        self.setWindowIcon(QIcon('icon.png'))

        x = int((size.width() - self.width()) / 2)
        y = int((size.height() - self.height()) / 2)
        self.move(x, y)

        self.textEdit = QTextEdit(self)
        self.textEdit.setGeometry(0, 0, 460, 170)
        self.textEdit.setReadOnly(True)
        self.fontSize = int(config['settings']['font_size'])
        self.textEdit.setFontPointSize(self.fontSize)
        self.textEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.textEdit.insertPlainText("~ Мигалка ~")
        self.textEdit.insertPlainText("\nЭта программа напоминает делать 15-минутный перерыв")
        self.textEdit.insertPlainText("\nпосле 45 минут работы и смотреть вдаль каждые 5 минут.")
        self.textEdit.insertPlainText("\n(Программа работает в фоне; окно можно закрыть)")
        self.textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.update_window_size()
        self.textEdit.setMinimumHeight(100)

        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.textEdit)
        wid.setLayout(layout)

        pixmap = QPixmap("settings.png")
        self.settings_btn = QPushButton(self)
        self.settings_btn.setIcon(QIcon(pixmap))
        self.settings_btn.setIconSize(pixmap.size())
        self.settings_btn.setFlat(True)
        self.settings_btn.resize(pixmap.width(), pixmap.height())
        self.settings_btn.setStyleSheet("""
    QPushButton {
        border: none;
        background-color: transparent;
    }

    QPushButton:hover {
        background-color: rgba(255, 255, 255, 127);
    }
                                        """)

        self.textEdit.verticalScrollBar().installEventFilter(self)
        self.update_settings_button_position()

        self.settings_btn.clicked.connect(self.on_settings_button_clicked)

        self.worker = Worker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.started.connect(self.worker.do_work)

        # Потокобезопасная связь: сигнал -> слот в главном потоке
        self.worker.new_log_message.connect(self.append_log)

        self.worker_thread.start()

        self.show()

    @pyqtSlot(str)
    def append_log(self, text):
        self.textEdit.moveCursor(QTextCursor.End)
        self.textEdit.insertPlainText(text)

    def eventFilter(self, obj, event):
        if obj is self.textEdit.verticalScrollBar():
            if event.type() in (QEvent.Show, QEvent.Hide):
                self.update_settings_button_position()
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_settings_button_position()

    def update_settings_button_position(self):
        sb = self.textEdit.verticalScrollBar()
        offset = sb.width() if sb.isVisible() else 0
        x = int(self.width() - offset - self.settings_btn.width() - 4)
        y = 5
        self.settings_btn.move(x, y)

    def on_settings_button_clicked(self):
        nt_posix_run('settings.pyw')

    def update_window_size(self):
        self.resize(self.fontSize * 40, self.fontSize * 17)

    def closeEvent(self, event):
        global sh
        event.ignore()
        sh = True
        self.hide()


config = configparser.ConfigParser()
config.read('config.ini')

def quit_window():
    os._exit(0)

def show_window():
    """Показывает окно и забирает фокус."""
    global sh
    global window
    sh = False
    force_activate_window(window)

def run_settings():
    nt_posix_run("settings.pyw")

def showIcon():
    image = Image.open("icon.png")
    menu = (
        item('Показать', show_window, default=True),
        item('Настройки', run_settings),
        item('Выход', quit_window),
    )
    icon = pystray.Icon('name', image, 'LifePart', menu)
    icon.run()

small_timer = 0
big_timer = 0
big_timer_start = floor(time.time())
small_timer_start = big_timer_start
locked = False

# --- ГЛАВНАЯ ТОЧКА ВХОДА С ПРОВЕРКОЙ SINGLEINSTANCE ---
App = QApplication(sys.argv)

screen = App.primaryScreen()
size = screen.size()

instance_manager = SingleInstanceManager(App)

if instance_manager.check_and_activate():
    x = threading.Thread(target=showIcon, args=(), daemon=True)
    x.start()

    sh = config['settings']['show_cmd']
    if sh == "False":
        sh = False
    else:
        sh = True

    window = Window()
    instance_manager.set_main_window(window)

    nt_posix_run("longBlink.pyw", 0)

    sys.exit(App.exec())
else:
    App.quit()
    sys.exit(0)

