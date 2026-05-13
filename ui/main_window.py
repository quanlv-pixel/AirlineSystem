"""
ui/main_window.py  (UPDATED — Dashboard giống ảnh mẫu)
---------------------------------------------------------
Đặt file này vào: ui/main_window.py
"""

import random
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import (
    QColor, QFont, QLinearGradient, QPainter, QBrush, QPen,
    QIcon, QPixmap, QPainterPath
)
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget,
    QSizePolicy, QLineEdit, QSpacerItem, QScrollArea,
    QApplication
)

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.patches as mpatches
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from models.account import Account
from services.flight_service import get_total_flights
from services.passenger_service import get_total_passengers
from services.booking_service import get_active_bookings_count, get_total_revenue


# ─────────────────────────────────────────────────────────────────────────────
# Màu sắc
# ─────────────────────────────────────────────────────────────────────────────
RED        = "#E53935"
RED_LIGHT  = "#FFEBEE"
WHITE      = "#FFFFFF"
BG_MAIN    = "#F8F9FB"
SIDEBAR_BG = "#FFFFFF"
GRAY_TEXT  = "#9E9E9E"
GRAY_BG    = "#F5F5F5"
TEXT_DARK  = "#1A1A2E"
TEXT_MED   = "#424242"
BORDER     = "#EEEEEE"


# ─────────────────────────────────────────────────────────────────────────────
# Helper widgets
# ─────────────────────────────────────────────────────────────────────────────

def _h_line():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {BORDER}; margin: 0;")
    return line


class AvatarCircle(QWidget):
    """Hình tròn chứa chữ cái đầu của tên."""
    def __init__(self, initials: str, color: str = RED, size: int = 36, parent=None):
        super().__init__(parent)
        self.initials = initials[:2].upper()
        self.color = color
        self.setFixedSize(size, size)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(1, 1, self.width()-2, self.height()-2)
        p.fillPath(path, QBrush(QColor(self.color)))
        p.setPen(QPen(QColor(WHITE)))
        f = QFont(); f.setPointSize(11); f.setWeight(QFont.Bold)
        p.setFont(f)
        p.drawText(self.rect(), Qt.AlignCenter, self.initials)


class StatCard(QWidget):
    """Card thống kê nhỏ."""
    def __init__(self, title, value, change, icon_char, icon_color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(110)
        self.setStyleSheet(f"""
            StatCard {{
                background: {WHITE};
                border-radius: 14px;
                border: 1px solid {BORDER};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # Icon circle
        icon_widget = QWidget()
        icon_widget.setFixedSize(48, 48)
        icon_widget.setStyleSheet(f"""
            QWidget {{
                background: {icon_color}22;
                border-radius: 12px;
            }}
        """)
        icon_layout = QVBoxLayout(icon_widget)
        icon_layout.setContentsMargins(0,0,0,0)
        icon_lbl = QLabel(icon_char)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"font-size: 22px; color: {icon_color};")
        icon_layout.addWidget(icon_lbl)

        # Text area
        text_col = QVBoxLayout()
        text_col.setSpacing(4)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"font-size: 10px; color: {GRAY_TEXT}; font-weight: 600; letter-spacing: 1px;")

        val_lbl = QLabel(str(value))
        val_lbl.setStyleSheet(f"font-size: 26px; font-weight: 800; color: {TEXT_DARK};")

        # Change badge
        is_up = not str(change).startswith("-")
        chg_color = "#43A047" if is_up else "#E53935"
        chg_lbl = QLabel(f"{'▲' if is_up else '▼'} {change}")
        chg_lbl.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {chg_color};")

        text_col.addWidget(title_lbl)
        text_col.addWidget(val_lbl)
        text_col.addWidget(chg_lbl)

        layout.addWidget(icon_widget)
        layout.addLayout(text_col)
        layout.addStretch()


class RouteBar(QWidget):
    """Thanh route với progress bar."""
    def __init__(self, route: str, label: str, percent: int, bar_color: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(4)

        top = QHBoxLayout()
        route_lbl = QLabel(route)
        route_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {TEXT_DARK};")
        pct_lbl = QLabel(f"{percent}%")
        pct_lbl.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {RED};")
        top.addWidget(route_lbl)
        top.addStretch()
        top.addWidget(pct_lbl)

        lbl_w = QLabel(label.upper())
        lbl_w.setStyleSheet(f"font-size: 9px; color: {GRAY_TEXT}; letter-spacing: 1px;")

        # Progress bar
        bar_frame = QFrame()
        bar_frame.setFixedHeight(6)
        bar_frame.setStyleSheet(f"background: {GRAY_BG}; border-radius: 3px;")
        bar_frame.setMinimumWidth(100)

        self._bar_color = bar_color
        self._percent = percent
        self._bar_frame = bar_frame

        layout.addLayout(top)
        layout.addWidget(lbl_w)
        layout.addWidget(bar_frame)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._draw_fill()

    def _draw_fill(self):
        w = self._bar_frame.width()
        fill_w = int(w * self._percent / 100)
        # Create inner fill widget
        for c in self._bar_frame.children():
            if isinstance(c, QWidget):
                c.deleteLater()
        fill = QWidget(self._bar_frame)
        fill.setGeometry(0, 0, fill_w, 6)
        fill.setStyleSheet(f"background: {self._bar_color}; border-radius: 3px;")
        fill.show()


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
class Sidebar(QWidget):
    def __init__(self, on_navigate, on_logout, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet(f"""
            Sidebar {{
                background: {SIDEBAR_BG};
                border-right: 1px solid {BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Logo area ────────────────────────────────────────────────────────
        logo_frame = QWidget()
        logo_frame.setFixedHeight(70)
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 0, 20, 0)
        logo_layout.setSpacing(10)

        logo_circle = AvatarCircle("✈", RED, 36)
        logo_circle.setStyleSheet("")  # Sẽ vẽ bằng paintEvent

        brand_col = QVBoxLayout()
        brand_col.setSpacing(0)
        name_lbl = QLabel("JETJET")
        name_lbl.setStyleSheet(f"font-size: 15px; font-weight: 900; color: {RED}; letter-spacing: 1px;")
        sub_lbl = QLabel("MANAGEMENT")
        sub_lbl.setStyleSheet(f"font-size: 8px; color: {GRAY_TEXT}; letter-spacing: 2px; font-weight: 600;")
        brand_col.addWidget(name_lbl)
        brand_col.addWidget(sub_lbl)

        logo_layout.addWidget(logo_circle)
        logo_layout.addLayout(brand_col)
        logo_layout.addStretch()
        layout.addWidget(logo_frame)
        layout.addWidget(_h_line())
        layout.addSpacing(12)

        # ── Nav items ────────────────────────────────────────────────────────
        nav_items = [
            ("📊", "Dashboard",   0),
            ("✈",  "Flights",     1),
            ("👥", "Passengers",  2),
            ("🎫", "Bookings",    3),
            ("📈", "Statistics",  4),
            ("⚙",  "Settings",   5),
        ]

        self._nav_btns = {}
        for icon, label, idx in nav_items:
            btn = self._make_nav_btn(icon, label, idx, on_navigate)
            self._nav_btns[idx] = btn
            layout.addWidget(btn)

        layout.addStretch()
        layout.addWidget(_h_line())

        # Logout
        logout_btn = QPushButton("  ⬅  Logout System")
        logout_btn.setFixedHeight(48)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(on_logout)
        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                text-align: left;
                padding-left: 22px;
                font-size: 13px;
                color: {GRAY_TEXT};
                font-weight: 500;
            }}
            QPushButton:hover {{
                color: {RED};
                background: {RED_LIGHT};
            }}
        """)
        layout.addWidget(logout_btn)

        self.set_active(0)

    def _make_nav_btn(self, icon, label, idx, callback):
        btn = QPushButton(f"  {icon}   {label}")
        btn.setFixedHeight(46)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda checked=False, i=idx: callback(i))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 10px;
                text-align: left;
                padding-left: 18px;
                font-size: 13px;
                color: {TEXT_MED};
                font-weight: 500;
                margin: 1px 12px;
            }}
            QPushButton:hover {{
                background: {GRAY_BG};
                color: {TEXT_DARK};
            }}
        """)
        return btn

    def set_active(self, idx: int):
        for i, btn in self._nav_btns.items():
            if i == idx:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {RED_LIGHT};
                        border: none;
                        border-radius: 10px;
                        text-align: left;
                        padding-left: 18px;
                        font-size: 13px;
                        color: {RED};
                        font-weight: 700;
                        margin: 1px 12px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        border: none;
                        border-radius: 10px;
                        text-align: left;
                        padding-left: 18px;
                        font-size: 13px;
                        color: {TEXT_MED};
                        font-weight: 500;
                        margin: 1px 12px;
                    }}
                    QPushButton:hover {{
                        background: {GRAY_BG};
                        color: {TEXT_DARK};
                    }}
                """)


# ─────────────────────────────────────────────────────────────────────────────
# Top Bar
# ─────────────────────────────────────────────────────────────────────────────
class TopBar(QWidget):
    def __init__(self, account: Account, parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)
        self.setStyleSheet(f"""
            TopBar {{
                background: {WHITE};
                border-bottom: 1px solid {BORDER};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(16)

        # Tiêu đề + breadcrumb
        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {TEXT_DARK};")
        breadcrumb = QLabel("Main Console  /  dashboard")
        breadcrumb.setStyleSheet(f"font-size: 11px; color: {GRAY_TEXT};")
        breadcrumb.setContentsMargins(0, 0, 0, 0)
        # Highlight "dashboard"
        title_col.addWidget(self.page_title)
        title_col.addWidget(breadcrumb)

        # Search
        search = QLineEdit()
        search.setPlaceholderText("Search flights, passengers or bookings...")
        search.setFixedWidth(300)
        search.setFixedHeight(36)
        search.setStyleSheet(f"""
            QLineEdit {{
                background: {GRAY_BG};
                border: 1px solid {BORDER};
                border-radius: 18px;
                padding: 0 16px;
                font-size: 13px;
                color: {TEXT_MED};
            }}
            QLineEdit:focus {{
                border-color: {RED};
            }}
        """)

        # Right area
        right = QHBoxLayout()
        right.setSpacing(16)

        loc_lbl = QLabel("🌐  HQ Seoul – JJ822")
        loc_lbl.setStyleSheet(f"font-size: 12px; color: {TEXT_MED}; font-weight: 500;")

        status_dot = QLabel("● System Online")
        status_dot.setStyleSheet("font-size: 12px; color: #43A047; font-weight: 600;")

        bell = QPushButton("🔔")
        bell.setFixedSize(36, 36)
        bell.setStyleSheet(f"background: {GRAY_BG}; border: none; border-radius: 18px; font-size: 16px;")

        # Profile
        initials = "".join([w[0] for w in account.display_name.split()][:2]) if account.display_name else "AJ"
        avatar = AvatarCircle(initials, RED, 36)

        prof_col = QVBoxLayout()
        prof_col.setSpacing(0)
        name_l = QLabel(account.display_name or account.username)
        name_l.setStyleSheet(f"font-size: 13px; font-weight: 700; color: {TEXT_DARK};")
        role_l = QLabel(account.role.upper())
        role_l.setStyleSheet(f"font-size: 9px; color: {GRAY_TEXT}; letter-spacing: 1px;")
        prof_col.addWidget(name_l)
        prof_col.addWidget(role_l)

        right.addWidget(loc_lbl)
        right.addWidget(status_dot)
        right.addWidget(bell)
        right.addWidget(avatar)
        right.addLayout(prof_col)

        layout.addLayout(title_col)
        layout.addStretch()
        layout.addWidget(search)
        layout.addLayout(right)


# ─────────────────────────────────────────────────────────────────────────────
# Revenue Chart (matplotlib) hoặc fallback
# ─────────────────────────────────────────────────────────────────────────────
class RevenueChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(260)
        self.setStyleSheet(f"background: {WHITE}; border-radius: 14px; border: 1px solid {BORDER};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 12)
        layout.setSpacing(4)

        header = QHBoxLayout()
        title = QLabel("Revenue Performance")
        title.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {TEXT_DARK};")
        sub = QLabel("GLOBAL COLLECTION SUMMARY")
        sub.setStyleSheet(f"font-size: 9px; color: {GRAY_TEXT}; letter-spacing: 1.5px;")
        date_lbl = QLabel("📅  FY 2026")
        date_lbl.setStyleSheet(f"font-size: 12px; color: {GRAY_TEXT};")

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_col.addWidget(title)
        title_col.addWidget(sub)
        header.addLayout(title_col)
        header.addStretch()
        header.addWidget(date_lbl)
        layout.addLayout(header)

        if HAS_MPL:
            fig = Figure(figsize=(5, 2.5), dpi=90, facecolor="white")
            ax = fig.add_subplot(111)
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            values = [4000, 2800, 2600, 2750, 1950, 2100, 3500]
            x = range(len(days))
            ax.plot(x, values, color=RED, linewidth=2.5, solid_capstyle="round")
            ax.fill_between(x, values, alpha=0.08, color=RED)
            ax.set_xticks(x)
            ax.set_xticklabels(days, fontsize=9, color="#9E9E9E")
            ax.set_ylim(0, 4500)
            ax.yaxis.set_tick_params(labelsize=9, labelcolor="#9E9E9E")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#EEEEEE")
            ax.spines["bottom"].set_color("#EEEEEE")
            ax.grid(axis="y", color="#F0F0F0", linewidth=1)
            fig.tight_layout(pad=0.5)
            canvas = FigureCanvas(fig)
            canvas.setStyleSheet("background: white;")
            layout.addWidget(canvas)
        else:
            placeholder = QLabel("📈  [Cài matplotlib để xem biểu đồ doanh thu]\npip install matplotlib")
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet(f"color: {GRAY_TEXT}; font-size: 13px; padding: 40px;")
            layout.addWidget(placeholder)


# ─────────────────────────────────────────────────────────────────────────────
# Routes Panel
# ─────────────────────────────────────────────────────────────────────────────
class RoutesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(300)
        self.setStyleSheet(f"background: {WHITE}; border-radius: 14px; border: 1px solid {BORDER};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(0)

        header = QHBoxLayout()
        title = QLabel("Routes")
        title.setStyleSheet(f"font-size: 16px; font-weight: 800; color: {TEXT_DARK};")
        icon_lbl = QLabel("↗")
        icon_lbl.setStyleSheet(f"font-size: 18px; color: {RED};")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(icon_lbl)
        layout.addLayout(header)
        layout.addSpacing(16)

        routes = [
            ("SGN → HAN", "HIGH TRAFFIC",    85, RED),
            ("SGN → DAD", "SEASONAL PEAKS",  65, "#1E88E5"),
            ("HAN → PQC", "LEISURE DEMAND",  45, "#8E24AA"),
            ("DAD → SGN", "EVENING SLOT",    30, "#7B1FA2"),
        ]
        for route, lbl, pct, color in routes:
            bar = RouteBar(route, lbl, pct, color)
            layout.addWidget(bar)
            layout.addWidget(_h_line())

        layout.addStretch()

        opt_btn = QPushButton("OPTIMIZATION REPORT")
        opt_btn.setFixedHeight(38)
        opt_btn.setCursor(Qt.PointingHandCursor)
        opt_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {RED};
                border-radius: 8px;
                color: {RED};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: {RED_LIGHT};
            }}
        """)
        layout.addWidget(opt_btn)


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Page
# ─────────────────────────────────────────────────────────────────────────────
class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG_MAIN};")

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background: {BG_MAIN};")
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        # ── Stat cards ───────────────────────────────────────────────────────
        try:
            total_flights    = get_total_flights()
            total_passengers = get_total_passengers()
            active_bookings  = get_active_bookings_count()
            total_revenue    = get_total_revenue()
        except Exception:
            total_flights, total_passengers, active_bookings, total_revenue = 42, 1280, 854, 124500

        rev_str = f"${total_revenue/1000:.1f}k" if total_revenue >= 1000 else f"${total_revenue:.0f}"

        cards_data = [
            ("Total Flights",     total_flights,    "+12.5%", "✈",  "#1E88E5"),
            ("Total Passengers",  total_passengers, "+18.2%", "👥", "#8E24AA"),
            ("Active Bookings",   active_bookings,  "-2.4%",  "📈", "#E53935"),
            ("Total Revenue",     rev_str,          "+24.5%", "💲", "#43A047"),
        ]

        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)
        for title, val, change, icon, color in cards_data:
            card = StatCard(title, val, change, icon, color)
            cards_row.addWidget(card)
        layout.addLayout(cards_row)

        # ── Chart + Routes ───────────────────────────────────────────────────
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)

        chart = RevenueChart()
        routes = RoutesPanel()

        bottom_row.addWidget(chart, 1)
        bottom_row.addWidget(routes)
        layout.addLayout(bottom_row)
        layout.addStretch()


# ─────────────────────────────────────────────────────────────────────────────
# Placeholder page
# ─────────────────────────────────────────────────────────────────────────────
class PlaceholderPage(QWidget):
    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG_MAIN};")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 52px;")
        text = QLabel(f"{title}\n(Đang phát triển…)")
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet(f"font-size: 18px; color: {GRAY_TEXT}; font-weight: 600;")
        layout.addWidget(icon_lbl)
        layout.addSpacing(12)
        layout.addWidget(text)


# ─────────────────────────────────────────────────────────────────────────────
# Main Window
# ─────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self, account: Account):
        super().__init__()
        self.account = account
        self.setWindowTitle("JetJet Air — Management Platform")
        self.resize(1400, 820)

        central = QWidget()
        central.setStyleSheet(f"background: {BG_MAIN};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top Bar ──────────────────────────────────────────────────────────
        self.topbar = TopBar(account)
        root.addWidget(self.topbar)

        # ── Body: Sidebar + Pages ────────────────────────────────────────────
        body = QHBoxLayout()
        body.setSpacing(0)
        body.setContentsMargins(0, 0, 0, 0)

        self.sidebar = Sidebar(self._navigate, self._logout)
        body.addWidget(self.sidebar)

        # Pages
        self.pages = QStackedWidget()
        self.pages.setStyleSheet(f"background: {BG_MAIN};")

        self.pages.addWidget(DashboardPage())                          # 0
        self.pages.addWidget(PlaceholderPage("✈",  "Flights"))        # 1
        self.pages.addWidget(PlaceholderPage("👥", "Passengers"))      # 2
        self.pages.addWidget(PlaceholderPage("🎫", "Bookings"))        # 3
        self.pages.addWidget(PlaceholderPage("📈", "Statistics"))      # 4
        self.pages.addWidget(PlaceholderPage("⚙",  "Settings"))       # 5

        body.addWidget(self.pages)
        root.addLayout(body)

    def _navigate(self, index: int):
        self.pages.setCurrentIndex(index)
        self.sidebar.set_active(index)

        labels = ["Dashboard", "Flights", "Passengers", "Bookings", "Statistics", "Settings"]
        if index < len(labels):
            self.topbar.page_title.setText(labels[index])

    def _logout(self):
        from ui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()