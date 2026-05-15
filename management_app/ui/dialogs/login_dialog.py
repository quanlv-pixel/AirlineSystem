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

from shared.services.account_service import login

from shared.styles.theme import *


class GradientBackground(QWidget):

    def paintEvent(self, event):

        painter = QPainter(self)

        gradient = QLinearGradient(
            0,
            0,
            self.width(),
            self.height()
        )

        gradient.setColorAt(0, QColor("#FF1632"))
        gradient.setColorAt(0.5, QColor("#FF2942"))
        gradient.setColorAt(1, QColor("#FF4B5F"))

        painter.fillRect(
            self.rect(),
            QBrush(gradient)
        )


class InputField(QLineEdit):

    def __init__(self, placeholder):

        super().__init__()

        self.setPlaceholderText(placeholder)

        self.setFixedHeight(58)

        self.setStyleSheet(f"""
            QLineEdit {{
                background: #F3F4F7;
                border: 1px solid #ECECF1;
                border-radius: 18px;

                padding-left: 20px;

                font-size: 14px;
                font-weight: 500;

                color: {TEXT_DARK};
            }}

            QLineEdit:focus {{
                border: 1.5px solid {RED_PRIMARY};
                background: white;
            }}

            QLineEdit::placeholder {{
                color: #9AA3B2;
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
                font-size: 32px;
                font-weight: 900;
                letter-spacing: 1px;
            }}
        """)

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(40, 40, 40, 40)

        card_layout.setSpacing(20)

        # Logo
        logo = QLabel("✈")

        logo.setAlignment(Qt.AlignCenter)

        logo.setStyleSheet(f"""
            font-size: 64px;
            color: {RED_PRIMARY};
        """)

        # Title
        title = QLabel("JETJET AIR")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet(f"""
            font-size: 34px;
            font-weight: 900;
            color: {TEXT_DARK};
            letter-spacing: 1px;
        """)

        subtitle = QLabel("AIRLINE MANAGEMENT PLATFORM")

        subtitle.setAlignment(Qt.AlignCenter)

        subtitle.setStyleSheet(f"""
            font-size: 11px;
            font-weight: 700;
            color: {GRAY_TEXT};
            letter-spacing: 4px;
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
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:0,
                    stop:0 #FF1632,
                    stop:1 #FF4A5F
                );

                border: none;
                border-radius: 22px;

                color: white;

                font-size: 13px;
                font-weight: 900;

                letter-spacing: 3px;
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
                background: white;

                border: 1px solid #ECECEC;
                border-radius: 18px;

                color: {TEXT_DARK};

                font-size: 13px;
                font-weight: 800;
            }}

            QPushButton:hover {{
                border: 1px solid {RED_PRIMARY};
                color: {RED_PRIMARY};
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

        from management_app.ui.dialogs.register_dialog import RegisterDialog

        dialog = RegisterDialog()

        dialog.exec()