"""
payment.py
----------
Thanh toán An toàn — JetJet Air Booking Flow
• Live Credit Card Preview (cập nhật theo input)
• Nhiều phương thức: Thẻ / Ví điện tử / Ngân hàng / Dặm Miles
• SSL Animation 3 giây trước khi hoàn tất
• Biểu tượng PCI-DSS, AES-256
"""
from __future__ import annotations
import hashlib, random, string, sys
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import (QColor, QPainter, QBrush, QPen, QPainterPath,
                            QLinearGradient, QFont, QFontMetrics)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QLineEdit,
    QDialog, QProgressBar, QSizePolicy
)
from booking_app.ui.pages.booking_shared import (lbl, h_sep, card_style, red_btn, page_header,
                             NavBar, C_RED, C_RED2, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY,
                             C_GREEN, C_BLUE, C_ORANGE)

# ── Auto-generate PNR ────────────────────────────────────────────────────────
def _gen_pnr():
    return "JJ" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

DEMO_PNR   = _gen_pnr()
DEMO_HASH  = hashlib.sha256(DEMO_PNR.encode()).hexdigest()[:16].upper()
DEMO_CTX   = dict(
    flight=dict(code="JJ101", dep="SGN", dst="HAN", dep_t="08:00",
                arr_t="10:15", dur="2H 15M", aircraft="AIRBUS A321NEO"),
    passenger=dict(name="Lê Văn Quân", email="quanle19112007@gmail.com"),
    seat_labels=["4B","5B"], seat_fee=50,
    base_price=120, tax=57, total=227, pnr=DEMO_PNR,
)


# ═════════════════════════════════════════════════════════════════════════════
# 1. CREDIT CARD PREVIEW  (live paint)
# ═════════════════════════════════════════════════════════════════════════════
class CreditCardPreview(QWidget):
    """Thẻ tín dụng ảo — cập nhật real-time theo input."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(340, 200)
        self._name   = ""
        self._number = ""          # chỉ giữ digits
        self._expiry = ""
        self._cvv    = ""
        self._show_back = False

    # ── Setters (kết nối với form signals) ───────────────────────────────────
    def set_name(self, v: str):
        self._name = v.upper()[:22]; self.update()

    def set_number(self, digits: str):
        self._number = digits[:16]; self.update()

    def set_expiry(self, v: str):
        self._expiry = v[:5]; self.update()

    def set_cvv(self, v: str):
        self._cvv = v[:3]; self.update()

    def show_back(self, v: bool):
        self._show_back = v; self.update()

    # ── Paint ────────────────────────────────────────────────────────────────
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        if self._show_back:
            self._draw_back(p, w, h)
        else:
            self._draw_front(p, w, h)

    def _draw_front(self, p, w, h):
        # ── Background gradient ──────────────────────────────────────────────
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor("#1A1A4E"))
        grad.setColorAt(0.6, QColor("#0F1E3A"))
        grad.setColorAt(1.0, QColor("#050A18"))
        card_path = QPainterPath()
        card_path.addRoundedRect(0, 0, w, h, 18, 18)
        p.fillPath(card_path, QBrush(grad))

        # ── Pattern overlay ──────────────────────────────────────────────────
        p.setPen(QPen(QColor(255, 255, 255, 6), 0.5))
        for i in range(0, w + h, 28):
            p.drawLine(i, 0, 0, i)

        # ── JetJet brand ─────────────────────────────────────────────────────
        p.setPen(QPen(QColor(C_WHITE)))
        f = QFont(); f.setPointSize(9); f.setWeight(QFont.Bold)
        p.setFont(f)
        p.drawText(18, 22, "✈  JETJET AIR")

        # ── Contactless icon (top right) ─────────────────────────────────────
        p.setPen(QPen(QColor(255, 255, 255, 180), 1.8))
        cx, cy = w - 30, 20
        for r in (8, 13, 18):
            p.drawArc(cx - r, cy - r, r * 2, r * 2, 315 * 16, 90 * 16)

        # ── Gold chip ─────────────────────────────────────────────────────────
        cx2, cy2, cw2, ch2 = 18, int(h * 0.34), 44, 30
        cg = QLinearGradient(cx2, cy2, cx2 + cw2, cy2 + ch2)
        cg.setColorAt(0.0, QColor("#F5D060"))
        cg.setColorAt(0.5, QColor("#E8B830"))
        cg.setColorAt(1.0, QColor("#C8A010"))
        cp = QPainterPath(); cp.addRoundedRect(cx2, cy2, cw2, ch2, 5, 5)
        p.fillPath(cp, QBrush(cg))
        p.setPen(QPen(QColor("#A07800"), 0.8))
        for lx in (cx2+14, cx2+28):
            p.drawLine(lx, cy2, lx, cy2 + ch2)
        for ly in (cy2+10, cy2+20):
            p.drawLine(cx2, ly, cx2 + cw2, ly)

        # ── Card number ───────────────────────────────────────────────────────
        f2 = QFont(); f2.setPointSize(14); f2.setLetterSpacing(QFont.AbsoluteSpacing, 2)
        f2.setWeight(QFont.Medium)
        p.setFont(f2)
        p.setPen(QPen(QColor(C_WHITE)))
        num = self._number.ljust(16)
        parts = [num[i:i+4] for i in range(0, 16, 4)]
        display_parts = []
        for i, part in enumerate(parts):
            if i < 3:
                display_parts.append("••••")
            else:
                disp = "".join(c if c.isdigit() else "▪" for c in part)
                display_parts.append(disp.ljust(4, "▪"))
        p.drawText(18, h - 48, "  ".join(display_parts))

        # ── Cardholder name ───────────────────────────────────────────────────
        f3 = QFont(); f3.setPointSize(9); f3.setWeight(QFont.Medium)
        p.setFont(f3)
        p.setPen(QPen(QColor(200, 210, 255, 180)))
        p.drawText(18, h - 28, "CARDHOLDER")
        p.setPen(QPen(QColor(C_WHITE)))
        p.drawText(18, h - 12, self._name or "FULL NAME")

        # ── Expiry ────────────────────────────────────────────────────────────
        p.setPen(QPen(QColor(200, 210, 255, 180)))
        p.drawText(w - 90, h - 28, "VALID THRU")
        p.setPen(QPen(QColor(C_WHITE)))
        p.drawText(w - 90, h - 12, self._expiry or "MM/YY")

        # ── VISA logo (stylised) ──────────────────────────────────────────────
        f4 = QFont(); f4.setPointSize(13); f4.setWeight(QFont.Black)
        f4.setItalic(True)
        p.setFont(f4)
        p.setPen(QPen(QColor("#FFFFFF")))
        p.drawText(w - 62, h - 10, "VISA")

    def _draw_back(self, p, w, h):
        # Dark background
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0, QColor("#1A1A4E"))
        grad.setColorAt(1, QColor("#050A18"))
        card_path = QPainterPath()
        card_path.addRoundedRect(0, 0, w, h, 18, 18)
        p.fillPath(card_path, QBrush(grad))

        # Magnetic stripe
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor("#111111")))
        p.drawRect(0, 30, w, 38)

        # Signature strip + CVV
        p.setBrush(QBrush(QColor(240, 238, 230)))
        p.drawRoundedRect(12, 85, w - 80, 30, 3, 3)

        # CVV box
        p.setBrush(QBrush(QColor(C_WHITE)))
        p.drawRoundedRect(w - 62, 85, 50, 30, 3, 3)
        f = QFont(); f.setPointSize(12); f.setWeight(QFont.Bold)
        p.setFont(f)
        p.setPen(QPen(QColor(C_DARK)))
        cvv_disp = self._cvv.ljust(3, "•")
        p.drawText(w - 58, 85, 46, 30, Qt.AlignCenter, cvv_disp)

        # Labels
        f2 = QFont(); f2.setPointSize(8)
        p.setFont(f2)
        p.setPen(QPen(QColor(C_GRAY)))
        p.drawText(w - 62, 122, "CVV")


# ═════════════════════════════════════════════════════════════════════════════
# 2. SSL ANIMATION DIALOG
# ═════════════════════════════════════════════════════════════════════════════
class SSLDialog(QDialog):
    """Giả lập quá trình xác thực SSL/PCI-DSS trong 3 giây."""
    payment_complete = Signal()

    STEPS = [
        ("🔒", "Khởi tạo kết nối SSL/TLS 1.3..."),
        ("🛡", "Xác thực chứng chỉ PCI-DSS Level 1..."),
        ("🔗", "Kết nối JetJet Payment Gateway..."),
        ("✅", "Mã hóa AES-256 — Xử lý giao dịch..."),
    ]

    def __init__(self, total: int, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)
        self.setFixedSize(440, 320)
        self.setStyleSheet(f"background:{C_WHITE};border-radius:20px;")

        self._step = 0
        self._step_labels: list[tuple[QLabel, QLabel]] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(36, 32, 36, 32)
        root.setSpacing(0)

        # Header
        hdr_col = QVBoxLayout(); hdr_col.setSpacing(6)
        hdr_col.addWidget(lbl("Đang Xử lý Thanh toán", 18, 800, C_TEXT))
        hdr_col.addWidget(lbl(f"Tổng tiền: ${total}  —  Vui lòng không đóng cửa sổ",
                              12, 400, C_GRAY))
        root.addLayout(hdr_col)
        root.addSpacing(24)
        root.addWidget(h_sep())
        root.addSpacing(20)

        # Steps
        for icon, text in self.STEPS:
            row = QHBoxLayout(); row.setSpacing(12)
            icon_lbl = QLabel("⏳"); icon_lbl.setFixedWidth(22)
            icon_lbl.setStyleSheet("font-size:16px;background:transparent;border:none;")
            text_lbl = lbl(text, 13, 500, C_GRAY)
            row.addWidget(icon_lbl); row.addWidget(text_lbl); row.addStretch()
            self._step_labels.append((icon_lbl, text_lbl))
            root.addLayout(row)
            root.addSpacing(10)

        root.addSpacing(16)

        # Progress bar
        self._prog = QProgressBar()
        self._prog.setRange(0, 100); self._prog.setValue(0)
        self._prog.setFixedHeight(8)
        self._prog.setTextVisible(False)
        self._prog.setStyleSheet(f"""
            QProgressBar {{
                background:{C_LGRAY}; border:none; border-radius:4px;
            }}
            QProgressBar::chunk {{
                background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C_RED},stop:1 #FF5252);
                border-radius:4px;
            }}
        """)
        root.addWidget(self._prog)
        root.addSpacing(16)

        self._status_lbl = lbl("Đang xác thực...", 11, 500, C_GRAY)
        self._status_lbl.setAlignment(Qt.AlignCenter)
        root.addWidget(self._status_lbl)

        # Timer: 750ms per step
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        QTimer.singleShot(400, lambda: self._timer.start(750))

    def _tick(self):
        if self._step < len(self.STEPS):
            # Mark current step done
            icon_lbl, text_lbl = self._step_labels[self._step]
            icon_lbl.setText("✅")
            text_lbl.setStyleSheet(text_lbl.styleSheet()
                                    .replace(C_GRAY, C_GREEN).replace(C_MID, C_GREEN))
            text_lbl.setStyleSheet(f"font-size:13px;font-weight:600;color:{C_GREEN};"
                                   "background:transparent;border:none;")
            self._prog.setValue(int((self._step + 1) * 100 / len(self.STEPS)))

            # Activate next step
            self._step += 1
            if self._step < len(self.STEPS):
                next_icon, next_text = self._step_labels[self._step]
                next_icon.setText("⏳")
                next_text.setStyleSheet(f"font-size:13px;font-weight:500;color:{C_TEXT};"
                                        "background:transparent;border:none;")
                self._status_lbl.setText(self.STEPS[self._step][1])
        else:
            self._timer.stop()
            self._status_lbl.setText("✅  Thanh toán thành công!")
            self._status_lbl.setStyleSheet(f"font-size:12px;font-weight:700;color:{C_GREEN};"
                                           "background:transparent;border:none;")
            QTimer.singleShot(600, self._finish)

    def _finish(self):
        self.payment_complete.emit()
        self.accept()


# ═════════════════════════════════════════════════════════════════════════════
# 3. FORM FIELDS
# ═════════════════════════════════════════════════════════════════════════════
def _form_input(placeholder="", default="", password=False):
    e = QLineEdit(); e.setPlaceholderText(placeholder); e.setText(default)
    e.setFixedHeight(46)
    if password: e.setEchoMode(QLineEdit.Password)
    e.setStyleSheet(f"""
        QLineEdit {{
            background:{C_LGRAY}; border:1.5px solid {C_BORDER};
            border-radius:12px; font-size:13px; color:{C_TEXT}; padding:0 14px;
        }}
        QLineEdit:focus{{border-color:{C_RED};background:{C_WHITE};}}
    """)
    return e

def _flbl(text): return lbl(text, 10, 600, C_GRAY, 0.5)


# ─────────────────────────────────────────────────────────────────────────────
# Card payment form
# ─────────────────────────────────────────────────────────────────────────────
class CardForm(QWidget):
    """Form nhập thẻ + live card preview."""

    def __init__(self, card_preview: CreditCardPreview, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        self._preview = card_preview

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)

        # Title + card icons
        title_row = QHBoxLayout()
        title_row.addWidget(lbl("Thông tin Thẻ", 15, 700, C_TEXT))
        title_row.addStretch()
        for brand in ["VISA", "MC", "JCB"]:
            b = QLabel(brand)
            b.setFixedHeight(22)
            b.setContentsMargins(8, 0, 8, 0)
            b.setStyleSheet(f"font-size:9px;font-weight:800;color:{C_MID};"
                            f"background:{C_LGRAY};border:1px solid {C_BORDER};"
                            f"border-radius:4px;")
            title_row.addWidget(b)
            title_row.addSpacing(4)
        root.addLayout(title_row)

        # Cardholder name
        self._name_e = _form_input("VD: NGUYEN VAN A")
        self._name_e.textChanged.connect(self._preview.set_name)
        root.addLayout(self._labeled_field("CHỦ THẺ (IN NỐI)", self._name_e))

        # Card number
        self._num_e = _form_input("**** **** **** ****")
        self._num_e.textChanged.connect(self._on_number)
        self._num_e.setMaxLength(19)  # 16 digits + 3 spaces
        root.addLayout(self._labeled_field("SỐ THẺ TÍN DỤNG", self._num_e))

        # Expiry + CVV row
        row = QHBoxLayout(); row.setSpacing(12)

        exp_col = QVBoxLayout(); exp_col.setSpacing(6)
        exp_col.addWidget(_flbl("NGÀY HẾT HẠN"))
        self._exp_e = _form_input("MM/YY")
        self._exp_e.setMaxLength(5)
        self._exp_e.textChanged.connect(self._on_expiry)
        exp_col.addWidget(self._exp_e)

        cvv_col = QVBoxLayout(); cvv_col.setSpacing(6)
        cvv_col.addWidget(_flbl("CVV / CVC"))
        cvv_row = QHBoxLayout(); cvv_row.setSpacing(6)
        self._cvv_e = _form_input("•••", password=True)
        self._cvv_e.setMaxLength(3)
        self._cvv_e.textChanged.connect(self._on_cvv)
        self._cvv_e.focusInEvent  = lambda e: (self._preview.show_back(True), QLineEdit.focusInEvent(self._cvv_e, e))
        self._cvv_e.focusOutEvent = lambda e: (self._preview.show_back(False), QLineEdit.focusOutEvent(self._cvv_e, e))

        eye_btn = QPushButton("👁")
        eye_btn.setFixedSize(40, 46)
        eye_btn.setCursor(Qt.PointingHandCursor)
        eye_btn.setCheckable(True)
        eye_btn.setStyleSheet(f"QPushButton{{background:{C_LGRAY};border:1.5px solid {C_BORDER};"
                              f"border-radius:12px;font-size:14px;}}"
                              f"QPushButton:checked{{background:{C_RED_L};}}")
        eye_btn.toggled.connect(
            lambda on: self._cvv_e.setEchoMode(
                QLineEdit.Normal if on else QLineEdit.Password
            )
        )
        cvv_row.addWidget(self._cvv_e, 1)
        cvv_row.addWidget(eye_btn)
        cvv_col.addLayout(cvv_row)

        row.addLayout(exp_col)
        row.addLayout(cvv_col)
        root.addLayout(row)

        # Security notice
        sec = QWidget()
        sec.setStyleSheet(f"background:{C_LGRAY};border:1px solid {C_BORDER};border-radius:10px;")
        sl = QHBoxLayout(sec); sl.setContentsMargins(14, 10, 14, 10); sl.setSpacing(10)
        sl.addWidget(lbl("🔒", 16, 400, C_BLUE))
        sc_col = QVBoxLayout(); sc_col.setSpacing(2)
        sc_col.addWidget(lbl("MÃ HÓA AES-256 BIT  •  PCI-DSS LEVEL 1", 10, 700, C_BLUE, 0.5))
        sc_col.addWidget(lbl("Thông tin thẻ được mã hóa hoàn toàn trước khi truyền đi.",
                             11, 400, C_MID))
        sl.addLayout(sc_col)
        root.addWidget(sec)

    @staticmethod
    def _labeled_field(label_text, widget):
        col = QVBoxLayout(); col.setSpacing(6)
        col.addWidget(_flbl(label_text)); col.addWidget(widget)
        return col

    def _on_number(self, text):
        digits = "".join(c for c in text if c.isdigit())[:16]
        formatted = " ".join(digits[i:i+4] for i in range(0, len(digits), 4))
        if text != formatted:
            self._num_e.blockSignals(True)
            cur = self._num_e.cursorPosition()
            self._num_e.setText(formatted)
            self._num_e.setCursorPosition(min(cur, len(formatted)))
            self._num_e.blockSignals(False)
        self._preview.set_number(digits)

    def _on_expiry(self, text):
        digits = "".join(c for c in text if c.isdigit())[:4]
        if len(digits) > 2:
            formatted = digits[:2] + "/" + digits[2:]
        else:
            formatted = digits
        if text != formatted:
            self._num_e.blockSignals(True)
            self._exp_e.blockSignals(True)
            self._exp_e.setText(formatted)
            self._exp_e.blockSignals(False)
        self._preview.set_expiry(formatted)

    def _on_cvv(self, text):
        self._preview.set_cvv(text)


# ─────────────────────────────────────────────────────────────────────────────
# E-Wallet form
# ─────────────────────────────────────────────────────────────────────────────
class EWalletForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        root = QVBoxLayout(self); root.setSpacing(16)
        root.addWidget(lbl("Chọn ví điện tử", 15, 700, C_TEXT))

        for icon, name, color in [("🟣", "MoMo",    "#AE2D68"),
                                   ("🔵", "ZaloPay", "#0068FF"),
                                   ("🔴", "VNPay",   "#D0021B")]:
            w = QWidget()
            w.setFixedHeight(60)
            w.setCursor(Qt.PointingHandCursor)
            w.setStyleSheet(f"background:{C_WHITE};border:1.5px solid {C_BORDER};"
                            f"border-radius:14px;")
            wl = QHBoxLayout(w); wl.setContentsMargins(20, 0, 20, 0)
            wl.addWidget(lbl(icon, 22, 400, C_TEXT))
            wl.addSpacing(14)
            wl.addWidget(lbl(name, 15, 700, color))
            wl.addStretch()
            wl.addWidget(lbl("→", 16, 700, C_GRAY))
            root.addWidget(w)

        root.addWidget(lbl("Chọn ví và quét QR để thanh toán", 12, 400, C_GRAY))
        root.addStretch()


# ─────────────────────────────────────────────────────────────────────────────
# Miles form
# ─────────────────────────────────────────────────────────────────────────────
class MilesForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        root = QVBoxLayout(self); root.setSpacing(16)
        root.addWidget(lbl("Dặm Tích Lũy JetJet", 15, 700, C_TEXT))

        balance_card = QWidget()
        balance_card.setStyleSheet(f"background:{C_DARK};border-radius:14px;")
        bl = QVBoxLayout(balance_card); bl.setContentsMargins(20, 18, 20, 18)
        bl.addWidget(lbl("DẶM TÍCH LŨY CỦA BẠN", 10, 600, C_GRAY, 1.5))
        bl.addWidget(lbl("12,450 DẶM", 28, 800, C_WHITE))
        bl.addSpacing(4)
        bl.addWidget(lbl("Tương đương: $62.25  •  Đủ cho chuyến này", 12, 400, C_GRAY))
        root.addWidget(balance_card)

        root.addWidget(lbl("5,000 dặm = $25  |  Tối thiểu: 1,000 dặm", 12, 500, C_MID))
        miles_e = _form_input("Nhập số dặm muốn dùng (VD: 5000)")
        root.addWidget(miles_e)
        root.addWidget(lbl("💡 Số dặm sẽ được khấu trừ trực tiếp vào tổng tiền.",
                           11, 400, C_GRAY))
        root.addStretch()


# ═════════════════════════════════════════════════════════════════════════════
# 4. ORDER SUMMARY  (right panel)
# ═════════════════════════════════════════════════════════════════════════════
class OrderSummary(QWidget):
    pay_clicked = Signal()

    def __init__(self, ctx: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(20))
        self._ctx = ctx

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(0)

        root.addWidget(lbl("Chi tiết đơn hàng", 17, 800, C_TEXT))
        root.addSpacing(18)

        pnr = ctx.get("pnr", DEMO_PNR)
        fl  = ctx.get("flight", DEMO_CTX["flight"])
        pax = ctx.get("passenger", DEMO_CTX["passenger"])
        seats = ctx.get("seat_labels", ["4B","5B"])

        def _info_row(key, val, val_color=C_TEXT, bold=False):
            r = QHBoxLayout(); r.setSpacing(4)
            r.addWidget(lbl(key, 11, 500, C_GRAY))
            r.addStretch()
            r.addWidget(lbl(val, 11, 700 if bold else 500, val_color))
            return r

        root.addLayout(_info_row("MÃ ĐẶT CHỖ (PNR)", pnr, C_RED, True))
        root.addSpacing(8)
        root.addLayout(_info_row("CHUYẾN BAY", fl.get("code","JJ101")))
        root.addSpacing(8)
        root.addLayout(_info_row("HÀNH KHÁCH", pax.get("name","—")))
        root.addSpacing(8)
        root.addLayout(_info_row("SỐ GHẾ", ", ".join(seats)))
        root.addSpacing(16)
        root.addWidget(h_sep())
        root.addSpacing(14)

        base     = ctx.get("base_price", 120)
        seat_fee = ctx.get("seat_fee", 50)
        tax      = ctx.get("tax", 57)
        total    = base + seat_fee + tax

        for key, val in [("Giá vé & Thuế", f"${base + tax}"),
                         ("Phụ phí Ghế",   f"${seat_fee}")]:
            root.addLayout(_info_row(key, val))
            root.addSpacing(10)

        root.addWidget(h_sep()); root.addSpacing(14)

        total_row = QHBoxLayout()
        total_row.addWidget(lbl("TỔNG CỘNG (Bao gồm VAT)", 10, 700, C_GRAY, 0.5))
        total_row.addStretch()
        total_row.addWidget(lbl(f"${total}", 28, 900, C_RED))
        root.addLayout(total_row)
        root.addSpacing(18)

        btn = red_btn("THANH TOÁN AN TOÀN  →", 52)
        btn.clicked.connect(self.pay_clicked)
        root.addWidget(btn)
        root.addSpacing(16)

        # Security badges
        badges = QHBoxLayout(); badges.setSpacing(8); badges.setAlignment(Qt.AlignCenter)
        for badge in ["🔒 SSL", "🛡 PCI-DSS", "✅ VERIFIED"]:
            b = QLabel(badge); b.setContentsMargins(8, 4, 8, 4)
            b.setStyleSheet(f"font-size:10px;font-weight:600;color:{C_MID};"
                            f"background:{C_LGRAY};border-radius:6px;")
            badges.addWidget(b)
        root.addLayout(badges)
        root.addStretch()

    def total(self):
        return (self._ctx.get("base_price", 120)
                + self._ctx.get("seat_fee", 50)
                + self._ctx.get("tax", 57))


# ═════════════════════════════════════════════════════════════════════════════
# 5. PAYMENT METHOD TABS
# ═════════════════════════════════════════════════════════════════════════════
class MethodSelector(QWidget):
    changed = Signal(int)

    _METHODS = [
        ("💳", "THẺ QUỐC TẾ"),
        ("📱", "VÍ ĐIỆN TỬ"),
        ("🏦", "NGÂN HÀNG"),
        ("✈",  "DẶM MILES"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        self.setFixedHeight(80)
        self._active = 0
        self._btns: list[QPushButton] = []

        lay = QHBoxLayout(self); lay.setSpacing(12); lay.setContentsMargins(0,0,0,0)
        for i, (icon, label) in enumerate(self._METHODS):
            btn = QPushButton(f"{icon}\n{label}")
            btn.setFixedHeight(72)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self._select(idx))
            self._btns.append(btn)
            lay.addWidget(btn)

        self._select(0)

    def _select(self, idx: int):
        self._active = idx
        for i, btn in enumerate(self._btns):
            if i == idx:
                btn.setStyleSheet(f"""
                    QPushButton{{
                        background:{C_WHITE};border:2px solid {C_RED};
                        border-radius:14px;font-size:12px;font-weight:700;
                        color:{C_RED};padding:4px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton{{
                        background:{C_WHITE};border:1.5px solid {C_BORDER};
                        border-radius:14px;font-size:12px;font-weight:500;
                        color:{C_MID};padding:4px;
                    }}
                    QPushButton:hover{{border-color:{C_GRAY};color:{C_TEXT};}}
                """)
        self.changed.emit(idx)


# ═════════════════════════════════════════════════════════════════════════════
# 6. PAYMENT PAGE
# ═════════════════════════════════════════════════════════════════════════════
C_RED_L = "#FFEBEE"   # local alias

class PaymentPage(QWidget):
    payment_complete = Signal(dict)   # phát ctx khi thanh toán xong
    go_back = Signal()

    def __init__(self, ctx: dict | None = None, parent=None):
        super().__init__(parent)
        self.ctx = ctx or DEMO_CTX
        if "pnr" not in self.ctx:
            self.ctx["pnr"] = _gen_pnr()
        self.setStyleSheet(f"background:{C_BG};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent;border:none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        outer.addWidget(scroll)

        inner = QWidget(); inner.setStyleSheet(f"background:{C_BG};")
        scroll.setWidget(inner)

        root = QVBoxLayout(inner)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(20)

        # Header
        hdr = page_header(
            "Thanh toán An toàn",
            "GIAO DỊCH ĐƯỢC BẢO VỆ BỞI JETJET SECURITY",
            on_back=self.go_back,
        )
        root.addLayout(hdr)

        # 2-column layout
        cols = QHBoxLayout(); cols.setSpacing(20)

        # ── Left: payment form ────────────────────────────────────────────────
        left = QVBoxLayout(); left.setSpacing(16)
        left_card = QWidget()
        left_card.setStyleSheet(card_style(20))
        lc = QVBoxLayout(left_card); lc.setContentsMargins(24, 22, 24, 24); lc.setSpacing(16)

        # Method selector
        self._selector = MethodSelector()
        self._selector.changed.connect(self._on_method)
        lc.addWidget(self._selector)
        lc.addWidget(h_sep())

        # Card preview + form
        preview_row = QHBoxLayout(); preview_row.setSpacing(20)
        self._card_preview = CreditCardPreview()
        preview_row.addWidget(self._card_preview)

        self._card_form = CardForm(self._card_preview)
        preview_row.addWidget(self._card_form, 1)
        lc.addLayout(preview_row)

        # Other method forms (hidden by default)
        self._ewallet_form = EWalletForm(); self._ewallet_form.hide()
        self._miles_form   = MilesForm();   self._miles_form.hide()
        lc.addWidget(self._ewallet_form)
        lc.addWidget(self._miles_form)

        left.addWidget(left_card); left.addStretch()
        lw = QWidget(); lw.setStyleSheet("background:transparent;")
        lw.setLayout(left)
        cols.addWidget(lw, 62)

        # ── Right: order summary ──────────────────────────────────────────────
        self._order = OrderSummary(self.ctx)
        self._order.pay_clicked.connect(self._on_pay)
        rw = QWidget(); rw.setStyleSheet("background:transparent;")
        rl = QVBoxLayout(rw); rl.setContentsMargins(0,0,0,0)
        rl.addWidget(self._order); rl.addStretch()
        cols.addWidget(rw, 38)

        root.addLayout(cols)

    # ── Method switch ─────────────────────────────────────────────────────────
    def _on_method(self, idx: int):
        self._card_form.setVisible(idx == 0)
        self._card_preview.setVisible(idx == 0)
        self._ewallet_form.setVisible(idx == 1)
        self._miles_form.setVisible(idx == 3)

    # ── Pay button ────────────────────────────────────────────────────────────
    def _on_pay(self):
        dlg = SSLDialog(self._order.total(), self)
        dlg.payment_complete.connect(self._on_complete)
        dlg.exec()

    def _on_complete(self):
        self.payment_complete.emit(self.ctx)


if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    win = QMainWindow(); win.setWindowTitle("JetJet Air — Thanh toán"); win.resize(1380, 860)
    w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
    lay.addWidget(NavBar(0)); lay.addWidget(PaymentPage())
    win.setCentralWidget(w); win.show()
    sys.exit(app.exec())