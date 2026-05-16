"""
confirm_page.py
---------------
Ảnh 6 — Xác nhận Thông tin: Bước 6
Hiển thị khi nhấn "XÁC NHẬN CHỖ NGỒI" ở trang chọn ghế.
"""
from __future__ import annotations
import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QPainterPath, QLinearGradient, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea
)
from booking_shared import (lbl, h_sep, card_style, red_btn, page_header,
                             NavBar, C_RED, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY,
                             C_GREEN, C_BLUE, C_ORANGE)

DEMO_CTX = dict(
    flight=dict(code="JJ101", aircraft="AIRBUS A321 NEO",
                dep="SGN", dst="HAN", dep_t="08:00",
                arr_t="10:15", dur="2H 15M", price=120),
    passenger=dict(name="Lê Văn Quân", email="quanle19112007@gmail.com"),
    seat_labels=["4B","5B"], seat_fee=50,
    base_price=120, tax=45, fee=12, total=177,
)


# ─────────────────────────────────────────────────────────────────────────────
# Flight timeline widget (dashed line + plane icon)
# ─────────────────────────────────────────────────────────────────────────────
class ConfirmTimeline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32)
        self.setStyleSheet("background:transparent;")

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cy = h // 2
        pen = QPen(QColor(C_BORDER), 1.5, Qt.DashLine)
        pen.setDashPattern([6, 4])
        p.setPen(pen)
        p.drawLine(0, cy, w//2 - 18, cy)
        p.drawLine(w//2 + 18, cy, w, cy)
        p.setPen(QPen(QColor(C_RED)))
        f = QFont(); f.setPointSize(14)
        p.setFont(f)
        p.drawText(w//2 - 12, 0, 24, h, Qt.AlignCenter, "✈")


# ─────────────────────────────────────────────────────────────────────────────
# Flight detail card (left big)
# ─────────────────────────────────────────────────────────────────────────────
class FlightSummaryCard(QWidget):
    def __init__(self, flight: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(16))

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(0)

        # Header badge
        hdr = QHBoxLayout(); hdr.setSpacing(10)
        icon_lbl = lbl("✈", 15, 700, C_RED)
        icon_lbl.setFixedWidth(20)
        hdr.addWidget(icon_lbl)
        hdr.addWidget(lbl("CHI TIẾT CHUYẾN BAY", 11, 700, C_TEXT, 1.0))
        hdr.addStretch()
        root.addLayout(hdr)
        root.addSpacing(18)

        # Times row
        times = QHBoxLayout(); times.setSpacing(0)

        # Dep
        dep_c = QVBoxLayout(); dep_c.setSpacing(4)
        dep_c.addWidget(lbl(flight.get("dep_t", "—"), 36, 800, C_TEXT))
        dep_c.addWidget(lbl(flight.get("dep", "—"),   14, 600, C_MID))
        times.addLayout(dep_c)
        times.addStretch()

        # Center
        mid_c = QVBoxLayout(); mid_c.setSpacing(6); mid_c.setAlignment(Qt.AlignCenter)
        mid_c.addWidget(lbl(flight.get("dur", "—"), 11, 500, C_GRAY))
        mid_c.addWidget(ConfirmTimeline())
        times.addLayout(mid_c)
        times.addStretch()

        # Arr
        arr_c = QVBoxLayout(); arr_c.setSpacing(4); arr_c.setAlignment(Qt.AlignRight)
        arr_c.addWidget(lbl(flight.get("arr_t", "—"), 36, 800, C_TEXT))
        arr_c.addWidget(lbl(flight.get("dst", "—"),   14, 600, C_MID))
        times.addLayout(arr_c)
        root.addLayout(times)


# ─────────────────────────────────────────────────────────────────────────────
# Seat badge (dark pill)
# ─────────────────────────────────────────────────────────────────────────────
class SeatPill(QLabel):
    def __init__(self, seat: str, parent=None):
        super().__init__(seat, parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(44, 34)
        self.setStyleSheet(f"""
            QLabel{{
                background:{C_DARK}; color:white;
                border-radius:12px; font-size:13px; font-weight:800;
                border:none;
            }}
        """)


# ─────────────────────────────────────────────────────────────────────────────
# Passenger card + Seat card (row below flight)
# ─────────────────────────────────────────────────────────────────────────────
class PassengerCard(QWidget):
    def __init__(self, pax: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(14))
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18); root.setSpacing(10)

        hdr = QHBoxLayout(); hdr.setSpacing(8)
        hdr.addWidget(lbl("◎", 16, 400, C_RED))
        hdr.addWidget(lbl("HÀNH KHÁCH", 11, 700, C_TEXT, 1.0))
        hdr.addStretch()
        root.addLayout(hdr)

        root.addWidget(lbl(pax.get("name","—"), 18, 700, C_TEXT))
        root.addWidget(lbl(pax.get("email","—"), 12, 400, C_GRAY))


class SeatCard(QWidget):
    def __init__(self, seat_labels: list[str], parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(14))
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18); root.setSpacing(12)

        hdr = QHBoxLayout(); hdr.setSpacing(8)
        hdr.addWidget(lbl("🪑", 16, 400, C_RED))
        hdr.addWidget(lbl("CHỖ NGỒI", 11, 700, C_TEXT, 1.0))
        hdr.addStretch()
        root.addLayout(hdr)

        pills = QHBoxLayout(); pills.setSpacing(10); pills.setAlignment(Qt.AlignLeft)
        for s in seat_labels:
            pills.addWidget(SeatPill(s))
        root.addLayout(pills)


# ─────────────────────────────────────────────────────────────────────────────
# Payment summary card (right)
# ─────────────────────────────────────────────────────────────────────────────
class PaymentSummaryCard(QWidget):
    proceed = Signal()

    def __init__(self, ctx: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(20))
        root = QVBoxLayout(self)
        root.setContentsMargins(24,24,24,24); root.setSpacing(0)

        root.addWidget(lbl("Chi tiết Thanh toán", 18, 800, C_TEXT))
        root.addSpacing(20)

        # ── Sửa lại công thức toán học tách biệt tax và fee ──
        base     = ctx.get("base_price", 120)
        seat_fee = ctx.get("seat_fee", 50)
        tax      = ctx.get("tax", 45)
        fee      = ctx.get("fee", 12)
        total    = base + seat_fee + tax + fee

        for title, amount in [
            ("Giá vé máy bay",        f"${base}"),
            ("Phí chọn ghế",          f"${seat_fee}"),
            ("Thuế & Phí sân bay",    f"${tax}"),
            ("Phí quản trị hệ thống", f"${fee}"),
        ]:
            row = QHBoxLayout()
            row.addWidget(lbl(title, 13, 400, C_MID))
            row.addStretch()
            row.addWidget(lbl(amount, 13, 600, C_TEXT))
            root.addLayout(row)
            root.addSpacing(12)

        root.addWidget(h_sep()); root.addSpacing(16)

        tot_row = QHBoxLayout()
        tot_row.addWidget(lbl("TỔNG THANH TOÁN", 11, 700, C_GRAY, 1.0))
        tot_row.addStretch()
        tot_row.addWidget(lbl(f"${total}", 32, 900, C_RED))
        root.addLayout(tot_row)
        root.addSpacing(20)

        btn = red_btn("THANH TOÁN NGAY  🪪", 52)
        btn.clicked.connect(self.proceed)
        root.addWidget(btn)
        root.addSpacing(16)

        # Security notice
        sec = QWidget()
        sec.setStyleSheet("background:#ECFDF5;border:1px solid #A7F3D0;border-radius:12px;")
        sl = QHBoxLayout(sec); sl.setContentsMargins(14,12,14,12); sl.setSpacing(10)
        sl.addWidget(lbl("🛡", 16, 400, C_GREEN))
        sl.addWidget(lbl("Giao dịch của bạn được bảo mật bởi chuẩn mã hóa "
                         "quốc tế SSL/TLS 1.2", 11, 500, C_MID))
        root.addWidget(sec)
        root.addStretch()


# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
def _footer():
    w = QWidget(); w.setFixedHeight(42)
    w.setStyleSheet(f"background:{C_WHITE};border-top:1px solid {C_BORDER};")
    lay = QHBoxLayout(w); lay.setContentsMargins(28,0,28,0)
    lay.addWidget(lbl("© 2026 JETJET AIR GLOBAL", 10, 400, C_GRAY, 0.5))
    lay.addSpacing(10)
    lay.addWidget(lbl("•", 10, 400, C_GRAY))
    lay.addSpacing(10)
    lay.addWidget(lbl("🛡  BẢO MẬT ĐẦU CUỐI", 10, 500, C_GRAY))
    lay.addStretch()
    for text in ["ĐIỀU KHOẢN", "HỖ TRỢ"]:
        lay.addWidget(lbl(text, 10, 600, C_MID)); lay.addSpacing(16)
    lay.addWidget(lbl("●", 10, 400, C_RED))
    lay.addSpacing(4)
    lay.addWidget(lbl("HỆ THỐNG SẴN SÀNG", 10, 700, C_RED, 0.5))
    return w


# ─────────────────────────────────────────────────────────────────────────────
# ConfirmPage
# ─────────────────────────────────────────────────────────────────────────────
class ConfirmPage(QWidget):
    proceed = Signal(dict)
    go_back = Signal()

    def __init__(self, ctx: dict | None = None, parent=None):
        super().__init__(parent)
        self.ctx = ctx or DEMO_CTX
        self.setStyleSheet(f"background:{C_BG};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent;border:none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(scroll, 1)
        outer.addWidget(_footer())

        inner = QWidget(); inner.setStyleSheet(f"background:{C_BG};")
        scroll.setWidget(inner)

        root = QVBoxLayout(inner)
        root.setContentsMargins(28,24,28,28); root.setSpacing(20)

        root.addLayout(page_header(
            "Xác nhận Thông tin",
            "Vui lòng kiểm tra kỹ trước khi thanh toán",
            on_back=self.go_back,
        ))

        cols = QHBoxLayout(); cols.setSpacing(20)

        # ── Left ──────────────────────────────────────────────────────────────
        left = QVBoxLayout(); left.setSpacing(14)

        flight = self.ctx.get("flight", DEMO_CTX["flight"])
        pax    = self.ctx.get("passenger", DEMO_CTX["passenger"])
        seats  = self.ctx.get("seat_labels", DEMO_CTX["seat_labels"])

        left.addWidget(FlightSummaryCard(flight))

        # Passenger + Seat row
        pax_row = QHBoxLayout(); pax_row.setSpacing(14)
        pax_row.addWidget(PassengerCard(pax))
        pax_row.addWidget(SeatCard(seats))
        left.addLayout(pax_row)
        left.addStretch()

        lw = QWidget(); lw.setStyleSheet("background:transparent;")
        lw.setLayout(left)
        cols.addWidget(lw, 62)

        # ── Right ─────────────────────────────────────────────────────────────
        ps = PaymentSummaryCard(self.ctx)
        ps.proceed.connect(self._on_proceed)
        rw = QWidget(); rw.setStyleSheet("background:transparent;")
        rl = QVBoxLayout(rw); rl.setContentsMargins(0,0,0,0)
        rl.addWidget(ps); rl.addStretch()
        cols.addWidget(rw, 38)

        root.addLayout(cols)

    def _on_proceed(self):
        self.proceed.emit(self.ctx)


if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    win = QMainWindow()
    win.setWindowTitle("JetJet Air — Xác nhận Thông tin")
    win.resize(1380, 860)
    w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
    lay.addWidget(NavBar(0)); lay.addWidget(ConfirmPage())
    win.setCentralWidget(w); win.show()
    sys.exit(app.exec())