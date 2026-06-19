"""
promotion.py
------------
Giao diện Chương trình Khuyến Mãi & Ưu Đãi Đặc Quyền
Updated: tier-aware promo codes visible only to activated members of matching tier.
"""
import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QFrame, QGridLayout
)
from booking_app.ui.pages.booking_shared import (lbl, card_style, C_RED, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY, C_ORANGE, C_GREEN)
from shared.services.member_service import TIER_PROMOS


class PromoCard(QWidget):
    def __init__(self, title: str, code: str, desc: str, exp: str,
                 exclusive: bool = False, parent=None):
        super().__init__(parent)
        
        # 1. FIX LỖI: Lưu lại mã code để dùng ở hàm copy_to_clipboard
        self.code = code 
        
        border_color = C_ORANGE if exclusive else C_BORDER
        bg_color     = "#FFFBF0" if exclusive else C_WHITE
        self.setStyleSheet(f"""
            QWidget {{
                background: {bg_color};
                border-radius: 14px;
                border: 1.5px solid {border_color};
            }}
        """)
        self.setFixedHeight(148)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(6)

        tag_lay = QHBoxLayout()
        if exclusive:
            tag = lbl(" ★ ĐẶC QUYỀN ", 9, 800, C_ORANGE)
            tag.setStyleSheet("background:#FFF3CD; border-radius:4px; padding:2px 6px; border:none;")
        else:
            tag = lbl(" CODE ƯU ĐÃI ", 9, 800, C_RED)
            tag.setStyleSheet("background:#FFEBEE; border-radius:4px; padding:2px 4px; border:none;")
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
        
        # 2. FIX LỖI: Phải khởi tạo QPushButton trước khi kết nối sự kiện (connect)
        self.copy_btn = QPushButton("Sao chép") 
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{ background:{C_LGRAY}; border:none; border-radius:6px;
                           padding:5px 12px; font-size:11px; font-weight:700; color:{C_MID}; }}
            QPushButton:hover {{ background:{C_BORDER}; color:{C_DARK}; }}
        """)
        btn_lay.addWidget(self.copy_btn)
        lay.addLayout(btn_lay)

    def copy_to_clipboard(self):
        # Lưu mã vào bộ nhớ đệm (Clipboard)
        QApplication.clipboard().setText(self.code)
        
        # Đổi chữ và màu để báo hiệu thành công
        self.copy_btn.setText("ĐÃ CHÉP")
        self.copy_btn.setStyleSheet("""
            QPushButton { 
                background: #22C55E; /* Đổi sang màu xanh lá */
                color: white; 
                border: none;
                border-radius: 6px; 
                font-size: 11px; 
                font-weight: bold; 
            }
        """)


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

    def __init__(self, tier: str | None = None, parent=None):
        """
        tier: current user's tier string or None if not activated.
              When set, tier-exclusive promos for that tier are shown.
        """
        super().__init__(parent)
        self._tier = tier
        self._build_ui()

    def set_tier(self, tier: str | None):
        """Refresh UI with a new tier (called when BookingWindow updates ctx)."""
        self._tier = tier
        # Clear and rebuild
        old_layout = self.layout()
        if old_layout:
            QWidget().setLayout(old_layout)
        self._build_ui()

    def _build_ui(self):
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

        lay.addWidget(lbl("Khuyến mãi & Ưu đãi đặc quyền", 24, 800, C_DARK))
        lay.addWidget(lbl("Khám phá các mã giảm giá hành trình và đặc quyền hội viên bay", 13, 400, C_GRAY))

        # Banner: only show activation CTA if NOT yet activated
        if not self._tier:
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
        else:
            # Activated: show tier status banner instead
            tier_colors = {
                "BẠCH KIM": ("#1A1A2E", "#D4AF37"),
                "HẠNG VÀNG": ("#AA7C11", "#FFF8DC"),
                "HẠNG BẠC":  ("#4A5568", "#E2E8F0"),
                "THÀNH VIÊN":("#1A6B3A", "#D1FAE5"),
            }
            bg, fg = tier_colors.get(self._tier, ("#2A2A42", C_WHITE))
            status_banner = QWidget()
            status_banner.setStyleSheet(f"background:{bg}; border-radius:14px;")
            status_banner.setFixedHeight(80)
            sb_lay = QHBoxLayout(status_banner)
            sb_lay.setContentsMargins(25, 15, 25, 15)
            sb_lay.addWidget(lbl(f"✓  Hội viên đang hoạt động — Hạng {self._tier}", 14, 800, fg))
            sb_lay.addStretch()
            sb_lay.addWidget(lbl("Các mã đặc quyền của bạn đã được mở khoá ↓", 12, 500, fg))
            lay.addWidget(status_banner)

        # ── Public promo codes (visible to everyone) ──────────────────────────
        lay.addWidget(lbl("Mã giảm giá đang diễn ra", 16, 700, C_DARK))
        grid = QGridLayout()
        grid.setSpacing(16)

        promos = [
            ("Ưu đãi Chặng Nội Địa",    "JETJET20",   "Giảm ngay 20% giá vé cơ bản cho toàn bộ chặng bay nội địa.",               "31/12/2026"),
            ("Chào Bạn Mới Đăng Ký",    "HELLOFIRST", "Tặng $15 trực tiếp vào hóa đơn cho giao dịch đặt vé đầu tiên.",              "15/08/2026"),
            ("Bay Khứ Hồi Thuận Tiện",  "ROUNDTRIP10","Giảm 10% tổng giá trị khi đặt hành trình khứ hồi.",                          "20/10/2026"),
            ("Cuối Tuần Vi Vu",          "WEEKEND5",   "Ưu đãi giảm giá đặc biệt khi khởi hành vào Thứ 7 hoặc Chủ Nhật.",           "01/07/2026"),
        ]

        for i, p in enumerate(promos):
            card = PromoCard(p[0], p[1], p[2], p[3])
            grid.addWidget(card, i // 2, i % 2)

        lay.addLayout(grid)

        # ── Tier-exclusive codes (only if activated) ──────────────────────────
        tier_promos = TIER_PROMOS.get(self._tier, []) if self._tier else []
        if tier_promos:
            lay.addSpacing(8)
            lay.addWidget(lbl(f"Ưu đãi độc quyền — {self._tier}", 16, 700, C_DARK))
            excl_grid = QGridLayout()
            excl_grid.setSpacing(16)
            for i, tp in enumerate(tier_promos):
                card = PromoCard(tp["label"], tp["code"], tp["desc"], tp["exp"], exclusive=True)
                excl_grid.addWidget(card, i // 2, i % 2)
            lay.addLayout(excl_grid)

        lay.addStretch()

        # Footer
        main_lay.addWidget(get_footer())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = QWidget()
    w.resize(1000, 700)
    l = QVBoxLayout(w)
    l.setContentsMargins(0, 0, 0, 0)
    p = PromotionPage(tier="HẠNG VÀNG")
    l.addWidget(p)
    w.show()
    sys.exit(app.exec())