from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QComboBox
)

from shared.services.passenger_service import get_all_passengers_enriched

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.ticker as mticker
    import numpy as np
    from scipy.interpolate import make_interp_spline
    HAS_MPL = True
    HAS_SCIPY = True
except:
    HAS_MPL = False
    HAS_SCIPY = False

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

        # CỐ ĐỊNH CHIỀU CAO để thẻ không bị giãn vô hạn gây vỡ UI
        self.setFixedHeight(130)
        self.setStyleSheet(card_style())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(4) # Thu hẹp khoảng cách chữ

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
        
        
        self._value_lbl  = value_lbl
        self._change_lbl = change_lbl

    def set_value(self, new_value: str) -> None:
        self._value_lbl.setText(str(new_value))


class RevenueChart(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"""
            RevenueChart {{
                background: {C_WHITE};
                border-radius: 16px;
                border: 1px solid {C_BORDER};
            }}
        """)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 20, 24, 18)

        # Header
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(3)
        title = QLabel("Hiệu suất Doanh thu")
        title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {C_TEXT};")
        subtitle = QLabel("TỔNG HỢP THU NHẬP (TỰ ĐỘNG TÍNH TOÁN)")
        subtitle.setStyleSheet(f"font-size: 9px; color: {C_GRAY}; letter-spacing: 2px; font-weight: 600;")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        fy_label = QLabel("📅 NĂM TÀI CHÍNH 2026")
        fy_label.setStyleSheet(f"font-size: 12px; color: {C_GRAY}; font-weight: 600;")

        header.addLayout(title_col)
        header.addStretch()
        header.addWidget(fy_label)
        self._layout.addLayout(header)

        self._canvas_widget = None

    def update_chart(self, month_index: int, total_revenue: float):
        """Vẽ biểu đồ động: Chia doanh thu thực tế ra các tuần/tháng để vẽ"""
        if self._canvas_widget is not None:
            self._layout.removeWidget(self._canvas_widget)
            self._canvas_widget.deleteLater()
            self._canvas_widget = None

        if HAS_MPL:
            fig = Figure(figsize=(5, 2.8), facecolor="white")
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)

            # Thuật toán sinh data vẽ biểu đồ tự động
            if month_index > 6: # Tháng 7-12 chưa có data
                days_x = np.arange(7)
                y_arr = np.zeros(7)
                x_labels = ["T2","T3","T4","T5","T6","T7","CN"]
            elif month_index == 0: # Cả năm -> Chia doanh thu cho 6 tháng (1-6)
                days_x = np.arange(6)
                # Mô phỏng biến động doanh thu giữa các tháng
                y_arr = np.array([total_revenue * p for p in [0.15, 0.1, 0.2, 0.25, 0.18, 0.12]])
                x_labels = ["Th.1", "Th.2", "Th.3", "Th.4", "Th.5", "Th.6"]
            else: # Từng tháng -> Chia thành 4 tuần
                days_x = np.arange(4)
                y_arr = np.array([total_revenue * p for p in [0.2, 0.35, 0.15, 0.3]])
                x_labels = ["Tuần 1", "Tuần 2", "Tuần 3", "Tuần 4"]

            # Vẽ đường uốn lượn (Spline)
            if HAS_SCIPY and len(days_x) > 3 and total_revenue > 0:
                x_new = np.linspace(days_x.min(), days_x.max(), 300)
                spl = make_interp_spline(days_x, y_arr, k=2)
                y_new = spl(x_new)
                y_new[y_new < 0] = 0 # Không cho âm
                ax.plot(x_new, y_new, color=C_RED, linewidth=2.8, solid_capstyle="round")
                ax.fill_between(x_new, y_new, alpha=0.07, color=C_RED)
            else:
                ax.plot(days_x, y_arr, color=C_RED, linewidth=2.8)
                ax.fill_between(days_x, y_arr, alpha=0.07, color=C_RED)

            ax.set_xticks(days_x)
            ax.set_xticklabels(x_labels)
            
            y_max = (max(y_arr) * 1.3) if max(y_arr) > 0 else 100
            ax.set_ylim(0, y_max)
            ax.yaxis.grid(True, color="#F0F0F0", linewidth=1)
            ax.set_axisbelow(True)
            ax.xaxis.grid(False)
            ax.set_facecolor("white")

            for spine in ax.spines.values():
                spine.set_visible(False)

            ax.tick_params(colors="#9E9E9E", labelsize=9)
            fig.tight_layout(pad=0.6)
            self._canvas_widget = canvas
        else:
            fallback = QLabel("Cài matplotlib để xem biểu đồ.")
            fallback.setAlignment(Qt.AlignCenter)
            fallback.setStyleSheet(f"color: {C_GRAY}; padding: 40px;")
            self._canvas_widget = fallback

        self._layout.addWidget(self._canvas_widget)

class InfoCard(QWidget):
    def __init__(self, title, rows):
        super().__init__()
        self.setStyleSheet(card_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)

        header = QLabel(title)
        header.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {C_TEXT};")
        layout.addWidget(header)
        layout.addSpacing(12)

        for key, value, color in rows:
            row = QHBoxLayout()
            left = QLabel(key)
            left.setStyleSheet(f"font-size: 12px; color: {C_GRAY}; font-weight: bold;")
            right = QLabel(value)
            right.setStyleSheet(f"font-size: 13px; color: {color}; font-weight: bold;")
            
            row.addWidget(left)
            row.addStretch()
            row.addWidget(right)
            layout.addLayout(row)

            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet(f"color: {C_BORDER};")
            layout.addWidget(line)

        layout.addStretch()

class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background: {C_BG};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
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
        _h = QLabel("Thống kê & Phân tích")
        _h.setStyleSheet(f"font-size:22px; font-weight:800; color:{C_TEXT};")
        _s = QLabel("Tổng hợp hoạt động kinh doanh JetJet Air")
        _s.setStyleSheet(f"font-size:13px; color:{C_GRAY};")
        title_col.addWidget(_h)
        title_col.addWidget(_s)
        top_hdr.addLayout(title_col)
        top_hdr.addStretch()

        self._time_combo = QComboBox()
        # ĐỦ 12 THÁNG
        self._time_combo.addItems([
            "Cả năm", "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
            "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"
        ])
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

        self._card_revenue = StatCard("$", C_RED, "Tổng Doanh Thu", "$0", "+18.4%")
        self._card_flights = StatCard("✈", C_BLUE, "Tổng Chuyến Bay", "0", "+8.2%")
        self._card_passengers = StatCard("👥", "#8E24AA", "Hành Khách", "0", "+12.1%")
        self._card_load = StatCard("↗", C_ORANGE, "Hệ Số Tải", "0%", "+3.8%")

        cards.addWidget(self._card_revenue)
        cards.addWidget(self._card_flights)
        cards.addWidget(self._card_passengers)
        cards.addWidget(self._card_load)
        layout.addLayout(cards)

        # MIDDLE & BOTTOM (Chart + 2 Info Cards)
        middle = QHBoxLayout()
        middle.setSpacing(14)

        self.chart = RevenueChart()
        middle.addWidget(self.chart, 5)

        right_col = QVBoxLayout()
        right_col.setSpacing(14)
        
        self.insights = InfoCard(
            "Thông tin chi tiết",
            [
                ("TUYẾN PHỔ BIẾN", "SGN → ICN", C_BLUE),
                ("CHẬM CHUYẾN",   "4", C_ORANGE),
                ("GIÁ TB/VÉ",     "$312", C_BLUE),
            ]
        )
        self.routes = InfoCard(
            "Tuyến bay hàng đầu",
            [
                ("SGN → HAN", "92%", C_GREEN),
                ("SGN → ICN", "88%", C_GREEN),
                ("HAN → DAD", "84%", C_BLUE),
                ("DAD → PQC", "78%", C_ORANGE),
            ]
        )
        right_col.addWidget(self.insights)
        right_col.addWidget(self.routes)
        
        middle.addLayout(right_col, 2)
        layout.addLayout(middle)

        # Lần đầu chạy hàm load
        self.load_statistics(0)

    def load_statistics(self, index=0):
        if index > 6: 
            rev, flt, pax, load = 0, 0, 0, 0
        else:
            db_pax = get_all_passengers_enriched()
            db_emails = {getattr(p, 'email', '') for p in db_pax}
            extra_mock = [p for p in MOCK_VIP_PASSENGERS if getattr(p, 'email', '') not in db_emails]
            all_pax = list(db_pax) + extra_mock
            
            if index == 0:   
                filtered_pax = all_pax
                filtered_flights = MOCK_FLIGHTS
            else:
                # Xử lý lọc tháng (Mock có field month, DB cần cắt từ created_at)
                filtered_pax = []
                for p in all_pax:
                    m = getattr(p, 'month', None)
                    if m is None and getattr(p, 'created_at', None):
                        try:
                            m = int(str(p.created_at)[5:7]) # Lấy tháng từ YYYY-MM-DD
                        except:
                            m = 0
                    if m == index:
                        filtered_pax.append(p)
                        
                filtered_flights = [f for f in MOCK_FLIGHTS if getattr(f, 'month', 0) == index]

            rev = sum(getattr(p, "total_spending", 0) for p in filtered_pax)
            pax = len(filtered_pax)
            flt = len(filtered_flights)
            
            if flt > 0:
                load = sum(((getattr(f, 'total_seats', 180) - getattr(f, 'available_seats', 150)) / getattr(f, 'total_seats', 180)) * 100 for f in filtered_flights) / flt
            else:
                load = 0

        self._card_revenue.set_value(f"${rev:,.0f}")
        self._card_flights.set_value(str(flt))
        self._card_passengers.set_value(str(pax))
        self._card_load.set_value(f"{load:.1f}%" if load > 0 else "0%")
        self.chart.update_chart(index, rev)

    def _on_time_filter(self, index: int) -> None:
        self.load_statistics(index)