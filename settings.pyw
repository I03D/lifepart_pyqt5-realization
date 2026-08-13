
import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLabel, 
                             QLineEdit, QCheckBox, QPushButton, QSpinBox, 
                             QFrame, QColorDialog, QSlider, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import configparser

import traceback


def exception_hook(exctype, value, traceback_):
    print("Unhandled exception:", exctype, value)
    print(''.join(traceback.format_exception(exctype, value, traceback_)))

sys.excepthook = exception_hook


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        # Получаем цвета из конфига
        bg_color = self.config.get('settings', 'background_color', fallback='#f0f0f0')
        fg_color = self.config.get('settings', 'foreground_color', fallback='#000000')
        #bg_alpha = self.config.getint('settings', 'background_transparency', fallback=255)
        
        # Формируем стиль окна (теперь прозрачность НЕ зависит от ползунка)
        style_sheet = f"background-color: rgba({QColor(bg_color).red()}, {QColor(bg_color).green()}, {QColor(bg_color).blue()}, 255); color: {fg_color};"
        self.setStyleSheet(style_sheet)
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Настройки')
        
        layout = QGridLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        row = 0

        # --- Заголовок ---
        title = QLabel("Параметры приложения")
        font_size = self.config.get('settings', 'font_size', fallback='14')
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: {font_size}px; font-weight: bold; padding-bottom: 10px;")
        
        layout.addWidget(title, row, 0, 1, 2, alignment=Qt.AlignCenter)
        row += 1

        # Разделитель (ВЕРХНИЙ)
        separator_top = QFrame()
        separator_top.setFrameShape(QFrame.HLine)
        separator_top.setStyleSheet("background-color: #555; height: 3px;") 
        layout.addWidget(separator_top, row, 0, 1, 2)
        row += 1

        # --- Размер шрифта (SpinBox) по центру ---
        spin_container = QWidget()
        spin_layout = QHBoxLayout(spin_container)
        spin_layout.setContentsMargins(0, 0, 0, 0)
        spin_layout.setSpacing(10)
        
        lbl_number = QLabel("Размер шрифта (px):")
        self.spin_font = QSpinBox()
        self.spin_font.setRange(8, 72)
        current_size = self.config.getint('settings', 'font_size', fallback=14)
        self.spin_font.setValue(current_size)
        
        lbl_number.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.spin_font.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        spin_layout.addWidget(lbl_number)
        spin_layout.addWidget(self.spin_font)
        
        layout.addWidget(spin_container, row, 0, 1, 2, alignment=Qt.AlignCenter)
        row += 1

        # --- Флажок show_cmd ---
        self.check_show_cmd = QCheckBox("Показывать основное окно при запуске")
        show_cmd_val = self.config.getboolean('settings', 'show_cmd', fallback=True)
        self.check_show_cmd.setChecked(show_cmd_val)
        layout.addWidget(self.check_show_cmd, row, 0, 1, 2, alignment=Qt.AlignCenter)
        row += 1

        # --- ЦВЕТА И ПРОЗРАЧНОСТЬ ---

        # 1. Выбор цвета фона
        lbl_bg_color = QLabel("Цвет фона:")
        self.btn_bg_color = QPushButton("Выбрать цвет")
        
        self.btn_bg_color.clicked.connect(lambda: self.open_color_dialog('bg'))
        
        self._apply_button_style(self.btn_bg_color)
        
        layout.addWidget(lbl_bg_color, row, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.btn_bg_color, row, 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        row += 1

        # 2. Прозрачность фона / запуск test.py
        lbl_trans = QLabel("Прозрачность окна короткого мигания:")
        self.slider_trans = QSlider(Qt.Horizontal)
        self.slider_trans.setRange(0, 255)
        trans_val = self.config.getint('settings', 'background_transparency', fallback=255)
        self.slider_trans.setValue(trans_val)
        # Теперь при изменении значения запускается test.py
        self.slider_trans.sliderReleased.connect(self.run_test_script)
        
        layout.addWidget(lbl_trans, row, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.slider_trans, row, 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        row += 1

        # 3. Выбор цвета текста
        lbl_fg_color = QLabel("Цвет текста:")
        self.btn_fg_color = QPushButton("Выбрать цвет")
        self.btn_fg_color.clicked.connect(lambda: self.open_color_dialog('fg'))
        
        self._apply_button_style(self.btn_fg_color)

        layout.addWidget(lbl_fg_color, row, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.btn_fg_color, row, 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        row += 1

        # 4. Частота обновления
        lbl_freq = QLabel("Частота обновления:")
        self.spin_freq = QSpinBox()
        self.spin_freq.setRange(1, 1000)
        freq_val = self.config.getint('settings', 'update_frequency', fallback=60)
        self.spin_freq.setValue(freq_val)
        
        layout.addWidget(lbl_freq, row, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.spin_freq, row, 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        row += 1

        # Разделитель (НИЖНИЙ)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #555; height: 3px;")
        layout.addWidget(separator, row, 0, 1, 2)
        row += 1

        # Кнопка сохранения
        btn_save = QPushButton("Сохранить настройки")
        btn_save.clicked.connect(self.save_settings)
        
        btn_save.setStyleSheet(self._get_button_css())
        
        layout.addWidget(btn_save, row, 0, 1, 2, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        
        self.adjustSize()
        self.setFixedSize(self.sizeHint())
        self.setMinimumHeight(300) 

    def _get_button_css(self):
        """Генерирует CSS строку для кнопок на основе текущего цвета текста из конфига"""
        fg_hex = self.config.get('settings', 'foreground_color', fallback='#000000')
        return f"""
            QPushButton {{
                padding: 10px; 
                background-color: #7F7F7F; 
                color: {fg_hex}; 
                border: none; 
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #999999;
            }}
            QPushButton:pressed {{
                background-color: #555555;
            }}
        """

    def _apply_button_style(self, button):
        """Применяет актуальный стиль к кнопке"""
        button.setStyleSheet(self._get_button_css())

    def open_color_dialog(self, mode):
        """Открывает диалог выбора цвета"""
        current_color = ""
        if mode == 'bg':
            current_color = self.config.get('settings', 'background_color', fallback='#f0f0f0')
        elif mode == 'fg':
            current_color = self.config.get('settings', 'foreground_color', fallback='#000000')
            
        color = QColorDialog.getColor(QColor(current_color), self, "Выберите цвет")
        
        if color.isValid():
            hex_color = color.name()
            if mode == 'bg':
                self.config['settings']['background_color'] = hex_color
                self.apply_dynamic_style()
                self._apply_button_style(self.btn_bg_color)
                self._apply_button_style(self.btn_fg_color)
            elif mode == 'fg':
                self.config['settings']['foreground_color'] = hex_color
                self.apply_dynamic_style()
                self._apply_button_style(self.btn_bg_color)
                self._apply_button_style(self.btn_fg_color)

    # ИЗМЕНЕНО: теперь это запускает test.py, а не меняет прозрачность
    def run_test_script(self):
        """Запускает test.py при изменении ползунка"""
        value = self.slider_trans.value()
        print('test')
        try:
            # Запуск test.py в отдельном процессе
            print("fk" + str(self.slider_trans.value()))
            subprocess.Popen([sys.executable, "longBlink.pyw", "1", str(self.slider_trans.value())])
            print("longBlink.pyw " + "1 " + str(self.slider_trans.value()))
        except Exception as e:
            print(f"Ошибка при запуске test.py: {e}")

    # УСТАРЕЛО: больше не используется для прозрачности, но можно оставить для других стилей
    def update_window_transparency(self, value):
        """Больше не используется для смены прозрачности окна"""
        pass

    def apply_dynamic_style(self):
        """Применяет стиль окна на основе текущих значений в конфиге"""
        bg_hex = self.config.get('settings', 'background_color', fallback='#f0f0f0')
        fg_hex = self.config.get('settings', 'foreground_color', fallback='#000000')
        alpha = self.slider_trans.value()  # Это значение теперь не влияет на прозрачность
        
        c = QColor(bg_hex)
        # Прозрачность теперь НЕ меняется динамически через ползунок
        style = f"background-color: rgba({c.red()}, {c.green()}, {c.blue()}, 255); color: {fg_hex};"
        self.setStyleSheet(style)
        
        self._apply_button_style(self.btn_bg_color)
        self._apply_button_style(self.btn_fg_color)

    def save_settings(self):
        """Сохраняет текущие значения виджетов в config.ini"""
        if not self.config.has_section('settings'):
            self.config.add_section('settings')

        self.config.set('settings', 'font_size', str(self.spin_font.value()))
        self.config.set('settings', 'show_cmd', str(self.check_show_cmd.isChecked()))
        self.config.set('settings', 'background_color', self.config.get('settings', 'background_color'))
        self.config.set('settings', 'foreground_color', self.config.get('settings', 'foreground_color'))
        # Сохраняем значение ползунка, но оно больше не меняет прозрачность окна
        self.config.set('settings', 'background_transparency', str(self.slider_trans.value()))
        self.config.set('settings', 'update_frequency', str(self.spin_freq.value()))

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        
        print("Настройки сохранены!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec_())
