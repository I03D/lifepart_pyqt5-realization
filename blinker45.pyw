from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5 import QtCore, QtWidgets
import sys
  
class Window(QMainWindow): 
    def __init__(self): 
        super().__init__() 
  
        self.setWindowTitle("Label")

        self.setGeometry(0, 0, size.width(), size.height())
        self.setStyleSheet("background-color: white;")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        
        pixmap = QPixmap('flower.png')
        self.label = QLabel('test', self)
        self.label.setGeometry(0, 0, size.width(), size.height())
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setPixmap(pixmap)
        
        timer = QTimer()
        timer.singleShot(350, sys.exit)
        self.show() 
  
App = QApplication(sys.argv) 
screen = App.primaryScreen()
size = screen.size()
        
window = Window() 

sys.exit(App.exec()) 
