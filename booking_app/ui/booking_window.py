"""
booking_window.py
-----------------
Giao diện chính Booking App — JetJet Air
Hiển thị sau khi đăng nhập thành công.
Chạy độc lập: python booking_window.py
"""
from __future__ import annotations
import hashlib, random, string, sys
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import (
    QColor, QFont, QPainter, QBrush, QPen,
    QPainterPath, QLinearGradient
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
    QLineEdit, QComboBox, QDateEdit, QStackedWidget,
    QGraphicsDropShadowEffect, QDialog, QMessageBox
)
from booking_app.ui.promotion import PromotionPage
from booking_app.ui.cur_mem import CurrentMemberPage
from booking_app.ui.members import MembersPage
from booking_app.ui.history import HistoryPage

# ─────────────────────────────────────────────────────────────────────────────
# Màu sắc
# ─────────────────────────────────────────────────────────────────────────────
C_RED     = "#E53935"
C_RED2    = "#C62828"
C_REDL    = "#FF5252"
C_DARK    = "#1A1A2E"
C_WHITE   = "#FFFFFF"
C_BG      = "#FAFBFF"
C_BORDER  = "#E8EAF0"
C_TEXT    = "#1A1A2E"
C_MID     = "#4A4A6A"
C_GRAY    = "#9B9BB4"
C_LGRAY   = "#F2F3F7"

# ─────────────────────────────────────────────────────────────────────────────
# Sân bay & dữ liệu mẫu
# ─────────────────────────────────────────────────────────────────────────────
AIRPORTS = [
    ("SGN", "TP. Hồ Chí Minh"),
    ("HAN", "Hà Nội"),
    ("DAD", "Đà Nẵng"),
    ("PQC", "Phú Quốc"),
    ("ICN", "Seoul"),
    ("NRT", "Tokyo"),
]

SAMPLE_FLIGHTS: list[dict] = [
    dict(fid=1, code="JJ101", aircraft="AIRBUS A321NEO",
         dep="SGN", dst="HAN", dep_t="08:00", arr_t="10:15",
         dur="2H 15M", direct=True, seats=42, price=120),
    dict(fid=2, code="JJ205", aircraft="BOEING 787-9",
         dep="SGN", dst="HAN", dep_t="12:30", arr_t="14:45",
         dur="2H 15M", direct=True, seats=18, price=185),
    dict(fid=3, code="JJ309", aircraft="AIRBUS A320",
         dep="SGN", dst="HAN", dep_t="18:00", arr_t="20:20",
         dur="2H 20M", direct=True, seats=5,  price=95),
    dict(fid=4, code="JJ420", aircraft="BOEING 737 MAX",
         dep="HAN", dst="DAD", dep_t="07:30", arr_t="08:45",
         dur="1H 15M", direct=True, seats=55, price=75),
    dict(fid=5, code="JJ512", aircraft="AIRBUS A321",
         dep="SGN", dst="PQC", dep_t="10:00", arr_t="11:10",
         dur="1H 10M", direct=True, seats=28, price=65),
    dict(fid=6, code="JJ601", aircraft="BOEING 787-9",
         dep="HAN", dst="ICN", dep_t="22:00", arr_t="05:15+1",
         dur="4H 15M", direct=True, seats=12, price=420),
]

_session_history: list[dict] = []


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _lbl(text: str, size: int = 13, weight: int = 400,
         color: str = C_TEXT, spacing: float = 0.0) -> QLabel:
    w = {400: "normal", 500: "500", 600: "600",
         700: "bold", 800: "800", 900: "900"}.get(weight, "normal")
    sp = f"letter-spacing:{spacing}px;" if spacing else ""
    l = QLabel(text)
    l.setStyleSheet(f"font-size:{size}px; font-weight:{w}; color:{color};"
                    f" background:transparent; border:none; {sp}")
    return l


def _h_sep() -> QFrame:
    f = QFrame(); f.setFrameShape(QFrame.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background:{C_BORDER}; border:none;")
    return f


def _gen_pnr() -> str:
    return "JJ" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

import os

def get_db_path():

    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "..", "database", "airline.db")
    return os.path.abspath(path)

# ─────────────────────────────────────────────────────────────────────────────
# Logo badge (navbar size)
# ─────────────────────────────────────────────────────────────────────────────
class NavLogo(QWidget):
    def __init__(self, size: int = 36, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        r = w * 0.28
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor("#FF5252"))
        grad.setColorAt(1.0, QColor("#C62828"))
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, r, r)
        p.fillPath(path, QBrush(grad))
        p.setPen(QPen(QColor(C_WHITE), 1))
        f = QFont(); f.setPointSize(int(w * 0.38)); f.setWeight(QFont.Bold)
        p.setFont(f)
        p.drawText(0, 0, w, h, Qt.AlignCenter, "✈")


# ─────────────────────────────────────────────────────────────────────────────
# Airplane badge trong flight card (vòng tròn đỏ)
# ─────────────────────────────────────────────────────────────────────────────
class AirplaneBadge(QWidget):
    def __init__(self, size: int = 52, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor("#FF5252"))
        grad.setColorAt(1.0, QColor("#C62828"))
        path = QPainterPath()
        path.addEllipse(0, 0, w, h)
        p.fillPath(path, QBrush(grad))
        p.setPen(QPen(QColor(C_WHITE), 1))
        f = QFont(); f.setPointSize(int(w * 0.38)); f.setWeight(QFont.Bold)
        p.setFont(f)
        p.drawText(0, 0, w, h, Qt.AlignCenter, "✈")


# ─────────────────────────────────────────────────────────────────────────────
# Cột tìm kiếm  (label + input)
# ─────────────────────────────────────────────────────────────────────────────
def _input_style() -> str:
    return f"""
        background: {C_WHITE}; border: 1.5px solid {C_BORDER};
        border-radius: 10px; font-size: 13px; font-weight: 500;
        color: {C_TEXT}; padding: 0 12px;
    """

def _combo_style() -> str:
    return f"""
        QComboBox {{
            background: {C_WHITE}; border: 1.5px solid {C_BORDER};
            border-radius: 10px; font-size: 13px; font-weight: 500;
            color: {C_TEXT}; padding: 0 10px 0 36px;
            height: 44px;
        }}
        QComboBox:focus {{ border-color: {C_RED}; }}
        QComboBox::drop-down {{ border:none; width:24px; }}
        QComboBox::down-arrow {{
            image:none; width:0; height:0;
            border-left:4px solid transparent;
            border-right:4px solid transparent;
            border-top:5px solid {C_GRAY};
        }}
        QComboBox QAbstractItemView {{
            background:{C_WHITE}; border:1px solid {C_BORDER};
            border-radius:8px; padding:4px;
            selection-background-color:#FFEBEE;
            selection-color:{C_RED}; font-size:13px;
        }}
    """

class SearchField(QWidget):
    """Một cột trong form tìm kiếm: label + input widget."""

    def __init__(self, label: str, icon: str, widget: QWidget, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # Label
        lbl = _lbl(label, 11, 600, C_GRAY, 0.5)
        root.addWidget(lbl)

        # Input wrapper (icon + widget)
        wrap = QWidget()
        wrap.setFixedHeight(46)
        wrap.setStyleSheet("background:transparent;")
        wl = QHBoxLayout(wrap)
        wl.setContentsMargins(0, 0, 0, 0)
        wl.setSpacing(0)

        # Icon overlay (absolute-ish)
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedWidth(36)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size:16px; color:{C_GRAY};"
                               " background:transparent; border:none;")

        # Position icon over widget
        container = QWidget()
        container.setFixedHeight(46)
        container.setStyleSheet("background:transparent;")
        cl = QHBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        widget.setFixedHeight(46)
        cl.addWidget(widget)

        # Use a layered approach
        outer = QHBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(icon_lbl)
        outer.addWidget(widget, 1)

        wl.addLayout(outer)
        root.addWidget(wrap)


# ─────────────────────────────────────────────────────────────────────────────
# Search Panel  (5 cột + nút tìm kiếm)
# ─────────────────────────────────────────────────────────────────────────────
class SearchPanel(QWidget):
    searched = Signal(str, str, str)  # dep_code, dst_code, date_str

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            SearchPanel {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 20px;
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(18)

        # ── 5 cột tìm kiếm ──────────────────────────────────────────────────
        fields_row = QHBoxLayout()
        fields_row.setSpacing(16)

        # ĐIỂM ĐI
        self._dep = QComboBox()
        for code, city in AIRPORTS:
            self._dep.addItem(f"{code} ({city})", code)
        self._dep.setStyleSheet(_combo_style())
        fields_row.addWidget(SearchField("ĐIỂM ĐI", "📍", self._dep))

        # ĐIỂM ĐẾN
        self._dst = QComboBox()
        for code, city in AIRPORTS:
            self._dst.addItem(f"{code} ({city})", code)
        self._dst.setCurrentIndex(1)  # HAN mặc định
        self._dst.setStyleSheet(_combo_style())
        fields_row.addWidget(SearchField("ĐIỂM ĐẾN", "📍", self._dst))

        # NGÀY ĐI
        self._date = QDateEdit(QDate.currentDate())
        self._date.setCalendarPopup(True)
        self._date.setDisplayFormat("dd/MM/yyyy")
        self._date.setStyleSheet(f"""
            QDateEdit {{
                {_input_style()}
                padding-left: 36px;
                height: 46px;
            }}
            QDateEdit::drop-down {{ border:none; width:28px; }}
            QDateEdit::down-arrow {{
                image:none; width:0; height:0;
                border-left:4px solid transparent;
                border-right:4px solid transparent;
                border-top:5px solid {C_GRAY};
            }}
        """)
        fields_row.addWidget(SearchField("NGÀY ĐI", "📅", self._date))

        # HÀNH KHÁCH
        self._pax = QComboBox()
        for i in range(1, 7):
            self._pax.addItem(f"{i} người lớn", i)
        self._pax.setStyleSheet(_combo_style())
        fields_row.addWidget(SearchField("HÀNH KHÁCH", "◎", self._pax))

        # HẠNG GHẾ
        self._cls = QComboBox()
        self._cls.addItems(["Phổ thông", "Phổ thông đặc biệt",
                             "Thương gia", "Hạng nhất"])
        self._cls.setStyleSheet(_combo_style())
        fields_row.addWidget(SearchField("HẠNG GHẾ", "☰", self._cls))

        root.addLayout(fields_row)

        # ── Nút TÌM KIẾM ────────────────────────────────────────────────────
        btn = QPushButton("  🔍  TÌM KIẾM CHUYẾN BAY")
        btn.setFixedHeight(56)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C_RED}, stop:1 {C_REDL});
                border: none; border-radius: 28px;
                font-size: 15px; font-weight: 800;
                color: {C_WHITE}; letter-spacing: 1.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C_RED2}, stop:1 {C_RED});
            }}
            QPushButton:pressed {{ background: {C_RED2}; }}
        """)
        # Glow effect
        glow = QGraphicsDropShadowEffect(btn)
        glow.setBlurRadius(28); glow.setXOffset(0); glow.setYOffset(10)
        glow.setColor(QColor(229, 57, 53, 90))
        btn.setGraphicsEffect(glow)
        btn.clicked.connect(self._on_search)
        root.addWidget(btn)

    def _on_search(self):
        dep  = self._dep.currentData()
        dst  = self._dst.currentData()
        date = self._date.date().toString("dd/MM/yyyy")
        self.searched.emit(dep, dst, date)


# ─────────────────────────────────────────────────────────────────────────────
# Flight Card
# ─────────────────────────────────────────────────────────────────────────────
class FlightCard(QWidget):
    selected = Signal(dict)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data = data
        self.setFixedHeight(96)
        self.setStyleSheet(f"""
            FlightCard {{
                background: {C_WHITE}; border: 1px solid {C_BORDER};
                border-radius: 16px;
            }}
            FlightCard:hover {{
                border-color: #C5C6D8;
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)

        # ── Badge + tên chuyến bay ───────────────────────────────────────────
        badge_sec = QHBoxLayout()
        badge_sec.setSpacing(14)
        badge_sec.addWidget(AirplaneBadge(52))

        info_col = QVBoxLayout()
        info_col.setSpacing(4)
        info_col.setAlignment(Qt.AlignVCenter)
        info_col.addWidget(_lbl(data["code"],     14, 800, C_TEXT))
        info_col.addWidget(_lbl(data["aircraft"], 11, 400, C_GRAY))
        badge_sec.addLayout(info_col)

        badge_w = QWidget()
        badge_w.setFixedWidth(190)
        badge_w.setStyleSheet("background:transparent;")
        badge_w.setLayout(badge_sec)
        lay.addWidget(badge_w)

        # ── Giờ khởi hành ───────────────────────────────────────────────────
        dep_col = QVBoxLayout()
        dep_col.setSpacing(2)
        dep_col.setAlignment(Qt.AlignVCenter)
        dep_col.addWidget(_lbl(data["dep_t"], 26, 800, C_TEXT))
        dep_col.addWidget(_lbl(data["dep"],   12, 500, C_GRAY))
        dep_w = QWidget()
        dep_w.setFixedWidth(90)
        dep_w.setStyleSheet("background:transparent;")
        dep_w.setLayout(dep_col)
        lay.addWidget(dep_w)

        # ── Thời gian + trực tiếp ────────────────────────────────────────────
        mid_col = QVBoxLayout()
        mid_col.setSpacing(6)
        mid_col.setAlignment(Qt.AlignCenter)

        dur_lbl = _lbl(data["dur"], 11, 600, C_GRAY)
        dur_lbl.setAlignment(Qt.AlignCenter)

        direct_row = QHBoxLayout()
        direct_row.setSpacing(4)
        direct_row.setAlignment(Qt.AlignCenter)
        dot = _lbl("●", 10, 700, C_RED)
        direct_row.addWidget(dot)
        direct_row.addWidget(_lbl("TRỰC TIẾP", 10, 600, C_GRAY, 0.5))

        mid_col.addWidget(dur_lbl)
        mid_col.addLayout(direct_row)

        mid_w = QWidget()
        mid_w.setFixedWidth(130)
        mid_w.setStyleSheet("background:transparent;")
        mid_w.setLayout(mid_col)
        lay.addWidget(mid_w)

        # ── Giờ hạ cánh ─────────────────────────────────────────────────────
        arr_col = QVBoxLayout()
        arr_col.setSpacing(2)
        arr_col.setAlignment(Qt.AlignVCenter)
        arr_col.addWidget(_lbl(data["arr_t"], 26, 800, C_TEXT))
        arr_col.addWidget(_lbl(data["dst"],   12, 500, C_GRAY))
        arr_w = QWidget()
        arr_w.setFixedWidth(90)
        arr_w.setStyleSheet("background:transparent;")
        arr_w.setLayout(arr_col)
        lay.addWidget(arr_w)

        lay.addStretch(1)

        # ── Ghế còn lại ──────────────────────────────────────────────────────
        if data["seats"] <= 5:
            seat_lbl = _lbl(f"Còn {data['seats']} ghế!", 11, 700, "#E53935")
            seat_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            lay.addWidget(seat_lbl)
            lay.addSpacing(12)

        # ── Giá vé ──────────────────────────────────────────────────────────
        price_col = QVBoxLayout()
        price_col.setSpacing(2)
        price_col.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        price_col.addWidget(_lbl("CHỈ TỪ",          11, 500, C_GRAY))
        price_col.addWidget(_lbl(f"${data['price']}", 24, 800, C_RED))
        price_w = QWidget()
        price_w.setFixedWidth(105)
        price_w.setStyleSheet("background:transparent;")
        price_w.setLayout(price_col)
        lay.addWidget(price_w)

        lay.addSpacing(16)

        # ── Nút CHỌN ────────────────────────────────────────────────────────
        btn = QPushButton("CHỌN  →")
        btn.setFixedSize(120, 46)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_DARK}; border: none;
                border-radius: 23px; font-size: 14px;
                font-weight: 800; color: {C_WHITE};
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{ background: #2C2C4A; }}
            QPushButton:pressed {{ background: #0A0A1A; }}
        """)
        btn.clicked.connect(lambda: self.selected.emit(self.data))
        lay.addWidget(btn)


# ─────────────────────────────────────────────────────────────────────────────
# Booking Dialog  (form đặt vé)
# ─────────────────────────────────────────────────────────────────────────────
class BookingDialog(QDialog):
    confirmed = Signal(dict)

    def __init__(self, flight: dict, account: dict | None, parent=None):
        super().__init__(parent)
        self.flight  = flight
        self.account = account or {}
        self.setWindowTitle(f"Đặt vé — {flight['code']}")
        self.setMinimumWidth(500)
        self.setStyleSheet(f"background:{C_WHITE};")

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(14)

        # Flight summary
        summary = QWidget()
        summary.setStyleSheet(
            f"background:{C_LGRAY}; border:1px solid {C_BORDER}; border-radius:12px;"
        )
        sl = QHBoxLayout(summary)
        sl.setContentsMargins(18, 14, 18, 14)
        sl.setSpacing(16)

        sl.addWidget(AirplaneBadge(44))
        info = QVBoxLayout()
        info.setSpacing(3)
        info.addWidget(_lbl(f"{flight['code']}  {flight['dep']} → {flight['dst']}",
                            15, 700, C_TEXT))
        info.addWidget(_lbl(f"{flight['dep_t']} → {flight['arr_t']}   |   "
                            f"{flight['dur']}   |   {flight['aircraft']}",
                            12, 400, C_MID))
        sl.addLayout(info)
        sl.addStretch()
        sl.addWidget(_lbl(f"${flight['price']}", 22, 800, C_RED))

        root.addWidget(summary)

        root.addWidget(_lbl("Thông tin hành khách", 15, 700, C_TEXT))

        def _field(ph: str, pw: bool = False, default: str = "") -> QLineEdit:
            e = QLineEdit()
            e.setPlaceholderText(ph)
            e.setText(default)
            e.setFixedHeight(44)
            e.setStyleSheet(f"""
                QLineEdit {{
                    background:{C_LGRAY}; border:1.5px solid {C_BORDER};
                    border-radius:10px; font-size:13px; color:{C_TEXT};
                    padding:0 14px;
                }}
                QLineEdit:focus {{ border-color:{C_RED}; background:{C_WHITE}; }}
            """)
            if pw: e.setEchoMode(QLineEdit.Password)
            return e

        self._name  = _field("Họ và tên",  default=self.account.get("full_name", ""))
        self._phone = _field("Số điện thoại")
        self._id    = _field("CCCD / Hộ chiếu")
        self._email = _field("Email", default=self.account.get("email", ""))

        for w in (self._name, self._phone, self._id, self._email):
            root.addWidget(w)

        self._err = QLabel("")
        self._err.setAlignment(Qt.AlignCenter)
        self._err.setStyleSheet(f"font-size:12px; color:{C_RED2};"
                                " background:transparent; border:none;")
        root.addWidget(self._err)

        # Buttons
        btn_row = QHBoxLayout()
        cancel = QPushButton("Huỷ")
        cancel.setFixedHeight(42)
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.setStyleSheet(f"""
            QPushButton {{
                background:transparent; border:1.5px solid {C_BORDER};
                border-radius:9px; font-size:13px; font-weight:600;
                color:{C_MID}; padding:0 24px;
            }}
            QPushButton:hover {{ background:{C_LGRAY}; }}
        """)
        cancel.clicked.connect(self.reject)

        confirm = QPushButton("  →]  XÁC NHẬN ĐẶT VÉ")
        confirm.setFixedHeight(42)
        confirm.setCursor(Qt.PointingHandCursor)
        confirm.setStyleSheet(f"""
            QPushButton {{
                background:{C_RED}; border:none; border-radius:9px;
                font-size:13px; font-weight:800; color:{C_WHITE};
                padding:0 24px;
            }}
            QPushButton:hover {{ background:{C_RED2}; }}
        """)
        confirm.clicked.connect(self._confirm)

        btn_row.addWidget(cancel)
        btn_row.addStretch()
        btn_row.addWidget(confirm)
        root.addLayout(btn_row)

    def _confirm(self):
        name  = self._name.text().strip()
        phone = self._phone.text().strip()
        id_   = self._id.text().strip()
        email = self._email.text().strip()
        if not name or not phone or not id_:
            self._err.setText("Vui lòng điền đầy đủ họ tên, SĐT và CCCD.")
            return
        pnr = _gen_pnr()
        seat = f"{random.randint(1,35):02d}{random.choice('ABCDEF')}"
        booking = dict(
            pnr=pnr, name=name, phone=phone, id=id_, email=email,
            flight=self.flight["code"], route=f"{self.flight['dep']}-{self.flight['dst']}",
            dep_t=self.flight["dep_t"], seat=seat,
            price=f"${self.flight['price']}",
            booked_at=datetime.now().strftime("%d/%m/%Y %H:%M"),
        )
        _session_history.append(booking)
        self._write_db(name, phone, id_, email, seat)
        self.confirmed.emit(booking)
        self.accept()

    def _write_db(self, name, phone, id_, email, seat):
        try:
            import os, sqlite3
            conn = sqlite3.connect(get_db_path())
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO passengers (full_name,gender,date_of_birth,phone,email,passport_number)"
                " VALUES (?,?,?,?,?,?)",
                (name, "N/A", "N/A", phone, email or None, id_)
            )
            pid = cur.lastrowid
            pnr = _gen_pnr()
            cur.execute(
                "INSERT INTO bookings"
                " (booking_reference,passenger_id,flight_id,seat_number,"
                "  booking_class,total_amount,payment_status,booking_status)"
                " VALUES (?,?,?,?,?,?,?,?)",
                (pnr, pid, self.flight["fid"], seat, "Economy",
                 self.flight["price"], "Pending", "Pending")
            )
            conn.commit(); conn.close()
        except Exception as e:
            print(f"[DB write] {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Tab: Chuyến Bay
# ─────────────────────────────────────────────────────────────────────────────
class FlightsPage(QWidget):
    def __init__(self, account: dict | None = None, parent=None):
        super().__init__(parent)
        self.account = account or {}
        self._all = list(SAMPLE_FLIGHTS)
        self.setStyleSheet(f"background:{C_BG};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent; border:none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        inner = QWidget()
        inner.setStyleSheet(f"background:{C_BG};")
        scroll.setWidget(inner)

        self._root = QVBoxLayout(inner)
        self._root.setContentsMargins(28, 24, 28, 28)
        self._root.setSpacing(18)

        # ── Page title ───────────────────────────────────────────────────────
        self._root.addWidget(_lbl("Tìm kiếm Chuyến bay", 28, 800, C_TEXT))
        self._root.addWidget(_lbl("Bước 1: Chọn điểm khởi hành và thời gian",
                                  13, 400, C_GRAY))

        # ── Search panel ─────────────────────────────────────────────────────
        self._search = SearchPanel()
        self._search.searched.connect(self._on_search)
        self._root.addWidget(self._search)

        # ── Kết quả tìm kiếm label ───────────────────────────────────────────
        self._result_lbl = _lbl("", 11, 700, C_GRAY, 1.0)
        self._root.addWidget(self._result_lbl)

        # ── Flight list container ────────────────────────────────────────────
        self._list_w = QWidget()
        self._list_w.setStyleSheet("background:transparent;")
        self._list_l = QVBoxLayout(self._list_w)
        self._list_l.setContentsMargins(0, 0, 0, 0)
        self._list_l.setSpacing(12)
        self._root.addWidget(self._list_w)
        self._root.addStretch()

        # Load ban đầu
        self._populate(self._all)

    def _on_search(self, dep: str, dst: str, date: str):
        db = self._load_db()
        if db:
            self._all = db
        filtered = [f for f in self._all
                    if f["dep"] == dep and f["dst"] == dst]
        if not filtered:
            filtered = self._all  # Nếu không có kết quả, show tất cả
        self._populate(filtered)

    def _populate(self, flights: list[dict]):
        while self._list_l.count():
            item = self._list_l.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        n = len(flights)
        self._result_lbl.setText(
            f"KẾT QUẢ TÌM KIẾM ({n} CHUYẾN BAY KHẢ DỤNG)"
            if n else "KHÔNG TÌM THẤY CHUYẾN BAY PHÙ HỢP"
        )

        for f in flights:
            card = FlightCard(f)
            card.selected.connect(self._on_select)
            self._list_l.addWidget(card)

    def _on_select(self, flight: dict):
        dlg = BookingDialog(flight, self.account, self)
        dlg.confirmed.connect(self._on_booked)
        dlg.exec()

    def _on_booked(self, booking: dict):
        QMessageBox.information(
            self, "🎉 Đặt vé thành công!",
            f"Mã PNR  : {booking['pnr']}\n"
            f"Chuyến  : {booking['flight']}  ({booking['route']})\n"
            f"Giờ bay : {booking['dep_t']}\n"
            f"Số ghế  : {booking['seat']}\n"
            f"Giá vé  : {booking['price']}\n\n"
            f"Vui lòng lưu mã PNR để tra cứu sau."
        )

    @staticmethod
    def _load_db() -> list[dict] | None:
        try:
            import os, sqlite3
            conn = sqlite3.connect(get_db_path())
            cur  = conn.cursor()
            cur.execute("""
                SELECT flight_id, flight_number, aircraft,
                       departure, destination,
                       departure_time, arrival_time,
                       available_seats, ticket_price
                FROM flights WHERE available_seats > 0
            """)
            rows = cur.fetchall(); conn.close()
            if not rows: return None
            return [dict(
                fid=r[0], code=r[1], aircraft=r[2] or "N/A",
                dep=r[3][:3].upper(), dst=r[4][:3].upper(),
                dep_t=str(r[5])[:5], arr_t=str(r[6])[:5],
                dur="N/A", direct=True, seats=r[7] or 0,
                price=int(r[8] or 0),
            ) for r in rows]
        except Exception as e:
            print(f"[FlightsPage DB] {e}"); return None


# ─────────────────────────────────────────────────────────────────────────────
# Tab: Lịch Sử
# ─────────────────────────────────────────────────────────────────────────────
class HistoryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C_BG};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent; border:none;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        inner = QWidget()
        inner.setStyleSheet(f"background:{C_BG};")
        scroll.setWidget(inner)

        self._root = QVBoxLayout(inner)
        self._root.setContentsMargins(28, 24, 28, 28)
        self._root.setSpacing(12)

        self._root.addWidget(_lbl("Lịch sử Đặt vé", 28, 800, C_TEXT))
        self._root.addWidget(_lbl("Danh sách vé bạn đã đặt trong phiên này",
                                  13, 400, C_GRAY))
        self._root.addSpacing(8)

        self._list_l = QVBoxLayout()
        self._list_l.setSpacing(10)
        self._root.addLayout(self._list_l)
        self._root.addStretch()

        self.refresh()

    def refresh(self):
        while self._list_l.count():
            item = self._list_l.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not _session_history:
            ph = _lbl("Bạn chưa đặt vé nào trong phiên này.", 14, 400, C_GRAY)
            ph.setAlignment(Qt.AlignCenter)
            ph.setContentsMargins(0, 60, 0, 60)
            self._list_l.addWidget(ph)
            return

        for b in reversed(_session_history):
            card = QWidget()
            card.setFixedHeight(72)
            card.setStyleSheet(
                f"background:{C_WHITE}; border:1px solid {C_BORDER}; border-radius:12px;"
            )
            cl = QHBoxLayout(card)
            cl.setContentsMargins(20, 0, 20, 0)
            cl.setSpacing(16)

            pnr = _lbl(b["pnr"], 14, 800, C_RED)
            pnr.setFixedWidth(100)
            cl.addWidget(pnr)

            info = QVBoxLayout()
            info.setSpacing(3)
            info.addWidget(_lbl(b["name"], 13, 700, C_TEXT))
            info.addWidget(_lbl(f"{b['flight']}  •  {b['route']}  •  Ghế {b['seat']}",
                                11, 400, C_GRAY))
            cl.addLayout(info)
            cl.addStretch()
            cl.addWidget(_lbl(b["price"],    16, 800, C_RED))
            cl.addSpacing(12)
            cl.addWidget(_lbl(b["booked_at"], 11, 400, C_GRAY))

            self._list_l.addWidget(card)


# ─────────────────────────────────────────────────────────────────────────────
# Placeholder pages
# ─────────────────────────────────────────────────────────────────────────────
class PlaceholderPage(QWidget):
    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C_BG};")
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(_lbl(icon,  52, 400, C_GRAY))
        lay.addSpacing(12)
        lay.addWidget(_lbl(f"{title}  —  Sắp ra mắt", 18, 600, C_GRAY))


# ─────────────────────────────────────────────────────────────────────────────
# Navigation Bar
# ─────────────────────────────────────────────────────────────────────────────
class NavBar(QWidget):
    tab_changed = Signal(int)

    _TABS = ["CHUYẾN BAY", "LỊCH SỬ", "KHUYẾN MÃI", "THÔNG TIN"]

    def __init__(self, account: dict | None = None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet(f"""
            NavBar {{
                background: {C_WHITE};
                border-bottom: 1px solid {C_BORDER};
            }}
        """)
        self._btns: list[QPushButton] = []

        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.setSpacing(0)

        # ── Logo ─────────────────────────────────────────────────────────────
        lay.addWidget(NavLogo(38))
        lay.addSpacing(10)

        brand = QLabel()
        brand.setTextFormat(Qt.RichText)
        brand.setText(
            f"<span style='font-size:16px;font-weight:900;color:{C_DARK};'>JETJET</span>"
            f"<span style='font-size:16px;font-weight:700;color:{C_RED};'> AIR</span>"
        )
        brand.setStyleSheet("background:transparent; border:none;")
        lay.addWidget(brand)
        lay.addSpacing(36)

        # ── Tabs ─────────────────────────────────────────────────────────────
        for i, label in enumerate(self._TABS):
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(64)
            btn.clicked.connect(lambda _, idx=i: self._select(idx))
            self._btns.append(btn)
            lay.addWidget(btn)
            if i < len(self._TABS) - 1:
                lay.addSpacing(8)

        lay.addStretch()

        # ── Bell ─────────────────────────────────────────────────────────────
        bell = QPushButton("🔔")
        bell.setFixedSize(38, 38)
        bell.setStyleSheet(
            f"QPushButton {{ background:{C_LGRAY}; border:none; border-radius:19px;"
            f" font-size:16px; }}"
            f"QPushButton:hover {{ background:{C_BORDER}; }}"
        )
        lay.addWidget(bell)

        self._select(0)

    def _select(self, idx: int):
        for i, btn in enumerate(self._btns):
            if i == idx:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background:transparent; border:none;
                        border-bottom:3px solid {C_RED};
                        font-size:13px; font-weight:800;
                        color:{C_RED}; padding:0 12px;
                        letter-spacing:0.5px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background:transparent; border:none;
                        border-bottom:3px solid transparent;
                        font-size:13px; font-weight:500;
                        color:{C_TEXT}; padding:0 12px;
                        letter-spacing:0.5px;
                    }}
                    QPushButton:hover {{ color:{C_RED}; }}
                """)
        self.tab_changed.emit(idx)


# ─────────────────────────────────────────────────────────────────────────────
# Main Window
# ─────────────────────────────────────────────────────────────────────────────
class BookingWindow(QMainWindow):
    """
    Cửa sổ chính sau khi đăng nhập.

    Sử dụng:
        from booking_window import BookingWindow
        win = BookingWindow(account=account_dict)
        win.show()
    """

    def __init__(self, account: dict | None = None):
        super().__init__()
        self.account = account or {}
        self.setWindowTitle("JetJet Air — Đặt vé")
        self.resize(1380, 860)
        self.setMinimumSize(1100, 700)

        central = QWidget()
        central.setStyleSheet(f"background:{C_BG};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Navbar
        nav = NavBar(account)
        nav.tab_changed.connect(self._switch)
        root.addWidget(nav)

        # Pages
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background:{C_BG};")

        self._flights_page = FlightsPage(account)
        self._history_page = HistoryPage()

        # 1. Khởi tạo thực tế các trang chức năng hội viên mới thay cho Placeholder
        self._promo_page = PromotionPage()
        self._members_page = MembersPage()
        self._cur_mem_page = CurrentMemberPage()

        # 2. Thêm các trang vào bộ quản lý Stack theo thứ tự Index
        self._stack.addWidget(self._flights_page)        # Index 0
        self._stack.addWidget(self._history_page)        # Index 1
        self._stack.addWidget(self._promo_page)          # Index 2: Trang khuyến mãi thật sự
        self._stack.addWidget(PlaceholderPage("◎",  "Thông Tin"))   # Index 3
        self._stack.addWidget(self._members_page)        # Index 4: Trang điền đơn kích hoạt (Ảnh 2)
        self._stack.addWidget(self._cur_mem_page)        # Index 5: Trang trạng thái thẻ Vàng (Ảnh 3)

        # 3. ── KẾT NỐI LUỒNG TƯƠNG TÁC GIỮA CÁC FILE GIAO DIỆN ─────────────────
        
        # Nhấn "Kích hoạt hội viên" ở Ảnh 1 (Trang 2) -> Chuyển sang Form đăng ký Ảnh 2 (Trang 4)
        self._promo_page.activate_member_clicked.connect(lambda: self._stack.setCurrentIndex(4))
        
        # Nhấn "Xác nhận đăng ký" ở Ảnh 2 (Trang 4) -> Chuyển sang thẻ thành viên Vàng Ảnh 3 (Trang 5)
        self._members_page.register_success.connect(lambda: self._stack.setCurrentIndex(5))

        root.addWidget(self._stack, 1)

    def _switch(self, idx: int):
        self._stack.setCurrentIndex(idx)
        if idx == 1:
            self._history_page.refresh()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    demo_account = {"full_name": "Khách Demo", "email": "demo@jetjetair.com",
                    "role": "customer"}
    win = BookingWindow(account=demo_account)
    win.show()
    sys.exit(app.exec())