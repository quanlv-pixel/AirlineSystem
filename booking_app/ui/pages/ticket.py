"""
ticket.py
---------
Vé máy bay điện tử — JetJet Air
• Boarding pass style chuyên nghiệp
• Mã vạch điện tử (từ PNR hash)
• PNR & SHA-256 security hash
• Thông tin đầy đủ: cổng, ga, khu vực ghế
• Tải về PNG / In vé (QPrinter fallback → save PNG)
"""
from __future__ import annotations
import hashlib, random, sys
from datetime import datetime
from PySide6.QtCore import Qt, Signal, QRect, QRectF, QSize
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
    lbl, h_sep, card_style, red_btn, page_header, NavBar, NavLogo,
    C_RED, C_RED2, C_DARK, C_WHITE, C_BG, C_BORDER,
    C_TEXT, C_MID, C_GRAY, C_LGRAY, C_GREEN, C_BLUE, C_ORANGE
)

# ── Demo data ────────────────────────────────────────────────────────────────
_NOW = datetime.now()
_TICKET_ID = f"TK-{_NOW.strftime('%Y%m%d')}-{random.randint(100,999)}"

DEMO_CTX = dict(
    pnr       = "JJXL92",
    flight    = dict(code="JJ101", aircraft="AIRBUS A321NEO",
                     dep="SGN", dst="HAN",
                     dep_full="Tân Sơn Nhất", dst_full="Nội Bài",
                     dep_t="08:00", arr_t="10:15", dur="2H 15M"),
    passenger = dict(name="Lê Văn Quân", email="quanle19112007@gmail.com"),
    seat_labels = ["4B", "5B"],
    seat_fee  = 50, base_price=120, tax=57, total=227,
    gate="B22", terminal="Nhà ga T1", zone="Khu B",
    flight_date="14 May 2026",
    ticket_id = _TICKET_ID,
)


# ═════════════════════════════════════════════════════════════════════════════
# 1. BARCODE WIDGET
# ═════════════════════════════════════════════════════════════════════════════
class BarcodeWidget(QWidget):
    """Mã vạch điện tử được tạo từ PNR hash."""

    def __init__(self, data: str, bar_h: int = 64, bg: QColor = None, parent=None):
        super().__init__(parent)
        self._data  = data
        self._bar_h = bar_h
        self._bg    = bg or QColor(C_WHITE)
        self.setFixedHeight(bar_h + 16)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _build_bars(self) -> list[tuple[int, bool]]:
        """Trả về list (width_units, is_dark) từ hash của data."""
        raw = hashlib.sha256(self._data.encode()).digest()
        bars: list[tuple[int, bool]] = []
        # Guard start
        for is_d in (True, False, True):
            bars.append((2, is_d))
        # Data bars (20 bytes → 80 bars)
        for byte in raw[:20]:
            nib_hi = (byte >> 4)
            nib_lo = (byte & 0xF)
            bars.append((max(1, nib_hi % 3 + 1), True))
            bars.append((max(1, nib_lo % 2 + 1), False))
            bars.append((max(1, (nib_hi ^ nib_lo) % 3 + 1), True))
            bars.append((1, False))
        # Guard end
        for is_d in (True, False, True):
            bars.append((2, is_d))
        return bars

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Background
        p.fillRect(0, 0, w, h, QBrush(self._bg))

        bars   = self._build_bars()
        total  = sum(u for u, _ in bars)
        unit_w = max(1.0, (w - 4) / total)

        x = 2.0
        for units, is_dark in bars:
            bw = max(1, int(units * unit_w))
            if is_dark:
                p.fillRect(int(x), 0, bw, self._bar_h, QColor(C_DARK))
            x += bw

        # Data text below bars
        p.setPen(QPen(QColor(C_GRAY)))
        f = QFont(); f.setFamily("Courier New"); f.setPointSize(7)
        p.setFont(f)
        display = " ".join(self._data[i:i+4] for i in range(0, len(self._data), 4))
        p.drawText(0, self._bar_h + 2, w, 14, Qt.AlignCenter, display)


# ═════════════════════════════════════════════════════════════════════════════
# 2. PERFORATED SEPARATOR (đường đứt giữa main và stub)
# ═════════════════════════════════════════════════════════════════════════════
class PerforatedSep(QWidget):
    def __init__(self, bg_color: str = C_BG, parent=None):
        super().__init__(parent)
        self._bg = QColor(bg_color)
        self.setFixedWidth(30)
        self.setStyleSheet("background:transparent;")

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx = w // 2

        # Semi-circle cutouts at top and bottom (page background color)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(self._bg))
        r = 13
        p.drawEllipse(cx - r, -r, r * 2, r * 2)
        p.drawEllipse(cx - r, h - r, r * 2, r * 2)

        # Dashed center line
        pen = QPen(QColor(200, 205, 220), 1.5, Qt.DashLine)
        pen.setDashPattern([5, 5])
        p.setPen(pen)
        p.drawLine(cx, r, cx, h - r)


# ═════════════════════════════════════════════════════════════════════════════
# 3. TICKET HEADER (red gradient bar)
# ═════════════════════════════════════════════════════════════════════════════
class TicketHeader(QWidget):
    HEIGHT = 64

    def __init__(self, ctx: dict, parent=None):
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self.setStyleSheet("background:transparent;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 0, 22, 0)
        lay.setSpacing(0)

        def _wlbl(text, size=11, weight=700, spacing=0):
            l = QLabel(text)
            l.setStyleSheet(
                f"font-size:{size}px;font-weight:{weight};"
                f"color:white;background:transparent;border:none;"
                + (f"letter-spacing:{spacing}px;" if spacing else "")
            )
            return l

        # Left: logo + brand
        left = QHBoxLayout(); left.setSpacing(10)
        logo_circle = QLabel("✈")
        logo_circle.setFixedSize(32, 32)
        logo_circle.setAlignment(Qt.AlignCenter)
        logo_circle.setStyleSheet(
            "font-size:16px;color:white;background:rgba(255,255,255,0.2);"
            "border-radius:16px;border:1.5px solid rgba(255,255,255,0.4);"
        )
        brand = QVBoxLayout(); brand.setSpacing(0)
        brand.addWidget(_wlbl("JETJET AIR", 15, 900, 1))
        brand.addWidget(_wlbl("AIRLINES", 8, 600, 3))
        left.addWidget(logo_circle)
        left.addLayout(brand)
        lay.addLayout(left)

        lay.addStretch()

        # Center: ticket type
        center = QVBoxLayout(); center.setSpacing(2); center.setAlignment(Qt.AlignCenter)
        center.addWidget(_wlbl("VÉ MÁY BAY ĐIỆN TỬ", 9, 600, 2.5))
        center.addWidget(_wlbl("E-BOARDING PASS", 8, 500, 1.5))
        lay.addLayout(center)

        lay.addStretch()

        # Right: flight + date
        right = QVBoxLayout(); right.setSpacing(2); right.setAlignment(Qt.AlignRight)
        fl = ctx.get("flight", {})
        right.addWidget(_wlbl(fl.get("code", "JJ101"), 16, 900))
        right.addWidget(_wlbl(ctx.get("flight_date", "14 May 2026"), 9, 500, 0.5))
        lay.addLayout(right)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(C_RED))
        grad.setColorAt(1.0, QColor(C_RED2))
        p.fillRect(0, 0, w, h, QBrush(grad))


# ═════════════════════════════════════════════════════════════════════════════
# 4. MAIN SECTION (left ~65% of body)
# ═════════════════════════════════════════════════════════════════════════════
class TicketMain(QWidget):
    def __init__(self, ctx: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")

        fl  = ctx.get("flight", {})
        pax = ctx.get("passenger", {})

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 16, 16)
        root.setSpacing(0)

        # ── Route timeline ────────────────────────────────────────────────────
        route_row = QHBoxLayout(); route_row.setSpacing(0)

        # Departure
        dep_col = QVBoxLayout(); dep_col.setSpacing(3)
        dep_col.addWidget(lbl(fl.get("dep_t","08:00"), 38, 900, C_TEXT))
        dep_col.addWidget(lbl(fl.get("dep","SGN"),     16, 800, C_TEXT))
        dep_col.addWidget(lbl(fl.get("dep_full","Tân Sơn Nhất"), 10, 400, C_GRAY))
        route_row.addLayout(dep_col)

        # Center timeline
        mid_col = QVBoxLayout(); mid_col.setSpacing(6); mid_col.setAlignment(Qt.AlignCenter)
        dur = lbl(fl.get("dur","2H 15M"), 10, 600, C_GRAY)
        dur.setAlignment(Qt.AlignCenter)
        mid_col.addWidget(dur)
        mid_col.addWidget(_RouteArrow())
        direct_row = QHBoxLayout(); direct_row.setSpacing(4); direct_row.setAlignment(Qt.AlignCenter)
        direct_row.addWidget(lbl("●", 9, 700, C_RED))
        direct_row.addWidget(lbl("BAY THẲNG", 9, 600, C_GRAY, 0.5))
        mid_col.addLayout(direct_row)
        route_row.addLayout(mid_col, 1)

        # Arrival
        arr_col = QVBoxLayout(); arr_col.setSpacing(3); arr_col.setAlignment(Qt.AlignRight)
        arr_col.addWidget(lbl(fl.get("arr_t","10:15"), 38, 900, C_TEXT))
        arr_col.addWidget(lbl(fl.get("dst","HAN"),     16, 800, C_TEXT))
        arr_col.addWidget(lbl(fl.get("dst_full","Nội Bài"), 10, 400, C_GRAY))
        route_row.addLayout(arr_col)

        root.addLayout(route_row)
        root.addSpacing(16)
        root.addWidget(_DashedHSep())
        root.addSpacing(14)

        # ── Info grid (3 columns) ─────────────────────────────────────────────
        grid = QHBoxLayout(); grid.setSpacing(0)

        def _col(pairs: list[tuple[str,str]]) -> QVBoxLayout:
            c = QVBoxLayout(); c.setSpacing(10)
            for key, val in pairs:
                item = QVBoxLayout(); item.setSpacing(2)
                item.addWidget(lbl(key, 9, 600, C_GRAY, 0.5))
                item.addWidget(lbl(val, 13, 700, C_TEXT))
                c.addLayout(item)
            return c

        seats_str = "  ".join(ctx.get("seat_labels", ["4B","5B"]))
        col1 = _col([
            ("HÀNH KHÁCH",       pax.get("name","—")),
            ("SỐ GHẾ",          seats_str),
            ("CỔNG KHỞI HÀNH",  ctx.get("gate","B22")),
        ])
        col2 = _col([
            ("NGÀY BAY",        ctx.get("flight_date","14 May 2026")),
            ("HẠNG GHẾ",        "Phổ thông"),
            ("NHÀ GA",          ctx.get("terminal","Nhà ga T1")),
        ])
        col3 = _col([
            ("LOẠI MÁY BAY",    fl.get("aircraft","AIRBUS A321NEO")),
            ("KHU VỰC",         ctx.get("zone","Khu B")),
            ("LOẠI CHUYẾN",     "Quốc nội"),
        ])

        grid.addLayout(col1); grid.addStretch()
        grid.addLayout(col2); grid.addStretch()
        grid.addLayout(col3)
        root.addLayout(grid)
        root.addStretch()


class _RouteArrow(QWidget):
    """Mũi tên có icon máy bay giữa hai điểm."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(24)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("background:transparent;")

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cy = h // 2
        # Left line
        pen = QPen(QColor(C_BORDER), 1.5); p.setPen(pen)
        p.drawLine(0, cy, w//2 - 14, cy)
        # Right line
        p.drawLine(w//2 + 14, cy, w, cy)
        # Arrow tip
        p.setPen(QPen(QColor(C_BORDER), 1.5))
        p.drawLine(w - 8, cy - 5, w, cy)
        p.drawLine(w - 8, cy + 5, w, cy)
        # Plane icon center
        p.setPen(QPen(QColor(C_RED)))
        f = QFont(); f.setPointSize(12)
        p.setFont(f)
        p.drawText(w//2 - 10, 0, 20, h, Qt.AlignCenter, "✈")


class _DashedHSep(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("background:transparent;")

    def paintEvent(self, _):
        p = QPainter(self)
        pen = QPen(QColor(C_BORDER), 1, Qt.DashLine)
        pen.setDashPattern([5, 5])
        p.setPen(pen)
        p.drawLine(0, 0, self.width(), 0)


# ═════════════════════════════════════════════════════════════════════════════
# 5. STUB SECTION (right, dark navy)
# ═════════════════════════════════════════════════════════════════════════════
class TicketStub(QWidget):
    STUB_W = 230

    def __init__(self, ctx: dict, parent=None):
        super().__init__(parent)
        self.setFixedWidth(self.STUB_W)
        self.setStyleSheet(f"background:{C_DARK};")

        pnr    = ctx.get("pnr", "JJXL92")
        seats  = "  ".join(ctx.get("seat_labels", ["4B","5B"]))
        total  = ctx.get("total", 227)
        ticket_id = ctx.get("ticket_id", _TICKET_ID)

        def _wlbl(text, size=11, weight=600, color=C_WHITE, spacing=0):
            l = QLabel(text)
            l.setStyleSheet(
                f"font-size:{size}px;font-weight:{weight};color:{color};"
                f"background:transparent;border:none;"
                + (f"letter-spacing:{spacing}px;" if spacing else "")
            )
            return l

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 16)
        root.setSpacing(0)

        # PNR label
        root.addWidget(_wlbl("MÃ ĐẶT CHỖ", 9, 600, C_GRAY, 2.0))
        root.addSpacing(4)
        root.addWidget(_wlbl(pnr, 28, 900, C_WHITE))
        root.addSpacing(16)

        # Barcode
        barcode = BarcodeWidget(pnr, bar_h=52,
                                bg=QColor(C_DARK))
        barcode.setStyleSheet("background:transparent;")
        root.addWidget(barcode)
        root.addSpacing(14)

        # Separator
        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:rgba(255,255,255,0.15);border:none;max-height:1px;")
        root.addWidget(sep)
        root.addSpacing(12)

        # Seats
        root.addWidget(_wlbl("GHẾ NGỒI", 9, 600, C_GRAY, 1.5))
        root.addSpacing(4)
        seat_row = QHBoxLayout(); seat_row.setSpacing(8)
        for s in ctx.get("seat_labels", ["4B","5B"]):
            pill = QLabel(s)
            pill.setAlignment(Qt.AlignCenter)
            pill.setFixedSize(38, 30)
            pill.setStyleSheet(f"font-size:12px;font-weight:800;"
                               f"color:{C_DARK};background:{C_WHITE};"
                               f"border-radius:8px;border:none;")
            seat_row.addWidget(pill)
        seat_row.addStretch()
        root.addLayout(seat_row)
        root.addSpacing(12)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background:rgba(255,255,255,0.15);border:none;max-height:1px;")
        root.addWidget(sep2)
        root.addSpacing(10)

        # Price
        root.addWidget(_wlbl("GIÁ ĐÃ THANH TOÁN", 9, 600, C_GRAY, 1.5))
        root.addSpacing(3)
        root.addWidget(_wlbl(f"${total}", 22, 900, "#FF7070"))
        root.addSpacing(10)

        # Ticket ID
        root.addWidget(_wlbl("ID VÉ:", 9, 500, C_GRAY))
        root.addWidget(_wlbl(ticket_id, 9, 600, "rgba(255,255,255,0.6)"))
        root.addStretch()


# ═════════════════════════════════════════════════════════════════════════════
# 6. SECURITY STRIP (bottom bar)
# ═════════════════════════════════════════════════════════════════════════════
class SecurityStrip(QWidget):
    HEIGHT = 46

    def __init__(self, ctx: dict, parent=None):
        super().__init__(parent)
        self.setFixedHeight(self.HEIGHT)
        self.setStyleSheet(f"background:{C_LGRAY};border-bottom-left-radius:20px;"
                           f"border-bottom-right-radius:20px;")

        pnr       = ctx.get("pnr", "JJXL92")
        hash_val  = hashlib.sha256(pnr.encode()).hexdigest()[:20].upper()

        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 0, 22, 0)
        lay.setSpacing(12)

        # Hash
        lay.addWidget(lbl("🔒", 14, 400, C_BLUE))
        lay.addWidget(lbl(f"SHA-256:  {hash_val}…", 9, 600, C_MID, 0.5))
        lay.addWidget(lbl("•", 10, 400, C_GRAY))
        lay.addWidget(lbl("PCI-DSS LEVEL 1", 9, 700, C_BLUE, 1.0))
        lay.addStretch()
        lay.addWidget(lbl("✅  ĐÃ XÁC MINH BẢO MẬT", 10, 700, C_GREEN, 0.5))


# ═════════════════════════════════════════════════════════════════════════════
# 7. TICKET WIDGET (boarding pass hoàn chỉnh)
# ═════════════════════════════════════════════════════════════════════════════
class TicketWidget(QWidget):
    """Widget vé máy bay — có thể grab() để lưu/in."""

    def __init__(self, ctx: dict, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self.setStyleSheet(f"""
            TicketWidget {{
                background: {C_WHITE};
                border-radius: 20px;
                border: 1px solid {C_BORDER};
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(36); shadow.setXOffset(0); shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 45))
        self.setGraphicsEffect(shadow)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        root.addWidget(TicketHeader(ctx))

        # Body row: main | perforation | stub
        body_w = QWidget(); body_w.setStyleSheet("background:transparent;")
        body_l = QHBoxLayout(body_w)
        body_l.setContentsMargins(0, 0, 0, 0)
        body_l.setSpacing(0)

        main = TicketMain(ctx)
        sep  = PerforatedSep(C_BG)   # match page bg for cutout effect
        stub = TicketStub(ctx)

        body_l.addWidget(main, 1)
        body_l.addWidget(sep)
        body_l.addWidget(stub)
        root.addWidget(body_w, 1)

        # Security strip
        root.addWidget(SecurityStrip(ctx))


# ═════════════════════════════════════════════════════════════════════════════
# 8. ACTION BUTTONS
# ═════════════════════════════════════════════════════════════════════════════
class ActionBar(QWidget):
    download_clicked = Signal()
    email_clicked    = Signal()
    home_clicked     = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(self); lay.setSpacing(12); lay.setContentsMargins(0,0,0,0)

        # Download / print
        btn_dl = red_btn("  📥  TẢI VỀ / IN VÉ", 48)
        btn_dl.setFixedWidth(220)
        btn_dl.clicked.connect(self.download_clicked)
        lay.addWidget(btn_dl)

        # Email
        btn_em = QPushButton("  📧  GỬI EMAIL")
        btn_em.setFixedHeight(48)
        btn_em.setFixedWidth(160)
        btn_em.setCursor(Qt.PointingHandCursor)
        btn_em.clicked.connect(self.email_clicked)
        btn_em.setStyleSheet(f"""
            QPushButton{{
                background:{C_WHITE};border:1.5px solid {C_BORDER};
                border-radius:24px;font-size:13px;font-weight:700;
                color:{C_MID};
            }}
            QPushButton:hover{{border-color:{C_GRAY};color:{C_TEXT};}}
        """)
        lay.addWidget(btn_em)

        lay.addStretch()

        # Home
        btn_home = QPushButton("↩  Về trang chủ")
        btn_home.setCursor(Qt.PointingHandCursor)
        btn_home.clicked.connect(self.home_clicked)
        btn_home.setStyleSheet(f"""
            QPushButton{{
                background:transparent;border:none;
                font-size:13px;font-weight:600;color:{C_GRAY};
            }}
            QPushButton:hover{{color:{C_RED};}}
        """)
        lay.addWidget(btn_home)


# ═════════════════════════════════════════════════════════════════════════════
# 9. SUCCESS BANNER
# ═════════════════════════════════════════════════════════════════════════════
class SuccessBanner(QWidget):
    def __init__(self, ctx: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:#ECFDF5;border:1.5px solid #A7F3D0;"
                           f"border-radius:16px;")
        lay = QHBoxLayout(self); lay.setContentsMargins(22, 16, 22, 16); lay.setSpacing(16)

        # Checkmark circle
        chk = QLabel("✅")
        chk.setFixedSize(48, 48)
        chk.setAlignment(Qt.AlignCenter)
        chk.setStyleSheet(f"font-size:28px;background:{C_GREEN};border-radius:24px;"
                          f"color:white;")
        lay.addWidget(chk)

        # Info
        info = QVBoxLayout(); info.setSpacing(4)
        info.addWidget(lbl("Đặt vé thành công! Cảm ơn bạn đã sử dụng JetJet Air.",
                           15, 800, "#065F46"))
        pax   = ctx.get("passenger", {})
        email = pax.get("email", "—")
        info.addWidget(lbl(f"Email xác nhận đã được gửi đến: {email}",
                           12, 500, "#047857"))
        lay.addLayout(info)
        lay.addStretch()

        # PNR badge
        pnr_col = QVBoxLayout(); pnr_col.setSpacing(3); pnr_col.setAlignment(Qt.AlignRight)
        pnr_col.addWidget(lbl("MÃ PNR", 9, 600, "#047857", 1.0))
        pnr_val = lbl(ctx.get("pnr","—"), 20, 900, C_TEXT)
        pnr_val.setAlignment(Qt.AlignRight)
        pnr_col.addWidget(pnr_val)
        lay.addLayout(pnr_col)


# ═════════════════════════════════════════════════════════════════════════════
# 10. TICKET PAGE
# ═════════════════════════════════════════════════════════════════════════════
class TicketPage(QWidget):
    go_home = Signal()

    def __init__(self, ctx: dict | None = None, parent=None):
        super().__init__(parent)
        self.ctx = ctx or DEMO_CTX
        if "ticket_id" not in self.ctx:
            self.ctx["ticket_id"] = _TICKET_ID

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
        root.setContentsMargins(28, 24, 28, 32)
        root.setSpacing(20)

        # ── Page header ───────────────────────────────────────────────────────
        hdr_row = QHBoxLayout(); hdr_row.setSpacing(0)
        title_col = QVBoxLayout(); title_col.setSpacing(4)
        title_col.addWidget(lbl("Vé Máy Bay Điện Tử", 24, 800, C_TEXT))
        title_col.addWidget(lbl("Vé của bạn đã sẵn sàng. Hãy lưu lại để check-in.",
                                13, 400, C_GRAY))
        hdr_row.addLayout(title_col)
        hdr_row.addStretch()
        root.addLayout(hdr_row)

        # ── Success banner ────────────────────────────────────────────────────
        root.addWidget(SuccessBanner(self.ctx))

        # ── Ticket ───────────────────────────────────────────────────────────
        self._ticket = TicketWidget(self.ctx)
        root.addWidget(self._ticket)

        # ── Info strip below ticket ───────────────────────────────────────────
        info_w = QWidget()
        info_w.setStyleSheet(f"background:{C_WHITE};border:1px solid {C_BORDER};"
                             f"border-radius:14px;")
        iw_l = QHBoxLayout(info_w); iw_l.setContentsMargins(20,14,20,14); iw_l.setSpacing(32)
        for icon, key, val in [
            ("🚪", "CỬA KHỞI HÀNH",     self.ctx.get("gate","B22")),
            ("🏢", "NHÀ GA",            self.ctx.get("terminal","Nhà ga T1")),
            ("🗺", "KHU VỰC GHẾ",       self.ctx.get("zone","Khu B")),
            ("🔐", "XÁC MINH BẢO MẬT",  "PCI-DSS Level 1"),
            ("💳", "GIÁ ĐÃ THANH TOÁN",f"${self.ctx.get('total',227)}"),
        ]:
            col = QVBoxLayout(); col.setSpacing(4)
            hd = QHBoxLayout(); hd.setSpacing(5)
            hd.addWidget(lbl(icon, 13, 400, C_GRAY))
            hd.addWidget(lbl(key, 9, 600, C_GRAY, 0.5))
            col.addLayout(hd)
            col.addWidget(lbl(val, 14, 700, C_TEXT))
            iw_l.addLayout(col)
        root.addWidget(info_w)

        # ── Action buttons ────────────────────────────────────────────────────
        self._actions = ActionBar()
        self._actions.download_clicked.connect(self._save_ticket)
        self._actions.email_clicked.connect(self._send_email)
        self._actions.home_clicked.connect(self.go_home)
        root.addWidget(self._actions)

        root.addStretch()

    # ── Save ticket as PNG ─────────────────────────────────────────────────────
    def _save_ticket(self):
        pnr  = self.ctx.get("pnr", "ticket")
        path, _ = QFileDialog.getSaveFileName(
            self, "Lưu vé máy bay",
            f"JetJet_Ticket_{pnr}.png",
            "Hình ảnh PNG (*.png);;PDF (*.pdf)"
        )
        if not path:
            return

        # Hide shadow before capture for clean print
        self._ticket.setGraphicsEffect(None)
        pixmap = self._ticket.grab()

        # Restore shadow
        sh = QGraphicsDropShadowEffect(self._ticket)
        sh.setBlurRadius(36); sh.setXOffset(0); sh.setYOffset(10)
        sh.setColor(QColor(0,0,0,45))
        self._ticket.setGraphicsEffect(sh)

        if path.lower().endswith(".pdf"):
            self._save_as_pdf(pixmap, path)
        else:
            if pixmap.save(path, "PNG"):
                QMessageBox.information(
                    self, "Đã lưu vé ✅",
                    f"Vé máy bay đã được lưu tại:\n{path}\n\n"
                    f"Mã PNR: {self.ctx.get('pnr','—')}"
                )
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể lưu file. Vui lòng thử lại.")

    def _save_as_pdf(self, pixmap: QPixmap, path: str):
        try:
            from PySide6.QtPrintSupport import QPrinter
            from PySide6.QtGui import QPainter as _QPainter
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(path)
            pp = _QPainter(printer)
            page_rect = printer.pageRect(QPrinter.DevicePixel)
            scaled = pixmap.scaled(
                int(page_rect.width()), int(page_rect.height()),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            pp.drawPixmap(0, 0, scaled)
            pp.end()
            QMessageBox.information(self, "Đã xuất PDF ✅", f"Đã lưu PDF tại:\n{path}")
        except ImportError:
            # Fallback: save as PNG
            png_path = path.replace(".pdf", ".png")
            pixmap.save(png_path, "PNG")
            QMessageBox.information(self, "Đã lưu ✅",
                                    f"Đã lưu ảnh PNG (không có module PDF):\n{png_path}")

    def _send_email(self):
        email = self.ctx.get("passenger",{}).get("email","—")
        QMessageBox.information(
            self, "📧 Gửi Email",
            f"Email xác nhận đã được gửi đến:\n{email}\n\n"
            f"(Chức năng thực tế cần SMTP server)"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Standalone test
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    win = QMainWindow()
    win.setWindowTitle("JetJet Air — Vé Máy Bay")
    win.resize(1380, 900)
    container = QWidget()
    lay = QVBoxLayout(container); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
    lay.addWidget(NavBar(0))
    lay.addWidget(TicketPage())
    win.setCentralWidget(container)
    win.show()
    sys.exit(app.exec())