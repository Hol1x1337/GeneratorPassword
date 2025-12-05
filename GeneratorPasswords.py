import sys
import random
import string
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QProgressBar, QFrame,
    QCheckBox, QSlider, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont


class PasswordGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор надежных паролей")
        self.setMinimumSize(500, 720)
        self.resize(520, 740)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(32, 28, 32, 28)
        main_layout.setSpacing(22)

        # Заголовок
        title = QLabel("Генератор паролей")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #e0e0ff;")
        main_layout.addWidget(title)

        subtitle = QLabel("Мгновенная генерация сверхнадёжных паролей")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 15px; color: #9999cc;")
        main_layout.addWidget(subtitle)

        # === Карточка настроек ===
        card = QFrame()
        card.setStyleSheet("background: #1e1e2e; border-radius: 16px; border: 1px solid #333355;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(20)

        # Длина пароля — слайдер + крупное число
        length_top = QHBoxLayout()
        lbl_length = QLabel("Длина пароля")
        lbl_length.setStyleSheet("font-size: 16px; font-weight: bold; color: #c7b0e3;")

        self.length_display = QLabel("20")
        self.length_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.length_display.setStyleSheet("""
            font-size: 32px; font-weight: bold; color: #9d4edd;
            background: #2a2a40; border: 2px solid #4a4a6a;
            border-radius: 14px; padding: 10px 20px; min-width: 100px;
        """)

        length_top.addWidget(lbl_length)
        length_top.addStretch()
        length_top.addWidget(self.length_display)
        card_layout.addLayout(length_top)

        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(4, 128)
        self.length_slider.setValue(20)
        self.length_slider.setPageStep(4)
        self.length_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 12px; background: #2a2a40; border-radius: 6px;
                border: 1px solid #444466;
            }
            QSlider::handle:horizontal {
                width: 32px; height: 32px; margin: -10px 0;
                background: qradialgradient(spread:pad, cx:0.5, cy:0.5,
                    stop:0 #e0aaff, stop:1 #7209b7);
                border: 3px solid #e0e0ff; border-radius: 16px;
            }
            QSlider::handle:horizontal:hover {
                background: qradialgradient(spread:pad, cx:0.5, cy:0.5,
                    stop:0 #ffffff, stop:1 #9d4edd);
                border: 3px solid #ffffff;
            }
        """)
        self.length_slider.valueChanged.connect(lambda v: self.length_display.setText(str(v)))
        self.length_slider.valueChanged.connect(self.update_strength_preview)  # ← Живая проверка
        card_layout.addWidget(self.length_slider)

        # Типы символов
        lbl_chars = QLabel("Включить символы")
        lbl_chars.setStyleSheet("font-size: 15px; font-weight: bold; color: #c7b0e3; margin-top: 10px;")
        card_layout.addWidget(lbl_chars)

        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(12)

        self.cb_lower = QCheckBox("Строчные буквы (a-z)")
        self.cb_upper = QCheckBox("Заглавные буквы (A-Z)")
        self.cb_digits = QCheckBox("Цифры (0-9)")
        self.cb_symbols = QCheckBox("Спецсимволы (!@#$%^&*)")

        for cb in (self.cb_lower, self.cb_upper, self.cb_digits, self.cb_symbols):
            cb.setChecked(True)
            cb.setStyleSheet("font-size: 14px; color: #ddd;")
            cb.stateChanged.connect(self.update_strength_preview)  # ← Живая проверка

        grid.addWidget(self.cb_lower, 0, 0)
        grid.addWidget(self.cb_upper, 0, 1)
        grid.addWidget(self.cb_digits, 1, 0)
        grid.addWidget(self.cb_symbols, 1, 1)
        card_layout.addLayout(grid)
        main_layout.addWidget(card)

        # Поле с паролем
        self.password_field = QTextEdit()
        self.password_field.setReadOnly(True)
        self.password_field.setFixedHeight(80)
        self.password_field.setFont(QFont("Consolas", 22, QFont.Weight.Bold))
        self.password_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_field.setStyleSheet("""
            background: #1e1e2e; border: 2px solid #444466;
            color: #64ffda; border-radius: 14px; padding: 16px;
        """)
        main_layout.addWidget(self.password_field)

        # Кнопки
        btns = QHBoxLayout()
        btns.setSpacing(16)

        self.btn_copy = QPushButton("Копировать")
        self.btn_generate = QPushButton("Сгенерировать")
        self.btn_generate.setDefault(True)
        self.btn_generate.setShortcut("Return")

        for btn, color in [(self.btn_copy, "#4361ee"), (self.btn_generate, "#7209b7")]:
            btn.setStyleSheet(f"""
                QPushButton {{background: {color}; color: white; border: none;
                              border-radius: 14px; padding: 18px; font-size: 16px; font-weight: bold;}}
                QPushButton:hover {{background: {color}dd;}}
                QPushButton:pressed {{background: {color}cc;}}
            """)

        btns.addWidget(self.btn_copy)
        btns.addWidget(self.btn_generate)
        main_layout.addLayout(btns)

        # Индикатор силы — обновляется в реальном времени
        strength_box = QFrame()
        strength_box.setStyleSheet("background: #1e1e2e; border-radius: 12px; border: 1px solid #333355;")
        sl = QVBoxLayout(strength_box)
        sl.setContentsMargins(20, 16, 20, 16)
        sl.setSpacing(10)

        sl.addWidget(QLabel("Уровень безопасности").setStyleSheet("color: #c7b0e3; font-weight: bold; font-size: 15px;"))
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(12)
        self.progress.setStyleSheet("QProgressBar {background: #2d2d44; border-radius: 6px;} QProgressBar::chunk {background: #9d4edd; border-radius: 6px;}")
        sl.addWidget(self.progress)

        self.strength_label = QLabel("Невзламываемый")
        self.strength_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.strength_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #9d4edd;")
        sl.addWidget(self.strength_label)
        main_layout.addWidget(strength_box)

        tip = QLabel("Чем длиннее и разнообразнее — тем надёжнее")
        tip.setStyleSheet("background: #1e1e2e; color: #8888bb; padding: 14px; border-radius: 10px; font-size: 13px;")
        tip.setWordWrap(True)
        main_layout.addWidget(tip)

        self.notify = QLabel()
        self.notify.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notify.setStyleSheet("""
            background: rgba(100, 255, 218, 0.15); color: #64ffda;
            padding: 14px; border-radius: 10px; font-weight: bold;
            border: 1px solid #64ffda44; margin-top: 10px;
        """)
        self.notify.hide()
        main_layout.addWidget(self.notify)

        # Подключения
        self.btn_generate.clicked.connect(self.generate_password)
        self.btn_copy.clicked.connect(self.copy_to_clipboard)

        self.apply_dark_theme()
        self.update_strength_preview()  # Первый расчёт при запуске

    def get_chars(self):
        s = ""
        if self.cb_lower.isChecked(): s += string.ascii_lowercase
        if self.cb_upper.isChecked(): s += string.ascii_uppercase
        if self.cb_digits.isChecked(): s += string.digits
        if self.cb_symbols.isChecked(): s += "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
        return s

    def generate_password(self):
        chars = self.get_chars()
        if not chars:
            self.show_notify("Выберите хотя бы один тип символов")
            return

        pwd = ''.join(random.SystemRandom().choice(chars) for _ in range(self.length_slider.value()))
        self.password_field.setText(pwd)
        self.update_strength_preview()  # Обновляем индикатор после генерации
        self.show_notify("Пароль сгенерирован")

    def update_strength_preview(self):
        """Живая оценка силы пароля на основе текущих настроек (без генерации полного пароля)"""
        length = self.length_slider.value()
        has_lower = self.cb_lower.isChecked()
        has_upper = self.cb_upper.isChecked()
        has_digits = self.cb_digits.isChecked()
        has_symbols = self.cb_symbols.isChecked()

        types_count = sum([has_lower, has_upper, has_digits, has_symbols])

        score = 0
        if length >= 30: score += 40
        elif length >= 20: score += 35
        elif length >= 16: score += 28
        elif length >= 12: score += 20
        else: score += 10

        score += types_count * 16
        if length >= 16 and types_count >= 3: score += 22
        if length >= 24 and types_count == 4: score += 15

        score = min(100, score)

        self.progress.setValue(score)
        levels = [
            (95, "Невзламываемый", "#9d4edd"),
            (80, "Отличный", "#649dff"),
            (65, "Хороший", "#4deeea"),
            (50, "Средний", "#ffd166"),
            (0, "Слабый", "#ef476f")
        ]
        for threshold, text, color in levels:
            if score >= threshold:
                self.strength_label.setText(text)
                self.strength_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
                self.progress.setStyleSheet(f"""
                    QProgressBar {{background: #2d2d44; border-radius: 6px;}}
                    QProgressBar::chunk {{background: {color}; border-radius: 6px;}}
                """)
                break

    def copy_to_clipboard(self):
        text = self.password_field.toPlainText().strip()
        if text:
            QApplication.clipboard().setText(text)
            self.show_notify("Пароль скопирован")
        else:
            self.show_notify("Сначала сгенерируйте пароль")

    def show_notify(self, text):
        self.notify.setText(text)
        self.notify.show()
        QTimer.singleShot(2200, self.notify.hide)

    def apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(15, 15, 25))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 40))
        palette.setColor(QPalette.ColorRole.Text, QColor(230, 230, 250))
        palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 80))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(114, 9, 183))
        self.setPalette(palette)
        self.setStyleSheet("background: #0f0f19;")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    window = PasswordGenerator()
    window.show()
    sys.exit(app.exec())