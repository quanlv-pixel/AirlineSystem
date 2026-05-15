"""
booking_app.py
--------------
Ứng dụng đặt vé hành khách — JetJet Air
Chạy độc lập : python booking_app.py
Dùng chung   : airline.db với management_app

Cấu trúc:
  JetBookWindow
  ├── AppHeader   (logo, tabs, trạng thái hệ thống)
  ├── StackedWidget
  │   ├── Tab 0 — Tìm Chuyến Bay  (search + danh sách chuyến)
  │   └── Tab 1 — Đặt Chỗ Của Tôi (danh sách booking đã đặt)
  └── Footer
"""
from __future__ import annotations
import sys
import random
import string
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import (
    QColor, QFont, QPainter, QBrush, QPen, QPainterPath,
    QLinearGradient
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
    QLineEdit, QComboBox, QDialog, QFormLayout, QDialogButtonBox,
    QMessageBox, QStackedWidget, QDateEdit, QSpinBox
)

# ─────────────────────────────────────────────────────────────────────────────
# Màu sắc (giữ nhất quán với management_app)
# ─────────────────────────────────────────────────────────────────────────────
C_BG     = "#F4F6FA"
C_WHITE  = "#FFFFFF"
C_BORDER = "#E4E6F0"
C_TEXT   = "#1A1A2E"
C_MID    = "#4A4A6A"
C_GRAY   = "#9B9BB4"
C_LGRAY  = "#F0F1F8"
C_RED    = "#E53935"
C_RED_L  = "#FFEBEE"
C_DARK   = "#0F1117"
C_GREEN  = "#22C55E"
C_BLUE   = "#1E88E5"
C_ORANGE = "#F59E0B"

# Badge màu trạng thái booking
STS_CFG = {
    "pending":   ("CHỜ XÁC NHẬN", "#92400E", "#FEF3C7"),
    "confirmed": ("ĐÃ XÁC NHẬN",  "#166534", "#DCFCE7"),
    "cancelled": ("ĐÃ HUỶ",       "#991B1B", "#FEE2E2"),
}

# Sân bay demo
AIRPORTS = ["SGN - Hồ Chí Minh", "HAN - Hà Nội", "DAD - Đà Nẵng",
            "PQC - Phú Quốc",     "ICN - Seoul",   "NRT - Tokyo"]

# ─────────────────────────────────────────────────────────────────────────────
# Dữ liệu chuyến bay mẫu (hard-code)
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_FLIGHTS: list[dict] = [
    dict(flight_id=1, code="JJ121", dep="SGN", dst="HAN",
         dep_time="06:00", arr_time="08:20", duration="2h 20m",
         seats=42, price=120),
    dict(flight_id=2, code="JJ342", dep="HAN", dst="DAD",
         dep_time="09:30", arr_time="10:45", duration="1h 15m",
         seats=18, price=85),
    dict(flight_id=3, code="JJ551", dep="SGN", dst="PQC",
         dep_time="12:15", arr_time="13:25", duration="1h 10m",
         seats=55, price=95),
    dict(flight_id=4, code="JJ207", dep="DAD", dst="HAN",
         dep_time="14:40", arr_time="16:00", duration="1h 20m",
         seats=7,  price=110),
    dict(flight_id=5, code="JJ890", dep="HAN", dst="SGN",
         dep_time="17:00", arr_time="19:10", duration="2h 10m",
         seats=29, price=75),
    dict(flight_id=6, code="JJ412", dep="SGN", dst="ICN",
         dep_time="22:30", arr_time="05:45+1", duration="4h 15m",
         seats=11, price=380),
]

# Booking đã đặt trong session (in-memory, sẽ thêm từ dialog)
_session_bookings: list[dict] = []


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _lbl(text: str, size: int = 13, weight: int = 400,
         color: str = C_TEXT, spacing: float = 0.0) -> QLabel:
    w = {400: "normal", 500: "500", 600: "600", 700: "bold", 800: "800"}.get(weight, "normal")
    sp = f"letter-spacing:{spacing}px;" if spacing else ""
    l = QLabel(text)
    l.setStyleSheet(
        f"font-size:{size}px; font-weight:{w}; color:{color};"
        f" background:transparent; border:none; {sp}"
    )
    return l


def _h_sep(alpha: int = 180) -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background:rgba(228,230,240,{alpha}); border:none;")
    return f


def _gen_pnr() -> str:
    return "JJ" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))


def _auto_seat() -> str:
    row = random.randint(1, 35)
    col = random.choice("ABCDEF")
    return f"{row:02d}{col}"


# ─────────────────────────────────────────────────────────────────────────────
# Logo badge (tương tự sidebar management)
# ─────────────────────────────────────────────────────────────────────────────
class LogoBadge(QWidget):
    def __init__(self, size: int = 38, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(2, 2, self.width()-4, self.height()-4, 10, 10)
        p.fillPath(path, QBrush(QColor(C_RED)))
        p.setPen(QPen(QColor("#FFFFFF")))
        f = QFont(); f.setPointSize(16)
        p.setFont(f)
        p.drawText(0, 0, self.width(), self.height(), Qt.AlignCenter, "✈")


# ─────────────────────────────────────────────────────────────────────────────
# Flight Code Badge (tương tự SeatBadge của booking_page)
# ─────────────────────────────────────────────────────────────────────────────
class FlightCodeBadge(QWidget):
    def __init__(self, code: str, parent=None):
        super().__init__(parent)
        self.code = code
        self.setFixedSize(72, 28)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(C_DARK)))
        bg = QPainterPath()
        bg.addRoundedRect(0, 0, self.width(), self.height(), 8, 8)
        p.drawPath(bg)
        p.setPen(QPen(QColor("#FFFFFF")))
        f = QFont(); f.setPointSize(9); f.setWeight(QFont.Bold)
        p.setFont(f)
        p.drawText(0, 0, self.width(), self.height(), Qt.AlignCenter, self.code)


# ─────────────────────────────────────────────────────────────────────────────
# Seat badge nhỏ (dùng trong tab "Đặt chỗ của tôi")
# ─────────────────────────────────────────────────────────────────────────────
class SeatBadge(QWidget):
    def __init__(self, seat: str, parent=None):
        super().__init__(parent)
        self.seat = seat
        self.setFixedSize(72, 26)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(C_DARK)))
        bg = QPainterPath()
        bg.addRoundedRect(0, 0, self.width(), self.height(), 8, 8)
        p.drawPath(bg)
        p.setPen(QPen(QColor("#FFFFFF")))
        f = QFont(); f.setPointSize(9); f.setWeight(QFont.Medium)
        p.setFont(f)
        p.drawText(0, 0, self.width(), self.height(),
                   Qt.AlignCenter, f"✈  {self.seat}")


# ─────────────────────────────────────────────────────────────────────────────
# TextBadge màu (trạng thái booking)
# ─────────────────────────────────────────────────────────────────────────────
class TextBadge(QLabel):
    def __init__(self, text: str, fg: str, bg: str, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(24)
        self.setContentsMargins(10, 0, 10, 0)
        self.setStyleSheet(f"""
            QLabel {{ font-size:11px; font-weight:700; color:{fg};
                      background:{bg}; border-radius:6px; border:none; }}
        """)


# ─────────────────────────────────────────────────────────────────────────────
# Seats indicator  (hiển thị số ghế trống)
# ─────────────────────────────────────────────────────────────────────────────
class SeatsIndicator(QWidget):
    def __init__(self, seats: int, parent=None):
        super().__init__(parent)
        self.setFixedHeight(28)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)
        lay.setAlignment(Qt.AlignCenter)

        if seats <= 5:
            color, bg = "#991B1B", "#FEE2E2"
            label = f"⚠  {seats} ghế"
        elif seats <= 15:
            color, bg = "#92400E", "#FEF3C7"
            label = f"{seats} ghế"
        else:
            color, bg = "#166534", "#DCFCE7"
            label = f"{seats} ghế"

        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"font-size:12px; font-weight:700; color:{color};"
            f" background:{bg}; border-radius:6px; padding:0 8px;"
            f" border:none;"
        )
        lbl.setFixedHeight(24)
        lay.addWidget(lbl)


# ─────────────────────────────────────────────────────────────────────────────
# Flight Row  (một chuyến bay trong danh sách)
# ─────────────────────────────────────────────────────────────────────────────
class FlightRow(QWidget):
    book_clicked = Signal(dict)

    # Độ rộng cột (giống pattern booking_page)
    _COLS = dict(code=90, route=160, dep=90, arr=90, dur=100,
                 seats=100, price=90, action=120)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data = data
        self.setFixedHeight(80)
        self.setStyleSheet(f"background:{C_WHITE};")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)

        # Số hiệu bay
        code_w = QWidget()
        code_w.setFixedWidth(self._COLS["code"])
        code_w.setStyleSheet("background:transparent;")
        cl = QHBoxLayout(code_w)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.addWidget(FlightCodeBadge(data["code"]))
        lay.addWidget(code_w)

        # Tuyến bay  DEP → DST
        route_col = QVBoxLayout()
        route_col.setSpacing(4)
        route_col.setAlignment(Qt.AlignVCenter)
        dep_dst = QHBoxLayout()
        dep_dst.setSpacing(8)
        dep_dst.addWidget(_lbl(data["dep"], 15, 800, C_TEXT))
        arrow = _lbl("→", 13, 400, C_GRAY)
        dep_dst.addWidget(arrow)
        dep_dst.addWidget(_lbl(data["dst"], 15, 800, C_TEXT))
        dep_dst.addStretch()
        route_sub = _lbl(f"{data['dep']} — {data['dst']}", 11, 400, C_GRAY)
        route_col.addLayout(dep_dst)
        route_col.addWidget(route_sub)
        route_w = QWidget()
        route_w.setFixedWidth(self._COLS["route"])
        route_w.setStyleSheet("background:transparent;")
        route_w.setLayout(route_col)
        lay.addWidget(route_w)

        # Giờ khởi hành
        dep_col = QVBoxLayout()
        dep_col.setSpacing(3)
        dep_col.setAlignment(Qt.AlignVCenter)
        dep_col.addWidget(_lbl(data["dep_time"], 17, 800, C_TEXT))
        dep_col.addWidget(_lbl("Khởi hành", 10, 400, C_GRAY))
        dep_w = QWidget()
        dep_w.setFixedWidth(self._COLS["dep"])
        dep_w.setStyleSheet("background:transparent;")
        dep_w.setLayout(dep_col)
        lay.addWidget(dep_w)

        # Giờ hạ cánh
        arr_col = QVBoxLayout()
        arr_col.setSpacing(3)
        arr_col.setAlignment(Qt.AlignVCenter)
        arr_col.addWidget(_lbl(data["arr_time"], 17, 800, C_TEXT))
        arr_col.addWidget(_lbl("Hạ cánh", 10, 400, C_GRAY))
        arr_w = QWidget()
        arr_w.setFixedWidth(self._COLS["arr"])
        arr_w.setStyleSheet("background:transparent;")
        arr_w.setLayout(arr_col)
        lay.addWidget(arr_w)

        # Thời gian bay
        dur_col = QVBoxLayout()
        dur_col.setAlignment(Qt.AlignVCenter)
        dur_col.addWidget(_lbl("⏱ " + data["duration"], 12, 600, C_MID))
        dur_w = QWidget()
        dur_w.setFixedWidth(self._COLS["dur"])
        dur_w.setStyleSheet("background:transparent;")
        dur_w.setLayout(dur_col)
        lay.addWidget(dur_w)

        # Ghế trống
        seats_w = QWidget()
        seats_w.setFixedWidth(self._COLS["seats"])
        seats_w.setStyleSheet("background:transparent;")
        sl = QHBoxLayout(seats_w)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setAlignment(Qt.AlignCenter)
        sl.addWidget(SeatsIndicator(data["seats"]))
        lay.addWidget(seats_w)

        # Giá vé
        price_col = QVBoxLayout()
        price_col.setSpacing(2)
        price_col.setAlignment(Qt.AlignVCenter)
        price_col.addWidget(_lbl(f"${data['price']}", 18, 800, C_RED))
        price_col.addWidget(_lbl("/người", 10, 400, C_GRAY))
        price_w = QWidget()
        price_w.setFixedWidth(self._COLS["price"])
        price_w.setStyleSheet("background:transparent;")
        price_w.setLayout(price_col)
        lay.addWidget(price_w)

        # Nút ĐẶT VÉ
        action_w = QWidget()
        action_w.setFixedWidth(self._COLS["action"])
        action_w.setStyleSheet("background:transparent;")
        al = QHBoxLayout(action_w)
        al.setContentsMargins(0, 0, 0, 0)
        al.setAlignment(Qt.AlignCenter)

        book_btn = QPushButton("ĐẶT VÉ")
        book_btn.setFixedSize(90, 36)
        book_btn.setCursor(Qt.PointingHandCursor)
        if data["seats"] == 0:
            book_btn.setText("HẾT VÉ")
            book_btn.setEnabled(False)
            book_btn.setStyleSheet(f"""
                QPushButton {{ background:{C_LGRAY}; border:none;
                    border-radius:9px; font-size:12px; font-weight:700;
                    color:{C_GRAY}; }}
            """)
        else:
            book_btn.setStyleSheet(f"""
                QPushButton {{ background:{C_RED}; border:none;
                    border-radius:9px; font-size:12px; font-weight:800;
                    color:white; letter-spacing:0.5px; }}
                QPushButton:hover {{ background:#C62828; }}
                QPushButton:pressed {{ background:#B71C1C; }}
            """)
            book_btn.clicked.connect(lambda: self.book_clicked.emit(self.data))

        al.addWidget(book_btn)
        lay.addWidget(action_w)

    def enterEvent(self, _): self.setStyleSheet("background:#FAFBFF;")
    def leaveEvent(self, _): self.setStyleSheet(f"background:{C_WHITE};")


# ─────────────────────────────────────────────────────────────────────────────
# Flight Table Header
# ─────────────────────────────────────────────────────────────────────────────
class FlightHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setStyleSheet("background:transparent;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)

        cols = [
            ("SỐ HIỆU",         90,  Qt.AlignLeft),
            ("TUYẾN BAY",       160,  Qt.AlignLeft),
            ("KHỞI HÀNH",        90,  Qt.AlignLeft),
            ("HẠ CÁNH",          90,  Qt.AlignLeft),
            ("THỜI GIAN",       100,  Qt.AlignLeft),
            ("GHẾ TRỐNG",       100,  Qt.AlignCenter),
            ("GIÁ VÉ",           90,  Qt.AlignLeft),
            ("THAO TÁC",        120,  Qt.AlignCenter),
        ]
        for text, width, align in cols:
            lbl = QLabel(text)
            lbl.setFixedWidth(width)
            lbl.setAlignment(align | Qt.AlignVCenter)
            lbl.setStyleSheet(
                f"font-size:10px; font-weight:600; color:{C_GRAY};"
                f" letter-spacing:1px; background:transparent; border:none;"
            )
            lay.addWidget(lbl)


# ─────────────────────────────────────────────────────────────────────────────
# Flight Table (header + rows)
# ─────────────────────────────────────────────────────────────────────────────
class FlightTable(QWidget):
    book_clicked = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            FlightTable {{
                background:{C_WHITE}; border:1px solid {C_BORDER};
                border-radius:14px;
            }}
        """)
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 8)
        self._root.setSpacing(0)

        self._root.addWidget(FlightHeader())
        self._root.addWidget(_h_sep())

        self._rows_w = QWidget()
        self._rows_w.setStyleSheet("background:transparent;")
        self._rows_l = QVBoxLayout(self._rows_w)
        self._rows_l.setContentsMargins(0, 0, 0, 0)
        self._rows_l.setSpacing(0)
        self._root.addWidget(self._rows_w)
        self._root.addStretch()

    def populate(self, flights: list[dict]):
        while self._rows_l.count():
            item = self._rows_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not flights:
            ph = _lbl("Không tìm thấy chuyến bay phù hợp.", 14, 400, C_GRAY)
            ph.setAlignment(Qt.AlignCenter)
            ph.setContentsMargins(0, 40, 0, 40)
            self._rows_l.addWidget(ph)
            return

        for i, f in enumerate(flights):
            row = FlightRow(f)
            row.book_clicked.connect(self.book_clicked)
            self._rows_l.addWidget(row)
            if i < len(flights) - 1:
                self._rows_l.addWidget(_h_sep())


# ─────────────────────────────────────────────────────────────────────────────
# Search Panel
# ─────────────────────────────────────────────────────────────────────────────
class SearchPanel(QWidget):
    searched = Signal(str, str)   # dep_code, dst_code

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(76)
        self.setStyleSheet(f"""
            SearchPanel {{
                background:{C_WHITE}; border:1px solid {C_BORDER};
                border-left:3px solid {C_RED}; border-radius:12px;
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(14)

        def _combo(items: list[str], width: int = 200) -> QComboBox:
            c = QComboBox()
            c.addItem("Tất cả")
            c.addItems(items)
            c.setFixedWidth(width)
            c.setFixedHeight(40)
            c.setStyleSheet(f"""
                QComboBox {{
                    background:{C_LGRAY}; border:1px solid {C_BORDER};
                    border-radius:10px; font-size:13px; font-weight:600;
                    color:{C_TEXT}; padding:0 12px;
                }}
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
                    selection-background-color:{C_RED_L};
                    selection-color:{C_RED};
                    font-size:13px;
                }}
            """)
            return c

        codes = ["SGN", "HAN", "DAD", "PQC", "ICN", "NRT"]

        # Từ
        lay.addWidget(_lbl("✈  Từ", 13, 600, C_GRAY))
        self._combo_dep = _combo(codes, 150)
        lay.addWidget(self._combo_dep)

        sep1 = QFrame(); sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet(f"background:{C_BORDER}; border:none;")
        sep1.setFixedWidth(1)
        lay.addWidget(sep1)

        # Đến
        lay.addWidget(_lbl("→  Đến", 13, 600, C_GRAY))
        self._combo_dst = _combo(codes, 150)
        lay.addWidget(self._combo_dst)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet(f"background:{C_BORDER}; border:none;")
        sep2.setFixedWidth(1)
        lay.addWidget(sep2)

        # Ngày bay
        lay.addWidget(_lbl("📅  Ngày", 13, 600, C_GRAY))
        date_e = QDateEdit(QDate.currentDate())
        date_e.setFixedSize(140, 40)
        date_e.setCalendarPopup(True)
        date_e.setStyleSheet(f"""
            QDateEdit {{
                background:{C_LGRAY}; border:1px solid {C_BORDER};
                border-radius:10px; font-size:13px; font-weight:600;
                color:{C_TEXT}; padding:0 12px;
            }}
            QDateEdit::drop-down {{ border:none; width:24px; }}
        """)
        lay.addWidget(date_e)

        lay.addStretch()

        # Nút TÌM
        search_btn = QPushButton("🔍  TÌM CHUYẾN BAY")
        search_btn.setFixedHeight(42)
        search_btn.setCursor(Qt.PointingHandCursor)
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background:{C_RED}; border:none; border-radius:10px;
                font-size:13px; font-weight:800; color:white;
                padding:0 22px; letter-spacing:0.5px;
            }}
            QPushButton:hover {{ background:#C62828; }}
            QPushButton:pressed {{ background:#B71C1C; }}
        """)
        search_btn.clicked.connect(
            lambda: self.searched.emit(
                self._combo_dep.currentText(),
                self._combo_dst.currentText()
            )
        )
        lay.addWidget(search_btn)


# ─────────────────────────────────────────────────────────────────────────────
# Booking Dialog  (form đặt vé)
# ─────────────────────────────────────────────────────────────────────────────
class BookingDialog(QDialog):
    booking_saved = Signal(dict)   # phát ra sau khi lưu thành công

    def __init__(self, flight: dict, parent=None):
        super().__init__(parent)
        self.flight = flight
        self.setWindowTitle(f"Đặt vé — {flight['code']}  {flight['dep']} → {flight['dst']}")
        self.setMinimumWidth(520)
        self.setStyleSheet(f"background:{C_WHITE};")

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        # ── Tóm tắt chuyến bay ──────────────────────────────────────────────
        summary = QWidget()
        summary.setStyleSheet(
            f"background:{C_LGRAY}; border:1px solid {C_BORDER}; border-radius:12px;"
        )
        sl = QHBoxLayout(summary)
        sl.setContentsMargins(18, 14, 18, 14)
        sl.setSpacing(20)

        sl.addWidget(FlightCodeBadge(flight["code"]))

        info_col = QVBoxLayout()
        info_col.setSpacing(4)
        route_row = QHBoxLayout()
        route_row.setSpacing(8)
        route_row.addWidget(_lbl(flight["dep"], 18, 800, C_TEXT))
        route_row.addWidget(_lbl("→", 14, 400, C_GRAY))
        route_row.addWidget(_lbl(flight["dst"], 18, 800, C_TEXT))
        route_row.addStretch()
        info_col.addLayout(route_row)
        info_col.addWidget(
            _lbl(f"{flight['dep_time']} → {flight['arr_time']}   |   {flight['duration']}",
                 12, 500, C_MID)
        )
        sl.addLayout(info_col)
        sl.addStretch()

        price_col = QVBoxLayout()
        price_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        price_col.addWidget(_lbl(f"${flight['price']}", 22, 800, C_RED))
        price_col.addWidget(_lbl("/người", 11, 400, C_GRAY))
        sl.addLayout(price_col)

        root.addWidget(summary)
        root.addWidget(_h_sep())

        # ── Form nhập thông tin ──────────────────────────────────────────────
        root.addWidget(_lbl("Thông tin hành khách", 15, 700, C_TEXT))

        def _field(placeholder: str) -> QLineEdit:
            e = QLineEdit()
            e.setPlaceholderText(placeholder)
            e.setFixedHeight(42)
            e.setStyleSheet(f"""
                QLineEdit {{
                    background:{C_LGRAY}; border:1px solid {C_BORDER};
                    border-radius:10px; font-size:13px; color:{C_TEXT};
                    padding:0 14px;
                }}
                QLineEdit:focus {{ border-color:{C_RED}; background:{C_WHITE}; }}
            """)
            return e

        self._name     = _field("Họ và tên (VD: Nguyen Van A)")
        self._phone    = _field("Số điện thoại")
        self._passport = _field("Số CCCD / Hộ chiếu")
        self._email    = _field("Email (tuỳ chọn)")

        for w in (self._name, self._phone, self._passport, self._email):
            root.addWidget(w)

        root.addWidget(_h_sep())

        # ── Nút ─────────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        cancel = QPushButton("HUỶ")
        cancel.setFixedHeight(42)
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.setStyleSheet(f"""
            QPushButton {{
                background:transparent; border:1.5px solid {C_BORDER};
                border-radius:10px; font-size:13px; font-weight:600;
                color:{C_MID}; padding:0 24px;
            }}
            QPushButton:hover {{ background:{C_LGRAY}; }}
        """)
        cancel.clicked.connect(self.reject)

        confirm = QPushButton("  ✈  XÁC NHẬN ĐẶT VÉ")
        confirm.setFixedHeight(42)
        confirm.setCursor(Qt.PointingHandCursor)
        confirm.setStyleSheet(f"""
            QPushButton {{
                background:{C_RED}; border:none; border-radius:10px;
                font-size:13px; font-weight:800; color:white;
                padding:0 24px; letter-spacing:0.5px;
            }}
            QPushButton:hover {{ background:#C62828; }}
            QPushButton:pressed {{ background:#B71C1C; }}
        """)
        confirm.clicked.connect(self._confirm)

        btn_row.addWidget(cancel)
        btn_row.addStretch()
        btn_row.addWidget(confirm)
        root.addLayout(btn_row)

    def _confirm(self):
        name = self._name.text().strip()
        phone = self._phone.text().strip()
        passport = self._passport.text().strip()
        email = self._email.text().strip()

        if not name or not phone or not passport:
            QMessageBox.warning(self, "Thiếu thông tin",
                                "Vui lòng điền đầy đủ họ tên, SĐT và CCCD.")
            return

        seat = _auto_seat()
        pnr  = _gen_pnr()

        # Ghi vào DB
        ok, err = self._write_db(name, phone, passport, email, seat)
        if not ok:
            print(f"[BookingDialog] DB write failed: {err} — dùng in-memory")

        booking = dict(
            pnr      = pnr,
            name     = name,
            flight   = self.flight["code"],
            route    = f"{self.flight['dep']}-{self.flight['dst']}",
            dep_time = self.flight["dep_time"],
            seat     = seat,
            price    = f"${self.flight['price']}",
            status   = "pending",
            booked_at= datetime.now().strftime("%d %b %Y, %H:%M"),
        )
        _session_bookings.append(booking)
        self.booking_saved.emit(booking)
        self.accept()

    def _write_db(self, name, phone, passport, email, seat) -> tuple[bool, str]:
        try:
            from database.db import connect_db
            conn = connect_db()
            cur  = conn.cursor()
            cur.execute(
                "INSERT INTO passengers (full_name, phone, passport_number, email)"
                " VALUES (?,?,?,?)",
                (name, phone, passport, email or None)
            )
            pid = cur.lastrowid
            cur.execute(
                "INSERT INTO bookings (passenger_id, flight_id, seat_number,"
                " booking_date, status) VALUES (?,?,?,?,?)",
                (pid, self.flight["flight_id"], seat,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "pending")
            )
            conn.commit()
            conn.close()
            return True, ""
        except Exception as e:
            return False, str(e)


# ─────────────────────────────────────────────────────────────────────────────
# Tab 0 — Tìm Chuyến Bay
# ─────────────────────────────────────────────────────────────────────────────
class FindFlightsTab(QWidget):
    booking_saved = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C_BG};")
        self._flights = list(SAMPLE_FLIGHTS)

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

        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 20, 28, 20)
        root.setSpacing(16)

        # Page title
        title_row = QHBoxLayout()
        tc = QVBoxLayout()
        tc.setSpacing(4)
        tc.addWidget(_lbl("Tìm Chuyến Bay", 26, 800, C_TEXT))
        tc.addWidget(_lbl("Chọn chuyến bay phù hợp và đặt vé ngay hôm nay", 13, 400, C_GRAY))
        title_row.addLayout(tc)
        title_row.addStretch()
        root.addLayout(title_row)

        # Search panel
        self._search = SearchPanel()
        self._search.searched.connect(self._on_search)
        root.addWidget(self._search)

        # Table
        self._table = FlightTable()
        self._table.book_clicked.connect(self._on_book)
        root.addWidget(self._table)
        root.addStretch()

        # Load ban đầu
        self._refresh_table(self._flights)

    def _refresh_table(self, flights):
        db = self._load_db()
        self._flights = db if db else list(SAMPLE_FLIGHTS)
        self._table.populate(flights)

    def _on_search(self, dep: str, dst: str):
        filtered = self._flights
        if dep != "Tất cả":
            filtered = [f for f in filtered if f["dep"] == dep]
        if dst != "Tất cả":
            filtered = [f for f in filtered if f["dst"] == dst]
        self._table.populate(filtered)

    def _on_book(self, flight: dict):
        dlg = BookingDialog(flight, self)
        dlg.booking_saved.connect(self._on_saved)
        dlg.exec()

    def _on_saved(self, booking: dict):
        self.booking_saved.emit(booking)
        QMessageBox.information(
            self, "🎉 Đặt vé thành công!",
            f"Mã PNR của bạn:  {booking['pnr']}\n"
            f"Chuyến bay    :  {booking['flight']}  ({booking['route']})\n"
            f"Giờ khởi hành :  {booking['dep_time']}\n"
            f"Số ghế        :  {booking['seat']}\n"
            f"Tổng tiền     :  {booking['price']}\n\n"
            f"Vui lòng lưu mã PNR để tra cứu sau."
        )

    @staticmethod
    def _load_db() -> list[dict] | None:
        try:
            from database.db import connect_db
            conn = connect_db()
            cur  = conn.cursor()
            cur.execute("""
                SELECT flight_id, airline_name, departure, destination,
                       departure_time, arrival_time, available_seats, ticket_price
                FROM flights WHERE available_seats > 0
            """)
            rows = cur.fetchall()
            conn.close()
            if not rows:
                return None
            result = []
            for r in rows:
                fid, airline, dep, dst, dtime, atime, seats, price = r
                result.append(dict(
                    flight_id=fid, code=f"JJ{fid:03d}",
                    dep=dep[:3].upper(), dst=dst[:3].upper(),
                    dep_time=str(dtime)[:5], arr_time=str(atime)[:5],
                    duration="N/A", seats=seats or 0, price=int(price or 0),
                ))
            return result
        except Exception as e:
            print(f"[FindFlights] DB: {e}")
            return None


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 — Đặt Chỗ Của Tôi
# ─────────────────────────────────────────────────────────────────────────────
class MyBookingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
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
        self._root.setContentsMargins(28, 20, 28, 20)
        self._root.setSpacing(16)

        # Title
        tc = QVBoxLayout()
        tc.setSpacing(4)
        tc.addWidget(_lbl("Đặt Chỗ Của Tôi", 26, 800, C_TEXT))
        tc.addWidget(_lbl("Danh sách vé đã đặt trong phiên làm việc này", 13, 400, C_GRAY))
        self._root.addLayout(tc)

        # Card bảng
        self._card = QWidget()
        self._card.setStyleSheet(
            f"background:{C_WHITE}; border:1px solid {C_BORDER}; border-radius:14px;"
        )
        self._card_l = QVBoxLayout(self._card)
        self._card_l.setContentsMargins(0, 0, 0, 8)
        self._card_l.setSpacing(0)

        # Header cột
        hdr = self._make_header()
        self._card_l.addWidget(hdr)
        self._card_l.addWidget(_h_sep())

        self._rows_w = QWidget()
        self._rows_w.setStyleSheet("background:transparent;")
        self._rows_l = QVBoxLayout(self._rows_w)
        self._rows_l.setContentsMargins(0, 0, 0, 0)
        self._rows_l.setSpacing(0)
        self._card_l.addWidget(self._rows_w)
        self._card_l.addStretch()

        self._root.addWidget(self._card)
        self._root.addStretch()

        self.refresh()

    def _make_header(self) -> QWidget:
        hdr = QWidget()
        hdr.setFixedHeight(46)
        hdr.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(hdr)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)
        cols = [("MÃ PNR", 110), ("CHUYẾN BAY", 140), ("TUYẾN", 110),
                ("GIỜ BAY", 90), ("SỐ GHẾ", 110), ("GIÁ VÉ", 90),
                ("TRẠNG THÁI", 130), ("ĐẶT LÚC", 0)]
        for text, w in cols:
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"font-size:10px; font-weight:600; color:{C_GRAY};"
                f" letter-spacing:1px; background:transparent; border:none;"
            )
            if w == 0:
                lbl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                lay.addWidget(lbl, 1)
            else:
                lbl.setFixedWidth(w)
                lay.addWidget(lbl)
        return hdr

    def add_booking(self, b: dict):
        self.refresh()

    def refresh(self):
        while self._rows_l.count():
            item = self._rows_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        data = list(_session_bookings)
        if not data:
            ph = _lbl("Bạn chưa đặt vé nào trong phiên này.", 14, 400, C_GRAY)
            ph.setAlignment(Qt.AlignCenter)
            ph.setContentsMargins(0, 40, 0, 40)
            self._rows_l.addWidget(ph)
            return

        for i, b in enumerate(reversed(data)):
            row = self._make_row(b)
            self._rows_l.addWidget(row)
            if i < len(data) - 1:
                self._rows_l.addWidget(_h_sep())

    def _make_row(self, b: dict) -> QWidget:
        row = QWidget()
        row.setFixedHeight(72)
        row.setStyleSheet(f"background:{C_WHITE};")
        lay = QHBoxLayout(row)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)

        def _fixed(widget, width: int):
            widget.setFixedWidth(width)
            return widget

        lay.addWidget(_fixed(_lbl(b["pnr"], 13, 700, C_RED), 110))

        flt_col = QVBoxLayout()
        flt_col.setSpacing(3)
        flt_col.setAlignment(Qt.AlignVCenter)
        flt_col.addWidget(_lbl(b["flight"], 13, 700, C_TEXT))
        flt_w = QWidget()
        flt_w.setFixedWidth(140)
        flt_w.setStyleSheet("background:transparent;")
        flt_w.setLayout(flt_col)
        lay.addWidget(flt_w)

        lay.addWidget(_fixed(_lbl(b["route"], 13, 600, C_MID), 110))
        lay.addWidget(_fixed(_lbl(b["dep_time"], 13, 600, C_TEXT), 90))

        seat_w = QWidget()
        seat_w.setFixedWidth(110)
        seat_w.setStyleSheet("background:transparent;")
        sl = QHBoxLayout(seat_w)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.addWidget(SeatBadge(b["seat"]))
        lay.addWidget(seat_w)

        lay.addWidget(_fixed(_lbl(b["price"], 14, 800, C_RED), 90))

        sts_text, sts_fg, sts_bg = STS_CFG.get(b["status"], ("?", C_GRAY, C_LGRAY))
        badge = TextBadge(sts_text, sts_fg, sts_bg)
        badge.setFixedWidth(120)
        badge_w = QWidget()
        badge_w.setFixedWidth(130)
        badge_w.setStyleSheet("background:transparent;")
        bwl = QHBoxLayout(badge_w)
        bwl.setContentsMargins(0, 0, 0, 0)
        bwl.addWidget(badge)
        lay.addWidget(badge_w)

        lay.addWidget(_lbl(b.get("booked_at", "—"), 11, 400, C_GRAY), 1)
        return row


# ─────────────────────────────────────────────────────────────────────────────
# App Header  (logo + tabs + trạng thái)
# ─────────────────────────────────────────────────────────────────────────────
class AppHeader(QWidget):
    tab_changed = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(66)
        self.setStyleSheet(f"""
            AppHeader {{
                background:{C_WHITE}; border-bottom:1px solid {C_BORDER};
            }}
        """)
        self._btns: list[QPushButton] = []

        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.setSpacing(16)

        # Logo
        badge = LogoBadge(38)
        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)
        brand_col.addWidget(_lbl("JETJET AIR", 15, 900, C_RED, 1.0))
        brand_col.addWidget(_lbl("ĐẶT VÉ TRỰC TUYẾN", 8, 600, C_GRAY, 2.0))

        lay.addWidget(badge)
        lay.addLayout(brand_col)
        lay.addSpacing(20)

        # Separator
        vs = QFrame(); vs.setFrameShape(QFrame.VLine)
        vs.setStyleSheet(f"background:{C_BORDER}; border:none;")
        vs.setFixedWidth(1); vs.setFixedHeight(28)
        lay.addWidget(vs)

        # Tabs
        for i, label in enumerate(["✈  Tìm Chuyến Bay", "🎫  Đặt Chỗ Của Tôi"]):
            btn = QPushButton(label)
            btn.setFixedHeight(36)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self._select(idx))
            self._btns.append(btn)
            lay.addWidget(btn)

        lay.addStretch()

        # Trạng thái hệ thống
        dot = QLabel("●")
        dot.setStyleSheet(f"color:{C_GREEN}; font-size:11px; background:transparent; border:none;")
        lay.addWidget(dot)
        lay.addSpacing(4)
        lay.addWidget(_lbl("Hệ thống Trực tuyến", 12, 600, C_GREEN))

        self._select(0)

    def _select(self, idx: int):
        on = (f"QPushButton {{ background:{C_RED_L}; border:none; border-radius:9px;"
              f" font-size:13px; font-weight:700; color:{C_RED}; padding:0 18px; }}")
        off = (f"QPushButton {{ background:transparent; border:none; border-radius:9px;"
               f" font-size:13px; font-weight:500; color:{C_MID}; padding:0 18px; }}"
               f"QPushButton:hover {{ background:{C_LGRAY}; }}")
        for i, btn in enumerate(self._btns):
            btn.setStyleSheet(on if i == idx else off)
        self.tab_changed.emit(idx)


# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
class AppFooter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet(
            f"background:{C_WHITE}; border-top:1px solid {C_BORDER};"
        )
        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 0, 24, 0)
        lay.addWidget(_lbl("© 2026 JETJET AIR  /  ĐẶT VÉ TRỰC TUYẾN",
                           10, 400, C_GRAY, 0.5))
        lay.addStretch()
        dot = QLabel("●")
        dot.setStyleSheet(f"color:{C_RED}; font-size:10px; background:transparent; border:none;")
        lay.addWidget(dot)
        lay.addSpacing(4)
        lay.addWidget(_lbl("PHIÊN BẢN 2.5.0 ÔN ĐỊNH", 10, 700, C_RED, 0.5))


# ─────────────────────────────────────────────────────────────────────────────
# Main Window
# ─────────────────────────────────────────────────────────────────────────────
class JetBookWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JetJet Air — Đặt vé trực tuyến")
        self.resize(1350, 820)
        self.setMinimumSize(1100, 700)

        central = QWidget()
        central.setStyleSheet(f"background:{C_BG};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = AppHeader()
        header.tab_changed.connect(self._switch_tab)
        root.addWidget(header)

        # Stacked pages
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background:{C_BG};")

        self._find_tab    = FindFlightsTab()
        self._mybooking_tab = MyBookingsTab()

        self._find_tab.booking_saved.connect(self._on_booking_saved)

        self._stack.addWidget(self._find_tab)
        self._stack.addWidget(self._mybooking_tab)

        root.addWidget(self._stack, 1)
        root.addWidget(AppFooter())

    def _switch_tab(self, idx: int):
        self._stack.setCurrentIndex(idx)
        if idx == 1:
            self._mybooking_tab.refresh()

    def _on_booking_saved(self, booking: dict):
        self._mybooking_tab.refresh()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = JetBookWindow()
    win.show()
    sys.exit(app.exec())