from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QTextEdit, QSizePolicy
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore, QtWidgets

from pystray import MenuItem as item
import pystray
from PIL import Image

import sys
import configparser
import threading

import os

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
        
        self.show()


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

App = QApplication(sys.argv) 
screen = App.primaryScreen()
size = screen.size()
        
window = Window() 
  
sys.exit(App.exec()) 
