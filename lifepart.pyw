from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QTextEdit, QSizePolicy, QPushButton
from PyQt5.QtCore import QTimer, QThread, QObject, pyqtSignal
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
from math import floor

import lockTest

import traceback


def exception_hook(exctype, value, traceback_):
    print("Unhandled exception:", exctype, value)
    print(''.join(traceback.format_exception(exctype, value, traceback_)))

sys.excepthook = exception_hook


os.chdir(os.path.dirname(os.path.realpath(__file__)))

def nt_posix_run(program, arg=None):
    # Формируем базовый список аргументов
    if os.name == 'posix':
        cmd = ["python", program]
    elif os.name == 'nt':
        cmd = ["pythonw", program]
    else:
        raise OSError(f"Unsupported OS: {os.name}")

    # Добавляем аргумент, если он передан
    if arg is not None:
        # Преобразуем в строку — subprocess ожидает строковые аргументы
        cmd.append(str(arg))

    subprocess.run(cmd)


class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()

    def do_work(self):
        self.timer = QTimer()
        updFreq = config['settings']['update_frequency']
        print('updFreq = ' + updFreq)
        self.timer.start(int(updFreq))

        # self.finished.emit()

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
        window.textEdit.moveCursor(QTextCursor.End)
        window.textEdit.insertPlainText(text)



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
        self.textEdit.setGeometry(0, 0, 460, 170)  # Set the position and size of the input field
        self.textEdit.setReadOnly(True)
        self.fontSize = int(config['settings']['font_size'])
        self.textEdit.setFontPointSize(self.fontSize);
        self.textEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.textEdit.insertPlainText("~ Мигалка ~")
        self.textEdit.insertPlainText("\nЭта программа напоминает делать 15-минутный перерыв")
        self.textEdit.insertPlainText("\nпосле 45 минут работы и смотреть вдаль каждые 5 минут.")
        self.textEdit.insertPlainText("\n(Программа работает в фоне; окно можно закрыть)")
        self.textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Подключаем сигнал на изменение текста
        #self.textEdit.document().contentsChanged.connect(self.update_window_size)
        self.update_window_size()
        
        # Опционально: ограничим минимальную высоту (например, чтобы не было слишком коротко)
        self.textEdit.setMinimumHeight(100)
        
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.textEdit)
        wid.setLayout(layout)

        pixmap = QPixmap("settings.png")        
        self.settings_btn = QPushButton(self)
        self.settings_btn.setIcon(QIcon(pixmap))
        self.settings_btn.setIconSize(pixmap.size())
        self.settings_btn.setFlat(True)
        x = int(self.width() - 16 - 5)
        y = 5
        self.settings_btn.move(x, y)
        self.settings_btn.resize(pixmap.width(), pixmap.height())
        self.settings_btn.setStyleSheet("""
    QPushButton {
        border: none;
        background-color: transparent; /* Убираем фон самой кнопки */
    }
    
    QPushButton:hover {
        /* Белый цвет с прозрачностью 127 (50%) */
        background-color: rgba(255, 255, 255, 127); 
        
        /* Опционально: можно добавить легкую рамку или эффект */
        /* border: 1px solid rgba(255, 255, 255, 200); */
    }
                                        """)

        self.settings_btn.clicked.connect(self.on_settings_button_clicked)
                
        # self.layout = QGridLayout()
        # self.layout.addWidget(self.textEdit)
        # self.setLayout(self.layout)
        
        # self.closeEvent = quit_window

        self.worker = Worker()
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.started.connect(self.worker.do_work)
        self.worker_thread.start()

        self.show()

    def on_settings_button_clicked(self):
        nt_posix_run('settings.pyw')
    
    def update_window_size(self):
        # Пример расчёта: ширина как количество символов, высота ~строк
        #char_width = self.textEdit.fontMetrics().width('a')
        self.resize(self.fontSize*40, self.fontSize*17)

    def closeEvent(self, event):
        event.ignore()
        toggle_window()

config = configparser.ConfigParser()
config.read('config.ini')

def quit_window():
    config['settings']['show_cmd'] = str(not sh)
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    os._exit(0)

def toggle_window():
    global sh
    if sh:
        sh = False
        window.show()
    else:
        sh = True
        window.hide()

def run_settings():
    nt_posix_run("settings.pyw")

def showIcon():
    image=Image.open("icon.png")
    menu=(
        item('Показать/скрыть', toggle_window, default=True),
        item('Настройки', run_settings),
        item('Выход', quit_window))
    default=True
    icon=pystray.Icon('name', image, 'LifePart', menu)
    icon.run()

x = threading.Thread(target=showIcon, args=())
x.start()

sh = config['settings']['show_cmd']

if sh == "False":
    sh = False
else:
    sh = True

# toggle_window()

small_timer = 0
big_timer = 0

big_timer_start = floor(time.time())
small_timer_start = big_timer_start

locked = False

App = QApplication(sys.argv)

screen = App.primaryScreen()
size = screen.size()
        
nt_posix_run("longBlink.pyw", 0)

window = Window() 
 
sys.exit(App.exec()) 

