"""
cur_mem.py
----------
Giao diện Trạng Thái Hội Viên Hiện Tại (Sau khi kích hoạt)
Fixed: QLayout re-assignment crash removed.
       update_member() now clears and repopulates a SINGLE permanent
       scroll widget rather than re-creating QVBoxLayout(self).
"""
import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QProgressBar, QGridLayout, QScrollArea, QFrame
)
from booking_app.ui.pages.booking_shared import (lbl, card_style, C_RED, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY, C_GREEN, C_ORANGE)
from booking_app.ui.promotion import get_footer
from shared.services.member_service import get_tier_for_spending, get_user_spending_from_db

# ── Tier metadata ─────────────────────────────────────────────────────────────
_TIER_META = {
    "BẠCH KIM": {
        "gradient": "qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1A1A2E,stop:1 #2D2D5E)",
        "label":    "BẠCH KIM • PLATINUM MEMBER",
        "next":     None,
        "next_amt": 0,
        "privileges": [
            ("✈", "Tích lũy dặm x2.0",   "Nhân đôi hoàn toàn số dặm thưởng trên mọi hành trình."),
            ("🧳", "Thêm 23kg ký gửi",    "Mang thêm hành lý ký gửi toàn phần ngoài tiêu chuẩn vé."),
            ("🛋", "Phòng chờ VIP",        "Sử dụng không giới hạn lounge cao cấp trên toàn cầu."),
            ("🛡", "Ưu tiên tuyệt đối",    "Check-in, boarding và hành lý ưu tiên số 1 mọi sân bay."),
        ],
    },
    "HẠNG VÀNG": {
        "gradient": "qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #D4AF37,stop:1 #AA7C11)",
        "label":    "HẠNG VÀNG • GOLD MEMBER",
        "next":     "BẠCH KIM",
        "next_amt": 3000,
        "privileges": [
            ("✈", "Tích lũy dặm x1.5",  "Nhận thêm 50% số dặm thưởng trên mỗi chuyến bay thực tế."),
            ("🧳", "Thêm 10kg ký gửi",  "Miễn phí mang thêm hành lý ký gửi ngoài tiêu chuẩn vé thường."),
            ("🛋", "Phòng chờ thương gia","Quyền sử dụng hệ thống phòng chờ cao cấp Bông Sen trước giờ bay."),
            ("🛡", "Ưu tiên làm thủ tục", "Check-in và ký gửi hành lý tại quầy SkyPriority siêu tốc."),
        ],
    },
    "HẠNG BẠC": {
        "gradient": "qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #8E9EAB,stop:1 #5C6B77)",
        "label":    "HẠNG BẠC • SILVER MEMBER",
        "next":     "HẠNG VÀNG",
        "next_amt": 1500,
        "privileges": [
            ("✈", "Tích lũy dặm x1.25", "Nhận thêm 25% số dặm thưởng so với hội viên thường."),
            ("🧳", "Thêm 5kg ký gửi",   "Miễn phí thêm 5kg hành lý ký gửi trên chặng nội địa."),
            ("🛋", "Ưu tiên chọn ghế",  "Chọn ghế ưu tiên trước (hàng thoát hiểm, ghế đầu)."),
            ("🛡", "Hỗ trợ 24/7",       "Đường dây hỗ trợ hội viên riêng, ưu tiên xử lý nhanh."),
        ],
    },
    "THÀNH VIÊN": {
        "gradient": "qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #1A6B3A,stop:1 #145230)",
        "label":    "THÀNH VIÊN • ELITE MEMBER",
        "next":     "HẠNG BẠC",
        "next_amt": 500,
        "privileges": [
            ("✈", "Tích lũy dặm x1.0",   "Bắt đầu hành trình tích lũy dặm bay thưởng của bạn."),
            ("🎁", "Quà tặng sinh nhật",  "Nhận voucher ưu đãi đặc biệt vào ngày sinh nhật mỗi năm."),
            ("📧", "Bản tin ưu đãi",      "Nhận thông báo sớm nhất về flash sale và mã giảm giá độc quyền."),
            ("🛡", "Hỗ trợ thành viên",   "Hỗ trợ đặt vé và giải đáp thắc mắc qua kênh thành viên."),
        ],
    },
}


def _clear_layout(layout):
    """Recursively remove and schedule-delete all items from a layout."""
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w:
            w.setParent(None)
            w.deleteLater()
        elif item.layout():
            _clear_layout(item.layout())


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
    """
    Safe re-usable member page.
    Layout structure (created ONCE in __init__, never recreated):

        QVBoxLayout(self)  ← self._outer
          ├─ QScrollArea
          │    └─ QWidget (self._body)
          │         └─ QVBoxLayout (self._body_lay)  ← populated/cleared each refresh
          └─ footer widget
    """

    def __init__(self, account: dict | None = None, parent=None):
        super().__init__(parent)
        self._account = account or {}

        # ── Permanent outer layout (created exactly once) ─────────────────────
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(0, 0, 0, 0)
        self._outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background:{C_BG}; border:none;")
        self._outer.addWidget(scroll, 1)

        self._body = QWidget()
        self._body.setStyleSheet(f"background:{C_BG};")
        scroll.setWidget(self._body)

        # Permanent inner layout — we clear/repopulate this, never replace it
        self._body_lay = QVBoxLayout(self._body)
        self._body_lay.setContentsMargins(30, 24, 30, 30)
        self._body_lay.setSpacing(20)

        # Footer slot — inserted once, stays at the bottom
        self._footer = get_footer()
        self._outer.addWidget(self._footer)

        # Initial population
        self._populate()

    # ─────────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────────
    def update_member(self, account: dict):
        """
        Safe refresh: clears and repopulates self._body_lay only.
        Never touches self._outer or creates a new top-level layout.
        """
        self._account = account
        self._populate()

    # ─────────────────────────────────────────────────────────────────────────
    # Internal population (no layout creation — only content)
    # ─────────────────────────────────────────────────────────────────────────
    def _populate(self):
        # 1. Clear all content from the body layout safely
        _clear_layout(self._body_lay)

        username = self._account.get("username", "")
        name     = self._account.get("name") or self._account.get("full_name") or "Hội Viên"

        # 2. Compute tier dynamically from DB spending
        spending = get_user_spending_from_db(username) if username else 0.0
        tier     = get_tier_for_spending(spending)
        meta     = _TIER_META.get(tier, _TIER_META["THÀNH VIÊN"])

        # ── Page title ────────────────────────────────────────────────────────
        self._body_lay.addWidget(lbl("Thành viên JetJet Elite", 24, 800, C_DARK))
        self._body_lay.addWidget(lbl(
            "Chào mừng trở lại! Xem thông tin phân hạng và ưu đãi dặm bay tích lũy của bạn.",
            13, 400, C_GRAY
        ))

        # ── Tier card ─────────────────────────────────────────────────────────
        tier_card = QWidget()
        tier_card.setStyleSheet(f"background:{meta['gradient']}; border-radius:14px;")
        tier_card.setFixedHeight(150)
        tc_lay = QVBoxLayout(tier_card)
        tc_lay.setContentsMargins(25, 20, 25, 20)

        top_row = QHBoxLayout()
        top_row.addWidget(lbl(meta["label"], 14, 800, C_WHITE))
        top_row.addStretch()
        top_row.addWidget(lbl(f"Chi tiêu: ${spending:,.0f}", 12, 500, C_WHITE))
        tc_lay.addLayout(top_row)
        tc_lay.addStretch()

        tc_lay.addWidget(lbl(name.upper(), 20, 800, C_WHITE))
        tc_lay.addSpacing(5)

        # Progress bar to next tier
        if meta["next"] and meta["next_amt"] > 0:
            bar_max = meta["next_amt"]
            bar_val = min(int(spending), bar_max)
            prog_lay = QHBoxLayout()
            pbar = QProgressBar()
            pbar.setRange(0, bar_max)
            pbar.setValue(bar_val)
            pbar.setTextVisible(False)
            pbar.setFixedHeight(8)
            pbar.setStyleSheet(
                "QProgressBar{background:rgba(255,255,255,0.3);border:none;border-radius:4px;}"
                f"QProgressBar::chunk{{background:{C_WHITE};border-radius:4px;}}"
            )
            prog_lay.addWidget(pbar, 1)
            remaining = max(0, meta["next_amt"] - spending)
            prog_lay.addWidget(lbl(f"${remaining:,.0f} đến {meta['next']}", 11, 700, C_WHITE))
            tc_lay.addLayout(prog_lay)
        else:
            tc_lay.addWidget(lbl("Bạn đang ở hạng cao nhất! ✨", 12, 600, C_WHITE))

        self._body_lay.addWidget(tier_card)

        # ── Privileges ────────────────────────────────────────────────────────
        self._body_lay.addWidget(lbl(f"Đặc quyền {tier} của bạn", 16, 700, C_DARK))
        grid = QGridLayout()
        grid.setSpacing(14)

        for i, (icon, title, desc) in enumerate(meta["privileges"]):
            card = PrivilegeCard(icon, title, desc)
            grid.addWidget(card, i // 2, i % 2)

        self._body_lay.addLayout(grid)
        self._body_lay.addStretch()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    w = QWidget()
    w.resize(1000, 700)
    l = QVBoxLayout(w)
    l.setContentsMargins(0, 0, 0, 0)
    p = CurrentMemberPage(account={"username": "quanlv", "name": "Lê Văn Quân"})
    l.addWidget(p)
    w.show()
    sys.exit(app.exec())