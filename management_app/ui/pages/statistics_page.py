from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QSizePolicy,
)

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.ticker as mticker
    import numpy as np
    from scipy.interpolate import make_interp_spline

    HAS_MPL = True

except:
    HAS_MPL = False


from shared.services.flight_service import (
    get_total_flights,
    get_average_load_factor,
)

from shared.services.passenger_service import (
    get_total_passengers,
)

from shared.services.booking_service import (
    get_total_revenue,
    get_total_bookings,
)


# COLORS
C_BG = "#F4F6FB"
C_WHITE = "#FFFFFF"
C_BORDER = "#E8EAF0"
C_TEXT = "#1A1A2E"
C_MID = "#4A4A6A"
C_GRAY = "#9999BB"
C_LGRAY = "#F0F1F7"
C_RED = "#E53935"
C_GREEN = "#22C55E"
C_BLUE = "#1E88E5"
C_ORANGE = "#F59E0B"
C_DARK = "#0E1117"


def card_style(radius=16):
    return f"""
        background: {C_WHITE};
        border: 1px solid {C_BORDER};
        border-radius: {radius}px;
    """


class StatCard(QWidget):

    def __init__(
        self,
        icon,
        icon_color,
        title,
        value,
        change,
        is_up=True,
    ):
        super().__init__()

        self.setMinimumHeight(130)

        self.setStyleSheet(card_style())

        layout = QVBoxLayout(self)

        layout.setContentsMargins(22, 18, 22, 18)

        top = QHBoxLayout()

        icon_lbl = QLabel(icon)

        icon_lbl.setStyleSheet(f"""
            font-size: 24px;
            color: {icon_color};
            font-weight: bold;
        """)

        top.addWidget(icon_lbl)
        top.addStretch()

        arrow = "↗" if is_up else "↘"

        color = C_GREEN if is_up else C_RED

        change_lbl = QLabel(f"{arrow} {change}")

        change_lbl.setStyleSheet(f"""
            font-size: 12px;
            color: {color};
            font-weight: bold;
        """)

        top.addWidget(change_lbl)

        title_lbl = QLabel(title.upper())

        title_lbl.setStyleSheet(f"""
            font-size: 11px;
            color: {C_GRAY};
            font-weight: 600;
            letter-spacing: 1px;
        """)

        value_lbl = QLabel(value)

        value_lbl.setStyleSheet(f"""
            font-size: 30px;
            font-weight: 800;
            color: {C_TEXT};
        """)

        layout.addLayout(top)
        layout.addStretch()
        layout.addWidget(title_lbl)
        layout.addWidget(value_lbl)


class RevenueChart(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumHeight(320)

        self.setStyleSheet(card_style())

        layout = QVBoxLayout(self)

        layout.setContentsMargins(24, 20, 20, 10)

        header = QHBoxLayout()

        left = QVBoxLayout()

        title = QLabel("Revenue Performance")

        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {C_TEXT};
        """)

        subtitle = QLabel("WEEKLY OVERVIEW")

        subtitle.setStyleSheet(f"""
            font-size: 11px;
            color: {C_GRAY};
            font-weight: bold;
            letter-spacing: 1px;
        """)

        left.addWidget(title)
        left.addWidget(subtitle)

        header.addLayout(left)

        header.addStretch()

        layout.addLayout(header)

        if HAS_MPL:

            fig = Figure(figsize=(8, 3.2), dpi=100)

            fig.patch.set_facecolor(C_WHITE)

            canvas = FigureCanvas(fig)

            ax = fig.add_subplot(111)

            ax.set_facecolor(C_WHITE)

            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

            raw_x = np.array([0, 1, 2, 3, 4, 5, 6], dtype=float)

            raw_y = np.array(
                [450, 548, 522, 488, 680, 828, 942],
                dtype=float
            )

            x_new = np.linspace(0, 6, 400)

            spline = make_interp_spline(raw_x, raw_y, k=3)

            y_new = spline(x_new)

            ax.fill_between(
                x_new,
                y_new,
                alpha=0.08,
                color=C_RED
            )

            ax.plot(
                x_new,
                y_new,
                color=C_RED,
                linewidth=2.6
            )

            ax.plot(
                raw_x,
                raw_y,
                "o",
                color=C_RED,
                markersize=5,
                markerfacecolor=C_WHITE,
                markeredgewidth=2,
            )

            ax.axhline(
                y=500,
                color="#D8DAE5",
                linestyle="--",
                linewidth=1,
            )

            ax.set_xticks(raw_x)

            ax.set_xticklabels(
                days,
                fontsize=10,
                color=C_GRAY,
            )

            ax.set_ylim(0, 1050)

            ax.set_yticks([0, 250, 500, 750, 1000])

            def y_format(val, pos):
                return f"${int(val)}k"

            ax.yaxis.set_major_formatter(
                mticker.FuncFormatter(y_format)
            )

            ax.tick_params(axis="y", labelsize=10, colors=C_GRAY)

            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.grid(True, axis="y", color="#ECEEF5")

            ax.grid(False, axis="x")

            fig.tight_layout()

            layout.addWidget(canvas)

        else:

            fallback = QLabel(
                "Install matplotlib + scipy to display chart."
            )

            fallback.setAlignment(Qt.AlignCenter)

            fallback.setStyleSheet(f"""
                font-size: 13px;
                color: {C_GRAY};
            """)

            layout.addWidget(fallback)


class InfoCard(QWidget):

    def __init__(self, title, rows):
        super().__init__()

        self.setStyleSheet(card_style())

        layout = QVBoxLayout(self)

        layout.setContentsMargins(20, 18, 20, 18)

        header = QLabel(title)

        header.setStyleSheet(f"""
            font-size: 15px;
            font-weight: bold;
            color: {C_TEXT};
        """)

        layout.addWidget(header)

        layout.addSpacing(12)

        for key, value, color in rows:

            row = QHBoxLayout()

            left = QLabel(key)

            left.setStyleSheet(f"""
                font-size: 12px;
                color: {C_GRAY};
                font-weight: bold;
            """)

            right = QLabel(value)

            right.setStyleSheet(f"""
                font-size: 13px;
                color: {color};
                font-weight: bold;
            """)

            row.addWidget(left)

            row.addStretch()

            row.addWidget(right)

            layout.addLayout(row)

            line = QFrame()

            line.setFrameShape(QFrame.HLine)

            line.setStyleSheet(f"""
                color: {C_BORDER};
            """)

            layout.addWidget(line)

        layout.addStretch()


class FleetEfficiency(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumHeight(120)

        self.setStyleSheet(f"""
            background: {C_DARK};
            border-radius: 16px;
        """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(22, 20, 22, 20)

        title = QLabel("FLEET EFFICIENCY")

        title.setStyleSheet("""
            font-size: 11px;
            color: #6B7280;
            font-weight: bold;
            letter-spacing: 1px;
        """)

        text = QLabel(
            "Operating at <span style='color:#E53935;'>94%</span> capacity."
        )

        text.setTextFormat(Qt.RichText)

        text.setStyleSheet("""
            font-size: 20px;
            color: white;
            font-weight: bold;
        """)

        bar_bg = QFrame()

        bar_bg.setFixedHeight(8)

        bar_bg.setStyleSheet("""
            background: #2A2F3E;
            border-radius: 4px;
        """)

        fill = QFrame(bar_bg)

        fill.setGeometry(0, 0, 300, 8)

        fill.setStyleSheet(f"""
            background: {C_RED};
            border-radius: 4px;
        """)

        layout.addWidget(title)

        layout.addSpacing(10)

        layout.addWidget(text)

        layout.addStretch()

        layout.addWidget(bar_bg)


class StatisticsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.load_statistics()

        self.setStyleSheet(f"""
            background: {C_BG};
        """)

        outer = QVBoxLayout(self)

        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(QFrame.NoFrame)

        scroll.setStyleSheet("""
            background: transparent;
            border: none;
        """)

        content = QWidget()

        scroll.setWidget(content)

        outer.addWidget(scroll)

        layout = QVBoxLayout(content)

        layout.setContentsMargins(28, 24, 28, 20)

        layout.setSpacing(18)

        # TOP CARDS
        cards = QHBoxLayout()

        cards.setSpacing(14)

        cards.addWidget(
            StatCard(
                "$",
                C_RED,
                "Total Revenue",
                f"${self.total_revenue:,.0f}",
                "+18.4%",
            )
        )

        cards.addWidget(
            StatCard(
                "✈",
                C_BLUE,
                "Total Flights",
                f"{self.total_flights:,}",
                "+8.2%",
            )
        )

        cards.addWidget(
            StatCard(
                "👥",
                "#8E24AA",
                "Passengers",
                f"{self.total_passengers:,}",
                "+12.1%",
            )
        )

        cards.addWidget(
            StatCard(
                "↗",
                C_ORANGE,
                "Load Factor",
                f"{self.load_factor}%",
                "+3.8%",
            )
        )

        layout.addLayout(cards)

        # MIDDLE
        middle = QHBoxLayout()

        middle.setSpacing(14)

        chart = RevenueChart()

        middle.addWidget(chart, 5)

        right = QVBoxLayout()

        right.setSpacing(14)

        insights = InfoCard(
            "Insights",
            [
                ("TOP ROUTE", "SGN → ICN", C_BLUE),
                ("OCCUPANCY", "96%", C_GREEN),
                ("DELAYED", "4", C_ORANGE),
                ("AVG PRICE", "$312", C_BLUE),
            ]
        )

        right.addWidget(insights)

        right.addWidget(FleetEfficiency())

        middle.addLayout(right, 2)

        layout.addLayout(middle)

        # BOTTOM
        bottom = QHBoxLayout()

        bottom.setSpacing(14)

        routes = InfoCard(
            "Top Routes",
            [
                ("SGN → HAN", "92%", C_GREEN),
                ("SGN → ICN", "88%", C_GREEN),
                ("HAN → DAD", "84%", C_BLUE),
                ("DAD → PQC", "78%", C_ORANGE),
            ]
        )

        system = InfoCard(
            "System Status",
            [
                ("BOOKING", "ONLINE", C_GREEN),
                ("PAYMENT", "STABLE", C_GREEN),
                ("API", "HEALTHY", C_GREEN),
            ]
        )

        bottom.addWidget(routes, 5)

        bottom.addWidget(system, 2)

        layout.addLayout(bottom)

        # FOOTER
        footer = QHBoxLayout()

        left = QLabel(
            "© 2026 JETJET AIR ANALYTICS"
        )

        left.setStyleSheet(f"""
            font-size: 11px;
            color: {C_GRAY};
            font-weight: bold;
            letter-spacing: 1px;
        """)

        right = QLabel(
            "● REALTIME ACTIVE"
        )

        right.setStyleSheet(f"""
            font-size: 11px;
            color: {C_GREEN};
            font-weight: bold;
        """)

        footer.addWidget(left)

        footer.addStretch()

        footer.addWidget(right)

        layout.addLayout(footer)

    def load_statistics(self):

        try:

            self.total_revenue = get_total_revenue()

            self.total_flights = get_total_flights()

            self.total_passengers = get_total_passengers()

            self.total_bookings = get_total_bookings()

            self.load_factor = get_average_load_factor()

        except:

            self.total_revenue = 4800000

            self.total_flights = 12842

            self.total_passengers = 324000

            self.total_bookings = 9500

            self.load_factor = 82