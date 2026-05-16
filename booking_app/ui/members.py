"""
members.py
----------
Giao diện Đăng Ký Kích Hoạt Hội Viên VIP
"""
import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QComboBox
from booking_app.ui.pages.booking_shared import (lbl, card_style, C_RED, C_RED2, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY)
from booking_app.ui.promotion import get_footer

class MembersPage(QWidget):
    register_success = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        
        body = QWidget()
        body.setStyleSheet(f"background:{C_BG};")
        main_lay.addWidget(body, 1)
        
        lay = QVBoxLayout(body)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.setAlignment(Qt.AlignHCenter)
        
        # Khung thẻ Card trung tâm Form đăng ký
        card = QWidget()
        card.setStyleSheet(card_style(16))
        card.setFixedWidth(520)
        lay.addWidget(card)
        
        form_lay = QVBoxLayout(card)
        form_lay.setContentsMargins(35, 35, 35, 35)
        form_lay.setSpacing(16)
        
        form_lay.addWidget(lbl("Kích Hoạt Hội Viên", 22, 800, C_DARK))
        form_lay.addWidget(lbl("Vui lòng xác nhận thông tin định danh để nâng cấp tài khoản lên phân hạng thành viên JetJet Elite.", 13, 400, C_GRAY))
        
        # Các trường nhập liệu mẫu Form
        form_lay.addWidget(lbl("Họ và tên chủ thẻ", 12, 700, C_MID))
        self.txt_name = QLineEdit("LÊ VĂN QUÂN")
        self.txt_name.setFixedHeight(42)
        self.txt_name.setStyleSheet(f"background:{C_LGRAY}; border:1.5px solid {C_BORDER}; border-radius:8px; padding:0 12px; color:{C_TEXT};")
        form_lay.addWidget(self.txt_name)
        
        form_lay.addWidget(lbl("Số điện thoại liên kết", 12, 700, C_MID))
        self.txt_phone = QLineEdit("0912345678")
        self.txt_phone.setFixedHeight(42)
        self.txt_phone.setStyleSheet(f"background:{C_LGRAY}; border:1.5px solid {C_BORDER}; border-radius:8px; padding:0 12px; color:{C_TEXT};")
        form_lay.addWidget(self.txt_phone)
        
        form_lay.addWidget(lbl("Gói phân hạng đăng ký", 12, 700, C_MID))
        self.cb_tier = QComboBox()
        self.cb_tier.addItems(["Hạng Bạc (Silver Elite) - Miễn Phí", "Hạng Vàng (Gold Elite) - Tích Lũy Chặng"])
        self.cb_tier.setFixedHeight(42)
        self.cb_tier.setStyleSheet(f"background:{C_LGRAY}; border:1.5px solid {C_BORDER}; border-radius:8px; padding:0 12px; color:{C_TEXT};")
        form_lay.addWidget(self.cb_tier)
        
        form_lay.addSpacing(10)
        
        # Nút xác nhận
        self.submit_btn = QPushButton("Xác nhận đăng ký")
        self.submit_btn.setCursor(Qt.PointingHandCursor)
        self.submit_btn.setFixedHeight(46)
        self.submit_btn.setStyleSheet(f"""
            QPushButton {{ background:{C_RED}; color:{C_WHITE}; border:none; border-radius:8px; font-size:14px; font-weight:700; }}
            QPushButton:hover {{ background:{C_RED2}; }}
        """)
        self.submit_btn.clicked.connect(self.register_success.emit)
        form_lay.addWidget(self.submit_btn)
        
        # Thêm Footer vào đáy trang
        main_lay.addWidget(get_footer())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = QWidget()
    w.resize(1000, 700)
    l = QVBoxLayout(w)
    l.setContentsMargins(0,0,0,0)
    p = MembersPage()
    l.addWidget(p)
    w.show()
    sys.exit(app.exec())