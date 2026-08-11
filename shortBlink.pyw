from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QHBoxLayout, QWidget
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QPixmap, QMovie, QColor
import sys
import argparse
import configparser
import os

# --- Конфигурация ---
CONFIG_FILE = 'config.ini'
DEFAULT_TRANSPARENCY = 150  # Значение по умолчанию, если ключа нет или файл не найден

def get_transparency():
    """Читает прозрачность из .ini файла"""
    if not os.path.exists(CONFIG_FILE):
        print(f"Файл {CONFIG_FILE} не найден. Используется значение по умолчанию: {DEFAULT_TRANSPARENCY}")
        return DEFAULT_TRANSPARENCY

    config = configparser.ConfigParser()
    try:
        config.read(CONFIG_FILE)
        # Получаем значение, преобразуем в int. Если ключа нет - берем дефолт
        val = config.getint('Settings', 'background_transparency', fallback=DEFAULT_TRANSPARENCY)
        
        # Ограничиваем диапазон 0-255
        if val < 0: val = 0
        if val > 255: val = 255
        
        return val
    except Exception as e:
        print(f"Ошибка чтения конфига: {e}. Используем значение по умолчанию.")
        return DEFAULT_TRANSPARENCY

class Window(QWidget): 
    def __init__(self): 
        super().__init__()

        # Парсинг аргументов
        parser = argparse.ArgumentParser(description="Программа мигания")
        parser.add_argument("count", nargs="?", type=int, default=1, help="Число от 1 до 9")
        args = parser.parse_args()
        count = args.count

        # Получение размера экрана (глобальная переменная size должна быть определена до создания окна)
        screen = QApplication.primaryScreen()
        size = screen.size()
        
        self.setGeometry(0, 0, size.width(), 120)

        # Настройка флагов окна
        self.setWindowFlags(
            self.windowFlags() | 
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint |
            Qt.WindowTransparentForInput |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        
        # ВАЖНО: Для работы setWindowOpacity окно не должно иметь флага WindowTransparentForInput,
        # если мы хотим, чтобы оно реагировало на мышь, но в вашем случае вы специально сделали его прозрачным для ввода.
        # Однако setWindowOpacity работает даже с этим флагом для самого виджета.
        
        # --- НАСТРОЙКА ПРОЗРАЧНОСТИ ---
        transparency_val = get_transparency()
        # setWindowOpacity принимает float от 0.0 до 1.0
        opacity = transparency_val / 255.0
        self.setWindowOpacity(opacity)
        #print(f"Установлена прозрачность: {transparency_val} ({opacity:.2f})")

        # Атрибут для игнорирования мыши
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # --- 1. Основное изображение (ФОН) ---
        # ИСПРАВЛЕНИЕ: Не перезаписываем self.label здесь, создаем отдельный виджет для фона
        pixmap = QPixmap('sun.png')

        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, size.width(), 100)
        self.bg_label.setAlignment(Qt.AlignCenter)
        self.bg_label.setPixmap(pixmap)
        # Фон лейбла должен быть прозрачным, чтобы видеть эффект windowOpacity
        self.bg_label.setStyleSheet("background-color: transparent;")

        # --- 2. Индикаторы ---
        pointPixmap = QPixmap('point.png')
        y_base = 75
        x_gap = 5
        last_y_offset = 5
        self.images = []

        img_width = pointPixmap.width()
        img_height = pointPixmap.height()

        total_width = img_width * 9 + x_gap * (9 - 1)
        start_x = (self.width() // 2) - (total_width // 2) 

        for i in range(count):
            x_pos = start_x + i * (img_width + x_gap)
            y_pos = y_base

            if i == count - 1:
                # Анимированный индикатор
                y_pos += last_y_offset
                
                anim_label = QLabel(self)
                anim_label.setAlignment(Qt.AlignCenter)
                anim_label.move(x_pos, y_pos - 5)
                anim_label.setStyleSheet("background-color: transparent;")
                
                movie = QMovie('activePoint.gif')
                if movie.isValid():
                    anim_label.setMovie(movie)
                    movie.start()
                else:
                    print("Ошибка: файл 'activePoint.gif' не найден!")
                
                self.images.append(anim_label)
            else:
                # Статичный индикатор прошлых вызовов
                label = QLabel(self)
                if not pointPixmap.isNull():
                    label.setPixmap(pointPixmap)
                label.move(x_pos, y_pos)
                label.setStyleSheet("background-color: transparent;")
                self.images.append(label)

        # --- 3. Индикаторы предстоящих вызовов ---
        pointPixmap2 = QPixmap('negativePoint.png')

        for i in range(9 - count):
            x_pos = start_x + i * (img_width + x_gap) + count * (img_width + x_gap)
            y_pos = y_base

            label2 = QLabel(self)
            if not pointPixmap2.isNull():
                label2.setPixmap(pointPixmap2)
            label2.move(x_pos, y_pos)
            label2.setStyleSheet("background-color: transparent;")
            self.images.append(label2)

        # Таймер закрытия
        timer = QTimer()
        timer.singleShot(600, sys.exit)
        
        self.show() 
  
if __name__ == '__main__':
    App = QApplication(sys.argv) 
    # Передаем size в класс или определяем внутри, как сделано выше в методе __init__
    window = Window()
    sys.exit(App.exec())
