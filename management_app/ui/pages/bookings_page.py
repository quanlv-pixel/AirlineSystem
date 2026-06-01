"""
ui/pages/booking_page.py
-------------------------
Đặt file này vào: ui/pages/booking_page.py
Trang Quản lý Đặt chỗ — JetJet Management App
"""
from __future__ import annotations
import random
import string
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import (
    QColor, QFont, QPainter, QBrush, QPen, QPainterPath
)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QLineEdit, QComboBox,
    QApplication, QMainWindow, QMessageBox, QSpacerItem
)

# ─────────────────────────────────────────────────────────────────────────────
# Màu sắc & hằng số
# ─────────────────────────────────────────────────────────────────────────────
C_BG      = "#F4F6FA"
C_WHITE   = "#FFFFFF"
C_BORDER  = "#E4E6F0"
C_TEXT    = "#1A1A2E"
C_MID     = "#4A4A6A"
C_GRAY    = "#9B9BB4"
C_LGRAY   = "#F0F1F8"
C_RED     = "#E53935"
C_RED_L   = "#FFEBEE"
C_DARK    = "#1A1A2E"

# Màu badge thanh toán
PAY_COLORS = {
    "ĐÃ TRẢ":  ("#166534", "#DCFCE7"),   # xanh lá
    "CHỜ TRẢ": ("#92400E", "#FEF3C7"),   # vàng cam
    "ĐÃ HUỶ":  ("#991B1B", "#FEE2E2"),   # đỏ nhạt
}
# Màu badge trạng thái
STS_COLORS = {
    "THÀNH CÔNG":  ("#1E40AF", "#DBEAFE"),  # xanh dương
    "ĐANG XỬ LÝ": ("#475569", "#F1F5F9"),  # xám
    "ĐÃ HUỶ":     ("#991B1B", "#FEE2E2"),  # đỏ nhạt
}

# Độ rộng cột (px). 0 = co giãn (stretch)
COL = {
    "pnr":     110,
    "name":      0,    # stretch
    "flight":  130,
    "seat":    110,
    "payment": 110,
    "status":  120,
    "price":    80,
    "actions": 110,
}

# ─────────────────────────────────────────────────────────────────────────────
# Dữ liệu mẫu (hard-code, dùng khi DB chưa sẵn sàng)
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE: list[dict] = [
    dict(pnr="JJXL92", name="Lê Văn Quân",         date="01 Jun 2026",
         flight="JJ121", route="SGN→HAN", seat="12A",
         payment="ĐÃ TRẢ",  status="THÀNH CÔNG",  price="$120"),
    dict(pnr="JJAS21", name="Nguyễn Thị Thu Hà",    date="31 May 2026",
         flight="JJ342", route="HAN→DAD", seat="04C",
         payment="CHỜ TRẢ", status="ĐANG XỬ LÝ", price="$85"),
    dict(pnr="JJPQ88", name="Trần Minh Khoa",       date="30 May 2026",
         flight="JJ551", route="SGN→PQC", seat="22F",
         payment="ĐÃ TRẢ",  status="THÀNH CÔNG",  price="$195"),
    dict(pnr="JJKM14", name="Hoàng Đức Thắng",      date="29 May 2026",
         flight="JJ207", route="DAD→HAN", seat="08B",
         payment="CHỜ TRẢ", status="ĐANG XỬ LÝ", price="$110"),
    dict(pnr="JJRR77", name="Phạm Thị Lan Anh",     date="28 May 2026",
         flight="JJ890", route="HAN→SGN", seat="31E",
         payment="ĐÃ TRẢ",  status="THÀNH CÔNG",  price="$75"),
    dict(pnr="JJVB03", name="Vũ Thị Mỹ Linh",       date="27 May 2026",
         flight="JJ412", route="SGN→CXR", seat="05A",
         payment="ĐÃ TRẢ",  status="THÀNH CÔNG",  price="$65"),
    dict(pnr="JJDB55", name="Đặng Quốc Bảo",        date="26 May 2026",
         flight="JJ203", route="HAN→SGN", seat="1A",
         payment="ĐÃ TRẢ",  status="THÀNH CÔNG",  price="$340"),
    dict(pnr="JJHN29", name="Bùi Thị Hồng Nhung",   date="25 May 2026",
         flight="JJ631", route="SGN→HAN", seat="18D",
         payment="ĐÃ HUỶ",  status="ĐÃ HUỶ",     price="$98"),
    dict(pnr="JJLT66", name="Lý Thành Trung",        date="24 May 2026",
         flight="JJ750", route="HAN→PQC", seat="11C",
         payment="ĐÃ TRẢ",  status="THÀNH CÔNG",  price="$155"),
    dict(pnr="JJNB41", name="Ngô Thị Bích Phượng",  date="23 May 2026",
         flight="JJ319", route="DAD→SGN", seat="27B",
         payment="CHỜ TRẢ", status="ĐANG XỬ LÝ", price="$72"),
    dict(pnr="JJDH88", name="Đinh Văn Hùng",        date="22 May 2026",
         flight="JJ481", route="SGN→DAD", seat="03F",
         payment="ĐÃ TRẢ",  status="THÀNH CÔNG",  price="$88"),
    dict(pnr="JJPL17", name="Phan Thị Diệu Linh",   date="21 May 2026",
         flight="JJ222", route="HAN→CXR", seat="14D",
         payment="ĐÃ TRẢ",  status="THÀNH CÔNG",  price="$115"),
    dict(pnr="JJMK39", name="Trần Minh Khoa",       date="20 May 2026",
         flight="JJ509", route="SGN→HAN", seat="2C",
         payment="ĐÃ TRẢ",  status="THÀNH CÔNG",  price="$285"),
    dict(pnr="JJTH10", name="Nguyễn Thị Thu Hà",    date="18 May 2026",
         flight="JJ171", route="HAN→DAD", seat="09A",
         payment="ĐÃ HUỶ",  status="ĐÃ HUỶ",     price="$90"),
    dict(pnr="JJLQ55", name="Lê Văn Quân",          date="15 May 2026",
         flight="JJ202", route="SGN→HAN", seat="16B",
         payment="ĐÃ TRẢ",  status="THÀNH CÔNG",  price="$120"),
    dict(pnr="JJHD72", name="Hoàng Đức Thắng",      date="12 May 2026",
         flight="JJ915", route="HAN→SGN", seat="07E",
         payment="CHỜ TRẢ", status="ĐANG XỬ LÝ", price="$130"),
]


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


def _h_sep(alpha: int = 200) -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setFixedHeight(1)
    f.setStyleSheet(f"background:rgba(228,230,240,{alpha}); border:none;")
    return f


def _icon_btn(icon: str, tip: str = "") -> QPushButton:
    btn = QPushButton(icon)
    btn.setFixedSize(30, 30)
    btn.setToolTip(tip)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent; border: none;
            font-size: 15px; color: {C_GRAY}; border-radius: 6px;
        }}
        QPushButton:hover {{ background: {C_LGRAY}; color: {C_MID}; }}
        QPushButton:pressed {{ background: {C_BORDER}; }}
    """)
    return btn


# ─────────────────────────────────────────────────────────────────────────────
# Seat Badge  ✈ 12A  (viên tối tròn)
# ─────────────────────────────────────────────────────────────────────────────
class SeatBadge(QWidget):
    def __init__(self, seat: str, parent=None):
        super().__init__(parent)
        self.seat = seat
        self.setFixedSize(78, 30)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Nền đen bo góc
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(C_DARK)))
        bg = QPainterPath()
        bg.addRoundedRect(0, 0, w, h, 10, 10)
        p.drawPath(bg)

        # Text  ✈ + seat
        p.setPen(QPen(QColor("#FFFFFF")))
        f = QFont(); f.setPointSize(9); f.setWeight(QFont.Medium)
        p.setFont(f)
        p.drawText(0, 0, w, h, Qt.AlignCenter, f"✈  {self.seat}")


# ─────────────────────────────────────────────────────────────────────────────
# Colored Text Badge  (thanh toán / trạng thái)
# ─────────────────────────────────────────────────────────────────────────────
class TextBadge(QLabel):
    def __init__(self, text: str, fg: str, bg: str, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(26)
        self.setContentsMargins(10, 0, 10, 0)
        self.setStyleSheet(f"""
            QLabel {{
                font-size: 11px; font-weight: 700;
                color: {fg}; background: {bg};
                border-radius: 6px; border: none;
                letter-spacing: 0.5px;
            }}
        """)


# ─────────────────────────────────────────────────────────────────────────────
# Table Header
# ─────────────────────────────────────────────────────────────────────────────
class TableHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setStyleSheet("background:transparent;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)

        cols = [
            ("MÃ PNR",           COL["pnr"],     Qt.AlignLeft),
            ("HÀNH KHÁCH",        0,              Qt.AlignLeft),
            ("CHUYẾN BAY /\nTUYẾN", COL["flight"], Qt.AlignLeft),
            ("SỐ GHẾ",           COL["seat"],    Qt.AlignCenter),
            ("THANH\nTOÁN",      COL["payment"], Qt.AlignCenter),
            ("TRẠNG\nTHÁI",      COL["status"],  Qt.AlignCenter),
            ("GIÁ",              COL["price"],   Qt.AlignRight),
            ("THAO TÁC",         COL["actions"], Qt.AlignCenter),
        ]
        for text, width, align in cols:
            lbl = QLabel(text)
            lbl.setAlignment(align | Qt.AlignVCenter)
            lbl.setStyleSheet(
                f"font-size:10px; font-weight:600; color:{C_GRAY};"
                f" letter-spacing:1px; background:transparent; border:none;"
                f" line-height:1.4;"
            )
            if width == 0:
                lay.addWidget(lbl, 1)
            else:
                lbl.setFixedWidth(width)
                lay.addWidget(lbl)


# ─────────────────────────────────────────────────────────────────────────────
# Booking Row  (một dòng dữ liệu)
# ─────────────────────────────────────────────────────────────────────────────
class BookingRow(QWidget):
    view_clicked   = Signal(dict)
    edit_clicked   = Signal(dict)
    print_clicked  = Signal(dict)

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data = data
        self.setFixedHeight(76)
        self.setStyleSheet(f"background:{C_WHITE};")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)

        # ── MÃ PNR ──────────────────────────────────────────────────────────
        pnr_lbl = _lbl(data["pnr"], 13, 700, C_RED)
        pnr_lbl.setFixedWidth(COL["pnr"])
        lay.addWidget(pnr_lbl)

        # ── HÀNH KHÁCH ──────────────────────────────────────────────────────
        pax_col = QVBoxLayout()
        pax_col.setSpacing(3)
        pax_col.setAlignment(Qt.AlignVCenter)
        pax_col.addWidget(_lbl(data["name"], 13, 700, C_TEXT))
        pax_col.addWidget(_lbl(data["date"], 11, 400, C_GRAY))
        lay.addLayout(pax_col, 1)

        # ── CHUYẾN BAY / TUYẾN ──────────────────────────────────────────────
        flt_col = QVBoxLayout()
        flt_col.setSpacing(3)
        flt_col.setAlignment(Qt.AlignVCenter)
        flt_col.addWidget(_lbl(data["flight"], 13, 700, C_TEXT))
        flt_col.addWidget(_lbl(data["route"],  11, 400, C_GRAY))
        flt_w = QWidget()
        flt_w.setFixedWidth(COL["flight"])
        flt_w.setStyleSheet("background:transparent;")
        flt_w.setLayout(flt_col)
        lay.addWidget(flt_w)

        # ── SỐ GHẾ ──────────────────────────────────────────────────────────
        seat_w = QWidget()
        seat_w.setFixedWidth(COL["seat"])
        seat_w.setStyleSheet("background:transparent;")
        sl = QHBoxLayout(seat_w)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setAlignment(Qt.AlignCenter)
        sl.addWidget(SeatBadge(data["seat"]))
        lay.addWidget(seat_w)

        # ── THANH TOÁN ──────────────────────────────────────────────────────
        pay_fg, pay_bg = PAY_COLORS.get(data["payment"], (C_GRAY, C_LGRAY))
        pay_badge = TextBadge(data["payment"], pay_fg, pay_bg)
        pay_badge.setFixedWidth(COL["payment"] - 10)
        pay_w = QWidget()
        pay_w.setFixedWidth(COL["payment"])
        pay_w.setStyleSheet("background:transparent;")
        pwl = QHBoxLayout(pay_w)
        pwl.setContentsMargins(0, 0, 0, 0)
        pwl.setAlignment(Qt.AlignCenter)
        pwl.addWidget(pay_badge)
        lay.addWidget(pay_w)

        # ── TRẠNG THÁI ──────────────────────────────────────────────────────
        sts_fg, sts_bg = STS_COLORS.get(data["status"], (C_GRAY, C_LGRAY))
        sts_badge = TextBadge(data["status"], sts_fg, sts_bg)
        sts_badge.setFixedWidth(COL["status"] - 10)
        sts_w = QWidget()
        sts_w.setFixedWidth(COL["status"])
        sts_w.setStyleSheet("background:transparent;")
        swl = QHBoxLayout(sts_w)
        swl.setContentsMargins(0, 0, 0, 0)
        swl.setAlignment(Qt.AlignCenter)
        swl.addWidget(sts_badge)
        lay.addWidget(sts_w)

        # ── GIÁ ─────────────────────────────────────────────────────────────
        price_lbl = _lbl(data["price"], 14, 700, C_TEXT)
        price_lbl.setFixedWidth(COL["price"])
        price_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lay.addWidget(price_lbl)

        # ── THAO TÁC ────────────────────────────────────────────────────────
        act_w = QWidget()
        act_w.setFixedWidth(COL["actions"])
        act_w.setStyleSheet("background:transparent;")
        al = QHBoxLayout(act_w)
        al.setContentsMargins(0, 0, 0, 0)
        al.setSpacing(4)
        al.setAlignment(Qt.AlignCenter)

        btn_view  = _icon_btn("👁",  "Xem chi tiết")
        btn_edit  = _icon_btn("✏",  "Chỉnh sửa")
        btn_print = _icon_btn("🖨",  "In vé")

        btn_view.clicked.connect(lambda: self.view_clicked.emit(self.data))
        btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.data))
        btn_print.clicked.connect(lambda: self.print_clicked.emit(self.data))

        al.addWidget(btn_view)
        al.addWidget(btn_edit)
        al.addWidget(btn_print)
        lay.addWidget(act_w)

    def enterEvent(self, e):
        self.setStyleSheet(f"background:#FAFBFF;")

    def leaveEvent(self, e):
        self.setStyleSheet(f"background:{C_WHITE};")


# ─────────────────────────────────────────────────────────────────────────────
# Search Bar  (card trắng + viền đỏ trái)
# ─────────────────────────────────────────────────────────────────────────────
class SearchBar(QWidget):
    search_changed  = Signal(str)
    filter_changed  = Signal(str)
    refresh_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        self.setStyleSheet(f"""
            SearchBar {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-left: 3px solid {C_RED};
                border-radius: 12px;
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        # Icon tìm kiếm
        search_ico = _lbl("🔍", 16, 400, C_GRAY)
        lay.addWidget(search_ico)

        # Input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Tìm theo mã PNR, tên khách, email hoặc số hiệu bay..."
        )
        self.search_input.setFrame(False)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent; border: none;
                font-size: 13px; color: {C_TEXT};
            }}
        """)
        self.search_input.textChanged.connect(self.search_changed)
        lay.addWidget(self.search_input, 1)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background:{C_BORDER}; border:none;")
        lay.addWidget(sep)

        # Dropdown trạng thái
        self.combo = QComboBox()
        self.combo.addItems([
            "TẤT CẢ TRẠNG THÁI",
            "THÀNH CÔNG",
            "ĐANG XỬ LÝ",
            "ĐÃ HUỶ",
        ])
        self.combo.setFixedWidth(200)
        self.combo.setFixedHeight(34)
        self.combo.setStyleSheet(f"""
            QComboBox {{
                background: transparent; border: none;
                font-size: 12px; font-weight: 600;
                color: {C_MID}; padding: 0 8px;
            }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {C_GRAY};
                width: 0; height: 0;
            }}
            QComboBox QAbstractItemView {{
                background: {C_WHITE}; border: 1px solid {C_BORDER};
                border-radius: 8px; padding: 4px;
                selection-background-color: {C_RED_L};
                selection-color: {C_RED};
                font-size: 12px; font-weight: 600;
            }}
        """)
        self.combo.currentTextChanged.connect(self.filter_changed)
        lay.addWidget(self.combo)

        # Nút Refresh
        ref_btn = _icon_btn("↻", "Làm mới dữ liệu")
        ref_btn.setFixedSize(32, 32)
        ref_btn.clicked.connect(self.refresh_clicked)
        lay.addWidget(ref_btn)

        # Icon filter
        filter_ico = _icon_btn("⊟", "Bộ lọc nâng cao")
        filter_ico.setFixedSize(32, 32)
        lay.addWidget(filter_ico)


# ─────────────────────────────────────────────────────────────────────────────
# Booking Table  (header + danh sách rows)
# ─────────────────────────────────────────────────────────────────────────────
class BookingTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            BookingTable {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 14px;
            }}
        """)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        # Header cố định
        self._root.addWidget(TableHeader())
        self._root.addWidget(_h_sep())

        # Vùng chứa rows (sẽ được xoá + thêm lại khi refresh/filter)
        self._rows_container = QWidget()
        self._rows_container.setStyleSheet("background:transparent;")
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setContentsMargins(0, 0, 0, 0)
        self._rows_layout.setSpacing(0)
        self._root.addWidget(self._rows_container)
        self._root.addStretch()

        self._current_rows: list[BookingRow] = []

    # ── Cập nhật nội dung bảng ──────────────────────────────────────────────
    def populate(self, data: list[dict]):
        # Xoá rows cũ
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._current_rows.clear()

        if not data:
            empty = _lbl("Không tìm thấy kết quả phù hợp.", 14, 400, C_GRAY)
            empty.setAlignment(Qt.AlignCenter)
            empty.setContentsMargins(0, 40, 0, 40)
            self._rows_layout.addWidget(empty)
            return

        for i, item in enumerate(data):
            row = BookingRow(item)
            row.view_clicked.connect(self._on_view)
            row.edit_clicked.connect(self._on_edit)
            row.print_clicked.connect(self._on_print)
            self._rows_layout.addWidget(row)
            self._current_rows.append(row)
            if i < len(data) - 1:
                self._rows_layout.addWidget(_h_sep())

    # ── Handlers ────────────────────────────────────────────────────────────
    def _on_view(self, data: dict):
        QMessageBox.information(
            self, "Chi tiết đặt chỗ",
            f"Mã PNR : {data['pnr']}\n"
            f"Hành khách: {data['name']}\n"
            f"Chuyến bay: {data['flight']}  ({data['route']})\n"
            f"Số ghế   : {data['seat']}\n"
            f"Thanh toán: {data['payment']}\n"
            f"Trạng thái: {data['status']}\n"
            f"Giá vé   : {data['price']}"
        )

    def _on_edit(self, data: dict):
        QMessageBox.information(self, "Chỉnh sửa",
                                f"Mở form chỉnh sửa booking {data['pnr']}…")

    def _on_print(self, data: dict):
        QMessageBox.information(self, "In vé",
                                f"Đang in vé cho {data['name']} — {data['pnr']}…")


# ─────────────────────────────────────────────────────────────────────────────
# Page Header
# ─────────────────────────────────────────────────────────────────────────────
class PageHeader(QWidget):
    new_clicked    = Signal()
    export_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)
        self.setStyleSheet("background:transparent; border:none;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        # Tiêu đề
        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        text_col.addWidget(_lbl("Quản lý Đặt chỗ", 26, 800, C_TEXT))
        text_col.addWidget(_lbl("Theo dõi và quản lý danh sách hành khách đặt vé",
                                13, 400, C_GRAY))
        lay.addLayout(text_col)
        lay.addStretch()

        # Nút XUẤT DỮ LIỆU
        export = QPushButton("  ↓  XUẤT DỮ LIỆU")
        export.setFixedHeight(42)
        export.setCursor(Qt.PointingHandCursor)
        export.clicked.connect(self.export_clicked)
        export.setStyleSheet(f"""
            QPushButton {{
                background: {C_WHITE}; border: 1.5px solid {C_BORDER};
                border-radius: 10px; font-size: 12px; font-weight: 700;
                color: {C_MID}; padding: 0 18px; letter-spacing: 0.5px;
            }}
            QPushButton:hover {{ background: {C_LGRAY}; border-color: {C_GRAY}; }}
            QPushButton:pressed {{ background: {C_BORDER}; }}
        """)

        # Nút ĐẶT CHỖ MỚI
        new_btn = QPushButton("  +  ĐẶT CHỖ MỚI")
        new_btn.setFixedHeight(42)
        new_btn.setCursor(Qt.PointingHandCursor)
        new_btn.clicked.connect(self.new_clicked)
        new_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_RED}; border: none;
                border-radius: 10px; font-size: 12px; font-weight: 800;
                color: white; padding: 0 20px; letter-spacing: 0.5px;
            }}
            QPushButton:hover {{ background: #C62828; }}
            QPushButton:pressed {{ background: #B71C1C; }}
        """)

        lay.addWidget(export)
        lay.addSpacing(10)
        lay.addWidget(new_btn)


# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
class Footer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setStyleSheet("background:transparent; border:none;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        lay.addWidget(_lbl(
            "© 2026 HỆ THỐNG QUẢN TRỊ JETJET  /  LƯU HÀNH NỘI BỘ",
            10, 400, C_GRAY, 0.5
        ))
        lay.addStretch()
        lay.addWidget(_lbl("CHÍNH SÁCH BẢO MẬT", 10, 600, C_GRAY, 1.0))
        lay.addSpacing(20)

        dot = QLabel("●")
        dot.setStyleSheet(f"color:{C_RED}; font-size:10px; background:transparent; border:none;")
        lay.addWidget(dot)
        lay.addSpacing(4)
        lay.addWidget(_lbl("PHIÊN BẢN 2.5.0 ÔN ĐỊNH", 10, 700, C_RED, 0.5))


# ─────────────────────────────────────────────────────────────────────────────
# DB loader  (fallback về SAMPLE nếu DB chưa sẵn sàng)
# ─────────────────────────────────────────────────────────────────────────────
def _load_from_db() -> list[dict] | None:
    try:
        from database.db import get_connection as connect_db

        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                b.booking_id,
                p.full_name,
                b.booking_date,
                f.flight_id,
                f.departure,
                f.destination,
                b.seat_number,
                b.payment_status,
                b.booking_status,
                b.total_amount
            FROM bookings b
            JOIN passengers p
                ON b.passenger_id = p.passenger_id
            JOIN flights f
                ON b.flight_id = f.flight_id
            ORDER BY b.booking_date DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return None

        payment_map = {
            "Paid": "ĐÃ TRẢ",
            "Pending": "CHỜ TRẢ",
            "Cancelled": "ĐÃ HUỶ"
        }

        status_map = {
            "Confirmed": "THÀNH CÔNG",
            "Pending": "ĐANG XỬ LÝ",
            "Cancelled": "ĐÃ HUỶ"
        }

        result = []

        for r in rows:
            (
                booking_id,
                full_name,
                booking_date,
                flight_id,
                departure,
                destination,
                seat_number,
                payment_status,
                booking_status,
                total_amount
            ) = r

            # Tạo mã PNR
            pnr = f"JJ{booking_id:04d}"

            # Format ngày
            try:
                dt = datetime.strptime(
                    str(booking_date)[:10],
                    "%Y-%m-%d"
                )
                date_str = dt.strftime("%d %b %Y")
            except Exception:
                date_str = str(booking_date)

            result.append({
                "pnr": pnr,
                "name": full_name,
                "date": date_str,
                "flight": f"JJ{flight_id:03d}",
                "route": f"{departure}-{destination}",
                "seat": seat_number or "--",
                "payment": payment_map.get(
                    payment_status,
                    "CHỜ TRẢ"
                ),
                "status": status_map.get(
                    booking_status,
                    "ĐANG XỬ LÝ"
                ),
                "price": f"${int(total_amount)}"
                if total_amount else "$0",
            })

        return result

    except Exception as exc:
        print(f"[BookingPage] DB ERROR: {exc}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Booking Page  —  tổng hợp
# ─────────────────────────────────────────────────────────────────────────────
class BookingsPage(QWidget):
    """
    Trang quản lý đặt chỗ.

    Tích hợp vào MainWindow:
        from ui.pages.booking_page import BookingPage
        self._pages.addWidget(BookingPage())
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C_BG};")
        self._all_data: list[dict] = []

        # ── Scroll wrapper ───────────────────────────────────────────────────
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

        # ── Page header ─────────────────────────────────────────────────────
        hdr = PageHeader()
        hdr.new_clicked.connect(self._on_new)
        hdr.export_clicked.connect(self._on_export)
        root.addWidget(hdr)

        # ── Search bar ──────────────────────────────────────────────────────
        self._search_bar = SearchBar()
        self._search_bar.search_changed.connect(self._apply_filter)
        self._search_bar.filter_changed.connect(self._apply_filter)
        self._search_bar.refresh_clicked.connect(self.refresh)
        root.addWidget(self._search_bar)

        # ── Table ────────────────────────────────────────────────────────────
        self._table = BookingTable()
        root.addWidget(self._table)

        # ── Footer ───────────────────────────────────────────────────────────
        root.addStretch()
        root.addWidget(_h_sep())
        root.addWidget(Footer())

        # ── Load dữ liệu ─────────────────────────────────────────────────────
        self.refresh()

    # ── Public API ──────────────────────────────────────────────────────────
    def refresh(self):
        """Tải lại dữ liệu từ DB (hoặc sample nếu DB chưa có)."""
        db_data = _load_from_db()
        self._all_data = db_data if db_data else list(SAMPLE)
        self._apply_filter()

    # ── Filter ───────────────────────────────────────────────────────────────
    def _apply_filter(self, *_):
        query  = self._search_bar.search_input.text().strip().lower()
        choice = self._search_bar.combo.currentText()

        filtered = self._all_data
        # Lọc theo trạng thái
        if choice != "TẤT CẢ TRẠNG THÁI":
            filtered = [r for r in filtered if r["status"] == choice]
        # Lọc theo text tìm kiếm
        if query:
            filtered = [
                r for r in filtered
                if (query in r["pnr"].lower()
                    or query in r["name"].lower()
                    or query in r["flight"].lower()
                    or query in r["route"].lower())
            ]
        self._table.populate(filtered)

    # ── Handlers ─────────────────────────────────────────────────────────────
    def _on_new(self):
        QMessageBox.information(self, "Đặt chỗ mới",
                                "Mở form đặt chỗ mới…\n(Tích hợp form sau)")

    def _on_export(self):
        QMessageBox.information(self, "Xuất dữ liệu",
                                "Đang xuất danh sách đặt chỗ ra file CSV…")


# ─────────────────────────────────────────────────────────────────────────────
# Chạy thử độc lập
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = QMainWindow()
    win.setWindowTitle("JetJet Air — Quản lý Đặt chỗ")
    win.resize(1380, 860)
    win.setCentralWidget(BookingsPage())
    win.show()
    sys.exit(app.exec())