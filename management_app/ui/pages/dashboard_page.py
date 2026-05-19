from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QScrollArea,
)

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import numpy as np
    HAS_MPL = True
except Exception:
    HAS_MPL = False

try:
    from scipy.interpolate import make_interp_spline
    HAS_SCIPY = True
except Exception:
    HAS_SCIPY = False

from shared.services.flight_service import get_total_flights
from shared.services.passenger_service import get_total_passengers
from shared.services.booking_service import (
    get_active_bookings_count,
    get_total_revenue,
)

# ── Màu sắc ──────────────────────────────────────────────────────────────────
RED       = "#E53935"
RED_LIGHT = "#FFEBEE"
WHITE     = "#FFFFFF"
BG_MAIN   = "#F8F9FB"
GRAY_TEXT = "#9E9E9E"
GRAY_BG   = "#F5F5F5"
TEXT_DARK = "#1A1A2E"
TEXT_MED  = "#424242"
BORDER    = "#EEEEEE"


def h_line():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color: {BORDER};")
    return line


# ─────────────────────────────────────────────────────────────────────────────
# Stat Card
# ─────────────────────────────────────────────────────────────────────────────
class StatCard(QWidget):
    def __init__(self, title, value, change, icon, color):
        super().__init__()
        self.setMinimumHeight(120)
        self.setStyleSheet(f"""
            StatCard {{
                background: {WHITE};
                border-radius: 16px;
                border: 1px solid {BORDER};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 18, 22, 18)
        root.setSpacing(10)

        # Hàng trên: icon + % change
        top_row = QHBoxLayout()
        top_row.setSpacing(0)

        icon_box = QLabel(icon)
        icon_box.setFixedSize(50, 50)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_box.setStyleSheet(f"""
            background: {color}22;
            border-radius: 14px;
            font-size: 22px;
            color: {color};
        """)

        top_row.addWidget(icon_box)
        top_row.addStretch()

        is_positive = not str(change).startswith("-")
        chg_color   = "#43A047" if is_positive else RED
        arrow       = "▲" if is_positive else "▼"
        chg_lbl     = QLabel(f"{arrow} {change}")
        chg_lbl.setStyleSheet(f"""
            color: {chg_color};
            font-size: 12px;
            font-weight: 700;
        """)
        chg_lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)
        top_row.addWidget(chg_lbl)

        root.addLayout(top_row)

        # Nhãn
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"""
            font-size: 10px;
            letter-spacing: 1px;
            color: {GRAY_TEXT};
            font-weight: 700;
        """)

        # Giá trị
        value_lbl = QLabel(str(value))
        value_lbl.setStyleSheet(f"""
            font-size: 30px;
            font-weight: 800;
            color: {TEXT_DARK};
        """)

        root.addWidget(title_lbl)
        root.addWidget(value_lbl)


# ─────────────────────────────────────────────────────────────────────────────
# Revenue Chart
# ─────────────────────────────────────────────────────────────────────────────
class RevenueChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"""
            RevenueChart {{
                background: {WHITE};
                border-radius: 16px;
                border: 1px solid {BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 18)

        # Header
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(3)

        title = QLabel("Hiệu suất Doanh thu")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 800;
            color: {TEXT_DARK};
        """)

        subtitle = QLabel("TỔNG HỢP THU NHẬP TOÀN CẦU")
        subtitle.setStyleSheet(f"""
            font-size: 9px;
            color: {GRAY_TEXT};
            letter-spacing: 2px;
            font-weight: 600;
        """)

        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        fy_label = QLabel("📅  NĂM TÀI CHÍNH 2026")
        fy_label.setStyleSheet(f"""
            font-size: 12px;
            color: {GRAY_TEXT};
            font-weight: 600;
        """)

        header.addLayout(title_col)
        header.addStretch()
        header.addWidget(fy_label)
        layout.addLayout(header)

        # Chart
        if HAS_MPL:
            fig = Figure(figsize=(5, 2.8), facecolor="white")
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            days_x = np.array([0, 1, 2, 3, 4, 5, 6], dtype=float)
            raw_y  = np.array([4000, 3000, 2000, 2800, 1900, 2400, 3500], dtype=float)

            if HAS_SCIPY:
                x_new = np.linspace(0, 6, 400)
                spl   = make_interp_spline(days_x, raw_y, k=3)
                y_new = spl(x_new)
                ax.plot(x_new, y_new, color=RED, linewidth=2.8,
                        solid_capstyle="round")
                ax.fill_between(x_new, y_new, alpha=0.07, color=RED)
            else:
                days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
                ax.plot(days, raw_y, color=RED, linewidth=2.8)
                ax.fill_between(days, raw_y, alpha=0.07, color=RED)
                days_x = np.arange(7)

            ax.set_xticks(np.arange(7))
            ax.set_xticklabels(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
            ax.set_xlim(-0.1, 6.1)
            ax.set_ylim(0, 4500)
            ax.set_yticks([0, 1000, 2000, 3000, 4000])

            ax.yaxis.grid(True, color="#F0F0F0", linewidth=1)
            ax.set_axisbelow(True)
            ax.xaxis.grid(False)
            ax.set_facecolor("white")

            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.tick_params(colors="#9E9E9E", labelsize=9)
            fig.tight_layout(pad=0.6)
            layout.addWidget(canvas)
        else:
            fallback = QLabel("Cài matplotlib để xem biểu đồ.")
            fallback.setAlignment(Qt.AlignCenter)
            fallback.setStyleSheet(f"color: {GRAY_TEXT}; padding: 40px;")
            layout.addWidget(fallback)


# ─────────────────────────────────────────────────────────────────────────────
# Route Item
# ─────────────────────────────────────────────────────────────────────────────
class RouteItem(QWidget):
    def __init__(self, route, label, percent, color):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tên + %
        top = QHBoxLayout()
        route_lbl = QLabel(route)
        route_lbl.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {TEXT_DARK};
        """)
        pct_lbl = QLabel(f"{percent}%")
        pct_lbl.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {RED};
        """)
        top.addWidget(route_lbl)
        top.addStretch()
        top.addWidget(pct_lbl)

        # Nhãn mô tả
        desc_lbl = QLabel(label.upper())
        desc_lbl.setStyleSheet(f"""
            font-size: 9px;
            color: {GRAY_TEXT};
            letter-spacing: 1px;
        """)

        # Thanh tiến trình
        bar_bg = QFrame()
        bar_bg.setFixedHeight(6)
        bar_bg.setStyleSheet(f"background: {GRAY_BG}; border-radius: 3px;")
        bar_lay = QHBoxLayout(bar_bg)
        bar_lay.setContentsMargins(0, 0, 0, 0)
        fill = QFrame()
        fill.setFixedHeight(6)
        fill.setFixedWidth(percent * 2)
        fill.setStyleSheet(f"background: {color}; border-radius: 3px;")
        bar_lay.addWidget(fill)
        bar_lay.addStretch()

        layout.addLayout(top)
        layout.addWidget(desc_lbl)
        layout.addWidget(bar_bg)


# ─────────────────────────────────────────────────────────────────────────────
# Routes Panel
# ─────────────────────────────────────────────────────────────────────────────
class RoutesPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(320)
        self.setStyleSheet(f"""
            RoutesPanel {{
                background: {WHITE};
                border-radius: 16px;
                border: 1px solid {BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)

        # Header
        header = QHBoxLayout()
        title = QLabel("Tuyến bay")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 800;
            color: {TEXT_DARK};
        """)
        icon = QLabel("↗")
        icon.setStyleSheet(f"font-size: 18px; color: {RED};")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(icon)
        layout.addLayout(header)
        layout.addSpacing(14)

        routes = [
            ("SGN -> HAN", "Lưu lượng cao",       85, RED),
            ("SGN -> DAD", "Cao điểm mùa vụ",     65, "#1E88E5"),
            ("HAN -> PQC", "Nhu cầu nghỉ dưỡng",  45, "#8E24AA"),
            ("DAD -> SGN", "Chuyến bay đêm",       30, "#5E35B1"),
        ]
        for route, label, pct, color in routes:
            item = RouteItem(route, label, pct, color)
            layout.addWidget(item)
            layout.addSpacing(10)

        layout.addStretch()

        btn = QPushButton("BÁO CÁO TỐI ƯU HÓA")
        btn.setFixedHeight(40)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {RED_LIGHT};
                border: none;
                border-radius: 10px;
                color: {RED};
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{ background: #FFDADA; }}
        """)
        layout.addWidget(btn)


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Page
# ─────────────────────────────────────────────────────────────────────────────
class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {BG_MAIN};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        content = QWidget()
        content.setStyleSheet(f"background: {BG_MAIN};")
        scroll.setWidget(content)
        outer.addWidget(scroll)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        # Lấy dữ liệu từ Service Layer
        try:
            total_flights    = get_total_flights()
            total_passengers = get_total_passengers()
            active_bookings  = get_active_bookings_count()
            total_revenue    = get_total_revenue()
        except Exception:
            total_flights, total_passengers = 42, 1280
            active_bookings, total_revenue  = 854, 124500

        revenue_text = f"${total_revenue/1000:.1f}k"

        # ── 4 Stat Cards ─────────────────────────────────────────────────────
        cards = QHBoxLayout()
        cards.setSpacing(16)
        cards.addWidget(StatCard("Tổng số Chuyến bay",  total_flights,    "+12.5%", "✈",  "#1E88E5"))
        cards.addWidget(StatCard("Tổng số Hành khách",  total_passengers, "+18.2%", "👥", "#8E24AA"))
        cards.addWidget(StatCard("Yêu cầu Đặt chỗ",    active_bookings,  "-2.4%",  "↗",  "#E53935"))
        cards.addWidget(StatCard("Tổng Doanh thu",      revenue_text,     "+24.5%", "💲", "#43A047"))
        layout.addLayout(cards)

        # ── Chart + Routes ────────────────────────────────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(18)
        bottom.addWidget(RevenueChart(), 1)
        bottom.addWidget(RoutesPanel())
        layout.addLayout(bottom)

        layout.addStretch()