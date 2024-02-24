from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QTextEdit, QSizePolicy
from PyQt5.QtCore import QTimer, QThread, QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QTextCursor
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

os.chdir(os.path.dirname(os.path.realpath(__file__)))

def nt_posix_run(program):
    if os.name == 'posix':
        subprocess.run(["python", program])
    elif os.name == 'nt':
        subprocess.run(["pythonw", program])

class Worker(QObject):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()

    def do_work(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.loopCheck)
        self.timer.start(1000)

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
                    nt_posix_run("blinker45.pyw")

                    if big_timer < 3000:
                        self.report('recommend')

                        if os.name == 'posix':
                            self.report('posix hint')
                        elif os.name == 'nt':
                            self.report('nt hint')
                        else:
                            self.report('recommend at least')
                else:
                    nt_posix_run("blinker5.pyw")

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
                text = '\nЗаблокируйте сессию (через i3lock), это  сбросит таймер в течение 5 минут)'
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
        self.setStyleSheet('background-color: ' + config['settings']['background_color'] + '; color: ' + config['settings']['foreground_color'] + ';')
        self.setGeometry(0, 0, 460, 170)
        
        x = int((size.width() - self.width()) / 2)
        y = int((size.height() - self.height()) / 2)
        self.move(x, y)
        
        self.textEdit = QTextEdit(self)
        self.textEdit.setGeometry(0, 0, 460, 170)  # Set the position and size of the input field
        self.textEdit.setReadOnly(True)
        self.textEdit.setFontPointSize(10);
        self.textEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.textEdit.insertPlainText("~ Мигалка ~")
        self.textEdit.insertPlainText("\nЭта программа напоминает делать 15-минутный перерыв")
        self.textEdit.insertPlainText("\nпосле 45 минут работы и смотреть вдаль каждые 5 минут.")
        self.textEdit.insertPlainText("\n(Программа работает в фоне; окно можно просто закрыть)")
        self.textEdit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.textEdit)
        wid.setLayout(layout)
        
        
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

def showIcon():
    image=Image.open("flower.png")
    menu=(item('Показать/скрыть', toggle_window), item('Выход', quit_window))
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
        
nt_posix_run("blinker45.pyw")

window = Window() 
 
sys.exit(App.exec()) 

