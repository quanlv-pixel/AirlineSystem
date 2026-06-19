"""
payment.py
----------
Thanh toán An toàn — JetJet Air Booking Flow
Updated: Promo code input in OrderSummary, dynamic total recalculation,
         promo_used stored in ctx for DB persistence.
"""
from __future__ import annotations
import hashlib, random, string, sys
import requests
import qrcode
import socket
from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtGui import (QColor, QPainter, QBrush, QPen, QPainterPath,
                            QLinearGradient, QFont, QImage, QPixmap)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QLineEdit,
    QDialog, QProgressBar
)
from booking_app.ui.pages.booking_shared import (lbl, h_sep, card_style, red_btn, page_header,
                             NavBar, C_RED, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY,
                             C_GREEN, C_BLUE, C_ORANGE)
from shared.services.member_service import apply_promo

def _gen_pnr():
    return "JJ" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

DEMO_CTX = dict(
    flight=dict(code="JJ101", dep="SGN", dst="HAN", dep_t="08:00", arr_t="10:15", dur="2H 15M", aircraft="AIRBUS A321NEO"),
    passenger=dict(name="Lê Văn Quân", email="quanle@example.com"),
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

class QRCodeWidget(QLabel):
    def __init__(self, url_data: str = "WAITING", size: int = 200, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setStyleSheet("background: white; border-radius: 12px; border: 1px solid #E4E6F0;")
        self.setAlignment(Qt.AlignCenter)
        self.update_qr(url_data)

    def update_qr(self, url_data: str):
        # Tạo mã QR thật
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(url_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Chuyển ảnh QR sang PySide6
        img = img.convert("RGBA")
        data = img.tobytes("raw", "RGBA")
        qimg = QImage(data, img.size[0], img.size[1], QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimg)
        
        self.setPixmap(pixmap.scaled(self.width() - 20, self.height() - 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))

class SSLDialog(QDialog):
    payment_complete = Signal()
    def __init__(self, total, parent=None):
        super().__init__(parent); self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog); self.setFixedSize(320, 180)
        self.setStyleSheet(f"background:{C_WHITE}; border:1px solid {C_BORDER}; border-radius:12px;")
        v = QVBoxLayout(self); v.setContentsMargins(30, 30, 30, 30); v.setSpacing(15)
        v.addWidget(lbl("🔒 ĐANG XỬ LÝ THANH TOÁN...", 13, 800, C_DARK), 0, Qt.AlignCenter)
        v.addWidget(lbl(f"Đang kết nối tới cổng thanh toán SSL bảo mật cho số tiền ${total}...", 11, 400, C_GRAY, 1.0), 0, Qt.AlignCenter)
        self._bar = QProgressBar(); self._bar.setRange(0, 0); self._bar.setFixedHeight(6)
        self._bar.setStyleSheet(f"QProgressBar {{ background:{C_LGRAY}; border:none; border-radius:3px; }} QProgressBar::chunk {{ background:{C_RED}; border-radius:3px; }}")
        v.addWidget(self._bar); QTimer.singleShot(2500, self._finish)
    def _finish(self): self.payment_complete.emit(); self.accept()


# ─────────────────────────────────────────────────────────────────────────────
# OrderSummary — with Promo Code input
# ─────────────────────────────────────────────────────────────────────────────
class OrderSummary(QWidget):
    pay_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(20))
        self._ctx: dict = {}
        self._discounted_total: float | None = None
        self._applied_code: str | None = None

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(22, 22, 22, 22)
        self._root.setSpacing(0)

    # ── Build / rebuild UI ────────────────────────────────────────────────────
    # ── Hàm cập nhật dữ liệu ──────────────────────────────────────────────────
    def update_data(self, ctx: dict):
        self._ctx = ctx
        self._applied_code = ctx.get("promo_used")
        
        # Lấy số lượng ghế để nhân tiền
        seats = self._ctx.get("seat_labels", [])
        num_seats = len(seats) if seats else 1
        
        base = self._ctx.get("base_price", 0) * num_seats
        tax = self._ctx.get("tax", 45) * num_seats
        fee = self._ctx.get("fee", 12) * num_seats
        seat_f = self._ctx.get("seat_fee", 0)
        
        subtotal = base + tax + fee + seat_f
        
        # Nếu có mã giảm giá thì tính lại
        if self._applied_code:
            from shared.services.member_service import apply_promo
            valid, msg, new_total = apply_promo(self._applied_code, base, seat_f, tax, fee)
            if valid:
                self._discounted_total = new_total
                self._ctx["total"] = new_total
            else:
                self._discounted_total = None
                self._ctx["total"] = subtotal
        else:
            self._discounted_total = None
            self._ctx["total"] = subtotal
            
        # Tự động vẽ lại toàn bộ các nhãn (labels) trên màn hình (không dùng setText)
        self._rebuild()

    def _rebuild(self):
        # Clear existing widgets
        while self._root.count():
            item = self._root.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._clear_layout(item.layout())

        ctx = self._ctx
        self._root.addWidget(lbl("Chi tiết đơn hàng", 17, 800, C_TEXT))
        self._root.addSpacing(18)

        pnr   = ctx.get("pnr", "TBA")
        fl    = ctx.get("flight", {})
        pax   = ctx.get("passenger", {})
        seats = ctx.get("seat_labels", [])

        def _row(k, v, c=C_TEXT, b=False):
            r = QHBoxLayout()
            r.addWidget(lbl(k, 11, 500, C_GRAY))
            r.addStretch()
            r.addWidget(lbl(v, 11, 700 if b else 500, c))
            return r

        self._root.addLayout(_row("PNR", pnr, C_RED, True));        self._root.addSpacing(8)
        self._root.addLayout(_row("CHUYẾN BAY", fl.get("code", "—"))); self._root.addSpacing(8)
        self._root.addLayout(_row("HÀNH KHÁCH", pax.get("name", "—"))); self._root.addSpacing(8)
        self._root.addLayout(_row("SỐ GHẾ", ", ".join(seats) if seats else "—"))
        self._root.addSpacing(16)
        self._root.addWidget(h_sep())
        self._root.addSpacing(14)

        num_seats = len(seats) if seats else 1
        base     = ctx.get("base_price", 0) * num_seats
        tax      = ctx.get("tax", 45) * num_seats
        fee      = ctx.get("fee", 12) * num_seats
        seat_fee = ctx.get("seat_fee", 0) 
        raw_total = base + seat_fee + tax + fee

        for k, v in [("Giá vé", f"${base}"), ("Ghế", f"${seat_fee}"), ("Thuế & Phí", f"${tax + fee}")]:
            self._root.addLayout(_row(k, v))
            self._root.addSpacing(10)

        # ── Promo code section ────────────────────────────────────────────────
        self._root.addWidget(h_sep())
        self._root.addSpacing(12)
        self._root.addWidget(lbl("Mã ưu đãi", 12, 700, C_MID))
        self._root.addSpacing(6)

        promo_row = QHBoxLayout()
        promo_row.setSpacing(8)
        self._promo_input = QLineEdit()
        self._promo_input.setPlaceholderText("Nhập mã giảm giá...")
        self._promo_input.setFixedHeight(38)
        self._promo_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C_LGRAY}; border: 1.5px solid {C_BORDER};
                border-radius: 8px; padding: 0 10px;
                font-size: 12px; color: {C_TEXT};
            }}
            QLineEdit:focus {{ border-color: {C_RED}; }}
        """)
        if self._applied_code:
            self._promo_input.setText(self._applied_code)
            self._promo_input.setEnabled(False)

        apply_btn = QPushButton("ÁP DỤNG")
        apply_btn.setFixedSize(80, 38)
        apply_btn.setCursor(Qt.PointingHandCursor)
        apply_btn.setStyleSheet(f"""
            QPushButton {{ background: {C_DARK}; color: {C_WHITE}; border: none;
                           border-radius: 8px; font-size: 11px; font-weight: 700; }}
            QPushButton:hover {{ background: {C_RED}; }}
        """)
        apply_btn.clicked.connect(self._on_apply_promo)
        if self._applied_code:
            apply_btn.setText("✓ ĐÃ ÁP")
            apply_btn.setEnabled(False)
            apply_btn.setStyleSheet(f"""
                QPushButton {{ background: {C_GREEN}; color: {C_WHITE}; border: none;
                               border-radius: 8px; font-size: 11px; font-weight: 700; }}
            """)

        promo_row.addWidget(self._promo_input, 1)
        promo_row.addWidget(apply_btn)
        self._root.addLayout(promo_row)
        self._root.addSpacing(6)

        # Promo feedback label
        self._promo_msg = QLabel("")
        self._promo_msg.setStyleSheet("font-size: 11px; color: #2E7D32; background: transparent;")
        self._root.addWidget(self._promo_msg)
        if self._applied_code:
            discount_amt = raw_total - self._discounted_total
            self._promo_msg.setText(f"✓ Đã áp dụng — tiết kiệm ${discount_amt:.0f}")

        self._root.addSpacing(12)
        self._root.addWidget(h_sep())
        self._root.addSpacing(14)

        # Total row
        display_total = self._discounted_total if self._discounted_total is not None else raw_total
        tr = QHBoxLayout()
        tr.addWidget(lbl("TỔNG CỘNG", 11, 700, C_GRAY, 1.0))
        tr.addStretch()
        self._total_lbl = lbl(f"${display_total:.0f}", 32, 900, C_RED)
        tr.addWidget(self._total_lbl)
        self._root.addLayout(tr)
        self._root.addSpacing(20)

        btn = red_btn("THANH TOÁN NGAY  🪪", 52)
        btn.clicked.connect(self.pay_clicked)
        self._root.addWidget(btn)
        self._root.addStretch()

    def _on_apply_promo(self):
        code = self._promo_input.text().strip().upper()
        if not code:
            self._promo_msg.setText("Vui lòng nhập mã ưu đãi.")
            self._promo_msg.setStyleSheet("font-size: 11px; color: #C62828; background: transparent;")
            return

        base     = self._ctx.get("base_price", 0)
        seat_fee = self._ctx.get("seat_fee", 0)
        tax      = self._ctx.get("tax", 45)
        fee      = self._ctx.get("fee", 12)

        valid, msg, new_total = apply_promo(code, base, seat_fee, tax, fee)
        if valid:
            self._applied_code = code
            self._discounted_total = new_total
            # Write back into ctx so BookingWindow saves it
            self._ctx["promo_used"]  = code
            self._ctx["total"]       = new_total
            self._promo_msg.setText(f"✓ {msg}")
            self._promo_msg.setStyleSheet("font-size: 11px; color: #2E7D32; background: transparent;")
        else:
            self._promo_msg.setText(f"✗ {msg}")
            self._promo_msg.setStyleSheet("font-size: 11px; color: #C62828; background: transparent;")
            return

        # Rebuild to lock the field and update total display
        self._rebuild()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_layout(child.layout())


# ─────────────────────────────────────────────────────────────────────────────
# PaymentPage
# ─────────────────────────────────────────────────────────────────────────────
class PaymentPage(QWidget):
    payment_complete = Signal(dict)
    go_back = Signal()

    def __init__(self, ctx: dict | None = None, parent=None):
        super().__init__(parent)
        self.ctx = ctx or {}
        self._is_paying: bool = False  # guard against double-click opening multiple SSLDialogs
        self.setStyleSheet(f"background:{C_BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(20)
        root.addLayout(page_header("Thanh toán An toàn", "GIAO DỊCH BẢO MẬT", on_back=self.go_back))

        body = QHBoxLayout(); body.setSpacing(20)
        left = QVBoxLayout(); left.setSpacing(15)

        # Method Tabs
        tab_lay = QHBoxLayout(); tab_lay.setSpacing(10)
        self.btn_card = QPushButton("Thẻ Tín Dụng")
        self.btn_qr   = QPushButton("Mã QR (VNPay/Momo)")
        for b in [self.btn_card, self.btn_qr]:
            b.setCheckable(True); b.setFixedHeight(45); b.setCursor(Qt.PointingHandCursor)
        self.btn_card.setChecked(True)
        tab_lay.addWidget(self.btn_card, 1); tab_lay.addWidget(self.btn_qr, 1)
        left.addLayout(tab_lay)

        # Payment Forms Stack
        from PySide6.QtWidgets import QStackedWidget
        self.method_stack = QStackedWidget()

        # Card Form
        card_w = QWidget(); card_w.setStyleSheet(card_style(20))
        cw_lay = QVBoxLayout(card_w); cw_lay.setSpacing(15)
        self._preview = CreditCardPreview(); cw_lay.addWidget(self._preview, 0, Qt.AlignCenter)
        self._f_num  = QLineEdit(); self._f_num.setPlaceholderText("SỐ THẺ");   self._f_num.textChanged.connect(self._preview.set_number);  cw_lay.addWidget(self._f_num)
        self._f_name = QLineEdit(); self._f_name.setPlaceholderText("TÊN CHỦ THẺ"); self._f_name.textChanged.connect(self._preview.set_name); cw_lay.addWidget(self._f_name)
        self.method_stack.addWidget(card_w)

        # QR Form
        qr_w = QWidget(); qr_w.setStyleSheet(card_style(20))
        qw_lay = QVBoxLayout(qr_w); qw_lay.setAlignment(Qt.AlignCenter)
        qw_lay.addWidget(lbl("QUÉT MÃ ĐỂ THANH TOÁN", 14, 800, C_DARK))
        self.qr_widget = QRCodeWidget("JETJET-ORDER-12345"); qw_lay.addWidget(self.qr_widget)
        qw_lay.addWidget(lbl("Sử dụng ứng dụng ngân hàng hoặc ví điện tử để quét", 11, 400, C_GRAY))
        self.method_stack.addWidget(qr_w)

        left.addWidget(self.method_stack); left.addStretch()
        body.addLayout(left, 62)

        self._order = OrderSummary()
        self._order.pay_clicked.connect(self._on_pay)
        body.addWidget(self._order, 38)
        root.addLayout(body)

        self.btn_card.clicked.connect(lambda: self._switch_method(0))
        self.btn_qr.clicked.connect(lambda: self._switch_method(1))

        # Thêm Radar quét trạng thái QR
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self._check_payment_status)
        self._switch_method(0)


    def _switch_method(self, idx):
        self.method_stack.setCurrentIndex(idx)
        st = "background:{}; color:{}; border:none; border-radius:8px; font-weight:700;"
        self.btn_card.setStyleSheet(st.format(C_RED if idx==0 else C_WHITE, C_WHITE if idx==0 else C_MID))
        self.btn_qr.setStyleSheet(st.format(C_RED if idx==1 else C_WHITE, C_WHITE if idx==1 else C_MID))
        
        # BẬT/TẮT RADAR QUÉT QR
        if idx == 1:
            pnr = self.ctx.get('pnr', 'TEST')
            amount = self.ctx.get('total', 0)
            
            # Tự động lấy IP máy tính
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            except:
                ip = "127.0.0.1"
            finally:
                s.close()
                
            # Tạo Link thật cho điện thoại quét
            payment_url = f"http://{ip}:5000/pay/{pnr}/{amount}"
            self.qr_widget.update_qr(payment_url)
            
            # Bật Radar, quét 2 giây 1 lần
            self.check_timer.start(2000)
        else:
            self.check_timer.stop()

    def _check_payment_status(self):
        pnr = self.ctx.get('pnr', 'TEST')
        try:
            # Máy tính hỏi Server xem điện thoại đã bấm nút chưa
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            
            res = requests.get(f"http://{ip}:5000/api/status/{pnr}", timeout=1)
            data = res.json()
            
            if data.get("status") == "PAID":
                self.check_timer.stop()
                # Tự động phát tín hiệu hoàn thành y hệt như lúc điền thẻ tín dụng!
                self.payment_complete.emit(self.ctx)
        except Exception as e:
            pass # Bỏ qua nếu mất mạng hoặc server chưa bật

    def update_page(self, ctx: dict | None = None):
        if ctx: self.ctx = ctx
        self._order.update_data(self.ctx)
        self.qr_widget.data = f"JETJET-{self.ctx.get('pnr', 'PAY')}-{self.ctx.get('total', 0)}"
        self.qr_widget.update()

    def _on_pay(self):
        # Prevent multiple SSLDialog instances from opening on rapid/double-click
        if self._is_paying:
            return
        self._is_paying = True
        try:
            total = self.ctx.get("total", 0)
            dlg = SSLDialog(total, self)
            # Qt.SingleShotConnection ensures the slot fires at most once per dialog,
            # preventing double create_booking() calls if the dialog is re-shown.
            dlg.payment_complete.connect(
                lambda: self.payment_complete.emit(self.ctx),
                Qt.SingleShotConnection
            )
            dlg.exec()
        finally:
            self._is_paying = False



if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    win = QMainWindow(); win.resize(1380, 860)
    w = QWidget(); lay = QVBoxLayout(w); lay.addWidget(NavBar(0)); lay.addWidget(PaymentPage(DEMO_CTX))
    win.setCentralWidget(w); win.show(); sys.exit(app.exec())
