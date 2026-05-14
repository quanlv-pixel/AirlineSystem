import sys

from PySide6.QtWidgets import QApplication

from management_app.ui.dialogs.login_dialog import LoginDialog
from management_app.ui.main_window import MainWindow


app = QApplication(sys.argv)

login_dialog = LoginDialog()

if login_dialog.exec():

    window = MainWindow(
        login_dialog.current_account
    )

    window.show()

    sys.exit(app.exec())