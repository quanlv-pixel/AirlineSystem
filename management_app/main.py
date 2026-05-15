import sys

from PySide6.QtWidgets import QApplication
from database.init_db import init_db
from management_app.ui.dialogs.login_dialog import LoginDialog
from management_app.ui.main_window import MainWindow


def main():

    init_db()
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    if login_dialog.exec():
        window = MainWindow(
            login_dialog.current_account
        )
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main()