from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
    QMessageBox,
)

from PySide6.QtCore import Qt

from shared.services.account_service import create_account

from management_app.ui.dialogs.login_dialog import (
    GradientBackground,
    InputField
)

from shared.styles.theme import *


class RegisterDialog(QDialog):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("Create Account")

        self.resize(500, 700)

        root = QVBoxLayout(self)

        root.setContentsMargins(0, 0, 0, 0)

        bg = GradientBackground()

        root.addWidget(bg)

        layout = QVBoxLayout(bg)

        layout.setAlignment(Qt.AlignCenter)

        # Card
        card = QWidget()

        card.setFixedWidth(420)

        card.setStyleSheet("""
            background: white;
            border-radius: 20px;
        """)

        card_layout = QVBoxLayout(card)

        card_layout.setContentsMargins(
            40,
            40,
            40,
            40
        )

        card_layout.setSpacing(14)

        title = QLabel("CREATE ACCOUNT")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        self.fullname_input = InputField(
            "Full Name"
        )

        self.username_input = InputField(
            "Username"
        )

        self.email_input = InputField(
            "Email"
        )

        self.password_input = InputField(
            "Password"
        )

        self.confirm_input = InputField(
            "Confirm Password"
        )

        self.password_input.setEchoMode(
            self.password_input.Password
        )

        self.confirm_input.setEchoMode(
            self.confirm_input.Password
        )

        self.error_label = QLabel("")

        self.error_label.setAlignment(Qt.AlignCenter)

        self.error_label.setStyleSheet("""
            color: #E53935;
            font-size: 12px;
        """)

        register_button = QPushButton(
            "REGISTER"
        )

        register_button.setFixedHeight(48)

        register_button.clicked.connect(
            self.handle_register
        )

        register_button.setStyleSheet(f"""
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

        card_layout.addWidget(title)

        card_layout.addSpacing(16)

        card_layout.addWidget(
            self.fullname_input
        )

        card_layout.addWidget(
            self.username_input
        )

        card_layout.addWidget(
            self.email_input
        )

        card_layout.addWidget(
            self.password_input
        )

        card_layout.addWidget(
            self.confirm_input
        )

        card_layout.addWidget(
            self.error_label
        )

        card_layout.addSpacing(8)

        card_layout.addWidget(
            register_button
        )

        layout.addWidget(card)

    def handle_register(self):

        full_name = self.fullname_input.text()

        username = self.username_input.text()

        email = self.email_input.text()

        password = self.password_input.text()

        confirm = self.confirm_input.text()

        if password != confirm:

            self.error_label.setText(
                "Passwords do not match."
            )

            return

        success, message = create_account(
            username,
            email,
            password,
            full_name
        )

        if success:

            QMessageBox.information(
                self,
                "Success",
                message
            )

            self.accept()

        else:

            self.error_label.setText(message)