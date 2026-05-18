"""
ticket.py
---------
Electronic Boarding Pass — JetJet Air
Fixed: 
  - Removed data-dependent rendering from __init__ to prevent startup crashes.
  - Implemented dynamic UI building in update_page().
  - Added robust None/empty handling for ctx, passenger, and flight data.
"""
from __future__ import annotations
import hashlib, random, sys
from datetime import datetime
from PySide6.QtCore import Qt, Signal, QRect, QRectF, QSize, QPoint
from PySide6.QtGui import (
    QColor, QPainter, QBrush, QPen, QPainterPath,
    QLinearGradient, QFont, QFontMetrics, QPixmap
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QSizePolicy,
    QGraphicsDropShadowEffect, QFileDialog, QMessageBox, QDialog
)
from booking_app.ui.pages.booking_shared import (
    lbl, h_sep, card_style, red_btn, page_header, NavBar,
    C_RED, C_RED2, C_DARK, C_WHITE, C_BG, C_BORDER,
    C_TEXT, C_MID, C_GRAY, C_LGRAY, C_GREEN, C_BLUE, C_ORANGE
)

# ── Helpers ──────────────────────────────────────────────────────────────────
def _safe_get(d: dict | None, key: str, default=None):
    if d is None: return default
    val = d.get(key)
    return val if val is not None else default

# ═════════════════════════════════════════════════════════════════════════════
# 1. BARCODE WIDGET
# ═════════════════════════════════════════════════════════════════════════════
class BarcodeWidget(QWidget):
    def __init__(self, data: str, bar_h: int = 64, bg: QColor = None, parent=None):
        super().__init__(parent)
        self._data  = data or "DEMO"
        self._bar_h = bar_h
        self._bg    = bg or QColor(C_WHITE)
        self.setFixedHeight(bar_h + 16)

    def _build_bars(self) -> list[tuple[int, bool]]:
        raw = hashlib.sha256(self._data.encode()).digest()
        bars: list[tuple[int, bool]] = []
        for is_d in (True, False, True): bars.append((2, is_d)) # Guard
        for byte in raw[:20]:
            nib_hi, nib_lo = (byte >> 4), (byte & 0xF)
            bars.append((max(1, nib_hi % 3 + 1), True))
            bars.append((max(1, nib_lo % 2 + 1), False))
            bars.append((max(1, (nib_hi ^ nib_lo) % 3 + 1), True))
            bars.append((1, False))
        for is_d in (True, False, True): bars.append((2, is_d)) # Guard
        return bars

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height(); p.fillRect(0, 0, w, h, QBrush(self._bg))
        bars = self._build_bars(); total = sum(u for u, _ in bars); unit_w = max(1.0, (w - 4) / total)
        x = 2.0
        for units, is_dark in bars:
            bw = max(1, int(units * unit_w))
            if is_dark: p.fillRect(int(x), 0, bw, self._bar_h, QColor(C_DARK))
            x += bw

# ═════════════════════════════════════════════════════════════════════════════
# 2. TICKET WIDGET (Visual Boarding Pass)
# ═════════════════════════════════════════════════════════════════════════════
class TicketWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ctx = {}
        self.setFixedSize(940, 360)
        self.setStyleSheet("background:transparent;")
        sh = QGraphicsDropShadowEffect(self); sh.setBlurRadius(36); sh.setXOffset(0); sh.setYOffset(10); sh.setColor(QColor(0, 0, 0, 45))
        self.setGraphicsEffect(sh)

    def update_data(self, ctx: dict):
        self.ctx = ctx; self.update()

    def paintEvent(self, _):
        if not self.ctx: return
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h, r = self.width(), self.height(), 20.0
        path = QPainterPath(); path.addRoundedRect(0, 0, w, h, r, r); p.fillPath(path, QBrush(QColor(C_WHITE)))
        
        # Perforation
        cut_x = 680.0; p.setPen(QPen(QColor(C_BORDER), 1.5, Qt.DashLine)); p.drawLine(int(cut_x), 15, int(cut_x), h - 15)
        p.setPen(Qt.NoPen); p.setBrush(QBrush(QColor(C_BG))); p.drawEllipse(int(cut_x - 12), -12, 24, 24); p.drawEllipse(int(cut_x - 12), h - 12, 24, 24)

        # Header
        p.save(); p.setClipPath(path); grad = QLinearGradient(0, 0, w, 0); grad.setColorAt(0, QColor(C_DARK)); grad.setColorAt(1, QColor("#2A2A4E"))
        p.fillRect(0, 0, w, 72, QBrush(grad)); p.restore()
        p.setPen(QPen(C_WHITE)); f = QFont(); f.setPointSize(14); f.setWeight(QFont.Black); p.setFont(f); p.drawText(24, 44, "JETJET AIR")
        f.setPointSize(9); f.setWeight(QFont.Medium); p.setFont(f); p.drawText(w - 240, 44, "BOARDING PASS  •  ECONOMY")

        # Data
        fl = _safe_get(self.ctx, "flight", {}); pax = _safe_get(self.ctx, "passenger", {})
        p.setPen(QPen(QColor(C_TEXT))); f.setPointSize(32); f.setWeight(QFont.ExtraBold); p.setFont(f)
        p.drawText(40, 150, _safe_get(fl, "dep_t", "00:00")); p.drawText(int(cut_x - 180), 150, _safe_get(fl, "arr_t", "00:00"))
        f.setPointSize(12); f.setWeight(QFont.Bold); p.setFont(f); p.setPen(QPen(QColor(C_MID)))
        p.drawText(40, 175, _safe_get(fl, "dep", "SGN")); p.drawText(int(cut_x - 180), 175, _safe_get(fl, "dst", "HAN"))
        p.setPen(QPen(QColor(C_GRAY))); f.setPointSize(9); p.setFont(f)
        p.drawText(40, 220, "HÀNH KHÁCH / PASSENGER"); p.drawText(40, 290, "MÃ ĐẶT CHỖ / PNR")
        p.setPen(QPen(QColor(C_TEXT))); f.setPointSize(14); f.setWeight(QFont.Bold); p.setFont(f)
        p.drawText(40, 245, str(_safe_get(pax, "name", "GUEST")).upper()); p.setPen(QPen(C_RED)); p.drawText(40, 315, str(_safe_get(self.ctx, "pnr", "TBA")))
        
        # Stub
        p.setPen(QPen(C_GRAY)); f.setPointSize(8); p.setFont(f); p.drawText(int(cut_x + 25), 110, "CHUYẾN BAY"); p.drawText(int(cut_x + 25), 180, "GHẾ / SEAT"); p.drawText(int(cut_x + 25), 250, "CỔNG / GATE")
        p.setPen(QPen(C_TEXT)); f.setPointSize(13); f.setWeight(QFont.Bold); p.setFont(f)
        p.drawText(int(cut_x + 25), 135, _safe_get(fl, "code", "—")); p.drawText(int(cut_x + 25), 205, ", ".join(_safe_get(self.ctx, "seat_labels", ["--"]))); p.drawText(int(cut_x + 25), 275, str(_safe_get(self.ctx, "gate", "B22")))

# ═════════════════════════════════════════════════════════════════════════════
# 3. SUCCESS BANNER
# ═════════════════════════════════════════════════════════════════════════════
class SuccessBanner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:#ECFDF5; border:1.5px solid #A7F3D0; border-radius:16px;")
        self._root = QHBoxLayout(self); self._root.setContentsMargins(22, 16, 22, 16); self._root.setSpacing(16)

    def update_data(self, ctx: dict):
        while self._root.count():
            item = self._root.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        chk = QLabel("✅"); chk.setFixedSize(48, 48); chk.setAlignment(Qt.AlignCenter)
        chk.setStyleSheet(f"font-size:28px; background:{C_GREEN}; border-radius:24px; color:white;")
        self._root.addWidget(chk)

        info = QVBoxLayout(); info.setSpacing(4)
        info.addWidget(lbl("Đặt vé thành công! Cảm ơn bạn đã sử dụng JetJet Air.", 15, 800, "#065F46"))
        pax = _safe_get(ctx, "passenger", {})
        email = _safe_get(pax, "email", "—")
        info.addWidget(lbl(f"Email xác nhận đã được gửi đến: {email}", 12, 500, "#047857"))
        self._root.addLayout(info); self._root.addStretch()

        pnr_col = QVBoxLayout(); pnr_col.setSpacing(3); pnr_col.setAlignment(Qt.AlignRight)
        pnr_col.addWidget(lbl("MÃ PNR", 9, 600, "#047857", 1.0))
        pnr_val = lbl(str(_safe_get(ctx, "pnr", "—")), 20, 900, C_TEXT); pnr_val.setAlignment(Qt.AlignRight)
        pnr_col.addWidget(pnr_val); self._root.addLayout(pnr_col)

# ═════════════════════════════════════════════════════════════════════════════
# 4. TICKET PAGE
# ═════════════════════════════════════════════════════════════════════════════
class TicketPage(QWidget):
    go_home = Signal()

    def __init__(self, ctx: dict | None = None, parent=None):
        super().__init__(parent)
        self.ctx = ctx or {}
        self.setStyleSheet(f"background:{C_BG};")
        
        main_lay = QVBoxLayout(self); main_lay.setContentsMargins(0, 0, 0, 0)
        self._scroll = QScrollArea(); self._scroll.setWidgetResizable(True); self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setStyleSheet("background:transparent; border:none;"); main_lay.addWidget(self._scroll)
        
        # Shell widgets (Empty at first)
        self._container = QWidget(); self._container.setStyleSheet(f"background:{C_BG};")
        self._root = QVBoxLayout(self._container); self._root.setContentsMargins(28, 24, 28, 32); self._root.setSpacing(20)
        
        self._header = QVBoxLayout(); self._root.addLayout(self._header)
        self._banner = SuccessBanner(); self._root.addWidget(self._banner)
        self._ticket = TicketWidget(); self._root.addWidget(self._ticket)
        self._info_strip = QHBoxLayout(); info_w = QWidget(); info_w.setStyleSheet(f"background:{C_WHITE}; border:1px solid {C_BORDER}; border-radius:14px;")
        info_w.setLayout(self._info_strip); self._root.addWidget(info_w)
        
        self._actions = QHBoxLayout(); self._root.addLayout(self._actions)
        self._root.addStretch()
        self._scroll.setWidget(self._container)

    def update_page(self, ctx: dict | None = None):
        if ctx: self.ctx = ctx
        
        # 1. Update Header
        while self._header.count(): self._header.takeAt(0).widget().deleteLater()
        self._header.addWidget(lbl("Vé Máy Bay Điện Tử", 24, 800, C_TEXT))
        self._header.addWidget(lbl("Vé của bạn đã sẵn sàng. Hãy lưu lại để check-in.", 13, 400, C_GRAY))

        # 2. Update Banner & Ticket
        self._banner.update_data(self.ctx)
        self._ticket.update_data(self.ctx)

        # 3. Update Info Strip
        while self._info_strip.count():
            item = self._info_strip.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._clear_layout(item.layout())
        
        for icon, key, val in [
            ("🚪", "CỬA KHỞI HÀNH", _safe_get(self.ctx, "gate", "B22")),
            ("🏢", "NHÀ GA", _safe_get(self.ctx, "terminal", "Nhà ga T1")),
            ("🗺", "KHU VỰC GHẾ", _safe_get(self.ctx, "zone", "Khu B")),
            ("🔐", "BẢO MẬT", "PCI-DSS Level 1"),
            ("💳", "TỔNG TIỀN", f"${_safe_get(self.ctx, 'total', 0)}")
        ]:
            col = QVBoxLayout(); col.setSpacing(4); hd = QHBoxLayout(); hd.setSpacing(5)
            hd.addWidget(lbl(icon, 13, 400, C_GRAY)); hd.addWidget(lbl(key, 9, 600, C_GRAY, 0.5))
            col.addLayout(hd); col.addWidget(lbl(str(val), 14, 700, C_TEXT)); self._info_strip.addLayout(col)
        self._info_strip.addStretch()

        # 4. Update Actions
        while self._actions.count(): self._actions.takeAt(0).widget().deleteLater()
        btn_dl = QPushButton("📥  TẢI VỀ (PNG)"); btn_dl.setFixedHeight(50); btn_dl.setCursor(Qt.PointingHandCursor)
        btn_dl.setStyleSheet(f"QPushButton{{background:{C_DARK}; color:white; border-radius:25px; font-size:13px; font-weight:700; padding:0 24px;}} QPushButton:hover{{background:#2A2A4E;}}")
        btn_dl.clicked.connect(self._save_ticket); self._actions.addWidget(btn_dl)
        
        btn_home = QPushButton("QUAY LẠI TRANG CHỦ"); btn_home.setFixedHeight(50); btn_home.setCursor(Qt.PointingHandCursor)
        btn_home.setStyleSheet(f"QPushButton{{background:transparent; border:1.5px solid {C_BORDER}; border-radius:25px; font-size:13px; font-weight:600; color:{C_GRAY}; padding:0 24px;}} QPushButton:hover{{color:{C_RED};}}")
        btn_home.clicked.connect(self.go_home.emit); self._actions.addWidget(btn_home); self._actions.addStretch()

    def _save_ticket(self):
        path, _ = QFileDialog.getSaveFileName(self, "Lưu vé", f"Ticket_{_safe_get(self.ctx, 'pnr', 'JJ')}.png", "PNG (*.png)")
        if path: self._ticket.grab().save(path); QMessageBox.information(self, "Thành công", f"Đã lưu vé tại:\n{path}")

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            elif item.layout(): self._clear_layout(item.layout())

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    win = QMainWindow(); win.resize(1200, 800)
    page = TicketPage(); win.setCentralWidget(page); win.show()
    # page.update_page(DEMO_CTX) # Uncomment to test with data
    sys.exit(app.exec())
