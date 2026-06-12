import sys
from PySide6.QtWidgets import QApplication

from booking_app.ui.dialogs.cus_login import LoginWindow
from booking_app.ui.dialogs.cus_register import RegisterWindow
from booking_app.ui.booking_window_origin import BookingWindow

class AppController:
    def __init__(self):
        self.login_win = None
        self.register_win = None
        self.main_win = None

    def show_login(self):
        
        if self.register_win:
            self.register_win.close()
            
       
        pos = self.register_win.pos() if self.register_win else None
        self.login_win = LoginWindow(pos=pos)
        
        
        self.login_win.go_register.connect(self.show_register)
        self.login_win.login_success.connect(self.show_booking_app)
        
        self.login_win.show()

    def show_register(self):
        """Hiển thị cửa sổ đăng ký"""
        pos = self.login_win.pos() if self.login_win else None
        self.login_win.close()
        
        self.register_win = RegisterWindow(pos=pos)
        # Khi bấm tab Đăng nhập trong RegisterCard, quay lại Login
        self.register_win.go_login.connect(self.show_login)
        
        self.register_win.show()

    def show_booking_app(self, account_data):
        """Đăng nhập thành công, mở giao diện đặt vé chính"""
        # Guard: if a BookingWindow is already open, ignore duplicate signal emissions
        # (can happen on rapid double-click before the button-disable propagates)
        if self.main_win is not None:
            return

        print(f"--- Welcome {account_data.get('full_name')} ---")

        if self.login_win:
            self.login_win.close()

        # Khởi tạo cửa sổ chính từ booking_window.py
        self.main_win = BookingWindow(account=account_data)
        self.main_win.show()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion") 
    
    controller = AppController()
    controller.show_login()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()