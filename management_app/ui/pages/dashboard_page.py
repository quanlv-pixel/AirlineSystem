from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QScrollArea,
)

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    HAS_MPL = True

except:
    HAS_MPL = False


from shared.services.flight_service import get_total_flights

from shared.services.passenger_service import get_total_passengers

from shared.services.booking_service import (
    get_active_bookings_count,
    get_total_revenue
)

# COLORS
RED = "#E53935"
RED_LIGHT = "#FFEBEE"

WHITE = "#FFFFFF"

BG_MAIN = "#F8F9FB"

GRAY_TEXT = "#9E9E9E"

GRAY_BG = "#F5F5F5"

TEXT_DARK = "#1A1A2E"

TEXT_MED = "#424242"

BORDER = "#EEEEEE"


def h_line():

    line = QFrame()

    line.setFrameShape(QFrame.HLine)

    line.setStyleSheet(f"""
        color: {BORDER};
    """)

    return line


class StatCard(QWidget):

    def __init__(
        self,
        title,
        value,
        change,
        icon,
        color
    ):
        super().__init__()

        self.setFixedHeight(125)

        self.setStyleSheet(f"""
            background: {WHITE};
            border-radius: 16px;
            border: 1px solid {BORDER};
        """)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            22,
            18,
            22,
            18
        )

        layout.setSpacing(16)

        # ICON
        icon_box = QLabel(icon)

        icon_box.setFixedSize(52, 52)

        icon_box.setAlignment(Qt.AlignCenter)

        icon_box.setStyleSheet(f"""
            background: {color}22;
            border-radius: 14px;
            font-size: 22px;
            color: {color};
        """)

        # TEXT
        text_layout = QVBoxLayout()

        text_layout.setSpacing(4)

        title_lbl = QLabel(title.upper())

        title_lbl.setStyleSheet(f"""
            font-size: 10px;
            letter-spacing: 1px;
            color: {GRAY_TEXT};
            font-weight: 700;
        """)

        value_lbl = QLabel(str(value))

        value_lbl.setStyleSheet(f"""
            font-size: 30px;
            font-weight: 800;
            color: {TEXT_DARK};
        """)

        is_positive = not str(change).startswith("-")

        change_color = "#43A047" if is_positive else RED

        arrow = "▲" if is_positive else "▼"

        change_lbl = QLabel(
            f"{arrow} {change}"
        )

        change_lbl.setStyleSheet(f"""
            color: {change_color};
            font-size: 11px;
            font-weight: 700;
        """)

        text_layout.addWidget(title_lbl)

        text_layout.addWidget(value_lbl)

        text_layout.addWidget(change_lbl)

        layout.addWidget(icon_box)

        layout.addLayout(text_layout)

        layout.addStretch()


class RevenueChart(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet(f"""
            background: {WHITE};
            border-radius: 16px;
            border: 1px solid {BORDER};
        """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            24,
            20,
            24,
            18
        )

        # HEADER
        header = QHBoxLayout()

        title_col = QVBoxLayout()

        title_col.setSpacing(2)

        title = QLabel(
            "Revenue Performance"
        )

        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 800;
            color: {TEXT_DARK};
        """)

        subtitle = QLabel(
            "GLOBAL COLLECTION SUMMARY"
        )

        subtitle.setStyleSheet(f"""
            font-size: 9px;
            color: {GRAY_TEXT};
            letter-spacing: 1.5px;
            font-weight: 600;
        """)

        title_col.addWidget(title)

        title_col.addWidget(subtitle)

        fy_label = QLabel("📅  FY 2026")

        fy_label.setStyleSheet(f"""
            font-size: 12px;
            color: {GRAY_TEXT};
            font-weight: 600;
        """)

        header.addLayout(title_col)

        header.addStretch()

        header.addWidget(fy_label)

        layout.addLayout(header)

        # CHART
        if HAS_MPL:

            fig = Figure(
                figsize=(5, 2.8),
                facecolor="white"
            )

            canvas = FigureCanvas(fig)

            ax = fig.add_subplot(111)

            days = [
                "Mon",
                "Tue",
                "Wed",
                "Thu",
                "Fri",
                "Sat",
                "Sun"
            ]

            values = [
                4000,
                3000,
                2000,
                2800,
                1900,
                2400,
                3500
            ]

            ax.plot(
                days,
                values,
                color=RED,
                linewidth=3
            )

            ax.fill_between(
                days,
                values,
                alpha=0.08,
                color=RED
            )

            ax.grid(
                axis="y",
                color="#F0F0F0"
            )

            ax.set_facecolor("white")

            ax.spines["top"].set_visible(False)

            ax.spines["right"].set_visible(False)

            ax.spines["left"].set_color("#EEEEEE")

            ax.spines["bottom"].set_color("#EEEEEE")

            ax.tick_params(
                colors="#9E9E9E"
            )

            fig.tight_layout()

            layout.addWidget(canvas)

        else:

            fallback = QLabel(
                "Install matplotlib to display chart."
            )

            fallback.setAlignment(Qt.AlignCenter)

            fallback.setStyleSheet(f"""
                color: {GRAY_TEXT};
                padding: 40px;
            """)

            layout.addWidget(fallback)


class RouteItem(QWidget):

    def __init__(
        self,
        route,
        label,
        percent,
        color
    ):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.setSpacing(5)

        # TOP
        top = QHBoxLayout()

        route_lbl = QLabel(route)

        route_lbl.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {TEXT_DARK};
        """)

        percent_lbl = QLabel(
            f"{percent}%"
        )

        percent_lbl.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 700;
            color: {RED};
        """)

        top.addWidget(route_lbl)

        top.addStretch()

        top.addWidget(percent_lbl)

        # LABEL
        desc_lbl = QLabel(label.upper())

        desc_lbl.setStyleSheet(f"""
            font-size: 9px;
            color: {GRAY_TEXT};
            letter-spacing: 1px;
        """)

        # BAR
        bar_bg = QFrame()

        bar_bg.setFixedHeight(6)

        bar_bg.setStyleSheet(f"""
            background: {GRAY_BG};
            border-radius: 3px;
        """)

        bar_layout = QHBoxLayout(bar_bg)

        bar_layout.setContentsMargins(0, 0, 0, 0)

        fill = QFrame()

        fill.setFixedHeight(6)

        fill.setFixedWidth(percent * 2)

        fill.setStyleSheet(f"""
            background: {color};
            border-radius: 3px;
        """)

        bar_layout.addWidget(fill)

        bar_layout.addStretch()

        layout.addLayout(top)

        layout.addWidget(desc_lbl)

        layout.addWidget(bar_bg)


class RoutesPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedWidth(320)

        self.setStyleSheet(f"""
            background: {WHITE};
            border-radius: 16px;
            border: 1px solid {BORDER};
        """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            22,
            20,
            22,
            20
        )

        header = QHBoxLayout()

        title = QLabel("Routes")

        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 800;
            color: {TEXT_DARK};
        """)

        icon = QLabel("↗")

        icon.setStyleSheet(f"""
            font-size: 18px;
            color: {RED};
        """)

        header.addWidget(title)

        header.addStretch()

        header.addWidget(icon)

        layout.addLayout(header)

        layout.addSpacing(12)

        routes = [
            ("SGN → HAN", "High Traffic", 85, RED),
            ("SGN → DAD", "Seasonal Peaks", 65, "#1E88E5"),
            ("HAN → PQC", "Leisure Demand", 45, "#8E24AA"),
            ("DAD → SGN", "Evening Slot", 30, "#5E35B1"),
        ]

        for route, label, pct, color in routes:

            item = RouteItem(
                route,
                label,
                pct,
                color
            )

            layout.addWidget(item)

            layout.addSpacing(10)

        layout.addStretch()

        btn = QPushButton(
            "OPTIMIZATION REPORT"
        )

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

            QPushButton:hover {{
                background: #FFDADA;
            }}
        """)

        layout.addWidget(btn)


class DashboardPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet(f"""
            background: {BG_MAIN};
        """)

        outer = QVBoxLayout(self)

        outer.setContentsMargins(
            0,
            0,
            0,
            0
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()

        scroll.setWidget(content)

        outer.addWidget(scroll)

        layout = QVBoxLayout(content)

        layout.setContentsMargins(
            28,
            24,
            28,
            28
        )

        layout.setSpacing(20)

        # DATA
        try:

            total_flights = get_total_flights()

            total_passengers = get_total_passengers()

            active_bookings = get_active_bookings_count()

            total_revenue = get_total_revenue()

        except:

            total_flights = 42

            total_passengers = 1280

            active_bookings = 854

            total_revenue = 124500

        revenue_text = (
            f"${total_revenue/1000:.1f}k"
        )

        # CARDS
        cards = QHBoxLayout()

        cards.setSpacing(16)

        cards.addWidget(
            StatCard(
                "Total Flights",
                total_flights,
                "+12.5%",
                "✈",
                "#1E88E5"
            )
        )

        cards.addWidget(
            StatCard(
                "Total Passengers",
                total_passengers,
                "+18.2%",
                "👥",
                "#8E24AA"
            )
        )

        cards.addWidget(
            StatCard(
                "Active Bookings",
                active_bookings,
                "-2.4%",
                "📈",
                "#E53935"
            )
        )

        cards.addWidget(
            StatCard(
                "Total Revenue",
                revenue_text,
                "+24.5%",
                "💲",
                "#43A047"
            )
        )

        layout.addLayout(cards)

        # BOTTOM SECTION
        bottom = QHBoxLayout()

        bottom.setSpacing(18)

        chart = RevenueChart()

        routes = RoutesPanel()

        bottom.addWidget(chart, 1)

        bottom.addWidget(routes)

        layout.addLayout(bottom)

        layout.addStretch()