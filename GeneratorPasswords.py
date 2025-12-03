import sys
import secrets
import string
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QCheckBox, QSlider, QPushButton, QMessageBox, QSpinBox,
    QFrame, QProgressBar, QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation, QRect, QSize, pyqtSignal
from PyQt6.QtGui import QClipboard, QFont, QColor, QPalette, QIcon, QCursor


class AnimatedCheckBox(QCheckBox):
    """Чекбокс с анимацией при наведении"""
    def __init__(self, text, color="#8A7CFE", parent=None):
        super().__init__(text, parent)
        self._color = color
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet(self._get_style())
    
    def _get_style(self):
        """Стиль чекбокса"""
        return f"""
            QCheckBox {{
                color: {self._color};
                font-weight: 600;
                spacing: 15px;
                font-size: 15px;
                padding: 8px 0;
            }}
            QCheckBox:hover {{
                color: {self._lighten_color(self._color, 20)};
            }}
            QCheckBox::indicator {{
                width: 24px;
                height: 24px;
                border-radius: 7px;
                border: 2px solid {self._darken_color(self._color, 30)};
                background-color: #151522;
                transition: all 0.2s ease;
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {self._color};
                box-shadow: 0 0 8px rgba(138, 124, 254, 0.3);
            }}
            QCheckBox::indicator:checked {{
                background-color: {self._color};
                border: none;
                image: url({self._get_check_icon()});
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: {self._lighten_color(self._color, 15)};
                box-shadow: 0 0 10px rgba(138, 124, 254, 0.5);
            }}
        """
    
    def _get_check_icon(self):
        """Иконка галочки"""
        return "image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBmaWxsPSIjRkZGIiBkPSJNOSAyMWwtNy03bDIuOS0yLjlsNC4xIDQuMWw5LjktOS45TDE5IDlsLTEwIDEweiIvPjwvc3ZnPg=="
    
    def _lighten_color(self, hex_color, percent):
        """Осветление цвета"""
        r, g, b = self._hex_to_rgb(hex_color)
        r = min(255, r + int((255 - r) * percent / 100))
        g = min(255, g + int((255 - g) * percent / 100))
        b = min(255, b + int((255 - b) * percent / 100))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, hex_color, percent):
        """Затемнение цвета"""
        r, g, b = self._hex_to_rgb(hex_color)
        r = max(0, r - int(r * percent / 100))
        g = max(0, g - int(g * percent / 100))
        b = max(0, b - int(b * percent / 100))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _hex_to_rgb(self, hex_color):
        """Конвертация HEX в RGB"""
        hex_color = hex_color.lstrip('#')
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )


class NotificationWidget(QWidget):
    """Уведомление"""
    closed = pyqtSignal()
    
    def __init__(self, title, message, parent=None, duration=3000):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._duration = duration
        
        self._init_ui(title, message)
        self._setup_animation()
        self._start_timer()
    
    def _init_ui(self, title, message):
        """Инициализация UI"""
        self.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #151522, stop:1 #1A1A28);
            border-radius: 14px;
            border: 1px solid #252535;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.5);
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #8A7CFE;")
        
        message_label = QLabel(message)
        message_label.setStyleSheet("font-size: 14px; color: #A0A0C0;")
        
        layout.addWidget(title_label)
        layout.addWidget(message_label)
    
    def _setup_animation(self):
        """Анимация появления"""
        self.setWindowOpacity(0.0)
        self.show()
        
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
    
    def _start_timer(self):
        """Автоматическое скрытие"""
        QTimer.singleShot(self._duration, self._animate_close)
    
    def _animate_close(self):
        """Анимация закрытия"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self._close)
        self.animation.start()
    
    def _close(self):
        """Закрытие"""
        self.closed.emit()
        self.deleteLater()


class PasswordGenerator(QMainWindow):
    """Генератор паролей"""
    
    # SVG иконки
    _SVG_ICONS = {
        'eye_visible': "image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBmaWxsPSIjQTBBMEMwIiBkPSJNMTIgNEwxMiA0QzYuNDggNCAxLjk4IDcuMzUgMSA5Ljk4YzAuOTEgMi42IDIuODUgNC42NCA0LjYgNS41N0M3LjE1IDE2LjIyIDguNzcgMTcuNSAxMiAxNy41czQuODUtMS4yOCA2LjQtMi4zNWMxLjc1LTAuOTMgMy42OS0yLjk3IDQuNi01LjU3QzIyLjAyIDcuMzUgMTcuNTIgNCAxMiA0eiIvPjxjaXJjbGUgZmlsbD0iI0EwQTBDMCIgY3g9IjEyIiBjeT0iMTIiIHI9IjIuNSIvPjwvc3ZnPg==",
        'eye_hidden': "image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBmaWxsPSIjQTBBMEMwIiBkPSJNMTIgNEwxMiA0QzYuNDggNCAxLjk4IDcuMzUgMSA5Ljk4YzAuOTEgMi42IDIuODUgNC42NCA0LjYgNS41N0M3LjE1IDE2LjIyIDguNzcgMTcuNSAxMiAxNy41czQuODUtMS4yOCA2LjQtMi4zNWMxLjc1LTAuOTMgMy42OS0yLjk3IDQuNi01LjU3QzIyLjAyIDcuMzUgMTcuNTIgNCAxMiA0em0wIDExLjVjLTIuMDEgMC0zLjg4LS42Ni01LjM4LTEuNTdDNy42NSAxMy4zMiA4LjcgMTIgMTIgMTJzMDEuNzUgMS4zMiAyLjYyIDEuODljMS41LjkxIDMuMzcgMS41NyA1LjM4IDEuNTdIMTJ6Ii8+PHBhdGggZmlsbD0iI0EwQTBDMCIgZD0iTTE2LjY3IDMuMjFDMTYuNDEgMy4xMSAxNi4xNCAzIDkuOTggMyA3LjMgMyA0LjQ4IDMuNzggMiA1LjEzLTAuMjcgNi4zOSAwIDIuMDQgMS42NiAwaDE3LjM0Yy4zMSAxLjM5LjQ5IDIuODIuNDkgNC4yNmMwIDYuOTktMi41MSAxMi4zOS02LjI5IDE1LjM3TDkuOTggMTIgMTYuNjcgMy4yMXoiLz48cGF0aCBmaWxsPSIjQTBBMEMwIiBkPSJNMTQgMTFjLjU1IDAgMSAuNDUgMSAxcy0uNDUgMS0xIDFjLS41NSAwLTEtLjQ1LTEtMXMuNDUtMSAxLTF6Ii8+PC9zdmc+",
        'copy': "image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBmaWxsPSIjRkZGIiBkPSJNMTYgMWMtMS4xIDAtMiAuOS0yIDJ2NGgyVjNjMC0uNTUuNDUtMSAxLTFoNFYxYzAtLjU1LS40NS0xLTEtMWgtNHptLTEgNWgtNEM5LjQ4IDYgOCA3LjQ4IDggOWgydjEwYzAgMS41MiAxLjQ4IDMgMyAzSDIwYzEuNTIgMCAzLTEuNDggMy0zVjloLTJjMC0xLjUyLTEuNDgtMy0zLTNIMTRjLS41NSAwLTEtLjQ1LTEtMXoiLz48cGF0aCBmaWxsPSIjRkZGIiBkPSJNMTYgMTlINmMtMS4xIDAtMi0uOS0yLTJWOGEyIDIgMCAwIDEgMi0yaDhjMS4xIDAgMiAuOSAyIDJ2NGgydi00YzAgMy4zMDEgMi42OSA2IDYgNmgydjJjMCAzLjMwMSAyLjY5IDYgNiA2czYtMi42OTkgNi02SDIwdjRoLTJjMCwxLjEwNS0uODk1IDIuMDk1IDIgMkg4Yy0xLjEwNSAwLTIuMDk1LS45LTEtMi4waDR6Ii8+PC9zdmc+",
        'down_arrow': "image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNiIgaGVpZ2h0PSIxNiIgdmlld0JveD0iMCAwIDI0IDI0Ij48cGF0aCBmaWxsPSIjQTBBMEMwIiBkPSJNMTIgMTRsLTQgNC00LTRoOHoiLz48L3N2Zz4="
    }
    
    # Шаблоны паролей
    _PASSWORD_TEMPLATES = [
        {"name": "Выберите шаблон", "length": 16, "uppercase": True, "lowercase": True, "digits": True, "symbols": True, "exclude_similar": False, "strength": "Ожидание генерации", "value": 0, "color": "#7A7A9A"},
        {"name": "Стандартный (16 символов)", "length": 16, "uppercase": True, "lowercase": True, "digits": True, "symbols": True, "exclude_similar": False, "strength": "Очень высокая", "value": 90, "color": "#8BC34A"},
        {"name": "PIN-код (4 цифры)", "length": 4, "uppercase": False, "lowercase": False, "digits": True, "symbols": False, "exclude_similar": True, "strength": "Низкая", "value": 30, "color": "#FFC107"},
        {"name": "Wi-Fi (12 символов)", "length": 12, "uppercase": False, "lowercase": True, "digits": True, "symbols": False, "exclude_similar": False, "strength": "Высокая", "value": 75, "color": "#4CAF50"},
        {"name": "Легко запоминаемый", "length": 3, "uppercase": False, "lowercase": True, "digits": True, "symbols": False, "exclude_similar": False, "strength": "Средняя (запоминаемый)", "value": 65, "color": "#2196F3"},
        {"name": "Максимальная надежность (32 символа)", "length": 32, "uppercase": True, "lowercase": True, "digits": True, "symbols": True, "exclude_similar": True, "strength": "Максимальная", "value": 100, "color": "#9C27B0"},
        {"name": "Банковский (24 символа)", "length": 24, "uppercase": True, "lowercase": True, "digits": True, "symbols": True, "exclude_similar": True, "strength": "Банковский уровень", "value": 95, "color": "#3F51B5"}
    ]
    
    # Словари для мнемонических паролей
    _MNEMONIC_WORDS = {
        "adjectives": ["солнечный", "тихий", "смелый", "умный", "быстрый", "яркий", "темный", "светлый", "добрый", "строгий", "легкий", "крепкий"],
        "nouns": ["тигр", "лес", "океан", "гора", "звезда", "дождь", "ветер", "камень", "орел", "львица", "волк", "медведь"]
    }
    
    def __init__(self):
        super().__init__()
        self._init_window()
        self._init_ui()
        self._apply_template(0)
    
    def _init_window(self):
        """Инициализация окна"""
        self.setWindowTitle("Генератор паролей")
        self.setGeometry(100, 100, 600, 600)
        self.setMinimumSize(550, 550)
        self._setup_dark_theme()
    
    def _init_ui(self):
        """Инициализация UI"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        main_content = QWidget()
        scroll.setWidget(main_content)
        
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(20)
        
        self.setCentralWidget(scroll)
        
        # Карточка пароля
        main_layout.addWidget(self._create_password_card())
        
        # Карточка настроек
        main_layout.addWidget(self._create_settings_card())
        
        # Нижняя панель
        main_layout.addWidget(self._create_bottom_card())
        
        # Подключение сигналов
        self.length_slider.valueChanged.connect(self._update_length_display)
        self.length_spinbox.valueChanged.connect(self.length_slider.setValue)
        self.template_combo.currentIndexChanged.connect(self._apply_template)
        self.hide_password_cb.stateChanged.connect(self._toggle_password_visibility)
        self.generate_btn.clicked.connect(self._generate_password)
        self.copy_btn.clicked.connect(self._copy_password)
        self.toggle_visibility_btn.clicked.connect(self._toggle_password_visibility)
    
    def _setup_dark_theme(self):
        """Настройка темной темы"""
        palette = QPalette()
        colors = [
            (QPalette.ColorRole.Window, QColor(18, 18, 24)),
            (QPalette.ColorRole.WindowText, QColor(220, 220, 240)),
            (QPalette.ColorRole.Base, QColor(20, 20, 32)),
            (QPalette.ColorRole.AlternateBase, QColor(25, 25, 40)),
            (QPalette.ColorRole.Text, QColor(220, 220, 240)),
            (QPalette.ColorRole.Button, QColor(30, 30, 45)),
            (QPalette.ColorRole.ButtonText, QColor(220, 220, 240)),
            (QPalette.ColorRole.Highlight, QColor(138, 124, 254)),
            (QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        ]
        
        for role, color in colors:
            palette.setColor(role, color)
        
        self.setPalette(palette)
        self.setStyleSheet(self._get_global_stylesheet())
    
    def _get_global_stylesheet(self):
        """Глобальный стиль"""
        return """
            QMainWindow { background-color: #121218; }
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical {
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #121218, stop:1 #181828);
                width: 14px;
                margin: 10px 0 10px 0;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #252535, stop:1 #2A2A3A);
                min-height: 30px;
                border-radius: 7px;
                margin: 0 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2A2A3A, stop:1 #303040);
            }
            QToolTip {
                background-color: #1A1A28;
                color: #E0E0FF;
                border: 1px solid #252535;
                border-radius: 8px;
                padding: 6px;
                font-size: 13px;
            }
        """
    
    def _create_password_card(self):
        """Карточка с паролем"""
        card = QFrame()
        card.setObjectName("passwordCard")
        card.setStyleSheet("""
            QFrame#passwordCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #151522, stop:1 #1A1A28);
                border-radius: 16px;
                padding: 20px;
                border: 1px solid #252535;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Поле пароля
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setFont(QFont("Consolas", 16, QFont.Weight.Bold))
        self.password_display.setPlaceholderText("Сгенерированный пароль появится здесь...")
        self.password_display.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #101018, stop:1 #151522);
                color: #FFFFFF;
                border: 2px solid #2A2A3A;
                border-radius: 12px;
                padding: 16px;
                font-size: 18px;
                selection-background-color: #6C63FF;
                selection-color: white;
                min-height: 60px;
                box-shadow: 0 3px 12px rgba(0, 0, 0, 0.3);
            }
            QLineEdit:focus {
                border: 2px solid #8A7CFE;
                box-shadow: 0 0 0 3px rgba(138, 124, 254, 0.2);
            }
        """)
        layout.addWidget(self.password_display)
        
        # Индикатор силы
        layout.addWidget(self._create_strength_card())
        
        # Панель управления
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        # Кнопка видимости
        self.toggle_visibility_btn = QPushButton()
        self.toggle_visibility_btn.setIcon(QIcon(self._SVG_ICONS['eye_visible']))
        self.toggle_visibility_btn.setIconSize(QSize(24, 24))
        self.toggle_visibility_btn.setFixedSize(50, 50)
        self.toggle_visibility_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.toggle_visibility_btn.setStyleSheet(self._get_visibility_button_style())
        
        # Кнопка копирования
        self.copy_btn = QPushButton("Копировать")
        self.copy_btn.setIcon(QIcon(self._SVG_ICONS['copy']))
        self.copy_btn.setIconSize(QSize(20, 20))
        self.copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.copy_btn.setEnabled(False)
        self.copy_btn.setStyleSheet(self._get_copy_button_style(False))
        
        controls_layout.addWidget(self.toggle_visibility_btn)
        controls_layout.addWidget(self.copy_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        return card
    
    def _create_strength_card(self):
        """Карточка с индикатором силы"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #12121E, stop:1 #181828);
                border-radius: 12px;
                padding: 15px;
                border: 1px solid #252535;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        
        self.strength_value = QLabel("Ожидание генерации")
        self.strength_value.setStyleSheet("""
            font-size: 16px;
            font-weight: 700;
            color: #7A7A9A;
        """)
        
        header_layout.addWidget(QLabel("Надежность:"))
        header_layout.addWidget(self.strength_value)
        header_layout.addStretch()
        
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 100)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(False)
        self.strength_bar.setStyleSheet(self._get_strength_bar_style("#6C63FF"))
        
        layout.addLayout(header_layout)
        layout.addWidget(self.strength_bar)
        
        return card
    
    def _create_settings_card(self):
        """Карточка с настройками"""
        card = QFrame()
        card.setObjectName("settingsCard")
        card.setStyleSheet("""
            QFrame#settingsCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #12121E, stop:1 #181828);
                border-radius: 16px;
                padding: 20px;
                border: 1px solid #252535;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)
        
        # Длина пароля
        layout.addWidget(self._create_length_group())
        
        # Состав пароля
        layout.addWidget(self._create_chars_group())
        
        # Дополнительные настройки
        layout.addWidget(self._create_options_group())
        
        return card
    
    def _create_length_group(self):
        """Группа для выбора длины пароля"""
        group = QGroupBox("Длина пароля")
        group.setStyleSheet(self._get_group_box_style())
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        slider_layout = QHBoxLayout()
        self.length_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_slider.setRange(4, 128)
        self.length_slider.setValue(16)
        self.length_slider.setStyleSheet(self._get_slider_style())
        
        self.length_label = QLabel("16")
        self.length_label.setStyleSheet("""
            font-weight: 700;
            color: #8A7CFE;
            font-size: 16px;
            min-width: 40px;
            text-align: center;
        """)
        self.length_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        slider_layout.addWidget(self.length_slider)
        slider_layout.addWidget(self.length_label)
        
        spinbox_layout = QHBoxLayout()
        spinbox_layout.addWidget(QLabel("Точное значение:"))
        
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setRange(4, 128)
        self.length_spinbox.setValue(16)
        self.length_spinbox.setStyleSheet(self._get_spinbox_style())
        spinbox_layout.addWidget(self.length_spinbox)
        spinbox_layout.addStretch()
        
        layout.addLayout(slider_layout)
        layout.addLayout(spinbox_layout)
        group.setLayout(layout)
        
        return group
    
    def _create_chars_group(self):
        """Группа для выбора состава пароля"""
        group = QGroupBox("Состав пароля")
        group.setStyleSheet(self._get_group_box_style())
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        self.uppercase_cb = AnimatedCheckBox("Заглавные буквы (A-Z)", "#8A7CFE")
        self.uppercase_cb.setChecked(True)
        
        self.lowercase_cb = AnimatedCheckBox("Строчные буквы (a-z)", "#64B5F6")
        self.lowercase_cb.setChecked(True)
        
        self.digits_cb = AnimatedCheckBox("Цифры (0-9)", "#FFB74D")
        self.digits_cb.setChecked(True)
        
        self.symbols_cb = AnimatedCheckBox("Специальные символы", "#BA68C8")
        self.symbols_cb.setChecked(True)
        
        self.exclude_similar_cb = AnimatedCheckBox("Исключить похожие символы", "#FF8A80")
        
        for cb in [self.uppercase_cb, self.lowercase_cb, self.digits_cb, self.symbols_cb, self.exclude_similar_cb]:
            layout.addWidget(cb)
        
        group.setLayout(layout)
        return group
    
    def _create_options_group(self):
        """Группа дополнительных настроек"""
        group = QGroupBox("Дополнительные настройки")
        group.setStyleSheet(self._get_group_box_style())
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        self.auto_copy_cb = AnimatedCheckBox("Автоматически копировать", "#A0A0C0")
        self.auto_copy_cb.setChecked(True)
        
        self.hide_password_cb = AnimatedCheckBox("Скрывать пароль", "#A0A0C0")
        self.hide_password_cb.setChecked(True)
        
        layout.addWidget(self.auto_copy_cb)
        layout.addWidget(self.hide_password_cb)
        group.setLayout(layout)
        
        return group
    
    def _create_bottom_card(self):
        """Нижняя карточка с шаблонами и генерацией"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #12121E, stop:1 #181828);
                border-radius: 16px;
                padding: 15px;
                border: 1px solid #252535;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Шаблоны
        self.template_combo = QComboBox()
        for template in self._PASSWORD_TEMPLATES:
            self.template_combo.addItem(template["name"])
        self.template_combo.setStyleSheet(self._get_template_combo_style())
        
        layout.addWidget(self.template_combo)
        
        # Кнопка генерации
        self.generate_btn = QPushButton("СГЕНЕРИРОВАТЬ ПАРОЛЬ")
        self.generate_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.generate_btn.setStyleSheet(self._get_generate_button_style())
        layout.addWidget(self.generate_btn)
        
        return card
    
    # Стили для виджетов
    def _get_group_box_style(self):
        return """
            QGroupBox {
                font-weight: 600;
                color: #C0C0E0;
                border: 1px solid #252535;
                border-radius: 12px;
                margin-top: 1ex;
                padding: 15px;
                background: rgba(20, 20, 32, 0.6);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                background-color: #151522;
                border-radius: 8px;
                color: #8A7CFE;
            }
        """
    
    def _get_slider_style(self):
        return """
            QSlider::groove:horizontal {
                border: 1px solid #2A2A3A;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #101018, stop:1 #181828);
                margin: 0 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.5, 
                                          stop:0 #8A7CFE, stop:1 #6C63FF);
                border: 2px solid #5A52E0;
                width: 24px;
                height: 24px;
                margin: -8px 0;
                border-radius: 12px;
            }
        """
    
    def _get_spinbox_style(self):
        return """
            QSpinBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #101018, stop:1 #151522);
                color: white;
                border: 1px solid #252535;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 15px;
                min-width: 80px;
            }
        """
    
    def _get_visibility_button_style(self):
        return """
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.5, stop:0 #1A1A28, stop:1 #202030);
                border-radius: 15px;
                border: 2px solid #2A2A3A;
            }
            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.5, stop:0 #202030, stop:1 #252535);
                border: 2px solid #6C63FF;
            }
        """
    
    def _get_copy_button_style(self, is_success=False):
        base_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A1A28, stop:1 #202030);
                color: #A0A0C0;
                font-weight: 600;
                font-size: 15px;
                border-radius: 14px;
                padding: 12px 24px;
                border: 1px solid #252535;
                min-width: 140px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #202030, stop:1 #252535);
                border: 1px solid #8A7CFE;
            }
        """
        
        success_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4CAF50, stop:1 #66BB6A);
                color: white;
                font-weight: 700;
                font-size: 16px;
                border-radius: 16px;
                padding: 14px 28px;
                min-width: 160px;
            }
        """
        
        return success_style if is_success else base_style
    
    def _get_template_combo_style(self):
        return f"""
            QComboBox {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #101018, stop:1 #151522);
                color: white;
                border: 1px solid #252535;
                border-radius: 12px;
                padding: 12px 18px;
                font-size: 15px;
                min-height: 45px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: url({self._SVG_ICONS['down_arrow']});
                width: 14px;
                height: 14px;
            }}
        """
    
    def _get_generate_button_style(self):
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8A7CFE, stop:1 #6C63FF);
                color: white;
                font-weight: 700;
                font-size: 16px;
                border-radius: 16px;
                padding: 14px 28px;
                border: none;
                min-height: 55px;
                box-shadow: 0 6px 20px rgba(138, 124, 254, 0.4);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #9A8CFE, stop:1 #7C73FF);
                box-shadow: 0 8px 25px rgba(138, 124, 254, 0.6);
            }
        """
    
    def _get_strength_bar_style(self, color):
        """Стиль прогресс-бара"""
        r, g, b = self._hex_to_rgb(color)
        rgb_str = f"{r},{g},{b}"
        light_color = self._lighten_color(color, 20)
        
        return f"""
            QProgressBar {{
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #101018, stop:1 #151522);
                border-radius: 8px;
                height: 10px;
            }}
            QProgressBar::chunk {{
                border-radius: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {color}, stop:1 {light_color});
                box-shadow: 0 0 6px rgba({rgb_str}, 0.5);
            }}
        """
    
    # Вспомогательные методы
    def _lighten_color(self, hex_color, percent):
        """Осветление цвета"""
        r, g, b = self._hex_to_rgb(hex_color)
        r = min(255, r + int((255 - r) * percent / 100))
        g = min(255, g + int((255 - g) * percent / 100))
        b = min(255, b + int((255 - b) * percent / 100))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _hex_to_rgb(self, hex_color):
        """Конвертация HEX в RGB"""
        hex_color = hex_color.lstrip('#')
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16)
        )
    
    def _update_length_display(self, value):
        """Обновление отображения длины"""
        self.length_label.setText(str(value))
        self.length_spinbox.setValue(value)
    
    def _toggle_password_visibility(self):
        """Переключение видимости пароля"""
        is_hidden = self.password_display.echoMode() == QLineEdit.EchoMode.Password
        self.password_display.setEchoMode(QLineEdit.EchoMode.Normal if is_hidden else QLineEdit.EchoMode.Password)
        self.toggle_visibility_btn.setIcon(QIcon(self._SVG_ICONS['eye_hidden' if is_hidden else 'eye_visible']))
    
    def _apply_template(self, index):
        """Применение шаблона"""
        if index < 0 or index >= len(self._PASSWORD_TEMPLATES):
            return
        
        template = self._PASSWORD_TEMPLATES[index]
        
        # Установка параметров
        self.length_slider.setValue(template["length"])
        self.uppercase_cb.setChecked(template["uppercase"])
        self.lowercase_cb.setChecked(template["lowercase"])
        self.digits_cb.setChecked(template["digits"])
        self.symbols_cb.setChecked(template["symbols"])
        self.exclude_similar_cb.setChecked(template["exclude_similar"])
        self.hide_password_cb.setChecked(True)
        
        # Обновление индикатора силы
        self._update_strength_display(
            template["strength"],
            template["value"],
            template["color"]
        )
        
        # Включение/отключение кнопки копирования
        self.copy_btn.setEnabled(index != 0)
    
    def _update_strength_display(self, text, value, color):
        """Обновление отображения надежности"""
        self.strength_value.setText(text)
        self.strength_value.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 700;
            color: {color};
        """)
        self.strength_bar.setValue(value)
        self.strength_bar.setStyleSheet(self._get_strength_bar_style(color))
    
    def _calculate_strength(self, password):
        """Оценка надежности пароля"""
        if not password:
            return "Пустой пароль", 0, "#7A7A9A"
        
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_symbol = any(c in string.punctuation for c in password)
        
        # Расчет баллов
        score = length * 2
        if has_upper: score += 10
        if has_lower: score += 10
        if has_digit: score += 15
        if has_symbol: score += 20
        
        # Проверки на слабые комбинации
        if length < 8: score -= 30
        if not (has_upper or has_symbol): score -= 20
        if len(set(password)) < length * 0.6: score -= 15
        
        # Определение уровня
        if score > 95: return "Максимальная", 100, "#9C27B0"
        if score > 85: return "Очень высокая", 95, "#4CAF50"
        if score > 75: return "Высокая", 85, "#8BC34A"
        if score > 65: return "Хорошая", 75, "#FFC107"
        if score > 50: return "Средняя", 60, "#FF9800"
        if score > 35: return "Слабая", 45, "#FF5722"
        return "Очень слабая", 30, "#F44336"
    
    def _update_strength_indicator(self, password):
        """Обновление индикатора силы пароля"""
        strength, value, color = self._calculate_strength(password)
        self._update_strength_display(strength, value, color)
    
    def _generate_password(self):
        """Генерация пароля"""
        template_index = self.template_combo.currentIndex()
        
        # Генерация мнемонического пароля
        if template_index == 4:  # Легко запоминаемый
            password = self._generate_memorable_password()
            self.password_display.setText(password)
            self._update_strength_indicator(password)
            self.copy_btn.setEnabled(True)
            
            if self.auto_copy_cb.isChecked():
                self._copy_password(silent=True)
            return
        
        # Сбор символов
        characters = ""
        similar_chars = "I1lO0"
        
        if self.uppercase_cb.isChecked():
            chars = string.ascii_uppercase
            if self.exclude_similar_cb.isChecked():
                chars = ''.join(c for c in chars if c not in similar_chars)
            characters += chars
            
        if self.lowercase_cb.isChecked():
            chars = string.ascii_lowercase
            if self.exclude_similar_cb.isChecked():
                chars = ''.join(c for c in chars if c not in similar_chars)
            characters += chars
            
        if self.digits_cb.isChecked():
            chars = string.digits
            if self.exclude_similar_cb.isChecked():
                chars = ''.join(c for c in chars if c not in similar_chars)
            characters += chars
            
        if self.symbols_cb.isChecked():
            characters += string.punctuation
        
        if not characters:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один тип символов!")
            return
        
        # Генерация
        password_length = self.length_slider.value()
        try:
            password = ''.join(secrets.choice(characters) for _ in range(password_length))
        except IndexError:
            QMessageBox.warning(self, "Ошибка", "Недостаточно символов для генерации!\nПопробуйте отключить исключение похожих символов.")
            return
        
        # Проверка для PIN-кода
        if template_index == 2 and len(password) != 4:  # PIN-код
            password = ''.join(secrets.choice(string.digits) for _ in range(4))
        
        self.password_display.setText(password)
        self._update_strength_indicator(password)
        self.copy_btn.setEnabled(True)
        
        # Автоматическое копирование
        if self.auto_copy_cb.isChecked():
            self._copy_password(silent=True)
    
    def _generate_memorable_password(self):
        """Генерация легко запоминаемого пароля"""
        parts = [
            secrets.choice(self._MNEMONIC_WORDS["adjectives"]),
            secrets.choice(self._MNEMONIC_WORDS["nouns"]),
            str(secrets.randbelow(9999))
        ]
        return secrets.choice(["-", "_", "."]).join(parts)
    
    def _copy_password(self, silent=False):
        """Копирование пароля"""
        password = self.password_display.text()
        if not password:
            return
        
        # Копирование в буфер
        QApplication.clipboard().setText(password)
        
        # Анимация кнопки
        original_text = self.copy_btn.text()
        original_style = self.copy_btn.styleSheet()
        
        self.copy_btn.setText("СКОПИРОВАНО!")
        self.copy_btn.setStyleSheet(self._get_copy_button_style(True))
        
        # Возврат к исходному состоянию
        QTimer.singleShot(1000, lambda: self._restore_copy_button(original_text, original_style))
        
        # Показ уведомления
        if not silent:
            NotificationWidget(
                "✅ Пароль скопирован!",
                "Пароль сохранен в буфер обмена!",
                self
            )
    
    def _restore_copy_button(self, original_text, original_style):
        """Восстановление кнопки копирования"""
        self.copy_btn.setText(original_text)
        self.copy_btn.setStyleSheet(original_style)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Установка шрифта
    font = QFont("Segoe UI", 11)
    app.setFont(font)
    
    window = PasswordGenerator()
    window.show()
    sys.exit(app.exec())