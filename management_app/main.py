import sys

from PySide6.QtWidgets import QApplication

from ui.dialogs.login_dialog import LoginDialog

from ui.main_window import MainWindow


app = QApplication(sys.argv)

login_dialog = LoginDialog()

if login_dialog.exec():

    window = MainWindow(
        login_dialog.current_account
    )

    window.show()

    sys.exit(app.exec())