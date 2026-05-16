"""
promotion.py
------------
Giao diện Chương trình Khuyến Mãi & Ưu Đãi Đặc Quyền
"""
import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QGridLayout
)
from booking_app.ui.pages.booking_shared import (lbl, card_style, C_RED, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY, C_ORANGE)

class PromoCard(QWidget):
    def __init__(self, title: str, code: str, desc: str, exp: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(14))
        self.setFixedHeight(140)
        
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(6)
        
        tag_lay = QHBoxLayout()
        tag = lbl(" CODE ƯU ĐÃI ", 9, 800, C_RED)
        tag.setStyleSheet(f"background:#FFEBEE; border-radius:4px; padding:2px 4px;")
        tag_lay.addWidget(tag)
        tag_lay.addStretch()
        tag_lay.addWidget(lbl(f"Hạn: {exp}", 11, 400, C_GRAY))
        lay.addLayout(tag_lay)
        
        lay.addWidget(lbl(title, 15, 700, C_TEXT))
        lay.addWidget(lbl(desc, 12, 400, C_MID))
        lay.addStretch()
        
        btn_lay = QHBoxLayout()
        btn_lay.addWidget(lbl(f"Mã: {code}", 13, 800, C_DARK))
        btn_lay.addStretch()
        copy_btn = QPushButton("Sao chép")
        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.setStyleSheet(f"""
            QPushButton {{ background:{C_LGRAY}; border:none; border-radius:6px; 
                           padding:5px 12px; font-size:11px; font-weight:700; color:{C_MID}; }}
            QPushButton:hover {{ background:{C_BORDER}; color:{C_DARK}; }}
        """)
        btn_lay.addWidget(copy_btn)
        lay.addLayout(btn_lay)

def get_footer() -> QWidget:
    """Hàm tạo Footer dùng chung đồng bộ cho các trang"""
    footer = QWidget()
    footer.setStyleSheet(f"background: {C_DARK}; border-top: 1px solid {C_BORDER};")
    footer.setFixedHeight(70)
    lay = QHBoxLayout(footer)
    lay.setContentsMargins(30, 0, 30, 0)
    
    lay.addWidget(lbl("© 2026 JetJet Air. All rights reserved.", 12, 400, C_GRAY))
    lay.addStretch()
    
    info_lay = QHBoxLayout()
    info_lay.setSpacing(20)
    info_lay.addWidget(lbl("📞 Hotline: 1900 6539", 12, 500, C_WHITE))
    info_lay.addWidget(lbl("🌐 jetjetair.com", 12, 500, C_WHITE))
    lay.addLayout(info_lay)
    return footer

class PromotionPage(QWidget):
    activate_member_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background:{C_BG}; border:none;")
        main_lay.addWidget(scroll, 1)
        
        content = QWidget()
        content.setStyleSheet(f"background:{C_BG};")
        scroll.setWidget(content)
        
        lay = QVBoxLayout(content)
        lay.setContentsMargins(30, 24, 30, 30)
        lay.setSpacing(20)
        
        # Header (Đã lược bỏ Thoát Portal)
        lay.addWidget(lbl("Khuyến mãi & Ưu đãi đặc quyền", 24, 800, C_DARK))
        lay.addWidget(lbl("Khám phá các mã giảm giá hành trình và đặc quyền hội viên bay", 13, 400, C_GRAY))
        
        # Banner Kích hoạt hội viên VIP
        member_banner = QWidget()
        member_banner.setStyleSheet(f"background:qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2A2A42, stop:1 {C_DARK}); border-radius:14px;")
        member_banner.setFixedHeight(120)
        mb_lay = QHBoxLayout(member_banner)
        mb_lay.setContentsMargins(25, 20, 25, 20)
        
        txt_col = QVBoxLayout()
        txt_col.addWidget(lbl("CHƯƠNG TRÌNH HỘI VIÊN JETJET ELITE CLUB", 12, 800, C_ORANGE))
        txt_col.addWidget(lbl("Kích hoạt thẻ hội viên ngay hôm nay để nhận x2 dặm thưởng và phòng chờ hạng thương gia.", 14, 400, C_WHITE))
        mb_lay.addLayout(txt_col, 1)
        
        self.join_btn = QPushButton("Kích hoạt hội viên")
        self.join_btn.setCursor(Qt.PointingHandCursor)
        self.join_btn.setFixedSize(160, 42)
        self.join_btn.setStyleSheet(f"""
            QPushButton {{ background:{C_RED}; color:{C_WHITE}; border:none; border-radius:8px; font-size:13px; font-weight:700; }}
            QPushButton:hover {{ background:{C_RED}; }}
        """)
        self.join_btn.clicked.connect(self.activate_member_clicked.emit)
        mb_lay.addWidget(self.join_btn)
        lay.addWidget(member_banner)
        
        # Grid Khuyến mãi
        lay.addWidget(lbl("Mã giảm giá đang diễn ra", 16, 700, C_DARK))
        grid = QGridLayout()
        grid.setSpacing(16)
        
        promos = [
            ("Ưu đãi Chặng Nội Địa", "JETJET20", "Giảm ngay 20% giá vé cơ bản cho toàn bộ chặng bay nội địa.", "31/12/2026"),
            ("Chào Bạn Mới Đăng Ký", "HELLOFIRST", "Tặng $15 trực tiếp vào hóa đơn cho giao dịch đặt vé đầu tiên.", "15/08/2026"),
            ("Bay Khứ Hồi Thuận Tiện", "ROUNDTRIP10", "Giảm 10% tổng giá trị khi đặt hành trình khứ hồi.", "20/10/2026"),
            ("Cuối Tuần Vi Vu", "WEEKEND5", "Ưu đãi giảm giá đặc biệt khi khởi hành vào Thứ 7 hoặc Chủ Nhật.", "01/07/2026")
        ]
        
        for i, p in enumerate(promos):
            card = PromoCard(p[0], p[1], p[2], p[3])
            grid.addWidget(card, i // 2, i % 2)
            
        lay.addLayout(grid)
        lay.addStretch()
        
        # Thêm Footer vào đáy trang
        main_lay.addWidget(get_footer())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = QWidget()
    w.resize(1000, 700)
    l = QVBoxLayout(w)
    l.setContentsMargins(0,0,0,0)
    p = PromotionPage()
    l.addWidget(p)
    w.show()
    sys.exit(app.exec())