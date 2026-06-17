from __future__ import annotations

from shared.services.passenger_service import get_all_passengers_enriched
from shared.mock_data import MOCK_VIP_PASSENGERS
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
    QComboBox,
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
    get_all_passengers_enriched,
)

from shared.services.booking_service import (
    get_total_revenue,
    get_total_bookings,
)

from shared.mock_data import MOCK_VIP_PASSENGERS, MOCK_FLIGHTS


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
        # store ref for dynamic update
        self._value_lbl  = value_lbl
        self._change_lbl = change_lbl

    def set_value(self, new_value: str) -> None:
        """Update displayed value without rebuilding the card."""
        self._value_lbl.setText(str(new_value))


class RevenueChart(QWidget):

    def __init__(self):
        super().__init__()

        self.setMinimumHeight(320)

        self.setStyleSheet(card_style())

        layout = QVBoxLayout(self)

        layout.setContentsMargins(24, 20, 20, 10)

        header = QHBoxLayout()

        left = QVBoxLayout()

        title = QLabel("Hiệu suất Doanh thu")

        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {C_TEXT};
        """)

        subtitle = QLabel("TỔNG HỢP TUẦN")

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

        title = QLabel("HIỆU QUẢ ĐỘI BAY")

        title.setStyleSheet("""
            font-size: 11px;
            color: #6B7280;
            font-weight: bold;
            letter-spacing: 1px;
        """)

        text = QLabel(
            "Đang hoạt động ở mức <span style='color:#E53935;'>94%</span> công suất."
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

        # TOP HEADER: title + time-filter combo
        top_hdr = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title_col.addWidget(
            _h := QLabel("Thống kê & Phân tích")
        )
        _h.setStyleSheet(f"font-size:22px; font-weight:800; color:{C_TEXT};")
        title_col.addWidget(
            _s := QLabel("Tổng hợp hoạt động kinh doanh JetJet Air")
        )
        _s.setStyleSheet(f"font-size:13px; color:{C_GRAY};")
        top_hdr.addLayout(title_col)
        top_hdr.addStretch()

        self._time_combo = QComboBox()
        self._time_combo.clear() # Tên biến combo box của bạn có thể là time_combo hoặc filter_box
        self._time_combo.addItems(["Cả năm", "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6"])
        self._time_combo.setFixedHeight(36)
        self._time_combo.setStyleSheet(f"""
            QComboBox {{
                background: {C_WHITE}; border: 1px solid {C_BORDER};
                border-radius: 10px; padding: 0 14px;
                font-size: 12px; font-weight: 700; color: {C_TEXT};
            }}
            QComboBox::drop-down {{ border: none; width: 18px; }}
            QComboBox QAbstractItemView {{
                background: {C_WHITE}; border: 1px solid {C_BORDER};
                selection-background-color: #FFEBEE;
                selection-color: {C_RED}; font-size: 12px;
            }}
        """)
        self._time_combo.currentIndexChanged.connect(self._on_time_filter)
        top_hdr.addWidget(self._time_combo)

        layout.addLayout(top_hdr)

        # TOP CARDS
        cards = QHBoxLayout()

        cards.setSpacing(14)

        self._card_revenue = StatCard(
            "$",
            C_RED,
            "Tổng Doanh Thu",
            f"${self.total_revenue:,.0f}",
            "+18.4%",
        )
        self._card_flights = StatCard(
            "✈",
            C_BLUE,
            "Tổng Chuyến Bay",
            f"{self.total_flights:,}",
            "+8.2%",
        )
        self._card_passengers = StatCard(
            "👥",
            "#8E24AA",
            "Hành Khách",
            f"{self.total_passengers:,}",
            "+12.1%",
        )
        self._card_load = StatCard(
            "↗",
            C_ORANGE,
            "Hệ Số Tải",
            f"{self.load_factor}%",
            "+3.8%",
        )

        cards.addWidget(self._card_revenue)
        cards.addWidget(self._card_flights)
        cards.addWidget(self._card_passengers)
        cards.addWidget(self._card_load)

        layout.addLayout(cards)

        # MIDDLE
        middle = QHBoxLayout()

        middle.setSpacing(14)

        chart = RevenueChart()

        middle.addWidget(chart, 5)

        right = QVBoxLayout()

        right.setSpacing(14)

        insights = InfoCard(
            "Thông tin chi tiết",
            [
                ("TUYẾN PHỔ BIẾN", "SGN → ICN", C_BLUE),
                ("TỶ LỆ LẤP ĐẦY", "96%", C_GREEN),
                ("CHẬM CHUYẾN",   "4", C_ORANGE),
                ("GIÁ TB/VÉ",     "$312", C_BLUE),
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
            "Tuyến bay hàng đầu",
            [
                ("SGN → HAN", "92%", C_GREEN),
                ("SGN → ICN", "88%", C_GREEN),
                ("HAN → DAD", "84%", C_BLUE),
                ("DAD → PQC", "78%", C_ORANGE),
            ]
        )

        system = InfoCard(
            "Trạng thái Hệ thống",
            [
                ("ĐẶT CHỖ",  "TRỰC TUYẾN", C_GREEN),
                ("THANH TOÁN", "ỔN ĐỊNH",   C_GREEN),
                ("API",        "HOẠT ĐỘNG", C_GREEN),
            ]
        )

        bottom.addWidget(routes, 5)

        bottom.addWidget(system, 2)

        layout.addLayout(bottom)

        # FOOTER
        footer = QHBoxLayout()

        left = QLabel(
            "© 2026 JETJET AIR PHÂN TÍCH DỮ LIỆU"
        )

        left.setStyleSheet(f"""
            font-size: 11px;
            color: {C_GRAY};
            font-weight: bold;
            letter-spacing: 1px;
        """)

        right = QLabel(
            "● HOẠT ĐỘNG THỜI GIAN THỰC"
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

    def load_statistics(self, index=0):
        try:
            # Import Mock Data từ file cấu hình của bạn
            from shared.mock_data import MOCK_VIP_PASSENGERS, MOCK_FLIGHTS

            # 1. Lọc dữ liệu theo tháng (index = 0 là Cả năm, 1->6 là Tháng 1->6)
            if index == 0:   
                filtered_pax = MOCK_VIP_PASSENGERS
                filtered_flights = MOCK_FLIGHTS
            else:            
                filtered_pax = [p for p in MOCK_VIP_PASSENGERS if getattr(p, 'month', 0) == index]
                filtered_flights = [f for f in MOCK_FLIGHTS if getattr(f, 'month', 0) == index]

            # 2. Tính toán các thông số từ dữ liệu Hard-core đã lọc
            self.total_revenue = sum(getattr(p, "total_spending", 0) for p in filtered_pax)
            self.total_passengers = len(filtered_pax)
            self.total_flights = len(filtered_flights)
            
            # Tính số vé đã đặt (bookings) dựa trên số ghế đã bán trong chuyến bay
            self.total_bookings = sum((getattr(f, 'total_seats', 180) - getattr(f, 'available_seats', 150)) for f in filtered_flights)
            
            # Tính tỷ lệ lấp đầy trung bình
            if self.total_flights > 0:
                self.load_factor = sum(((getattr(f, 'total_seats', 180) - getattr(f, 'available_seats', 150)) / getattr(f, 'total_seats', 180)) * 100 for f in filtered_flights) / self.total_flights
            else:
                self.load_factor = 0

        except Exception as e:
            print(f"Lỗi load_statistics: {e}")
            self.total_revenue = 0
            self.total_flights = 0
            self.total_passengers = 0
            self.total_bookings = 0
            self.load_factor = 0

    def _on_time_filter(self, index: int) -> None:
        """
        Recalculate displayed stats based on the selected time period.
        index 0 = Năm nay  (modifier ~1.0)
        index 1 = Tháng này (modifier ~0.10 with variation)
        index 2 = Tuần này  (modifier ~0.05 with variation)
        """
        base_rev   = self.total_revenue
        base_flt   = self.total_flights
        base_pax   = self.total_passengers
        base_load  = self.load_factor

        if index == 0:   # Năm nay — full-year baseline
            rev  = base_rev
            flt  = base_flt
            pax  = base_pax
            load = base_load
            chg_r, chg_f, chg_p, chg_l = "+18.4%", "+8.2%", "+12.1%", "+3.8%"

        elif index == 1: # Tháng này — ~1/10 of annual + realistic variation
            rev  = round(base_rev  * 0.097,  2)
            flt  = max(1, round(base_flt  * 0.092))
            pax  = max(1, round(base_pax  * 0.101))
            load = min(100, round(base_load * 1.03, 1))
            chg_r, chg_f, chg_p, chg_l = "+5.2%", "+3.1%", "+4.7%", "+1.2%"

        else:            # Tuần này — ~1/52 of annual + realistic variation
            rev  = round(base_rev  * 0.023,  2)
            flt  = max(1, round(base_flt  * 0.021))
            pax  = max(1, round(base_pax  * 0.024))
            load = min(100, round(base_load * 1.01, 1))
            chg_r, chg_f, chg_p, chg_l = "+1.8%", "+0.9%", "+2.1%", "+0.4%"

        self._card_revenue.set_value(f"${rev:,.0f}")
        self._card_flights.set_value(f"{flt:,}")
        self._card_passengers.set_value(f"{pax:,}")
        self._card_load.set_value(f"{load}%")