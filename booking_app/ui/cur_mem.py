"""
cur_mem.py
----------
Giao diện Trạng Thái Hội Viên Hiện Tại (Sau khi kích hoạt)
"""
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QGridLayout
from booking_app.ui.pages.booking_shared import (lbl, card_style, C_RED, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY, C_GREEN, C_ORANGE)
from booking_app.ui.promotion import get_footer

class PrivilegeCard(QWidget):
    def __init__(self, icon: str, title: str, desc: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(12))
        self.setFixedHeight(90)
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(14)
        
        ico = lbl(icon, 20, 400, C_RED)
        ico.setFixedWidth(28)
        lay.addWidget(ico)
        
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.addWidget(lbl(title, 14, 700, C_TEXT))
        text_col.addWidget(lbl(desc, 12, 400, C_GRAY))
        lay.addLayout(text_col)
        lay.addStretch()

class CurrentMemberPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        
        body = QWidget()
        body.setStyleSheet(f"background:{C_BG};")
        main_lay.addWidget(body, 1)
        
        lay = QVBoxLayout(body)
        lay.setContentsMargins(30, 24, 30, 30)
        lay.setSpacing(20)
        
        # Tiêu đề trạng thái thành viên
        lay.addWidget(lbl("Thành viên JetJet Elite", 24, 800, C_DARK))
        lay.addWidget(lbl("Chào mừng trở lại! Xem thông tin phân hạng và ưu đãi dặm bay tích lũy của bạn.", 13, 400, C_GRAY))
        
        # Thẻ thông tin hạng Vàng
        tier_card = QWidget()
        tier_card.setStyleSheet("background:qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D4AF37, stop:1 #AA7C11); border-radius:14px;")
        tier_card.setFixedHeight(140)
        tc_lay = QVBoxLayout(tier_card)
        tc_lay.setContentsMargins(25, 20, 25, 20)
        
        top_row = QHBoxLayout()
        top_row.addWidget(lbl("HẠNG VÀNG • GOLD MEMBER", 14, 800, C_WHITE))
        top_row.addStretch()
        top_row.addWidget(lbl("Mã số: JJ-991823", 12, 500, C_WHITE))
        tc_lay.addLayout(top_row)
        tc_lay.addStretch()
        
        tc_lay.addWidget(lbl("LÊ VĂN QUÂN", 20, 800, C_WHITE))
        tc_lay.addSpacing(5)
        
        # Thanh tiến trình dặm bay lên hạng Bạch Kim
        prog_lay = QHBoxLayout()
        pbar = QProgressBar()
        pbar.setRange(0, 25000)
        pbar.setValue(18500)
        pbar.setTextVisible(False)
        pbar.setFixedHeight(8)
        pbar.setStyleSheet(f"QProgressBar{{background:rgba(255,255,255,0.3); border:none; border-radius:4px;}}"
                           f"QProgressBar::chunk{{background:{C_WHITE}; border-radius:4px;}}")
        prog_lay.addWidget(pbar, 1)
        prog_lay.addWidget(lbl("18,500 / 25,000 dặm", 12, 700, C_WHITE))
        tc_lay.addLayout(prog_lay)
        
        lay.addWidget(tier_card)
        
        # Khối hiển thị Đặc quyền phân hạng
        lay.addWidget(lbl("Đặc quyền hạng Vàng của bạn", 16, 700, C_DARK))
        grid = QGridLayout()
        grid.setSpacing(14)
        
        privileges = [
            ("✈", "Tích lũy dặm x1.5", "Nhận thêm 50% số lượng dặm thưởng trên mỗi chuyến bay thực tế."),
            ("🧳", "Thêm 10kg ký gửi", "Miễn phí mang thêm hành lý ký gửi ngoài tiêu chuẩn vé thường."),
            ("🛋", "Phòng chờ thương gia", "Quyền sử dụng hệ thống phòng chờ cao cấp Bông Sen trước giờ bay."),
            ("🛡", "Ưu tiên làm thủ tục", "Check-in và ký gửi hành lý tại quầy phục vụ SkyPriority siêu tốc.")
        ]
        
        for i, p in enumerate(privileges):
            card = PrivilegeCard(p[0], p[1], p[2])
            grid.addWidget(card, i // 2, i % 2)
            
        lay.addLayout(grid)
        lay.addStretch()
        
        # BỔ SUNG: Thêm Footer đầy đủ từ Ảnh 1 vào đáy Ảnh 3 theo đúng yêu cầu
        main_lay.addWidget(get_footer())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = QWidget()
    w.resize(1000, 700)
    l = QVBoxLayout(w)
    l.setContentsMargins(0,0,0,0)
    p = CurrentMemberPage()
    l.addWidget(p)
    w.show()
    sys.exit(app.exec())