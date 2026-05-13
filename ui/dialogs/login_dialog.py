from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QLinearGradient, QBrush

from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QHBoxLayout,
    QLineEdit,
)

from services.account_service import login

from styles.theme import *


class GradientBackground(QWidget):

    def paintEvent(self, event):

        painter = QPainter(self)

        gradient = QLinearGradient(
            0,
            0,
            self.width(),
            self.height()
        )

        gradient.setColorAt(0, QColor("#FF5252"))
        gradient.setColorAt(0.5, QColor("#E53935"))
        gradient.setColorAt(1, QColor("#B71C1C"))

        painter.fillRect(
            self.rect(),
            QBrush(gradient)
        )


class InputField(QLineEdit):

    def __init__(self, placeholder):

        super().__init__()

        self.setPlaceholderText(placeholder)

        self.setFixedHeight(45)

        self.setStyleSheet(f"""
            QLineEdit {{
                background: {GRAY_BG};
                border: 1px solid {GRAY_BORDER};
                border-radius: 10px;
                padding-left: 12px;
                font-size: 14px;
            }}

            QLineEdit:focus {{
                border: 1.5px solid {RED_PRIMARY};
            }}
        """)


class LoginDialog(QDialog):

    def __init__(self):

        super().__init__()

        self.current_account = None

        self.setWindowTitle("JetJet Air Login")

        self.resize(500, 600)

        root = QVBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)

        # Background
        bg = GradientBackground()

        root.addWidget(bg)

        layout = QVBoxLayout(bg)

        layout.setAlignment(Qt.AlignCenter)

        # Card
        card = QWidget()

        card.setFixedWidth(400)

        card.setStyleSheet(f"""
            QWidget {{
                background: white;
                border-radius: 20px;
            }}
        """)

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(40, 40, 40, 40)

        card_layout.setSpacing(16)

        # Logo
        logo = QLabel("✈")

        logo.setAlignment(Qt.AlignCenter)

        logo.setStyleSheet(f"""
            font-size: 48px;
            color: {RED_PRIMARY};
        """)

        # Title
        title = QLabel("JETJET AIR")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet(f"""
            font-size: 26px;
            font-weight: bold;
            color: {TEXT_DARK};
            letter-spacing: 2px;
        """)

        subtitle = QLabel("AIRLINE MANAGEMENT PLATFORM")

        subtitle.setAlignment(Qt.AlignCenter)

        subtitle.setStyleSheet(f"""
            font-size: 10px;
            color: {GRAY_TEXT};
            letter-spacing: 2px;
        """)

        # Inputs
        self.identifier_input = InputField(
            "Username or Email"
        )

        self.password_input = InputField(
            "Password"
        )

        self.password_input.setEchoMode(
            QLineEdit.Password
        )

        # Error label
        self.error_label = QLabel("")

        self.error_label.setAlignment(Qt.AlignCenter)

        self.error_label.setStyleSheet("""
            color: #E53935;
            font-size: 12px;
        """)

        # Login button
        login_button = QPushButton(
            "LOGIN"
        )

        login_button.setFixedHeight(48)

        login_button.clicked.connect(
            self.handle_login
        )

        login_button.setStyleSheet(f"""
            QPushButton {{
                background: {RED_PRIMARY};
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background: {RED_DARK};
            }}
        """)

        # Register button
        register_button = QPushButton(
            "CREATE ACCOUNT"
        )

        register_button.setFixedHeight(44)

        register_button.clicked.connect(
            self.open_register
        )

        register_button.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {RED_PRIMARY};
                border-radius: 10px;
                color: {RED_PRIMARY};
                font-size: 13px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background: #FFEBEE;
            }}
        """)

        # Add widgets
        card_layout.addWidget(logo)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(20)

        card_layout.addWidget(
            self.identifier_input
        )

        card_layout.addWidget(
            self.password_input
        )

        card_layout.addWidget(
            self.error_label
        )

        card_layout.addSpacing(8)

        card_layout.addWidget(login_button)

        card_layout.addWidget(register_button)

        layout.addWidget(card)

    def handle_login(self):

        identifier = self.identifier_input.text()

        password = self.password_input.text()

        account = login(
            identifier,
            password
        )

        if account:

            self.current_account = account

            self.accept()

        else:

            self.error_label.setText(
                "Invalid username or password."
            )

    def open_register(self):

        from ui.dialogs.register_dialog import RegisterDialog

        dialog = RegisterDialog()

        dialog.exec()