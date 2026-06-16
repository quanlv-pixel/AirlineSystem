from collections import namedtuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QScrollArea, QComboBox, QFileDialog, QMessageBox, QDialog, QSizePolicy
)
import csv
from management_app.ui.dialogs.flight_dialog import FlightDialog
from shared.services.flight_service import search_flights, update_flight
from shared.services.flight_service import (
    get_all_flights,
    get_flight_by_id,
)
from shared.api.weather_api import get_weather_by_airport

# ── Màu sắc ──────────────────────────────────────────────────────────────────
RED       = "#E53935"
RED_LIGHT = "#FFEBEE"
WHITE     = "#FFFFFF"
BG_MAIN   = "#F7F8FA"
GRAY_BG   = "#F3F4F6"
GRAY_TEXT = "#9CA3AF"
TEXT_DARK = "#111827"
TEXT_MED  = "#4B5563"
BORDER    = "#E5E7EB"

# ── Trạng thái → (nhãn VI, màu chữ, màu nền) ─────────────────────────────────
_STATUS_MAP = {
    "Scheduled":   ("ĐÃ LÊN LỊCH",  "#64748B", "#F1F5F9"),
    "Delayed":     ("CHẬM CHUYẾN",   "#DC2626", "#FEF2F2"),
    "Boarding":    ("ĐANG LÊN MÁY",  "#2563EB", "#EFF6FF"),
    "Completed":   ("HOÀN THÀNH",    "#64748B", "#F1F5F9"),
    "In Air":      ("ĐANG BAY",       "#7C3AED", "#EDE9FE"),
    "Gate Closed": ("ĐÓNG CỔNG",     "#B45309", "#FEF3C7"),
    "Canceled":    ("ĐÃ HỦY",         "#9CA3AF", "#F3F4F6"),
}
_STATUS_DEFAULT = ("ĐÚNG GIỜ", "#16A34A", "#DCFCE7")


def _status_info(status: str):
    return _STATUS_MAP.get(status, _STATUS_DEFAULT)


# ── Dữ liệu mẫu (fallback khi DB chưa có data) ───────────────────────────────
_FL = namedtuple("_FL", ["flight_code","aircraft","departure","destination",
                          "occupancy_percent","status"])

FALLBACK_FLIGHTS = [
    _FL("JJ101", "Airbus A321NEO", "SGN", "HAN", 96, "Delayed"),
    _FL("JJ102", "Boeing 787-9",   "SGN", "ICN", 100,"In Air"),
    _FL("JJ103", "Airbus A350",    "HAN", "NRT", 93, "Gate Closed"),
    _FL("JJ104", "Airbus A321NEO", "DAD", "SGN", 91, "Completed"),
    _FL("JJ201", "Boeing 737 MAX", "HAN", "SGN", 20, "Scheduled"),
    _FL("JJ202", "Boeing 737 MAX", "SGN", "DAD", 5,  "Scheduled"),
    _FL("JJ301", "Airbus A320",    "SGN", "PQC", 48, "Boarding"),
    _FL("JJ302", "Airbus A320",    "CXR", "HAN", 33, "Boarding"),
    _FL("JJ401", "ATR 72",         "PQC", "SGN", 12, "Scheduled"),
]

# ── Separator dọc ─────────────────────────────────────────────────────────────
class _VSep(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFixedWidth(1)
        self.setFixedHeight(22)
        self.setStyleSheet(f"background: {BORDER}; border: none;")

# ── RECOVERY DIALOG (Thùng Rác) ────────────────────────────────────────────────
class RecoveryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thùng Rác - Khôi phục Chuyến bay")
        self.setFixedSize(600, 400)
        self.setStyleSheet(f"background: {BG_MAIN};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QWidget()
        header.setStyleSheet(f"background: {WHITE}; border-bottom: 1px solid {BORDER};")
        header.setFixedHeight(50)
        h_lay = QHBoxLayout(header)
        title = QLabel("Danh sách Chuyến bay đã hủy")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {TEXT_DARK};")
        h_lay.addWidget(title)
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        scroll.setWidget(content)
        
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(10)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(scroll)

        self.load_canceled_flights()

    def load_canceled_flights(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        flights = get_all_flights()
        canceled = [f for f in flights if getattr(f, "status", "") == "Canceled"]

        if not canceled:
            empty = QLabel("Thùng rác trống. Không có chuyến bay nào bị hủy.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color: {GRAY_TEXT}; font-size: 14px; padding-top: 50px;")
            self.content_layout.addWidget(empty)
            return

        for f in canceled:
            row = QWidget()
            row.setFixedHeight(60)
            row.setStyleSheet(f"background: {WHITE}; border: 1px solid {BORDER}; border-radius: 10px;")
            r_lay = QHBoxLayout(row)
            
            code = getattr(f, "flight_number", "?")
            dep = getattr(f, "departure", "?")
            dst = getattr(f, "destination", "?")

            info = QLabel(f"✈ {code}   |   {dep} ➔ {dst}")
            info.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {TEXT_DARK}; border: none;")
            r_lay.addWidget(info)
            r_lay.addStretch()

            restore_btn = QPushButton("Khôi phục")
            restore_btn.setCursor(Qt.PointingHandCursor)
            restore_btn.setStyleSheet(f"""
                background: #DCFCE7; color: #16A34A; border: none;
                border-radius: 6px; padding: 8px 16px; font-weight: bold;
            """)
            restore_btn.clicked.connect(lambda checked, fl=f: self.restore_flight(fl))
            r_lay.addWidget(restore_btn)

            self.content_layout.addWidget(row)

    def restore_flight(self, flight):
        f_id = getattr(flight, "flight_id", None)
        if update_flight(f_id, status="Scheduled"):
            QMessageBox.information(self, "Thành công", f"Đã khôi phục chuyến bay {getattr(flight, 'flight_number', '')}!")
            self.load_canceled_flights()


# ── Flight Row ─────────────────────────────────────────────────────────────
class FlightRow(QWidget):
    def __init__(self, code, aircraft, departure, arrival,
                 percent, status, status_color, flight=None, edit_callback=None,
                 cancel_callback=None):
        super().__init__()
        self.flight = flight
        self.edit_callback = edit_callback
        self.cancel_callback = cancel_callback
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setStyleSheet("background: transparent;")

        base_lay = QVBoxLayout(self)
        base_lay.setContentsMargins(0, 0, 0, 0)
        base_lay.setSpacing(0)
        base_lay.setAlignment(Qt.AlignTop) 

        main_container = QWidget()
        main_container.setFixedHeight(72)
        lay = QHBoxLayout(main_container)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)

        # THÔNG TIN
        info_w = QWidget(); info_w.setStyleSheet("background:transparent;")
        info_l = QHBoxLayout(info_w)
        info_l.setContentsMargins(0, 0, 0, 0)
        info_l.setSpacing(12)

        icon_lbl = QLabel("✈")
        icon_lbl.setFixedSize(32, 32)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background: {RED_LIGHT};
            border-radius: 10px;
            color: {RED};
            font-size: 14px;
        """)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.setAlignment(Qt.AlignVCenter)

        code_lbl = QLabel(code)
        code_lbl.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: {TEXT_DARK};
        """)

        aircraft_lbl = QLabel(aircraft.upper())
        aircraft_lbl.setStyleSheet(f"""
            font-size: 10px;
            color: {GRAY_TEXT};
            font-weight: 600;
            letter-spacing: 0.5px;
        """)

        text_col.addWidget(code_lbl)
        text_col.addWidget(aircraft_lbl)

        info_l.addWidget(icon_lbl)
        info_l.addLayout(text_col)
        info_l.addStretch()

        lay.addWidget(info_w, 35)

        # TUYẾN BAY
        route_w = QWidget(); route_w.setStyleSheet("background:transparent;")
        route_l = QHBoxLayout(route_w)
        route_l.setContentsMargins(0, 0, 0, 0)
        route_l.setSpacing(20)
        route_l.setAlignment(Qt.AlignVCenter)

        for airport in (departure, arrival):
            lbl = QLabel(airport)
            lbl.setStyleSheet(f"""
                font-size: 14px;
                font-weight: 700;
                color: {TEXT_DARK};
            """)
            route_l.addWidget(lbl)
        route_l.addStretch()

        lay.addWidget(route_w, 18)

        # LƯỢNG KHÁCH
        occ_w = QWidget(); occ_w.setStyleSheet("background:transparent;")
        occ_l = QHBoxLayout(occ_w)
        occ_l.setContentsMargins(0, 0, 0, 0)
        occ_l.setSpacing(10)
        occ_l.setAlignment(Qt.AlignVCenter)

        bar_frame = QFrame()
        bar_frame.setFixedSize(100, 5)
        bar_frame.setStyleSheet("background: #EEEEEE; border-radius: 2px;")

        fill = QFrame(bar_frame)
        fill.setGeometry(0, 0, min(100, int(percent)), 5)
        fill.setStyleSheet(f"background: {RED}; border-radius: 2px;")

        pct_lbl = QLabel(f"{percent}%")
        pct_lbl.setStyleSheet(f"""
            font-size: 12px;
            color: {TEXT_MED};
            font-weight: 600;
        """)

        occ_l.addWidget(bar_frame)
        occ_l.addWidget(pct_lbl)
        occ_l.addStretch()

        lay.addWidget(occ_w, 22)

        # TRẠNG THÁI
        vi_label, fg, bg = _status_info(status)

        badge_outer = QWidget(); badge_outer.setStyleSheet("background:transparent;")
        badge_outer_l = QHBoxLayout(badge_outer)
        badge_outer_l.setContentsMargins(0, 0, 0, 0)
        badge_outer_l.setAlignment(Qt.AlignVCenter)

        badge = QWidget()
        badge.setFixedHeight(28)
        badge.setStyleSheet(f"""
            background: {bg};
            border-radius: 14px;
        """)

        badge_l = QHBoxLayout(badge)
        badge_l.setContentsMargins(12, 0, 10, 0)
        badge_l.setSpacing(6)

        vi_lbl = QLabel(vi_label)
        vi_lbl.setStyleSheet(f"""
            color: {fg};
            font-size: 11px;
            font-weight: 700;
        """)

        drop_btn = QPushButton("▼")
        drop_btn.setFixedSize(16, 16)
        drop_btn.setCursor(Qt.PointingHandCursor)
        drop_btn.setStyleSheet(f"""
            color: {fg};
            font-size: 9px;
            background: transparent;
            border: none;
        """)

        badge_l.addWidget(vi_lbl)
        badge_l.addWidget(drop_btn)

        badge_outer_l.addWidget(badge)
        badge_outer_l.addStretch()

        lay.addWidget(badge_outer, 20)

        # THAO TÁC
        action_w = QWidget(); action_w.setStyleSheet("background:transparent;")
        action_l = QHBoxLayout(action_w)
        action_l.setContentsMargins(0, 0, 0, 0)
        action_l.setAlignment(Qt.AlignCenter)
        
        action_btn = QPushButton("✎")
        action_btn.setFixedSize(26, 26)
        action_btn.setCursor(Qt.PointingHandCursor)
        action_btn.setStyleSheet(f"""
            color: {GRAY_TEXT};
            font-size: 14px;
            border: 1.5px solid {BORDER};
            border-radius: 13px;
            background: transparent;
        """)
        if self.edit_callback and self.flight:
            action_btn.clicked.connect(lambda: self.edit_callback(self.flight))

        action_l.addWidget(action_btn)

        cancel_btn = QPushButton("✕")
        cancel_btn.setFixedSize(26, 26)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        is_canceled = (status == "Canceled")
        cancel_btn.setEnabled(not is_canceled)
        cancel_btn.setStyleSheet(f"""
            color: {'#9CA3AF' if is_canceled else '#E53935'};
            font-size: 13px;
            font-weight: 700;
            border: 1.5px solid {'#D1D5DB' if is_canceled else '#FECACA'};
            border-radius: 13px;
            background: {'#F9FAFB' if is_canceled else '#FFF5F5'};
        """)
        if self.cancel_callback and self.flight and not is_canceled:
            cancel_btn.clicked.connect(lambda: self.cancel_callback(self.flight))
        action_l.addWidget(cancel_btn)

        lay.addWidget(action_w, 5)

        base_lay.addWidget(main_container)

        # LÝ DO DELAY
        self.reason_container = QWidget()
        self.reason_container.hide()
        reason_lay = QVBoxLayout(self.reason_container)
        reason_lay.setContentsMargins(65, 0, 20, 15)
        
        self.reason_lbl = QLabel("")
        self.reason_lbl.setStyleSheet(f"""
            background: #FEF2F2;
            color: #991B1B;
            border: 1px solid #FCA5A5;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: bold;
        """)
        reason_lay.addWidget(self.reason_lbl)
        base_lay.addWidget(self.reason_container)

        if status == "Delayed":
            weather = get_weather_by_airport(departure)
            reason_text = (f"Lý do chậm chuyến: Thời tiết tại sân bay {departure} - "
                           f"{weather['icon']} {weather['condition']}, Nhiệt độ: {weather['temperature']}°C, "
                           f"Rủi ro: {weather['delay_risk']}")
            self.reason_lbl.setText(reason_text)
            drop_btn.clicked.connect(self.toggle_reason)
        else:
            drop_btn.hide()

    def toggle_reason(self):
        if self.reason_container.isHidden():
            self.reason_container.show()
        else:
            self.reason_container.hide()
        self.adjustSize()

    def mouseDoubleClickEvent(self, event):
        if self.edit_callback and self.flight:
            self.edit_callback(self.flight)
        super().mouseDoubleClickEvent(event)


# ── Flights Page ─────────────────────────────────────────────────────────────
class FlightsPage(QWidget):
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
        layout.setContentsMargins(28, 20, 28, 28)
        layout.setSpacing(16)

        action_bar = QHBoxLayout()
        action_bar.setSpacing(10)
        action_bar.addStretch()

        self.export_btn = QPushButton("↓  Xuất Danh sách")
        self.export_btn.setFixedHeight(36)
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 600;
                color: {TEXT_MED};
            }}
            QPushButton:hover {{ background: {GRAY_BG}; }}
        """)

        self.recover_btn = QPushButton("↺ Thùng rác")
        self.recover_btn.setFixedHeight(36)
        self.recover_btn.setCursor(Qt.PointingHandCursor)
        self.recover_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 0 16px;
                font-size: 12px;
                font-weight: 600;
                color: {TEXT_MED};
            }}
            QPushButton:hover {{ background: {GRAY_BG}; color: {TEXT_DARK}; }}
        """)
        self.recover_btn.clicked.connect(self.open_recovery_dialog)

        self.add_btn = QPushButton("+  Thêm Chuyến bay")
        self.add_btn.setFixedHeight(36)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {RED};
                border: none;
                border-radius: 10px;
                padding: 0 18px;
                color: white;
                font-size: 12px;
                font-weight: 700;
            }}
            QPushButton:hover {{ background: #C62828; }}
        """)

        self.add_btn.clicked.connect(self.open_add_dialog)
        self.export_btn.clicked.connect(self.export_csv)

        action_bar.addWidget(self.export_btn)
        action_bar.addWidget(self.recover_btn)
        action_bar.addWidget(self.add_btn)
        layout.addLayout(action_bar)

        search_frame = QFrame()
        search_frame.setFixedHeight(56)
        search_frame.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)

        sl = QHBoxLayout(search_frame)
        sl.setContentsMargins(16, 0, 16, 0)
        sl.setSpacing(12)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet(f"font-size: 14px; color: {GRAY_TEXT};")
        sl.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm theo Mã chuyến hoặc Tuyến bay...")
        self.search_input.setFrame(False)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                font-size: 13px;
                color: {TEXT_DARK};
            }}
        """)
        sl.addWidget(self.search_input, 1)

        sl.addWidget(_VSep())

        for icon in ("☰", "⊞"):
            btn = QPushButton(icon)
            btn.setFixedSize(30, 30)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    font-size: 14px;
                    color: {GRAY_TEXT};
                    border-radius: 6px;
                }}
                QPushButton:hover {{ background: {GRAY_BG}; color: {TEXT_DARK}; }}
            """)
            sl.addWidget(btn)

        sl.addWidget(_VSep())

        status_lbl = QLabel("Trạng thái:")
        status_lbl.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {TEXT_MED};
        """)
        sl.addWidget(status_lbl)

        self.filter_box = QComboBox()
        self.filter_box.addItems([
            "Tất cả", "Scheduled", "Boarding", "Delayed",
            "In Air", "Gate Closed", "Completed",
        ])
        self.filter_box.setFixedHeight(32)
        self.filter_box.setStyleSheet(f"""
            QComboBox {{
                background: transparent;
                border: none;
                font-size: 13px;
                font-weight: 700;
                color: {TEXT_DARK};
                padding-right: 4px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 18px;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {GRAY_TEXT};
            }}
            QComboBox QAbstractItemView {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 8px;
                selection-background-color: {RED_LIGHT};
                selection-color: {RED};
                font-size: 13px;
                padding: 4px;
            }}
        """)
        sl.addWidget(self.filter_box)

        sl.addWidget(_VSep())

        refresh_btn = QPushButton("↺")
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                font-size: 15px;
                color: {GRAY_TEXT};
                border-radius: 6px;
            }}
            QPushButton:hover {{ background: {GRAY_BG}; color: {TEXT_DARK}; }}
        """)
        refresh_btn.clicked.connect(lambda: self.load_flights())
        sl.addWidget(refresh_btn)

        layout.addWidget(search_frame)

        self.table = QFrame()
        self.table.setStyleSheet(f"""
            QFrame {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 20px;
            }}
        """)

        table_l = QVBoxLayout(self.table)
        table_l.setContentsMargins(0, 0, 0, 8)
        table_l.setSpacing(0)

        hdr_row = QWidget()
        hdr_row.setFixedHeight(48)
        hdr_row.setStyleSheet("background: transparent;")
        hdr_l = QHBoxLayout(hdr_row)
        hdr_l.setContentsMargins(20, 0, 20, 0)

        for text, stretch in [
            ("THÔNG TIN",   35),
            ("TUYẾN BAY",   18),
            ("LƯỢNG KHÁCH", 22),
            ("TRẠNG THÁI",  20),
            ("THAO TÁC",     5),
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"""
                font-size: 10px;
                color: {GRAY_TEXT};
                font-weight: 700;
                letter-spacing: 0.8px;
            """)
            hdr_l.addWidget(lbl, stretch)

        table_l.addWidget(hdr_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {BORDER}; border: none;")
        table_l.addWidget(sep)

        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(0)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        table_l.addLayout(self.rows_layout)

        layout.addWidget(self.table)

        self.search_input.textChanged.connect(self.handle_search)
        self.filter_box.currentTextChanged.connect(self.handle_search)

        self.load_flights()

    def load_flights(self, flights=None):
        if flights is None:
            try:
                flights = get_all_flights()
            except Exception:
                flights = []
            if not flights:
                flights = FALLBACK_FLIGHTS

        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        selected_status = self.filter_box.currentText()
        shown = 0

        for flight in flights:
            status = flight.get("status") if isinstance(flight, dict) else getattr(flight, "status", "Scheduled")
            
            if status == "Canceled":
                continue

            if selected_status != "Tất cả" and status != selected_status:
                continue

            if isinstance(flight, dict):
                percent_raw  = flight.get("occupancy_percent")
                if percent_raw is None:
                    total  = flight.get("total_seats", 180) or 180
                    avail  = flight.get("available_seats", total)
                    percent_raw = round((1 - avail / total) * 100)
                percent = int(percent_raw)
                code    = flight.get("flight_number", flight.get("flight_code", "—"))
                aircraft= flight.get("aircraft", "—")
                dep     = flight.get("departure", "—")
                dst     = flight.get("destination", "—")
            else:
                percent_raw  = getattr(flight, "occupancy_percent", None)
                if percent_raw is None:
                    total = getattr(flight, "total_seats", 180) or 180
                    avail = getattr(flight, "available_seats", total)
                    percent_raw = round((1 - avail / total) * 100)
                percent = int(percent_raw)
                code    = getattr(flight, "flight_code", getattr(flight, "flight_number", "—"))
                aircraft= getattr(flight, "aircraft", "—")
                dep     = getattr(flight, "departure", "—")
                dst     = getattr(flight, "destination", "—")

            color_map = {
                "Delayed":     "#DC2626",
                "Boarding":    "#2563EB",
                "Scheduled":   "#64748B",
                "In Air":      "#7C3AED",
                "Gate Closed": "#B45309",
                "Completed":   "#64748B",
            }
            status_color = color_map.get(status, "#16A34A")

            row = FlightRow(
                code, aircraft, dep, dst,
                percent, status, status_color,
                flight=flight,
                edit_callback=self.open_edit_dialog,
                cancel_callback=self.handle_cancel_flight
            )
            self.rows_layout.addWidget(row)

            if shown > 0:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFixedHeight(1)
                line.setStyleSheet(f"background: {BORDER}; border: none;")
                self.rows_layout.addWidget(line)

            shown += 1

        if shown == 0:
            empty = QLabel("Không tìm thấy chuyến bay phù hợp.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"color: {GRAY_TEXT}; font-size: 14px; padding: 40px;")
            self.rows_layout.addWidget(empty)

    def handle_search(self):
        keyword = self.search_input.text().strip()

        if not keyword:
            try:
                flights = get_all_flights()
            except Exception:
                flights = []
            if flights is None:
                flights=[]
        else:
            try:
                flights = search_flights(keyword)
            except Exception:
                flights = []
            if not flights:
                kw = keyword.lower()
                flights = [
                    f for f in FALLBACK_FLIGHTS
                    if kw in f.flight_code.lower()
                    or kw in f.departure.lower()
                    or kw in f.destination.lower()
                ]

        self.load_flights(flights)

    def open_add_dialog(self):
        dialog = FlightDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_flights()

    def open_edit_dialog(self, flight):
        dialog = FlightDialog(flight=flight, parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.load_flights()
            
    def open_recovery_dialog(self):
        dialog = RecoveryDialog(parent=self)
        dialog.exec()
        self.load_flights()

    def handle_cancel_flight(self, flight):
        flight_id = getattr(flight, 'flight_id', None) or (flight.get('flight_id') if isinstance(flight, dict) else None)
        code = getattr(flight, 'flight_number', None) or (flight.get('flight_number', '?') if isinstance(flight, dict) else '?')
        reply = QMessageBox.question(
            self,
            "Xác nhận hủy chuyến bay",
            f"Chuyến bay {code} sẽ được đưa vào Thùng rác. Bạn có chắc muốn tiếp tục?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ok = update_flight(flight_id, status="Canceled")
            if ok:
                QMessageBox.information(self, "Thành công", f"Đã chuyển {code} vào Thùng rác.")
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể hủy chuyến bay.")
            self.handle_search()
            
    def export_csv(self):
        flights = get_all_flights()
        if not flights:
            QMessageBox.warning(self, "Trống", "Không có dữ liệu để xuất!")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Lưu danh sách chuyến bay", "", "CSV Files (*.csv)")
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Mã Chuyến", "Hãng", "Sân bay đi", "Sân bay đến", "Giờ đi", "Giờ đến", "Tổng ghế", "Trạng thái", "Tàu bay"])
                for fl in flights:
                    writer.writerow([
                        fl.flight_number, fl.airline_name, fl.departure, fl.destination,
                        fl.departure_time, fl.arrival_time,
                        fl.total_seats, fl.status, fl.aircraft
                    ])
            QMessageBox.information(self, "Thành công", f"Đã xuất file CSV thành công:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu file: {str(e)}")