"""
ui/pages/booking_page.py
────────────────────────────────────────
JetJet Management App — Booking Page
"""

from __future__ import annotations

import random
import string
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QFont,
    QPainterPath,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QLineEdit,
    QComboBox,
    QApplication,
    QMainWindow,
    QMessageBox,
)

from shared.services.booking_service import (
    get_all_bookings,
)

# ─────────────────────────────────────
# COLORS
# ─────────────────────────────────────
C_BG = "#F4F6FA"
C_WHITE = "#FFFFFF"
C_BORDER = "#E4E6F0"
C_TEXT = "#1A1A2E"
C_MID = "#4A4A6A"
C_GRAY = "#9B9BB4"
C_LGRAY = "#F0F1F8"
C_RED = "#E53935"
C_RED_L = "#FFEBEE"
C_DARK = "#1A1A2E"

PAY_COLORS = {
    "PAID": ("#166534", "#DCFCE7"),
    "PENDING": ("#92400E", "#FEF3C7"),
    "CANCELLED": ("#991B1B", "#FEE2E2"),
}

STS_COLORS = {
    "CONFIRMED": ("#1E40AF", "#DBEAFE"),
    "PENDING": ("#475569", "#F1F5F9"),
    "CANCELLED": ("#991B1B", "#FEE2E2"),
}

COL = {
    "pnr": 120,
    "name": 0,
    "flight": 140,
    "seat": 100,
    "payment": 120,
    "status": 120,
    "price": 100,
    "actions": 120,
}


# ─────────────────────────────────────
# HELPERS
# ─────────────────────────────────────
def _lbl(
    text: str,
    size: int = 13,
    weight: int = 400,
    color: str = C_TEXT,
):
    label = QLabel(text)

    font_weight = {
        400: "normal",
        500: "500",
        600: "600",
        700: "bold",
        800: "800",
    }.get(weight, "normal")

    label.setStyleSheet(f"""
        font-size: {size}px;
        font-weight: {font_weight};
        color: {color};
        border: none;
        background: transparent;
    """)

    return label


def _separator():
    line = QFrame()

    line.setFrameShape(QFrame.HLine)

    line.setFixedHeight(1)

    line.setStyleSheet(f"""
        background: {C_BORDER};
        border: none;
    """)

    return line


def _icon_btn(icon: str, tooltip=""):

    btn = QPushButton(icon)

    btn.setFixedSize(30, 30)

    btn.setCursor(Qt.PointingHandCursor)

    btn.setToolTip(tooltip)

    btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            border: none;
            border-radius: 6px;
            color: {C_GRAY};
            font-size: 15px;
        }}

        QPushButton:hover {{
            background: {C_LGRAY};
            color: {C_MID};
        }}
    """)

    return btn


# ─────────────────────────────────────
# BADGES
# ─────────────────────────────────────
class TextBadge(QLabel):

    def __init__(self, text, fg, bg):
        super().__init__(text)

        self.setAlignment(Qt.AlignCenter)

        self.setFixedHeight(26)

        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
                padding: 0 10px;
            }}
        """)


class SeatBadge(QWidget):

    def __init__(self, seat):
        super().__init__()

        self.seat = seat

        self.setFixedSize(75, 30)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()

        path.addRoundedRect(
            0,
            0,
            self.width(),
            self.height(),
            10,
            10,
        )

        painter.fillPath(
            path,
            QBrush(QColor(C_DARK))
        )

        painter.setPen(QPen(QColor(C_WHITE)))

        font = QFont()

        font.setPointSize(9)

        font.setBold(True)

        painter.setFont(font)

        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            f"✈ {self.seat}"
        )


# ─────────────────────────────────────
# ROW
# ─────────────────────────────────────
class BookingRow(QWidget):

    def __init__(self, data: dict):
        super().__init__()

        self.data = data

        self.setFixedHeight(76)

        self.setStyleSheet(f"""
            background: {C_WHITE};
        """)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(20, 0, 20, 0)

        layout.setSpacing(0)

        # PNR
        pnr = _lbl(
            data["pnr"],
            13,
            700,
            C_RED
        )

        pnr.setFixedWidth(COL["pnr"])

        layout.addWidget(pnr)

        # PASSENGER
        passenger_col = QVBoxLayout()

        passenger_col.setSpacing(3)

        passenger_col.addWidget(
            _lbl(
                data["name"],
                13,
                700,
            )
        )

        passenger_col.addWidget(
            _lbl(
                data["date"],
                11,
                400,
                C_GRAY
            )
        )

        layout.addLayout(
            passenger_col,
            1
        )

        # FLIGHT
        flight_col = QVBoxLayout()

        flight_col.setSpacing(3)

        flight_col.addWidget(
            _lbl(
                data["flight"],
                13,
                700
            )
        )

        flight_col.addWidget(
            _lbl(
                data["route"],
                11,
                400,
                C_GRAY
            )
        )

        flight_wrap = QWidget()

        flight_wrap.setFixedWidth(
            COL["flight"]
        )

        fw_layout = QVBoxLayout(flight_wrap)

        fw_layout.setContentsMargins(0, 0, 0, 0)

        fw_layout.addLayout(flight_col)

        layout.addWidget(flight_wrap)

        # SEAT
        seat_wrap = QWidget()

        seat_wrap.setFixedWidth(
            COL["seat"]
        )

        sw_layout = QHBoxLayout(seat_wrap)

        sw_layout.setAlignment(Qt.AlignCenter)

        sw_layout.addWidget(
            SeatBadge(data["seat"])
        )

        layout.addWidget(seat_wrap)

        # PAYMENT
        pay_fg, pay_bg = PAY_COLORS.get(
            data["payment"],
            (C_GRAY, C_LGRAY)
        )

        pay_badge = TextBadge(
            data["payment"],
            pay_fg,
            pay_bg
        )

        pay_wrap = QWidget()

        pay_wrap.setFixedWidth(
            COL["payment"]
        )

        pw_layout = QHBoxLayout(pay_wrap)

        pw_layout.setAlignment(Qt.AlignCenter)

        pw_layout.addWidget(pay_badge)

        layout.addWidget(pay_wrap)

        # STATUS
        sts_fg, sts_bg = STS_COLORS.get(
            data["status"],
            (C_GRAY, C_LGRAY)
        )

        sts_badge = TextBadge(
            data["status"],
            sts_fg,
            sts_bg
        )

        sts_wrap = QWidget()

        sts_wrap.setFixedWidth(
            COL["status"]
        )

        st_layout = QHBoxLayout(sts_wrap)

        st_layout.setAlignment(Qt.AlignCenter)

        st_layout.addWidget(sts_badge)

        layout.addWidget(sts_wrap)

        # PRICE
        price = _lbl(
            data["price"],
            14,
            700
        )

        price.setFixedWidth(
            COL["price"]
        )

        price.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter
        )

        layout.addWidget(price)

        # ACTIONS
        actions = QWidget()

        actions.setFixedWidth(
            COL["actions"]
        )

        actions_layout = QHBoxLayout(actions)

        actions_layout.setSpacing(4)

        actions_layout.setAlignment(Qt.AlignCenter)

        btn_view = _icon_btn("👁")

        btn_edit = _icon_btn("✏")

        btn_print = _icon_btn("🖨")

        btn_view.clicked.connect(
            lambda:
            QMessageBox.information(
                self,
                "Booking",
                f"Booking: {data['pnr']}"
            )
        )

        actions_layout.addWidget(btn_view)

        actions_layout.addWidget(btn_edit)

        actions_layout.addWidget(btn_print)

        layout.addWidget(actions)


# ─────────────────────────────────────
# TABLE
# ─────────────────────────────────────
class BookingTable(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet(f"""
            background: {C_WHITE};
            border: 1px solid {C_BORDER};
            border-radius: 14px;
        """)

        self.root = QVBoxLayout(self)

        self.root.setContentsMargins(0, 0, 0, 0)

        self.root.setSpacing(0)

        self.rows_widget = QWidget()

        self.rows_layout = QVBoxLayout(
            self.rows_widget
        )

        self.rows_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.rows_layout.setSpacing(0)

        self.root.addWidget(self.rows_widget)

    def populate(self, data):

        while self.rows_layout.count():

            item = self.rows_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        if not data:

            empty = _lbl(
                "No bookings found.",
                14,
                400,
                C_GRAY
            )

            empty.setAlignment(Qt.AlignCenter)

            empty.setContentsMargins(
                0,
                50,
                0,
                50
            )

            self.rows_layout.addWidget(empty)

            return

        for i, item in enumerate(data):

            row = BookingRow(item)

            self.rows_layout.addWidget(row)

            if i < len(data) - 1:
                self.rows_layout.addWidget(
                    _separator()
                )


# ─────────────────────────────────────
# SEARCH BAR
# ─────────────────────────────────────
class SearchBar(QWidget):

    search_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.setFixedHeight(56)

        self.setStyleSheet(f"""
            background: {C_WHITE};
            border: 1px solid {C_BORDER};
            border-left: 3px solid {C_RED};
            border-radius: 12px;
        """)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            16,
            0,
            16,
            0
        )

        icon = _lbl(
            "🔍",
            16,
            400,
            C_GRAY
        )

        layout.addWidget(icon)

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Search bookings..."
        )

        self.search_input.setFrame(False)

        self.search_input.textChanged.connect(
            self.search_changed
        )

        self.search_input.setStyleSheet(f"""
            background: transparent;
            border: none;
            font-size: 13px;
            color: {C_TEXT};
        """)

        layout.addWidget(
            self.search_input,
            1
        )


# ─────────────────────────────────────
# PAGE
# ─────────────────────────────────────
class BookingsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet(f"""
            background: {C_BG};
        """)

        self.all_data = []

        outer = QVBoxLayout(self)

        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(QFrame.NoFrame)

        outer.addWidget(scroll)

        inner = QWidget()

        scroll.setWidget(inner)

        root = QVBoxLayout(inner)

        root.setContentsMargins(
            28,
            20,
            28,
            20
        )

        root.setSpacing(16)

        # TITLE
        title = _lbl(
            "Booking Management",
            26,
            800
        )

        root.addWidget(title)

        subtitle = _lbl(
            "Manage airline bookings",
            13,
            400,
            C_GRAY
        )

        root.addWidget(subtitle)

        # SEARCH
        self.search_bar = SearchBar()

        self.search_bar.search_changed.connect(
            self.apply_filter
        )

        root.addWidget(self.search_bar)

        # TABLE
        self.table = BookingTable()

        root.addWidget(self.table)

        root.addStretch()

        self.refresh()

    # ─────────────────────────────────
    # LOAD DATA
    # ─────────────────────────────────
    def refresh(self):

        self.all_data = []

        try:

            bookings = get_all_bookings()

            for booking in bookings:

                pnr = ''.join(
                    random.choices(
                        string.ascii_uppercase +
                        string.digits,
                        k=6
                    )
                )

                self.all_data.append({
                    "pnr":
                        pnr,

                    "name":
                        booking.passenger_name,

                    "date":
                        str(booking.booking_date),

                    "flight":
                        booking.flight_number,

                    "route":
                        f"{booking.departure}-{booking.destination}",

                    "seat":
                        booking.seat_number or "N/A",

                    "payment":
                        "PAID",

                    "status":
                        booking.status.upper(),

                    "price":
                        f"${booking.total_price}",
                })

        except Exception as e:

            print(
                f"[BookingPage] {e}"
            )

        self.apply_filter()

    # ─────────────────────────────────
    # FILTER
    # ─────────────────────────────────
    def apply_filter(self, *_):

        query = (
            self.search_bar
            .search_input
            .text()
            .lower()
            .strip()
        )

        data = self.all_data

        if query:

            data = [
                item
                for item in data
                if (
                    query in item["pnr"].lower()
                    or query in item["name"].lower()
                    or query in item["flight"].lower()
                )
            ]

        self.table.populate(data)
