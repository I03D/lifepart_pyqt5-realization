import sys
import subprocess
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLabel, 
                             QLineEdit, QCheckBox, QPushButton, QSpinBox, 
                             QFrame, QColorDialog, QSlider, QHBoxLayout,
                             QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPalette
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
        
        self.pal = self.palette()
        self._apply_palette(bg_color, fg_color)
        
        self.init_ui()

    def _apply_palette(self, bg_hex, fg_hex):
        """Применяет палитру для всего окна"""
        c_bg = QColor(bg_hex)
        c_fg = QColor(fg_hex)
        
        for role in [QPalette.Normal, QPalette.Inactive, QPalette.Disabled]:
            self.pal.setColor(role, QPalette.Window, c_bg)
            self.pal.setColor(role, QPalette.WindowText, c_fg)
        
        self.setPalette(self.pal)

    def init_ui(self):
        self.setWindowTitle('Параметры')
        self.setAutoFillBackground(True)
        
        layout = QGridLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        row = 0

        # --- Заголовок ---
        self.title = QLabel("Настройки LifePart")
        font_size = self.config.get('settings', 'font_size', fallback='14')
        self.title.setAlignment(Qt.AlignCenter)

        font = self.title.font()
        font.setWeight(QFont.Weight.Bold)
        self.title.setFont(font)
        
        layout.addWidget(self.title, row, 0, 1, 2, alignment=Qt.AlignCenter)
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

        test_lbl_number = QLabel("Размер шрифта:")
        self.test_spin_font = QSpinBox()
        self.test_spin_font.setRange(4, 72)
        current_size = self.config.getint('settings', 'font_size', fallback=14)
        self.test_spin_font.setValue(current_size)
        self.test_spin_font.valueChanged.connect(self.set_test_font)

        test_lbl_number.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.test_spin_font.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        spin_layout.addWidget(test_lbl_number)
        spin_layout.addWidget(self.test_spin_font)
        
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
        
        layout.addWidget(lbl_bg_color, row, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.btn_bg_color, row, 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        row += 1

        # 2. Прозрачность фона / запуск test.py
        lbl_trans = QLabel("Прозрачность мигания:")
        self.slider_trans = QSlider(Qt.Horizontal)
        self.slider_trans.setRange(0, 255)
        trans_val = self.config.getint('settings', 'background_transparency', fallback=255)
        self.slider_trans.setValue(trans_val)
        self.slider_trans.sliderReleased.connect(self.run_test_script)
        
        layout.addWidget(lbl_trans, row, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.slider_trans, row, 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        row += 1

        # 3. Выбор цвета текста
        lbl_fg_color = QLabel("Цвет текста:")
        self.btn_fg_color = QPushButton("Выбрать цвет")
        self.btn_fg_color.clicked.connect(lambda: self.open_color_dialog('fg'))

        layout.addWidget(lbl_fg_color, row, 0, alignment=Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.btn_fg_color, row, 1, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        row += 1

        # 4. Частота обновления
        lbl_freq = QLabel("Частота обновления (мс):")
        self.spin_freq = QSpinBox()
        self.spin_freq.setRange(1, 1000000)
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
        self.btn_save = QPushButton("Сохранить и выйти")
        self.btn_save.clicked.connect(self.save_settings)
        
        self.btn_save.setStyleSheet(self._get_button_css())
        
        layout.addWidget(self.btn_save, row, 0, 1, 2, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # Применяем начальный шрифт
        value = self.test_spin_font.value()
        new_font = QFont()
        new_font.setPointSize(value)
        self.setFont(new_font)
        self._update_fonts(new_font)

        # Убираем setFixedSize — пусть окно само подстраивается
        # self.setFixedSize(self.sizeHint())
        self.adjustSize()

    def _get_button_css(self):
        fg_hex = self.config.get('settings', 'foreground_color', fallback='#000000')
        bg_hex = self.config.get('settings', 'background_color', fallback='#cccccc')
        return f"""
            QPushButton {{
                padding: 12px;
                color: {fg_hex};
                font-weight: bold;
                background-color: {bg_hex};
                border: 1px solid #555;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #ddd;
            }}
        """

    def _get_spinBox_css(self):
        fg_hex = self.config.get('settings', 'foreground_color', fallback='#000000')
        bg_hex = self.config.get('settings', 'background_color', fallback='#ffffff')
        return f"""
            QSpinBox {{
                background-color: {bg_hex};
                color: {fg_hex};
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }}
        """

    def _update_fonts(self, font):
        widgets_to_update = [
            self.test_spin_font, self.spin_freq,
            self.btn_bg_color, self.btn_fg_color, self.btn_save
        ]
        for w in widgets_to_update:
            w.setFont(font)

    def open_color_dialog(self, mode):
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
                self._apply_palette(hex_color, self.config.get('settings', 'foreground_color'))
            elif mode == 'fg':
                self.config['settings']['foreground_color'] = hex_color
                self._apply_palette(
                    self.config.get('settings', 'background_color'), hex_color
                )
            
            # Обновляем стили и шрифты
            self.btn_bg_color.setStyleSheet(self._get_button_css())
            self.btn_fg_color.setStyleSheet(self._get_button_css())
            self.btn_save.setStyleSheet(self._get_button_css())
            
            self.test_spin_font.setStyleSheet(self._get_spinBox_css())
            self.spin_freq.setStyleSheet(self._get_spinBox_css())

            # Принудительно обновляем layout
            self.layout().activate()
            self.adjustSize()

    def run_test_script(self):
        try:
            subprocess.Popen([sys.executable, "longBlink.pyw", "5", str(self.slider_trans.value())])
        except Exception as e:
            print(f"Ошибка при запуске test.py: {e}")

    def set_test_font(self):
        value = self.test_spin_font.value()
        new_font = QFont()
        new_font.setPointSize(value)
        self.setFont(new_font)
        self._update_fonts(new_font)
        
        # Обновляем стили (padding может зависеть от размера шрифта)
        self.btn_bg_color.setStyleSheet(self._get_button_css())
        self.btn_fg_color.setStyleSheet(self._get_button_css())
        self.btn_save.setStyleSheet(self._get_button_css())
        self.test_spin_font.setStyleSheet(self._get_spinBox_css())
        self.spin_freq.setStyleSheet(self._get_spinBox_css())
        
        self.layout().activate()
        self.adjustSize()

    def save_settings(self):
        if not self.config.has_section('settings'):
            self.config.add_section('settings')

        self.config.set('settings', 'font_size', str(self.test_spin_font.value()))
        self.config.set('settings', 'show_cmd', str(self.check_show_cmd.isChecked()))
        self.config.set('settings', 'background_color', self.config.get('settings', 'background_color'))
        self.config.set('settings', 'foreground_color', self.config.get('settings', 'foreground_color'))
        self.config.set('settings', 'background_transparency', str(self.slider_trans.value()))
        self.config.set('settings', 'update_frequency', str(self.spin_freq.value()))

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)
        
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec_())
