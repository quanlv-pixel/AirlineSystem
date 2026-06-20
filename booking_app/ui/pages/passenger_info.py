"""
passenger_info_page.py
----------------------
Passenger Information Page for the booking application.
Fixed: Safe initialization and dynamic update_page() method.
"""
from __future__ import annotations
import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QLineEdit, QComboBox, QSpinBox
)
from booking_app.ui.pages.booking_shared import (lbl, h_sep, card_style, red_btn, page_header,
                             NavBar, C_RED, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY,
                             C_GREEN, C_BLUE, C_ORANGE)

def _input(placeholder="", default=""):
    e = QLineEdit()
    e.setPlaceholderText(placeholder); e.setText(default); e.setFixedHeight(46)
    e.setStyleSheet(f"""
        QLineEdit {{ background:{C_LGRAY}; border:1.5px solid {C_BORDER}; border-radius:12px; font-size:13px; color:{C_TEXT}; padding:0 16px; }}
        QLineEdit:focus {{ border-color:{C_RED}; background:{C_WHITE}; }}
        QLineEdit::placeholder {{ color:{C_GRAY}; }}
    """)
    return e

def _combo(items: list[str]):
    c = QComboBox(); c.addItems(items); c.setFixedHeight(46)
    c.setStyleSheet(f"""
        QComboBox {{ background:{C_LGRAY}; border:1.5px solid {C_BORDER}; border-radius:12px; font-size:13px; color:{C_TEXT}; padding:0 16px; }}
        QComboBox:focus {{ border-color:{C_RED}; }}
        QComboBox::drop-down {{ border:none; width:30px; }}
        QComboBox::down-arrow {{ image:none; width:0; height:0; border-left:5px solid transparent; border-right:5px solid transparent; border-top:6px solid {C_GRAY}; }}
        QComboBox QAbstractItemView {{ background:{C_WHITE}; border:1px solid {C_BORDER}; border-radius:8px; selection-background-color:#FFEBEE; selection-color:{C_RED}; font-size:13px; }}
    """)
    return c

def _field_label(text):
    return lbl(text, 11, 600, C_GRAY, 0.5)

class SectionCard(QWidget):
    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(16))
        self._root = QVBoxLayout(self); self._root.setContentsMargins(24, 22, 24, 24); self._root.setSpacing(0)
        hdr = QHBoxLayout(); hdr.setSpacing(12)
        icon_lbl = lbl(icon, 18, 400, C_RED); icon_lbl.setFixedWidth(24); hdr.addWidget(icon_lbl)
        hdr.addWidget(lbl(title, 12, 700, C_TEXT, 1.2)); hdr.addStretch()
        self._root.addLayout(hdr); self._root.addSpacing(20); self._root.addWidget(h_sep()); self._root.addSpacing(20)

class BookingSummaryCard(QWidget):
    proceed = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(20))
        root = QVBoxLayout(self); root.setContentsMargins(24, 24, 24, 24); root.setSpacing(0)
        root.addWidget(lbl("Tóm tắt đặt vé", 18, 800, C_TEXT)); root.addSpacing(20)
        ft_row = QHBoxLayout(); ft_row.setSpacing(14)
        globe_badge = QLabel("🌐"); globe_badge.setFixedSize(44, 44); globe_badge.setAlignment(Qt.AlignCenter)
        globe_badge.setStyleSheet(f"background:{C_LGRAY}; border-radius:22px; font-size:20px;")
        ft_info = QVBoxLayout(); ft_info.setSpacing(3); ft_info.addWidget(lbl("LOẠI CHUYẾN BAY", 10, 600, C_GRAY, 1.0))
        self.flight_type_lbl = lbl("QUỐC NỘI (DOMESTIC)", 13, 700, C_TEXT)
        ft_info.addWidget(self.flight_type_lbl)
        ft_row.addWidget(globe_badge); ft_row.addLayout(ft_info); ft_row.addStretch(); root.addLayout(ft_row)
        root.addSpacing(18); root.addWidget(h_sep()); root.addSpacing(16)
        def _status_row(key, val, val_color=C_TEXT):
            r = QHBoxLayout(); r.addWidget(lbl(key, 12, 500, C_GRAY)); r.addStretch(); r.addWidget(lbl(val, 12, 700, val_color)); return r
        root.addLayout(_status_row("Trạng thái ghế", "ĐANG CHỜ CHỌN", C_ORANGE)); root.addSpacing(12)
        root.addLayout(_status_row("Hành lý dự kiến", "7KG XÁCH TAY", C_TEXT)); root.addSpacing(16)
        root.addWidget(h_sep()); root.addSpacing(16)
        # ── Ticket quantity selector ──────────────────────────────────────────
        qty_lbl = lbl("SỐ LƯỢNG VÉ", 11, 600, C_GRAY, 0.5)
        root.addWidget(qty_lbl); root.addSpacing(8)
        self._qty_spin = QSpinBox()
        self._qty_spin.setRange(1, 6)
        self._qty_spin.setValue(1)
        self._qty_spin.setFixedHeight(46)
        self._qty_spin.setStyleSheet(f"""
            QSpinBox {{
                background:{C_LGRAY}; border:1.5px solid {C_BORDER}; border-radius:12px;
                font-size:14px; font-weight:700; color:{C_TEXT}; padding:0 16px;
            }}
            QSpinBox:focus {{ border-color:{C_RED}; background:{C_WHITE}; }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width:32px; border:none; border-radius:8px;
                background:{C_LGRAY};
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background:#FFCDD2;
            }}
            QSpinBox::up-arrow {{
                border-left:5px solid transparent; border-right:5px solid transparent;
                border-bottom:6px solid {C_GRAY}; width:0; height:0;
            }}
            QSpinBox::down-arrow {{
                border-left:5px solid transparent; border-right:5px solid transparent;
                border-top:6px solid {C_GRAY}; width:0; height:0;
            }}
        """)
        root.addWidget(self._qty_spin); root.addSpacing(20)
        # ─────────────────────────────────────────────────────────────────────
        self.err_lbl = QLabel(""); self.err_lbl.setAlignment(Qt.AlignCenter)
        self.err_lbl.setStyleSheet(f"color: {C_RED}; font-size: 12px; font-weight: bold;"); root.addWidget(self.err_lbl)
        root.addSpacing(10); btn = red_btn("TIẾP TỤC CHỌN GHẾ  →", 52); btn.clicked.connect(self.proceed); root.addWidget(btn); root.addStretch()

    def ticket_count(self) -> int:
        """Return the currently selected ticket quantity."""
        return self._qty_spin.value()

class PassengerInfoPage(QWidget):
    proceed = Signal(dict)
    go_back = Signal()

    def __init__(self, ctx: dict | None = None, parent=None):
        super().__init__(parent)
        self.ctx = ctx or {}
        self.setStyleSheet(f"background:{C_BG};")
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent;border:none;"); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.addWidget(scroll)
        inner = QWidget(); inner.setStyleSheet(f"background:{C_BG};"); scroll.setWidget(inner)
        root = QVBoxLayout(inner); root.setContentsMargins(28, 24, 28, 28); root.setSpacing(20)
        root.addLayout(page_header("Thông tin Hành khách", "Bước 3: Cung cấp thông tin giấy tờ đi lại", on_back=self.go_back))
        cols = QHBoxLayout(); cols.setSpacing(20)
        left = QVBoxLayout(); left.setSpacing(16)
        self._card1 = SectionCard("◎", "THÔNG TIN CÁ NHÂN")
        name_col = QVBoxLayout(); name_col.setSpacing(6); name_col.addWidget(_field_label("HỌ VÀ TÊN (NHƯ HỘ CHIẾU)"))
        self._name = _input("Ví dụ: NGUYEN VAN A"); name_col.addWidget(self._name); self._card1._root.addLayout(name_col); self._card1._root.addSpacing(14)
        dob_col = QVBoxLayout(); dob_col.setSpacing(6); dob_col.addWidget(_field_label("NGÀY SINH")); self._dob = _input("DD/MM/YYYY"); dob_col.addWidget(self._dob)
        gender_col = QVBoxLayout(); gender_col.setSpacing(6); gender_col.addWidget(_field_label("GIỚI TÍNH")); self._gender = _combo(["Nam", "Nữ", "Khác"]); gender_col.addWidget(self._gender)
        row1 = QHBoxLayout(); row1.setSpacing(16); row1.addLayout(dob_col); row1.addLayout(gender_col); self._card1._root.addLayout(row1); self._card1._root.addSpacing(14)
        nat_col = QVBoxLayout(); nat_col.setSpacing(6); nat_col.addWidget(_field_label("QUỐC TỊCH")); self._nationality = _input("Việt Nam", "Việt Nam"); nat_col.addWidget(self._nationality)
        pass_col = QVBoxLayout(); pass_col.setSpacing(6); pass_col.addWidget(_field_label("CCCD / HỘ CHIẾU")); self._passport = _input("Nhập số CCCD/Hộ chiếu"); pass_col.addWidget(self._passport)
        row_nat_pass = QHBoxLayout(); row_nat_pass.setSpacing(16); row_nat_pass.addLayout(nat_col); row_nat_pass.addLayout(pass_col); self._card1._root.addLayout(row_nat_pass)
        left.addWidget(self._card1)
        self._card2 = SectionCard("📋", "THÔNG TIN LIÊN HỆ")
        email_col = QVBoxLayout(); email_col.setSpacing(6); email_col.addWidget(_field_label("ĐỊA CHỈ EMAIL")); self._email = _input("example@email.com"); email_col.addWidget(self._email)
        phone_col = QVBoxLayout(); phone_col.setSpacing(6); phone_col.addWidget(_field_label("SỐ ĐIỆN THOẠI")); self._phone = _input("+84 9xx xxx xxx"); phone_col.addWidget(self._phone)
        row2 = QHBoxLayout(); row2.setSpacing(16); row2.addLayout(email_col); row2.addLayout(phone_col); self._card2._root.addLayout(row2); left.addWidget(self._card2)
        left.addStretch(); left_w = QWidget(); left_w.setStyleSheet("background:transparent;"); left_w.setLayout(left); cols.addWidget(left_w, 63)
        self._summary = BookingSummaryCard(); self._summary.proceed.connect(self._on_proceed)
        right_w = QWidget(); right_w.setStyleSheet("background:transparent;"); rl = QVBoxLayout(right_w); rl.setContentsMargins(0,0,0,0); rl.addWidget(self._summary); rl.addStretch(); cols.addWidget(right_w, 37)
        root.addLayout(cols)

    def update_page(self, ctx: dict | None = None):
        if ctx: self.ctx = ctx
        account = self.ctx.get("account", {})
        if account:
            if not self._name.text(): self._name.setText(account.get("full_name", "").upper())
            if not self._email.text(): self._email.setText(account.get("email", ""))

        # TỰ ĐỘNG NHẬN DIỆN QUỐC TẾ / QUỐC NỘI
        flight = self.ctx.get("flight", {})
        dep = flight.get("dep", "").upper()
        dst = flight.get("dst", "").upper()
        
        # Danh sách mã sân bay tại Việt Nam
        vn_airports = {"SGN", "HAN", "DAD", "PQC", "CXR", "VCA", "HPH", "VDO", "UIH", "VII", "BMV", "VKG", "DLI", "TBB", "THD", "PXU", "VDH", "VCL", "VCS", "CAH"}
        
        if dep and dst and (dep not in vn_airports or dst not in vn_airports):
            # ĐÃ FIX: Thêm self._summary. vào phía trước
            self._summary.flight_type_lbl.setText("QUỐC TẾ (INTERNATIONAL)")
            self._summary.flight_type_lbl.setStyleSheet(f"font-size:13px; font-weight:800; color:{C_BLUE};") 
        else:
            self._summary.flight_type_lbl.setText("QUỐC NỘI (DOMESTIC)")
            self._summary.flight_type_lbl.setStyleSheet(f"font-size:13px; font-weight:700; color:{C_TEXT};")

    def _on_proceed(self):
        name = self._name.text().strip(); passport = self._passport.text().strip(); phone = self._phone.text().strip()
        if not name or not passport or not phone: self._summary.err_lbl.setText("Vui lòng điền đủ Tên, CCCD và SĐT!"); return
        self._summary.err_lbl.setText("")
        pax = dict(name=name, dob=self._dob.text() or "DD/MM/YYYY", gender=self._gender.currentText(), nationality=self._nationality.text() or "Việt Nam", passport=passport, email=self._email.text(), phone=phone)
        self.ctx["passenger"] = pax
        self.ctx["ticket_count"] = self._summary.ticket_count()
        self.proceed.emit(self.ctx)

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    win = QMainWindow(); win.resize(1380, 860)
    w = QWidget(); lay = QVBoxLayout(w); lay.addWidget(NavBar(0)); lay.addWidget(PassengerInfoPage())
    win.setCentralWidget(w); win.show(); sys.exit(app.exec())
