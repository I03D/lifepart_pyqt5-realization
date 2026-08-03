from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QHBoxLayout,QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
import sys
import argparse
  
class Window(QWidget): 
    def __init__(self): 
        super().__init__()

        parser = argparse.ArgumentParser(description="Программа мигания, аргумент принимает число от 1 до 9 для индикатора.")
        parser.add_argument("count", nargs="?", type=int, default=1, help="Целое число от 1 до 9 (по умолчанию: 1)")
        args = parser.parse_args()

        self.setGeometry(0, 0, size.width(), 120)
        self.setStyleSheet("background-color: white;")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)

    # 1. Основное изображение
        pixmap = QPixmap('sun.png')
        self.label = QLabel('test', self)
        self.label.setGeometry(0, 0, size.width(), 100)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setPixmap(pixmap)

    # 2. Индикаторы текущего и предыдущих вызовов
        pointPixmap = QPixmap('point.png')
        y_base = 75
        x_gap = 5
        count = args.count
        last_y_offset = 5
        self.images = []

        img_width = pointPixmap.width()
        img_height = pointPixmap.height()

        # Общая ширина ряда
        total_width = img_width * 9 + x_gap * (9 - 1)
        start_x = (self.width() // 2) - (total_width // 2) 

        for i in range(count):
            x_pos = start_x + i * (img_width + x_gap)
            y_pos = y_base
    # 3. Анимированный индикатор для текущего вызова 
            if i == count - 1:
                y_pos += last_y_offset
                
                self.label = QLabel(self)
                self.label.setAlignment(Qt.AlignCenter)
                self.label.move(x_pos, y_pos - 5)
                self.label.setStyleSheet("background-color: transparent;")
                
                movie = QMovie('activePoint.gif')
                self.label.setMovie(movie)
                movie.start()
    # 4. Индикаторы предыдущих вызовов
            else:
                label = QLabel(self)
                label.setPixmap(pointPixmap)
                label.move(x_pos, y_pos)
                label.setStyleSheet("background-color: transparent;")
                self.images.append(label)

    # 5. Индикаторы предстоящих вызовов
        pointPixmap2 = QPixmap('negativePoint.png')

        for i in range(9-count):
            x_pos = start_x + i * (img_width + x_gap) + count*(img_width+x_gap)
            y_pos = y_base

            label2 = QLabel(self)
            label2.setPixmap(pointPixmap2)
            label2.move(x_pos, y_pos)
            label2.setStyleSheet("background-color: transparent;")
            self.images.append(label2)

        
        timer = QTimer()
        timer.singleShot(600, sys.exit) # 350
        self.setWindowFlags(self.windowFlags() | Qt.WindowTransparentForInput)
        self.show() 
  
App = QApplication(sys.argv) 
screen = App.primaryScreen()
size = screen.size()

window = Window()

sys.exit(App.exec())
