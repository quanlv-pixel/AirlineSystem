"""
flight_detail_page.py
---------------------
Ảnh 2 — Chi tiết Chuyến bay: Bước 2
Hiển thị khi nhấn "CHỌN" ở trang tìm kiếm.
"""
from __future__ import annotations
import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (QColor, QPainter, QBrush, QPen,
                            QPainterPath, QLinearGradient, QFont)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy
)
from booking_app.ui.pages.booking_shared import (lbl, h_sep, card_style, red_btn, page_header,
                             NavBar, NavLogo,
                             C_RED, C_RED2, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY,
                             C_GREEN, C_BLUE, C_ORANGE)

SAMPLE_FLIGHT = dict(
    fid=1, code="JJ101", aircraft="AIRBUS A321 NEO",
    dep="SGN", dst="HAN", dep_t="08:00", arr_t="10:15",
    dur="2H 15M", direct=True, seats=42, price=120,
    dep_full="Tân Sơn Nhất (Ga quốc nội)",
    dst_full="Nội Bài (Ga quốc nội)",
)


# ─────────────────────────────────────────────────────────────────────────────
# Flight timeline (đường kẻ giữa với icon máy bay)
# ─────────────────────────────────────────────────────────────────────────────
class FlightTimeline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(36)
        self.setStyleSheet("background:transparent;")

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cy = h // 2

        # Dashed line left
        pen = QPen(QColor(C_BORDER), 1.5, Qt.DashLine)
        pen.setDashPattern([6, 4])
        p.setPen(pen)
        p.drawLine(0, cy, w // 2 - 22, cy)
        p.drawLine(w // 2 + 22, cy, w, cy)

        # Plane icon center
        p.setPen(QPen(QColor(C_RED)))
        f = QFont(); f.setPointSize(16)
        p.setFont(f)
        p.drawText(w // 2 - 14, 0, 28, h, Qt.AlignCenter, "✈")


# ─────────────────────────────────────────────────────────────────────────────
# Flight detail card (left big card)
# ─────────────────────────────────────────────────────────────────────────────
class FlightDetailCard(QWidget):
    def __init__(self, flight: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(20))

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(0)

        # ── Header: badge + flight code + status ───────────────────────────
        hdr = QHBoxLayout()
        badge = _dark_badge(52)
        hdr.addWidget(badge)
        hdr.addSpacing(16)

        code_col = QVBoxLayout()
        code_col.setSpacing(3)
        code_col.addWidget(lbl(flight["code"], 16, 800, C_TEXT))
        code_col.addWidget(lbl(flight["aircraft"], 12, 600, C_RED))
        hdr.addLayout(code_col)
        hdr.addStretch()

        status_col = QVBoxLayout()
        status_col.setAlignment(Qt.AlignRight)
        status_col.addWidget(lbl("TRẠNG THÁI", 10, 600, C_GRAY, 1.0))
        status_lbl = lbl("ĐANG MỞ BÁN", 12, 700, C_GREEN)
        status_lbl.setAlignment(Qt.AlignRight)
        status_col.addWidget(status_lbl)
        hdr.addLayout(status_col)
        root.addLayout(hdr)
        root.addSpacing(28)

        # ── Times ────────────────────────────────────────────────────────────
        times = QHBoxLayout()
        times.setSpacing(0)

        # Departure
        dep_col = QVBoxLayout()
        dep_col.setSpacing(4)
        dep_t = lbl(flight["dep_t"], 52, 800, C_TEXT)
        dep_t.setStyleSheet(dep_t.styleSheet() + "line-height:1;")
        dep_col.addWidget(dep_t)
        dep_col.addWidget(lbl(flight["dep"], 18, 800, C_TEXT))
        dep_col.addWidget(lbl(flight.get("dep_full", ""), 12, 400, C_GRAY))
        times.addLayout(dep_col)

        # Timeline center
        tl_col = QVBoxLayout()
        tl_col.setAlignment(Qt.AlignCenter)
        tl_col.addWidget(lbl(flight["dur"], 11, 600, C_GRAY))
        tl_col.addWidget(FlightTimeline())
        direct = QHBoxLayout()
        direct.setAlignment(Qt.AlignCenter)
        direct.setSpacing(5)
        direct.addWidget(lbl("●", 10, 700, C_RED))
        direct.addWidget(lbl("BAY THẲNG (DIRECT)", 11, 600, C_GRAY, 0.5))
        tl_col.addLayout(direct)
        times.addLayout(tl_col, 1)

        # Arrival
        arr_col = QVBoxLayout()
        arr_col.setSpacing(4)
        arr_col.setAlignment(Qt.AlignRight)
        arr_t = lbl(flight["arr_t"], 52, 800, C_TEXT)
        arr_col.addWidget(arr_t)
        arr_col.addWidget(lbl(flight["dst"], 18, 800, C_TEXT))
        arr_col.addWidget(lbl(flight.get("dst_full", ""), 12, 400, C_GRAY))
        times.addLayout(arr_col)

        root.addLayout(times)
        root.addSpacing(28)
        root.addWidget(h_sep())
        root.addSpacing(18)

        # ── Footer info ──────────────────────────────────────────────────────
        info_row = QHBoxLayout()
        info_row.setSpacing(0)
        for icon, key, val in [
            ("🗺", "LỖ TRÌNH", "7,240 km / 4,498 miles"),
            ("🕐", "DỰ KIẾN",  "Đúng giờ (On-time)"),
            ("🛡", "BẢO HIỂM", "Đã bao gồm trong giá"),
        ]:
            item = QVBoxLayout()
            item.setSpacing(4)
            top = QHBoxLayout()
            top.setSpacing(6)
            top.addWidget(lbl(icon, 14, 400, C_GRAY))
            top.addWidget(lbl(key, 11, 600, C_GRAY, 0.5))
            item.addLayout(top)
            item.addWidget(lbl(val, 13, 700, C_TEXT))
            info_row.addLayout(item)
            info_row.addStretch()
        root.addLayout(info_row)


# ─────────────────────────────────────────────────────────────────────────────
# Dark badge (circle airplane)
# ─────────────────────────────────────────────────────────────────────────────
def _dark_badge(size=52):
    w = QWidget(); w.setFixedSize(size, size)
    class _B(QWidget):
        def __init__(self, s): super().__init__(); self.setFixedSize(s, s)
        def paintEvent(self, _):
            p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
            s = self.width()
            pp = QPainterPath(); pp.addEllipse(0, 0, s, s)
            p.fillPath(pp, QBrush(QColor(C_DARK)))
            p.setPen(QPen(QColor(C_WHITE)))
            f = QFont(); f.setPointSize(int(s*0.38)); f.setWeight(QFont.Bold)
            p.setFont(f); p.drawText(0, 0, s, s, Qt.AlignCenter, "✈")
    return _B(size)


# ─────────────────────────────────────────────────────────────────────────────
# Cost summary card (right)
# ─────────────────────────────────────────────────────────────────────────────
class CostCard(QWidget):
    proceed = Signal()

    def __init__(self, flight: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(20))

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(0)

        root.addWidget(lbl("Tổng kết Chi phí", 18, 800, C_TEXT))
        root.addSpacing(20)

        base  = flight["price"]
        tax   = 45
        fee   = 12
        total = base + tax + fee

        for title, amount in [
            ("Giá vé cơ bản",        f"${base}"),
            ("Thuế & Phí sân bay",   f"${tax}"),
            ("Phí quản trị hệ thống", f"${fee}"),
        ]:
            row = QHBoxLayout()
            row.addWidget(lbl(title, 13, 400, C_MID))
            row.addStretch()
            row.addWidget(lbl(amount, 13, 600, C_TEXT))
            root.addLayout(row)
            root.addSpacing(12)

        root.addWidget(h_sep())
        root.addSpacing(16)

        total_row = QHBoxLayout()
        total_row.addWidget(lbl("TỔNG CỘNG", 11, 700, C_GRAY, 1.0))
        total_row.addStretch()
        total_lbl = lbl(f"${total}", 30, 900, C_TEXT)
        total_row.addWidget(total_lbl)
        root.addLayout(total_row)
        root.addSpacing(20)

        btn = red_btn("TIẾP TỤC ĐẶT CHỖ  →", 52)
        btn.clicked.connect(self.proceed)
        root.addWidget(btn)
        root.addSpacing(12)

        note = QHBoxLayout()
        note.setSpacing(5)
        note.addWidget(lbl("●", 10, 400, C_GRAY))
        note.addWidget(lbl("GIÁ VÉ CÓ THỂ THAY ĐỔI SAU 10 PHÚT",
                           10, 500, C_GRAY, 0.5))
        root.addLayout(note)
        root.addStretch()


# ─────────────────────────────────────────────────────────────────────────────
# Baggage info card
# ─────────────────────────────────────────────────────────────────────────────
class BaggageCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(16))

        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 18, 22, 18)
        lay.setSpacing(16)

        icon = lbl("ℹ", 18, 700, C_BLUE)
        icon.setFixedWidth(24)
        lay.addWidget(icon)

        text_col = QVBoxLayout()
        text_col.setSpacing(6)
        text_col.addWidget(lbl("QUY ĐỊNH VỀ HÀNH LÝ", 12, 700, C_TEXT, 1.0))
        for item in ["Miễn phí 07kg hành lý xách tay.",
                     "Ưu đãi mua thêm hành lý ký gửi ngay khi đặt chỗ."]:
            r = QHBoxLayout(); r.setSpacing(6)
            r.addWidget(lbl("•", 12, 400, C_MID))
            r.addWidget(lbl(item, 12, 400, C_MID))
            r.addStretch()
            text_col.addLayout(r)
        lay.addLayout(text_col)


# ─────────────────────────────────────────────────────────────────────────────
# FlightDetailPage
# ─────────────────────────────────────────────────────────────────────────────
class FlightDetailPage(QWidget):
    proceed = Signal(dict)   # phát (flight + cost ctx) khi tiếp tục
    go_back = Signal()

    def __init__(self, flight: dict | None = None, parent=None):
        super().__init__(parent)
        self.flight = flight or SAMPLE_FLIGHT
        self.setStyleSheet(f"background:{C_BG};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent;border:none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.addWidget(scroll)

        inner = QWidget(); inner.setStyleSheet(f"background:{C_BG};")
        scroll.setWidget(inner)

        root = QVBoxLayout(inner)
        root.setContentsMargins(28,24,28,28)
        root.setSpacing(20)

        root.addLayout(page_header(
            "Chi tiết Chuyến bay",
            "Bước 2: Xác nhận lịch trình dự kiến",
            on_back=self.go_back
        ))

        # 2-column layout
        cols = QHBoxLayout(); cols.setSpacing(20)

        # Left
        left = QVBoxLayout(); left.setSpacing(14)
        left.addWidget(FlightDetailCard(self.flight))
        left.addWidget(BaggageCard())
        left.addStretch()
        left_w = QWidget(); left_w.setStyleSheet("background:transparent;")
        left_w.setLayout(left)
        cols.addWidget(left_w, 63)

        # Right
        self._cost = CostCard(self.flight)
        self._cost.proceed.connect(self._on_proceed)
        right_w = QWidget(); right_w.setStyleSheet("background:transparent;")
        rl = QVBoxLayout(right_w)
        rl.setContentsMargins(0,0,0,0)
        rl.addWidget(self._cost)
        rl.addStretch()
        cols.addWidget(right_w, 37)

        root.addLayout(cols)

    def _on_proceed(self):
        ctx = dict(flight=self.flight,
                   base_price=self.flight["price"],
                   tax=45, fee=12,
                   total=self.flight["price"]+57)
        self.proceed.emit(ctx)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = QMainWindow()
    win.setWindowTitle("JetJet Air — Chi tiết Chuyến bay")
    win.resize(1380, 860)
    w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
    lay.addWidget(NavBar(0)); lay.addWidget(FlightDetailPage())
    win.setCentralWidget(w); win.show()
    sys.exit(app.exec())