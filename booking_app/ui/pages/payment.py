"""
payment.py
----------
Thanh toán An toàn — JetJet Air Booking Flow
Fixed: Safe initialization and dynamic update_page() method.
"""
from __future__ import annotations
import hashlib, random, string, sys
from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtGui import (QColor, QPainter, QBrush, QPen, QPainterPath,
                            QLinearGradient, QFont)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QLineEdit,
    QDialog, QProgressBar
)
from booking_app.ui.pages.booking_shared import (lbl, h_sep, card_style, red_btn, page_header,
                             NavBar, C_RED, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY,
                             C_GREEN, C_BLUE, C_ORANGE)

def _gen_pnr():
    return "JJ" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

DEMO_CTX = dict(
    flight=dict(code="JJ101", dep="SGN", dst="HAN", dep_t="08:00", arr_t="10:15", dur="2H 15M", aircraft="AIRBUS A321NEO"),
    passenger=dict(name="Lê Văn Quân", email="quanle19112007@gmail.com"),
    seat_labels=["4B","5B"], seat_fee=50, base_price=120, tax=57, total=227, pnr=_gen_pnr(),
)

class CreditCardPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self.setFixedSize(340, 200); self._name = ""; self._number = ""; self._expiry = ""; self._cvv = ""; self._show_back = False
    def set_name(self, v): self._name = v.upper(); self.update()
    def set_number(self, v): self._number = v; self.update()
    def set_expiry(self, v): self._expiry = v; self.update()
    def set_cvv(self, v): self._cvv = v; self.update()
    def show_back(self, v): self._show_back = v; self.update()
    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing); w, h = self.width(), self.height()
        grad = QLinearGradient(0, 0, w, h); grad.setColorAt(0, QColor("#1A1A4E")); grad.setColorAt(1, QColor("#050A18"))
        path = QPainterPath(); path.addRoundedRect(0, 0, w, h, 18, 18); p.fillPath(path, QBrush(grad))
        p.setPen(QPen(C_WHITE)); f = QFont(); f.setPointSize(10); f.setWeight(QFont.Bold); p.setFont(f); p.drawText(20, 30, "JETJET AIR")
        f.setPointSize(14); p.setFont(f); p.drawText(20, h-40, " ".join([self._number[i:i+4] for i in range(0,16,4)]).ljust(19, "*"))
        f.setPointSize(9); p.setFont(f); p.drawText(20, h-15, self._name or "FULL NAME"); p.drawText(w-70, h-15, self._expiry or "MM/YY")

class SSLDialog(QDialog):
    payment_complete = Signal()
    def __init__(self, total, parent=None):
        super().__init__(parent); self.setWindowFlags(Qt.FramelessWindowHint); self.setFixedSize(300, 150)
        v = QVBoxLayout(self); v.addWidget(lbl("🔒 ĐANG XỬ LÝ THANH TOÁN...", 14, 700, C_DARK)); v.addWidget(lbl(f"Số tiền: ${total}", 12, 500, C_GRAY))
        self._bar = QProgressBar(); self._bar.setRange(0, 0); v.addWidget(self._bar)
        QTimer.singleShot(2000, self._finish)
    def _finish(self): self.payment_complete.emit(); self.accept()

class OrderSummary(QWidget):
    pay_clicked = Signal()
    def __init__(self, parent=None):
        super().__init__(parent); self.setStyleSheet(card_style(20))
        self._root = QVBoxLayout(self); self._root.setContentsMargins(22, 22, 22, 22); self._root.setSpacing(0)
    def update_data(self, ctx: dict):
        while self._root.count():
            item = self._root.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._clear_layout(item.layout())
        self._root.addWidget(lbl("Chi tiết đơn hàng", 17, 800, C_TEXT)); self._root.addSpacing(18)
        pnr = ctx.get("pnr", "TBA"); fl = ctx.get("flight", {}); pax = ctx.get("passenger", {}); seats = ctx.get("seat_labels", [])
        def _row(k, v, c=C_TEXT, b=False):
            r = QHBoxLayout(); r.addWidget(lbl(k, 11, 500, C_GRAY)); r.addStretch(); r.addWidget(lbl(v, 11, 700 if b else 500, c)); return r
        self._root.addLayout(_row("PNR", pnr, C_RED, True)); self._root.addSpacing(8)
        self._root.addLayout(_row("CHUYẾN BAY", fl.get("code", "—"))); self._root.addSpacing(8)
        self._root.addLayout(_row("HÀNH KHÁCH", pax.get("name", "—"))); self._root.addSpacing(8)
        self._root.addLayout(_row("SỐ GHẾ", ", ".join(seats) if seats else "—")); self._root.addSpacing(16); self._root.addWidget(h_sep()); self._root.addSpacing(14)
        base = ctx.get("base_price", 0); seat_fee = ctx.get("seat_fee", 0); tax = ctx.get("tax", 45); fee = ctx.get("fee", 12); total = base + seat_fee + tax + fee
        for k, v in [("Giá vé", f"${base}"), ("Ghế", f"${seat_fee}"), ("Thuế & Phí", f"${tax + fee}")]:
            self._root.addLayout(_row(k, v)); self._root.addSpacing(10)
        self._root.addWidget(h_sep()); self._root.addSpacing(14); tr = QHBoxLayout(); tr.addWidget(lbl("TỔNG CỘNG", 11, 700, C_GRAY, 1.0)); tr.addStretch()
        tr.addWidget(lbl(f"${total}", 32, 900, C_RED)); self._root.addLayout(tr); self._root.addSpacing(20)
        btn = red_btn("THANH TOÁN NGAY  🪪", 52); btn.clicked.connect(self.pay_clicked); self._root.addWidget(btn); self._root.addStretch()
    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_layout(child.layout())

class PaymentPage(QWidget):
    payment_complete = Signal(dict)
    go_back = Signal()
    def __init__(self, ctx: dict | None = None, parent=None):
        super().__init__(parent); self.ctx = ctx or {}; self.setStyleSheet(f"background:{C_BG};")
        root = QVBoxLayout(self); root.setContentsMargins(28, 24, 28, 28); root.setSpacing(20)
        root.addLayout(page_header("Thanh toán An toàn", "GIAO DỊCH BẢO MẬT", on_back=self.go_back))
        body = QHBoxLayout(); body.setSpacing(20)
        left = QVBoxLayout(); left_card = QWidget(); left_card.setStyleSheet(card_style(20)); lc = QVBoxLayout(left_card)
        self._preview = CreditCardPreview(); lc.addWidget(self._preview, 0, Qt.AlignCenter)
        self._f_num = QLineEdit(); self._f_num.setPlaceholderText("SỐ THẺ"); self._f_num.textChanged.connect(self._preview.set_number); lc.addWidget(self._f_num)
        self._f_name = QLineEdit(); self._f_name.setPlaceholderText("TÊN CHỦ THẺ"); self._f_name.textChanged.connect(self._preview.set_name); lc.addWidget(self._f_name)
        left.addWidget(left_card); left.addStretch(); body.addLayout(left, 62)
        self._order = OrderSummary(); self._order.pay_clicked.connect(self._on_pay); body.addWidget(self._order, 38)
        root.addLayout(body)
    def update_page(self, ctx: dict | None = None):
        if ctx: self.ctx = ctx
        self._order.update_data(self.ctx)
    def _on_pay(self):
        total = self.ctx.get("base_price",0) + self.ctx.get("seat_fee",0) + 57
        dlg = SSLDialog(total, self); dlg.payment_complete.connect(lambda: self.payment_complete.emit(self.ctx)); dlg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    win = QMainWindow(); win.resize(1380, 860)
    w = QWidget(); lay = QVBoxLayout(w); lay.addWidget(NavBar(0)); lay.addWidget(PaymentPage(DEMO_CTX))
    win.setCentralWidget(w); win.show(); sys.exit(app.exec())
