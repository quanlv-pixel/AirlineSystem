"""
confirm_page.py
---------------
Confirmation Page for the booking application.
Fixed: Safe initialization and dynamic update_page() method.
"""
from __future__ import annotations
import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QPainterPath, QLinearGradient, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea
)
from booking_app.ui.pages.booking_shared import (lbl, h_sep, card_style, red_btn, page_header,
                             NavBar, C_RED, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY,
                             C_GREEN, C_BLUE, C_ORANGE)

class ConfirmTimeline(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(32); self.setStyleSheet("background:transparent;")
    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); w, h = self.width(), self.height(); cy = h // 2
        pen = QPen(QColor(C_BORDER), 1.5, Qt.DashLine); pen.setDashPattern([6, 4]); p.setPen(pen)
        p.drawLine(0, cy, w//2 - 18, cy); p.drawLine(w//2 + 18, cy, w, cy)
        p.setPen(QPen(QColor(C_RED))); f = QFont(); f.setPointSize(14); p.setFont(f); p.drawText(w//2 - 12, 0, 24, h, Qt.AlignCenter, "✈")

class FlightSummaryCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(16))
        self._root = QVBoxLayout(self); self._root.setContentsMargins(24, 20, 24, 20); self._root.setSpacing(0)

    def update_data(self, ctx: dict):
        while self._root.count():
            child = self._root.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

        self._root.addWidget(
            lbl("Chi tiết Thanh toán", 18, 800, C_TEXT)
        )
        self._root.addSpacing(20)

        # KIỂM TRA XEM CÓ PHẢI VÉ KHỨ HỒI KHÔNG
        is_rt = ctx.get("is_roundtrip", False)
        multiplier = 2 if is_rt else 1

        ticket_count = ctx.get("ticket_count", 1)
        base_unit = ctx.get("base_price", 0)
        seat_fee  = ctx.get("seat_fee", 0) * multiplier # Nhân đôi phí ghế nếu khứ hồi
        tax_unit  = ctx.get("tax", 45)
        fee_unit  = ctx.get("fee", 12)

        # Nhân tiền với số lượng vé VÀ nhân với hệ số khứ hồi (x2)
        base = base_unit * ticket_count * multiplier
        tax  = tax_unit  * ticket_count * multiplier
        fee  = fee_unit  * ticket_count * multiplier

        grand_total = base + seat_fee + tax + fee
        ctx["total"] = grand_total

        # Build label suffixes
        suffix = f" (x{ticket_count})" if ticket_count > 1 else ""
        if is_rt:
            suffix += " [Khứ Hồi]" # Thêm nhãn để khách hàng dễ hiểu

        for title, amount in [
            (f"Giá vé máy bay{suffix}", f"${base}"),
            ("Phí chọn ghế (Cả đi & về)" if is_rt else "Phí chọn ghế", f"${seat_fee}"),
            (f"Thuế & Phí sân bay{suffix}", f"${tax}"),
            (f"Phí quản trị hệ thống{suffix}", f"${fee}"),
        ]:
            row = QHBoxLayout()
            row.addWidget(lbl(title, 13, 400, C_MID))
            row.addStretch()
            row.addWidget(lbl(amount, 13, 600, C_TEXT))
            self._root.addLayout(row)
            self._root.addSpacing(12)

        self._root.addWidget(h_sep())
        self._root.addSpacing(16)

        tot_row = QHBoxLayout()
        tot_row.addWidget(
            lbl("TỔNG THANH TOÁN", 11, 700, C_GRAY, 1.0)
        )
        tot_row.addStretch()
        tot_row.addWidget(
            lbl(f"${ctx['total']}", 32, 900, C_RED)
        )
        self._root.addLayout(tot_row)
        self._root.addSpacing(20)

        btn = red_btn("THANH TOÁN NGAY 🪪", 52)
        btn.clicked.connect(self.proceed)
        self._root.addWidget(btn)
        self._root.addSpacing(16)

        sec = QWidget()
        sec.setStyleSheet(
            "background:#ECFDF5; border:1px solid #A7F3D0; border-radius:12px;"
        )
        sl = QHBoxLayout(sec)
        sl.setContentsMargins(14,12,14,12)
        sl.setSpacing(10)
        sl.addWidget(lbl("🛡", 16, 400, C_GREEN))
        sl.addWidget(lbl("Giao dịch của bạn được bảo mật bởi chuẩn mã hóa SSL/TLS 1.2", 11, 500, C_MID))

        self._root.addWidget(sec)
        self._root.addStretch()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_layout(child.layout())

class SeatPill(QLabel):
    def __init__(self, seat: str, parent=None):
        super().__init__(seat, parent)
        self.setAlignment(Qt.AlignCenter); self.setFixedSize(44, 34)
        self.setStyleSheet(f"QLabel{{background:{C_DARK}; color:white; border-radius:12px; font-size:13px; font-weight:800; border:none;}}")

class PassengerCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(14))
        self._root = QVBoxLayout(self); self._root.setContentsMargins(20, 18, 20, 18); self._root.setSpacing(10)

    def update_data(self, pax: dict):
        while self._root.count():
            child = self._root.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        hdr = QHBoxLayout(); hdr.setSpacing(8); hdr.addWidget(lbl("◎", 16, 400, C_RED)); hdr.addWidget(lbl("HÀNH KHÁCH", 11, 700, C_TEXT, 1.0)); hdr.addStretch(); self._root.addLayout(hdr)
        self._root.addWidget(lbl(pax.get("name","—"), 18, 700, C_TEXT)); self._root.addWidget(lbl(pax.get("email","—"), 12, 400, C_GRAY))

class SeatCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(14))
        self._root = QVBoxLayout(self); self._root.setContentsMargins(20, 18, 20, 18); self._root.setSpacing(12)

    def update_data(self, seat_labels: list[str]):
        while self._root.count():
            child = self._root.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_layout(child.layout())
        hdr = QHBoxLayout(); hdr.setSpacing(8); hdr.addWidget(lbl("🪑", 16, 400, C_RED)); hdr.addWidget(lbl("CHỖ NGỒI", 11, 700, C_TEXT, 1.0)); hdr.addStretch(); self._root.addLayout(hdr)
        pills = QHBoxLayout(); pills.setSpacing(10); pills.setAlignment(Qt.AlignLeft)
        for s in seat_labels: pills.addWidget(SeatPill(s))
        self._root.addLayout(pills)

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_layout(child.layout())

class PaymentSummaryCard(QWidget):
    proceed = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(20))
        self._root = QVBoxLayout(self); self._root.setContentsMargins(24,24,24,24); self._root.setSpacing(0)

    def update_data(self, ctx: dict):
        while self._root.count():
            child = self._root.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())

        self._root.addWidget(
            lbl("Chi tiết Thanh toán", 18, 800, C_TEXT)
        )
        self._root.addSpacing(20)

        ticket_count = ctx.get("ticket_count", 1)
        base_unit = ctx.get("base_price", 0)
        seat_fee  = ctx.get("seat_fee", 0)
        tax_unit  = ctx.get("tax", 45)
        fee_unit  = ctx.get("fee", 12)

        # Multiply per-ticket amounts by the number of tickets
        base = base_unit * ticket_count
        tax  = tax_unit  * ticket_count
        fee  = fee_unit  * ticket_count
        # seat_fee is already the sum of all selected seats (SEAT_PRICE * n_seats)

        grand_total = base + seat_fee + tax + fee
        ctx["total"] = grand_total

        # Build label suffixes
        suffix = f" (x{ticket_count})" if ticket_count > 1 else ""

        for title, amount in [
            (f"Giá vé máy bay{suffix}", f"${base}"),
            ("Phí chọn ghế", f"${seat_fee}"),
            (f"Thuế & Phí sân bay{suffix}", f"${tax}"),
            (f"Phí quản trị hệ thống{suffix}", f"${fee}"),
        ]:
            row = QHBoxLayout()
            row.addWidget(lbl(title, 13, 400, C_MID))
            row.addStretch()
            row.addWidget(lbl(amount, 13, 600, C_TEXT))
            self._root.addLayout(row)
            self._root.addSpacing(12)

        self._root.addWidget(h_sep())
        self._root.addSpacing(16)

        tot_row = QHBoxLayout()
        tot_row.addWidget(
            lbl("TỔNG THANH TOÁN", 11, 700, C_GRAY, 1.0)
        )
        tot_row.addStretch()
        tot_row.addWidget(
            lbl(f"${ctx['total']}", 32, 900, C_RED)
        )
        self._root.addLayout(tot_row)

        self._root.addSpacing(20)

        btn = red_btn("THANH TOÁN NGAY 🪪", 52)
        btn.clicked.connect(self.proceed)
        self._root.addWidget(btn)

        self._root.addSpacing(16)

        sec = QWidget()
        sec.setStyleSheet(
            "background:#ECFDF5;"
            "border:1px solid #A7F3D0;"
            "border-radius:12px;"
        )

        sl = QHBoxLayout(sec)
        sl.setContentsMargins(14,12,14,12)
        sl.setSpacing(10)

        sl.addWidget(lbl("🛡", 16, 400, C_GREEN))
        sl.addWidget(
            lbl(
                "Giao dịch của bạn được bảo mật bởi chuẩn mã hóa SSL/TLS 1.2",
                11, 500, C_MID
            )
        )

        self._root.addWidget(sec)
        self._root.addStretch()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_layout(child.layout())

class ConfirmPage(QWidget):
    proceed = Signal(dict)
    go_back = Signal()

    def __init__(self, ctx: dict | None = None, parent=None):
        super().__init__(parent)
        self.ctx = ctx or {}
        self.setStyleSheet(f"background:{C_BG};")
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.NoFrame); scroll.setStyleSheet("background:transparent;border:none;"); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); outer.addWidget(scroll, 1)
        inner = QWidget(); inner.setStyleSheet(f"background:{C_BG};"); scroll.setWidget(inner)
        root = QVBoxLayout(inner); root.setContentsMargins(28,24,28,28); root.setSpacing(20)
        root.addLayout(page_header("Xác nhận Thông tin", "Vui lòng kiểm tra kỹ trước khi thanh toán", on_back=self.go_back))
        cols = QHBoxLayout(); cols.setSpacing(20)
        left = QVBoxLayout(); left.setSpacing(14)
        self._flight_card = FlightSummaryCard(); left.addWidget(self._flight_card)
        pax_row = QHBoxLayout(); pax_row.setSpacing(14)
        self._pax_card = PassengerCard(); self._seat_card = SeatCard(); pax_row.addWidget(self._pax_card); pax_row.addWidget(self._seat_card); left.addLayout(pax_row); left.addStretch()
        lw = QWidget(); lw.setStyleSheet("background:transparent;"); lw.setLayout(left); cols.addWidget(lw, 62)
        self._payment_card = PaymentSummaryCard(); self._payment_card.proceed.connect(self._on_proceed)
        rw = QWidget(); rw.setStyleSheet("background:transparent;"); rl = QVBoxLayout(rw); rl.setContentsMargins(0,0,0,0); rl.addWidget(self._payment_card); rl.addStretch(); cols.addWidget(rw, 38)
        root.addLayout(cols)

    def update_page(self, ctx: dict | None = None):
        if ctx: self.ctx = ctx
        self._flight_card.update_data(self.ctx.get("flight", {}))
        self._pax_card.update_data(self.ctx.get("passenger", {}))
        self._seat_card.update_data(self.ctx.get("seat_labels", []))
        self._payment_card.update_data(self.ctx)

    def _on_proceed(self):
        self.proceed.emit(self.ctx)

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    win = QMainWindow(); win.resize(1380, 860)
    w = QWidget(); lay = QVBoxLayout(w); lay.addWidget(NavBar(0)); lay.addWidget(ConfirmPage())
    win.setCentralWidget(w); win.show(); sys.exit(app.exec())
