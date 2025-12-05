import sys
import random
import string
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QPushButton, QProgressBar, QFrame, QCheckBox, QSlider, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QColor, QPalette, QFont

class PasswordGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор паролей")
        self.setMinimumSize(450, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной лэйаут
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(20)
        
        # Заголовок
        title_label = QLabel("Генератор надежных паролей")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #e0e0ff;
            text-align: center;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Описание
        desc_label = QLabel("Настройте параметры для генерации безопасного пароля")
        desc_label.setStyleSheet("""
            font-size: 15px;
            color: #aaa;
            text-align: center;
            margin-bottom: 10px;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(desc_label)
        
        # Панель настроек
        settings_card = QFrame()
        settings_card.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border-radius: 12px;
                border: 1px solid #333355;
            }
        """)
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(20, 15, 20, 15)
        settings_layout.setSpacing(15)
        
        # Настройка длины пароля
        length_layout = QHBoxLayout()
        length_layout.setSpacing(15)
        
        length_label = QLabel("Длина пароля:")
        length_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #c7b0e3;")
        
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setRange(8, 64)
        self.length_spinbox.setValue(16)
        self.length_spinbox.setFixedWidth(80)
        self.length_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #2a2a40;
                border: 1px solid #4a4a6a;
                color: white;
                border-radius: 6px;
                padding: 5px;
                font-size: 14px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background-color: #3a3a5a;
            }
        """)
        self.length_spinbox.valueChanged.connect(self.update_password_preview)
        
        length_layout.addWidget(length_label)
        length_layout.addWidget(self.length_spinbox)
        length_layout.addStretch()
        settings_layout.addLayout(length_layout)
        
        # Слайдер длины
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(8, 64)
        self.length_slider.setValue(16)
        self.length_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #333355;
                height: 6px;
                background: #2a2a40;
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #7209b7;
                border: 2px solid #9d4edd;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #8d47cc;
            }
        """)
        self.length_slider.valueChanged.connect(self.sync_slider_spinbox)
        settings_layout.addWidget(self.length_slider)
        
        # Выбор типов символов
        chars_label = QLabel("Использовать символы:")
        chars_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #c7b0e3; margin-top: 5px;")
        settings_layout.addWidget(chars_label)
        
        chars_layout = QVBoxLayout()
        chars_layout.setSpacing(10)
        
        # Чекбоксы для типов символов
        self.checkbox_lowercase = QCheckBox("Строчные буквы (a-z)")
        self.checkbox_lowercase.setChecked(True)
        self.checkbox_lowercase.setStyleSheet("font-size: 14px; color: #ddd;")
        self.checkbox_lowercase.stateChanged.connect(self.update_password_preview)
        
        self.checkbox_uppercase = QCheckBox("Заглавные буквы (A-Z)")
        self.checkbox_uppercase.setChecked(True)
        self.checkbox_uppercase.setStyleSheet("font-size: 14px; color: #ddd;")
        self.checkbox_uppercase.stateChanged.connect(self.update_password_preview)
        
        self.checkbox_digits = QCheckBox("Цифры (0-9)")
        self.checkbox_digits.setChecked(True)
        self.checkbox_digits.setStyleSheet("font-size: 14px; color: #ddd;")
        self.checkbox_digits.stateChanged.connect(self.update_password_preview)
        
        self.checkbox_symbols = QCheckBox("Специальные символы (!, @, #, $ и т.д.)")
        self.checkbox_symbols.setChecked(True)
        self.checkbox_symbols.setStyleSheet("font-size: 14px; color: #ddd;")
        self.checkbox_symbols.stateChanged.connect(self.update_password_preview)
        
        chars_layout.addWidget(self.checkbox_lowercase)
        chars_layout.addWidget(self.checkbox_uppercase)
        chars_layout.addWidget(self.checkbox_digits)
        chars_layout.addWidget(self.checkbox_symbols)
        settings_layout.addLayout(chars_layout)
        
        main_layout.addWidget(settings_card)
        
        # Поле для пароля
        self.password_output = QTextEdit()
        self.password_output.setReadOnly(True)
        self.password_output.setFixedHeight(60)
        self.password_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border: 2px solid #3a3a5a;
                color: #64ffda;
                font-family: 'Consolas', monospace;
                font-size: 20px;
                font-weight: bold;
                border-radius: 10px;
                padding: 10px 15px;
            }
        """)
        main_layout.addWidget(self.password_output)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Кнопка копирования
        self.copy_btn = QPushButton("Копировать пароль")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4361ee;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 15px;
                font-weight: bold;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #3a0ca3;
            }
            QPushButton:pressed {
                background-color: #4895ef;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        
        # Кнопка генерации
        self.generate_btn = QPushButton("Сгенерировать")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #7209b7;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 15px;
                font-weight: bold;
                min-height: 50px;
            }
            QPushButton:hover {
                background-color: #5a189a;
            }
            QPushButton:pressed {
                background-color: #8d47cc;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_password)
        self.generate_btn.setShortcut("Return")
        
        buttons_layout.addWidget(self.copy_btn, 1)
        buttons_layout.addWidget(self.generate_btn, 1)
        main_layout.addLayout(buttons_layout)
        
        # Индикатор безопасности
        security_layout = QVBoxLayout()
        security_layout.setSpacing(10)
        
        security_title = QLabel("Уровень безопасности")
        security_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #c7b0e3;
        """)
        security_layout.addWidget(security_title)
        
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(95)
        self.strength_bar.setFixedHeight(10)
        self.strength_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 5px;
                background-color: #2d2d44;
            }
            QProgressBar::chunk {
                background-color: #9d4edd;
                border-radius: 5px;
            }
        """)
        security_layout.addWidget(self.strength_bar)
        
        self.strength_label = QLabel("Невзламываемый")
        self.strength_label.setStyleSheet("""
            font-size: 15px;
            font-weight: bold;
            color: #9d4edd;
            text-align: center;
        """)
        self.strength_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        security_layout.addWidget(self.strength_label)
        
        main_layout.addLayout(security_layout)
        
        # Совет
        tip_label = QLabel("💡 Совет: Для максимальной безопасности используйте длину 16+ символов и все типы символов")
        tip_label.setStyleSheet("""
            font-size: 13px;
            color: #888;
            background-color: #1e1e2e;
            padding: 12px;
            border-radius: 8px;
            margin-top: 8px;
        """)
        main_layout.addWidget(tip_label)
        
        # Уведомление
        self.notification = QLabel()
        self.notification.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notification.setWordWrap(True)
        self.notification.setStyleSheet("""
            background-color: #1e1e2e;
            color: #64ffda;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
            margin-top: 10px;
            min-height: 25px;
        """)
        self.notification.hide()
        main_layout.addWidget(self.notification)
        
        # Генерация первого пароля
        self.generate_password()
        
        # Применение темной темы
        self.apply_dark_theme()

    def sync_slider_spinbox(self, value):
        """Синхронизация слайдера и поля ввода длины"""
        self.length_spinbox.setValue(value)
        self.update_password_preview()

    def update_password_preview(self):
        """Обновление предпросмотра пароля и индикатора безопасности при изменении настроек"""
        # Генерация примера пароля с текущими настройками для оценки безопасности
        temp_password = self.generate_temp_password()
        strength = self.get_password_strength(temp_password)
        self.set_strength_ui(strength)

    def generate_temp_password(self):
        """Генерация временного пароля для оценки безопасности настроек"""
        length = self.length_slider.value()
        characters = self.get_selected_characters()
        
        if not characters:
            return "Выберите хотя бы один тип символов"
        
        # Генерация простого примера для оценки
        return ''.join(random.choice(characters) for _ in range(min(length, 10)))

    def get_selected_characters(self):
        """Получение строки с символами на основе выбранных чекбоксов"""
        characters = ""
        if self.checkbox_lowercase.isChecked():
            characters += string.ascii_lowercase
        if self.checkbox_uppercase.isChecked():
            characters += string.ascii_uppercase
        if self.checkbox_digits.isChecked():
            characters += string.digits
        if self.checkbox_symbols.isChecked():
            characters += "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
        return characters

    def apply_dark_theme(self):
        """Применяет темную тему к приложению"""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(15, 15, 25))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 40))
        palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 80))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(94, 73, 153))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f0f19;
            }
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #555;
                background-color: #2a2a40;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #7209b7;
                border: 2px solid #9d4edd;
                image: url(checked.png); /* Символ галочки будет добавлен программно */
            }
        """)

    def get_password_strength(self, password):
        """Рассчитывает надежность пароля"""
        length = len(password)
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbols = any(not c.isalnum() for c in password)
        
        score = 0
        
        # Оценка длины
        if length >= 24:
            score += 40
        elif length >= 16:
            score += 32
        elif length >= 12:
            score += 24
        elif length >= 8:
            score += 16
            
        # Оценка разнообразия символов
        character_types = sum([has_lower, has_upper, has_digit, has_symbols])
        score += character_types * 14
        
        # Бонус за сочетание длины и разнообразия
        if length >= 12 and character_types >= 3:
            score += 18
        elif length >= 8 and character_types >= 2:
            score += 10
            
        return min(100, score)

    def set_strength_ui(self, strength):
        """Обновляет UI для индикатора надежности"""
        self.strength_bar.setValue(strength)
        
        # Определение уровня и цвета
        if strength >= 95:
            level = "Невзламываемый"
            color = "#9d4edd"
            chunk_color = "#9d4edd"
        elif strength >= 80:
            level = "Отличный"
            color = "#649dff"
            chunk_color = "#649dff"
        elif strength >= 65:
            level = "Хороший"
            color = "#4deeea"
            chunk_color = "#4deeea"
        elif strength >= 50:
            level = "Средний"
            color = "#ffd166"
            chunk_color = "#ffd166"
        else:
            level = "Слабый"
            color = "#ef476f"
            chunk_color = "#ef476f"
        
        # Обновление стилей
        self.strength_label.setText(level)
        self.strength_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: bold;
            color: {color};
            text-align: center;
        """)
        
        self.strength_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: #2d2d44;
            }}
            QProgressBar::chunk {{
                background-color: {chunk_color};
                border-radius: 5px;
            }}
        """)

    def generate_password(self):
        """Генерирует новый пароль на основе настроек"""
        length = self.length_slider.value()
        characters = self.get_selected_characters()
        
        if not characters:
            self.show_notification("⚠️ Выберите хотя бы один тип символов")
            return
            
        password = ''.join(random.SystemRandom().choice(characters) for _ in range(length))
        self.password_output.setText(password)
        
        # Обновление индикатора безопасности
        strength = self.get_password_strength(password)
        self.set_strength_ui(strength)
        
        # Уведомление
        self.show_notification("✅ Пароль успешно сгенерирован")

    def copy_to_clipboard(self):
        """Копирует пароль в буфер обмена"""
        password = self.password_output.toPlainText().strip()
        if password and password != "Выберите хотя бы один тип символов":
            clipboard = QApplication.clipboard()
            clipboard.setText(password)
            self.show_notification("📋 Пароль скопирован в буфер обмена")
        else:
            self.show_notification("⚠️ Нет пароля для копирования")

    def show_notification(self, text):
        """Показывает уведомление"""
        self.notification.setText(text)
        self.notification.show()
        
        # Скрытие через 2 секунды
        QTimer.singleShot(2000, self.notification.hide)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Установка шрифта по умолчанию
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Включение масштабирования для высокого DPI
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    window = PasswordGenerator()
    window.show()
    sys.exit(app.exec())