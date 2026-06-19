from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QPushButton, QScrollArea, QComboBox,
)
from PySide6.QtGui import QPixmap

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

from shared.mock_data import MOCK_VIP_PASSENGERS, MOCK_FLIGHTS
from shared.services.flight_service import get_total_flights
from shared.services.passenger_service import get_total_passengers
from shared.services.booking_service import (
    get_active_bookings_count,
    get_total_revenue,
)
from database.db import get_connection

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

        # Giá trị — stored as instance attr so refresh() can update it
        self._value_lbl = QLabel(str(value))
        self._value_lbl.setStyleSheet(f"""
            font-size: 30px;
            font-weight: 800;
            color: {TEXT_DARK};
        """)

        root.addWidget(title_lbl)
        root.addWidget(self._value_lbl)

    def set_value(self, new_value):
        """Update the displayed value without rebuilding the card."""
        self._value_lbl.setText(str(new_value))


# ─────────────────────────────────────────────────────────────────────────────
# Revenue Chart
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# Revenue Chart (Đã chuyển thành Banner Hình Ảnh)
# ─────────────────────────────────────────────────────────────────────────────
class BannerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"""
            BannerWidget {{
                background: {WHITE};
                border-radius: 16px;
                border: 1px solid {BORDER};
            }}
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 20, 24, 18)

        # Header giữ nguyên UI
        header = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(3)
        title = QLabel("Hình ảnh Hãng bay")
        title.setStyleSheet(f"font-size: 18px; font-weight: 800; color: {TEXT_DARK};")
        subtitle = QLabel("JETJET AIR PROMOTION")
        subtitle.setStyleSheet(f"font-size: 9px; color: {GRAY_TEXT}; letter-spacing: 2px; font-weight: 600;")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        fy_label = QLabel("📅 NĂM TÀI CHÍNH 2026")
        fy_label.setStyleSheet(f"font-size: 12px; color: {GRAY_TEXT}; font-weight: 600;")
        
        header.addLayout(title_col)
        header.addStretch()
        header.addWidget(fy_label)
        self._layout.addLayout(header)

        # Image Label có khả năng bắt sự kiện resize
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setStyleSheet("background: transparent;")
        self.pixmap_src = QPixmap("assets/banner.png")
        
        if self.pixmap_src.isNull():
            self.img_label.setText("✈ HÌNH ẢNH HÃNG BAY ✈\\n(Vui lòng lưu ảnh vào assets/banner.png)")
            self.img_label.setStyleSheet(f"color: {GRAY_TEXT}; font-size: 16px;")
            
        self._layout.addWidget(self.img_label, 1)

    def resizeEvent(self, event):
        """Hàm này giúp ảnh LUÔN co giãn theo khung chứa, không tạo ra scroll"""
        if not self.pixmap_src.isNull():
            # Scale ảnh theo kích thước hiện tại của Label
            scaled_pix = self.pixmap_src.scaled(self.img_label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.img_label.setPixmap(scaled_pix)
        super().resizeEvent(event)

    def update_chart(self, month: int):
        pass 

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
ROUTE_COLORS = [RED, "#1E88E5", "#8E24AA", "#5E35B1"]


def _fetch_top_routes(limit: int = 4):
    """
    Query the DB for the most-booked departure → destination pairs.
    Returns a list of dicts: {route, count}.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT f.departure, f.destination, COUNT(b.booking_id) AS cnt
            FROM bookings b
            JOIN flights f ON b.flight_id = f.flight_id
            WHERE b.booking_status IN ('Confirmed', 'Paid')
            GROUP BY f.departure, f.destination
            ORDER BY cnt DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{"route": f"{(r[0] or '')[:3].upper()} -> {(r[1] or '')[:3].upper()}",
                 "count": r[2]} for r in rows]
    except Exception as e:
        print(f"[RoutesPanel] DB error: {e}")
        return []


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

        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(22, 20, 22, 20)

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
        self._outer.addLayout(header)
        self._outer.addSpacing(14)

        # Placeholder container for route items (rebuilt on refresh)
        self._routes_container = QWidget()
        self._routes_container.setStyleSheet("background:transparent;")
        self._routes_layout = QVBoxLayout(self._routes_container)
        self._routes_layout.setContentsMargins(0, 0, 0, 0)
        self._routes_layout.setSpacing(10)
        self._outer.addWidget(self._routes_container)

        self._outer.addStretch()

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
        self._outer.addWidget(btn)

        # Build routes on first load
        self._build_routes()

    def _build_routes(self):
        """Clear and re-render RouteItem widgets from DB data."""
        # Remove all existing route items
        while self._routes_layout.count():
            child = self._routes_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        top_routes = _fetch_top_routes(4)

        # Grand total = ALL confirmed/paid bookings in the DB (not just top-4 sum)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM bookings
                WHERE booking_status IN ('Confirmed', 'Paid')
            """)
            grand_total = cursor.fetchone()[0] or 1
            conn.close()
        except Exception:
            grand_total = sum(r["count"] for r in top_routes) or 1

        if top_routes:
            for i, r in enumerate(top_routes):
                pct = max(1, int(round(r["count"] / grand_total * 100)))
                color = ROUTE_COLORS[i % len(ROUTE_COLORS)]
                cnt   = r['count']
                label = f"{cnt} đặt chỗ" if cnt != 1 else "1 đặt chỗ"
                item = RouteItem(r["route"], label, pct, color)
                self._routes_layout.addWidget(item)
        else:
            # Fallback: static placeholder data when DB has no bookings yet
            fallback = [
                ("SGN -> HAN", "Lưu lượng cao",       85, RED),
                ("SGN -> DAD", "Cao điểm mùa vụ",     65, "#1E88E5"),
                ("HAN -> PQC", "Nhu cầu nghỉ dưỡng",  45, "#8E24AA"),
                ("DAD -> SGN", "Chuyến bay đêm",       30, "#5E35B1"),
            ]
            for route, label, pct, color in fallback:
                item = RouteItem(route, label, pct, color)
                self._routes_layout.addWidget(item)

    def refresh(self):
        """Public method: re-query DB and re-render route items."""
        self._build_routes()


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
        tf, tp, ab, tr_ = self._fetch_stats()
        total_flights    = tf
        total_passengers = tp
        active_bookings  = ab
        total_revenue    = tr_
        revenue_text = f"${total_revenue/1000:.1f}k"

        # ── 4 Stat Cards ──────────────────────────────────────────
        cards = QHBoxLayout()
        cards.setSpacing(16)
        self._card_flights = StatCard("Tổng số Chuyến bay",  total_flights,    "+12.5%", "✈",  "#1E88E5")
        self._card_passengers = StatCard("Tổng số Hành khách",  total_passengers, "+18.2%", "👥", "#8E24AA")
        self._card_bookings = StatCard("Yêu cầu Đặt chỗ",    active_bookings,  "-2.4%",  "↗",  "#E53935")
        self._card_revenue = StatCard("Tổng Doanh thu",      revenue_text,     "+24.5%", "💲", "#43A047")
        cards.addWidget(self._card_flights)
        cards.addWidget(self._card_passengers)
        cards.addWidget(self._card_bookings)
        cards.addWidget(self._card_revenue)
        layout.addLayout(cards)

        # ── Chart + Routes ───────────────────────────────────────────────────────
        bottom = QHBoxLayout()
        bottom.setSpacing(18)

        # Time-filter combo above the chart
        chart_col = QVBoxLayout()
        chart_col.setSpacing(8)

        time_bar = QHBoxLayout()
        time_lbl = QLabel("📅 Chọn thời gian:")
        time_lbl.setStyleSheet(f"font-size:12px; font-weight:700; color:{GRAY_TEXT};")
        self._time_combo = QComboBox()
        self._time_combo.addItems([
            "Cả năm",
            "Tháng 1",  "Tháng 2",  "Tháng 3",
            "Tháng 4",  "Tháng 5",  "Tháng 6",
            "Tháng 7",  "Tháng 8",  "Tháng 9",
            "Tháng 10", "Tháng 11", "Tháng 12",
        ])
        self._time_combo.setFixedHeight(30)
        self._time_combo.setStyleSheet(f"""
            QComboBox {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 2px 10px;
                font-size: 12px;
                font-weight: 600;
                color: {TEXT_DARK};
            }}
            QComboBox::drop-down {{ border: none; width: 18px; }}
            QComboBox QAbstractItemView {{
                background: {WHITE};
                border: 1px solid {BORDER};
                selection-background-color: #FFEBEE;
                selection-color: {RED};
            }}
        """)
        time_bar.addWidget(time_lbl)
        time_bar.addWidget(self._time_combo)
        time_bar.addStretch()
        chart_col.addLayout(time_bar)

        self._revenue_chart = BannerWidget()
        self._time_combo.currentIndexChanged.connect(self._revenue_chart.update_chart)
        chart_col.addWidget(self._revenue_chart)

        bottom.addLayout(chart_col, 1)
        self._routes_panel = RoutesPanel()
        bottom.addWidget(self._routes_panel)
        layout.addLayout(bottom)

        layout.addStretch()

    # ── Helpers ───────────────────────────────────────────────
    @staticmethod
    def _fetch_stats():
        try:
            from shared.services.passenger_service import get_all_passengers_enriched
            
            # Gộp dữ liệu hành khách (DB + Mock VIP)
            db_pax = get_all_passengers_enriched()
            db_emails = {getattr(p, 'email', '') for p in db_pax}
            extra_mock = [p for p in MOCK_VIP_PASSENGERS if getattr(p, 'email', '') not in db_emails]
            
            total_pax = len(db_pax) + len(extra_mock)
            total_revenue = sum(getattr(p, 'total_spending', 0) for p in (list(db_pax) + extra_mock))
            total_flights = len(MOCK_FLIGHTS)
            
            # Đếm số yêu cầu đặt chỗ
            active_bookings = sum(getattr(p, 'tickets', 1) for p in (list(db_pax) + extra_mock))
            
            return total_flights, total_pax, active_bookings, total_revenue
        except Exception as e:
            print("Lỗi fetch dashboard:", e)
            return 0, 0, 0, 0

    # ── Public API ─────────────────────────────────────────────
    def refresh(self):
        """Re-query all 4 stat metrics and update the displayed values."""
        tf, tp, ab, tr_ = self._fetch_stats()
        revenue_text = f"${tr_/1000:.1f}k"
        self._card_flights.set_value(tf)
        self._card_passengers.set_value(tp)
        self._card_bookings.set_value(ab)
        self._card_revenue.set_value(revenue_text)
        self._routes_panel.refresh()