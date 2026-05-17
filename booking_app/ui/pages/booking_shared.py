"""
booking_shared.py  [FIXED]
--------------------------
Fix: NavBar tab buttons giờ gọi self.tab_changed.emit(i) khi click.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QBrush, QPen, QPainterPath, QLinearGradient
from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QFrame,
                                QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect)

# ── Colors ──────────────────────────────────────────────────────────────────
C_RED    = "#E53935"
C_RED2   = "#C62828"
C_REDL   = "#FF5252"
C_DARK   = "#1A1A2E"
C_WHITE  = "#FFFFFF"
C_BG     = "#FAFBFF"
C_BORDER = "#E8EAF0"
C_TEXT   = "#1A1A2E"
C_MID    = "#4A4A6A"
C_GRAY   = "#9B9BB4"
C_LGRAY  = "#F2F3F7"
C_GREEN  = "#22C55E"
C_BLUE   = "#1E88E5"
C_ORANGE = "#F59E0B"


# ── Label helper ─────────────────────────────────────────────────────────────
def lbl(text, size=13, weight=400, color=C_TEXT, spacing=0.0):
    w = {400:"normal",500:"500",600:"600",700:"bold",800:"800",900:"900"}.get(weight,"normal")
    sp = f"letter-spacing:{spacing}px;" if spacing else ""
    l = QLabel(text)
    l.setStyleSheet(f"font-size:{size}px;font-weight:{w};color:{color};"
                    f"background:transparent;border:none;{sp}")
    return l


# ── Separator ────────────────────────────────────────────────────────────────
def h_sep(alpha=200):
    f = QFrame(); f.setFrameShape(QFrame.HLine); f.setFixedHeight(1)
    f.setStyleSheet(f"background:rgba(232,234,240,{alpha});border:none;")
    return f


# ── Card style ───────────────────────────────────────────────────────────────
def card_style(radius=16):
    return (f"background:{C_WHITE};border:1px solid {C_BORDER};"
            f"border-radius:{radius}px;")


# ── Red button ───────────────────────────────────────────────────────────────
def red_btn(text, height=52):
    btn = QPushButton(text)
    btn.setFixedHeight(height)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton {{
            background:qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 {C_RED},stop:1 {C_REDL});
            border:none;border-radius:{height//2}px;
            font-size:14px;font-weight:800;color:white;
            letter-spacing:1.5px;
        }}
        QPushButton:hover{{background:{C_RED2};}}
        QPushButton:pressed{{background:#B71C1C;}}
    """)
    glow = QGraphicsDropShadowEffect(btn)
    glow.setBlurRadius(24); glow.setXOffset(0); glow.setYOffset(8)
    glow.setColor(QColor(229,57,53,80))
    btn.setGraphicsEffect(glow)
    return btn


# ── Back button ──────────────────────────────────────────────────────────────
def back_btn():
    btn = QPushButton("<")
    btn.setFixedSize(38,38)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(f"""
        QPushButton{{background:{C_WHITE};border:1.5px solid {C_BORDER};
            border-radius:19px;font-size:15px;font-weight:700;color:{C_MID};}}
        QPushButton:hover{{background:{C_LGRAY};}}
    """)
    return btn


# ── Page header ──────────────────────────────────────────────────────────────
def page_header(title, subtitle, on_back=None):
    row = QHBoxLayout()
    row.setSpacing(14); row.setContentsMargins(0,0,0,0)
    b = back_btn()
    if on_back:
        b.clicked.connect(on_back)
    col = QVBoxLayout(); col.setSpacing(3)
    col.addWidget(lbl(title, 24, 800, C_TEXT))
    col.addWidget(lbl(subtitle, 13, 400, C_GRAY))
    row.addWidget(b)
    row.addLayout(col)
    row.addStretch()
    return row


# ── NavLogo ──────────────────────────────────────────────────────────────────
class NavLogo(QWidget):
    def __init__(self, size=36, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height(); r = w*0.28
        g = QLinearGradient(0,0,w,h)
        g.setColorAt(0,QColor("#FF5252")); g.setColorAt(1,QColor("#C62828"))
        pp = QPainterPath(); pp.addRoundedRect(0,0,w,h,r,r)
        p.fillPath(pp,QBrush(g))
        p.setPen(QPen(QColor(C_WHITE),1))
        f=QFont(); f.setPointSize(int(w*0.38)); f.setWeight(QFont.Bold)
        p.setFont(f); p.drawText(0,0,w,h,Qt.AlignCenter,"✈")


# ── NavBar ────────────────────────────────────────────────────────────────────
class NavBar(QWidget):
    """
    [FIXED] Tab buttons giờ gọi self.tab_changed.emit(i) khi click.
    Tham số đầu tiên là active_tab (int), KHÔNG phải account dict.
    """
    tab_changed = Signal(int)

    _TABS = ["CHUYẾN BAY", "LỊCH SỬ", "KHUYẾN MÃI", "THÔNG TIN"]

    def __init__(self, active_tab: int = 0, on_logout=None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet(
            f"NavBar{{background:{C_WHITE};border-bottom:1px solid {C_BORDER};}}"
        )
        self._active = active_tab
        self._tab_btns: list[QPushButton] = []

        lay = QHBoxLayout(self)
        lay.setContentsMargins(24,0,24,0); lay.setSpacing(0)

        lay.addWidget(NavLogo(36))
        lay.addSpacing(10)

        brand = QLabel()
        brand.setTextFormat(Qt.RichText)
        brand.setText(
            f"<span style='font-size:16px;font-weight:900;color:{C_DARK};'>JETJET</span>"
            f"<span style='font-size:16px;font-weight:700;color:{C_RED};'> AIR</span>"
        )
        brand.setStyleSheet("background:transparent;border:none;")
        lay.addWidget(brand)
        lay.addSpacing(36)

        # ── FIX: Tab buttons có clicked.connect → emit tab_changed ────────────
        for i, t in enumerate(self._TABS):
            btn = QPushButton(t)
            btn.setFixedHeight(64)
            btn.setCursor(Qt.PointingHandCursor)
            # Kết nối signal click → emit tab_changed(i)
            btn.clicked.connect(lambda checked=False, idx=i: self._on_tab_click(idx))
            self._tab_btns.append(btn)
            lay.addWidget(btn)
            if i < 3:
                lay.addSpacing(8)

        lay.addStretch()

        # Chuông
        bell = QPushButton("🔔")
        bell.setFixedSize(38,38)
        bell.setStyleSheet(
            f"QPushButton{{background:{C_LGRAY};border:none;border-radius:19px;font-size:16px;}}"
        )
        lay.addWidget(bell)
        lay.addSpacing(12)

        sep = QFrame(); sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet(f"background:{C_BORDER};border:none;")
        sep.setFixedWidth(1); sep.setFixedHeight(30)
        lay.addWidget(sep)
        lay.addSpacing(12)

        exit_btn = QPushButton("→  THOÁT PORTAL")
        exit_btn.setCursor(Qt.PointingHandCursor)
        exit_btn.setStyleSheet(
            f"QPushButton{{background:transparent;border:none;"
            f"font-size:13px;font-weight:600;color:{C_MID};}}"
            f"QPushButton:hover{{color:{C_RED};}}"
        )
        if on_logout:
            exit_btn.clicked.connect(on_logout)
        lay.addWidget(exit_btn)

        # Áp dụng style tab active ban đầu
        self._apply_tab_styles()

    def _on_tab_click(self, idx: int):
        """Đổi tab active và emit signal."""
        self._active = idx
        self._apply_tab_styles()
        self.tab_changed.emit(idx)

    def set_active_tab(self, idx: int):
        """Gọi từ bên ngoài để đồng bộ tab active mà không emit signal."""
        self._active = idx
        self._apply_tab_styles()

    def _apply_tab_styles(self):
        for i, btn in enumerate(self._tab_btns):
            active = (i == self._active)
            btn.setStyleSheet(f"""
                QPushButton{{
                    background:transparent; border:none;
                    border-bottom:3px solid {'#E53935' if active else 'transparent'};
                    font-size:13px; font-weight:{'800' if active else '500'};
                    color:{'#E53935' if active else C_TEXT}; padding:0 12px;
                }}
                QPushButton:hover{{color:#E53935;}}
            """)