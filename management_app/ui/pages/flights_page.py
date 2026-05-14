from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QLineEdit,
    QScrollArea,
    QComboBox,
)

from shared.services.flight_service import (
    get_all_flights,
    search_flights,
)

RED = "#FF3B3F"
RED_LIGHT = "#FFF1F1"
WHITE = "#FFFFFF"
BG_MAIN = "#F7F8FA"
GRAY_BG = "#F3F4F6"
GRAY_TEXT = "#9CA3AF"
TEXT_DARK = "#111827"
BORDER = "#ECECEC"


class FlightRow(QWidget):

    def __init__(
        self,
        code,
        aircraft,
        departure,
        arrival,
        percent,
        status,
        status_color,
    ):
        super().__init__()

        self.setFixedHeight(82)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)

        # INFO
        info_layout = QHBoxLayout()

        icon = QLabel("✈")
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignCenter)

        icon.setStyleSheet(f"""
            background: {RED_LIGHT};
            border-radius: 12px;
            color: {RED};
            font-size: 18px;
        """)

        text_layout = QVBoxLayout()

        code_label = QLabel(code)
        code_label.setStyleSheet(f"""
            font-size: 15px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        aircraft_label = QLabel(aircraft.upper())
        aircraft_label.setStyleSheet(f"""
            font-size: 11px;
            color: {GRAY_TEXT};
            font-weight: bold;
        """)

        text_layout.addWidget(code_label)
        text_layout.addWidget(aircraft_label)

        info_layout.addWidget(icon)
        info_layout.addSpacing(14)
        info_layout.addLayout(text_layout)

        # ROUTE
        route = QLabel(f"{departure}  ─────  {arrival}")

        route.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        # PASSENGER BAR
        progress_layout = QHBoxLayout()

        progress_bg = QFrame()
        progress_bg.setFixedSize(95, 5)

        progress_bg.setStyleSheet("""
            background: #EEEEEE;
            border-radius: 2px;
        """)

        progress_fill = QFrame(progress_bg)

        progress_fill.setGeometry(
            0,
            0,
            int(percent * 0.95),
            5
        )

        progress_fill.setStyleSheet(f"""
            background: {RED};
            border-radius: 2px;
        """)

        percent_label = QLabel(f"{percent}%")

        percent_label.setStyleSheet("""
            font-size: 12px;
            color: #64748B;
            font-weight: bold;
        """)

        progress_layout.addWidget(progress_bg)
        progress_layout.addWidget(percent_label)

        # STATUS
        status_box = QLabel(status)

        status_box.setAlignment(Qt.AlignCenter)

        status_box.setFixedSize(140, 30)

        status_box.setStyleSheet(f"""
            background: {status_color}22;
            color: {status_color};
            border-radius: 14px;
            font-size: 11px;
            font-weight: bold;
        """)

        # ACTION
        action = QLabel("⟳")

        action.setStyleSheet("""
            font-size: 18px;
            color: #C0C4CC;
        """)

        layout.addLayout(info_layout, 3)
        layout.addWidget(route, 2)
        layout.addLayout(progress_layout, 2)
        layout.addWidget(status_box, 2)
        layout.addWidget(action, 1)


class FlightsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet(f"""
            background: {BG_MAIN};
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()

        scroll.setWidget(content)

        outer.addWidget(scroll)

        layout = QVBoxLayout(content)

        layout.setContentsMargins(28, 24, 28, 28)
        layout.setSpacing(20)

        # HEADER
        header = QHBoxLayout()

        title_layout = QVBoxLayout()

        title = QLabel("Điều phối Bay")

        title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        subtitle = QLabel(
            "Quản lý và giám sát lịch trình bay thương mại"
        )

        subtitle.setStyleSheet(f"""
            font-size: 13px;
            color: {GRAY_TEXT};
        """)

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header.addLayout(title_layout)

        header.addStretch()

        export_btn = QPushButton("↓  Xuất Danh sách")

        export_btn.setFixedHeight(42)

        export_btn.setStyleSheet(f"""
            QPushButton {{
                background: white;
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: bold;
                color: #4B5563;
            }}
        """)

        add_btn = QPushButton("+  Thêm Chuyến bay")

        add_btn.setFixedHeight(42)

        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {RED};
                border: none;
                border-radius: 12px;
                padding: 0 22px;
                color: white;
                font-size: 13px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background: #E53935;
            }}
        """)

        header.addWidget(export_btn)
        header.addSpacing(10)
        header.addWidget(add_btn)

        layout.addLayout(header)

        # SEARCH BAR
        search_frame = QFrame()

        search_frame.setFixedHeight(72)

        search_frame.setStyleSheet(f"""
            background: white;
            border: 1px solid {BORDER};
            border-radius: 20px;
        """)

        search_layout = QHBoxLayout(search_frame)

        search_layout.setContentsMargins(20, 0, 20, 0)

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Tìm theo Mã chuyến hoặc Tuyến bay..."
        )

        self.search_input.setFixedHeight(42)

        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {GRAY_BG};
                border: none;
                border-radius: 14px;
                padding-left: 16px;
                font-size: 13px;
                color: {TEXT_DARK};
            }}
        """)

        self.filter_box = QComboBox()

        self.filter_box.addItems([
            "Tất cả",
            "Scheduled",
            "Boarding",
            "Delayed",
            "Completed",
        ])

        self.filter_box.setFixedSize(180, 42)

        self.filter_box.setStyleSheet(f"""
            QComboBox {{
                background: {GRAY_BG};
                border: none;
                border-radius: 12px;
                padding-left: 14px;
                font-size: 13px;
                font-weight: bold;
                color: #4B5563;
            }}
        """)

        search_layout.addWidget(self.search_input)
        search_layout.addSpacing(10)
        search_layout.addWidget(self.filter_box)

        layout.addWidget(search_frame)

        # TABLE
        table = QFrame()

        table.setStyleSheet(f"""
            background: white;
            border: 1px solid {BORDER};
            border-radius: 24px;
        """)

        table_layout = QVBoxLayout(table)

        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # TABLE HEADER
        header_row = QWidget()

        header_row.setFixedHeight(56)

        header_layout = QHBoxLayout(header_row)

        header_layout.setContentsMargins(24, 0, 24, 0)

        headers = [
            ("THÔNG TIN", 3),
            ("TUYẾN BAY", 2),
            ("LƯỢNG KHÁCH", 2),
            ("TRẠNG THÁI", 2),
            ("THAO TÁC", 1),
        ]

        for text, stretch in headers:

            label = QLabel(text)

            label.setStyleSheet(f"""
                font-size: 11px;
                color: {GRAY_TEXT};
                font-weight: bold;
            """)

            header_layout.addWidget(label, stretch)

        table_layout.addWidget(header_row)

        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(0)

        table_layout.addLayout(self.rows_layout)

        layout.addWidget(table)

        # SIGNALS
        self.search_input.textChanged.connect(
            self.handle_search
        )

        self.filter_box.currentTextChanged.connect(
            self.handle_search
        )

        # LOAD DATA
        self.load_flights()

    def load_flights(self, flights=None):

        if flights is None:
            flights = get_all_flights()

        while self.rows_layout.count():

            item = self.rows_layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

        selected_status = self.filter_box.currentText()

        for flight in flights:

            if (
                selected_status != "Tất cả"
                and flight.status != selected_status
            ):
                continue

            percent = flight.occupancy_percent

            status = flight.status

            color = "#22C55E"

            if status == "Delayed":
                color = "#EF4444"

            elif status == "Boarding":
                color = "#2563EB"

            elif status == "Scheduled":
                color = "#64748B"

            row = FlightRow(
                flight.flight_code,
                flight.aircraft,
                flight.departure,
                flight.destination,
                percent,
                status.upper(),
                color
            )

            self.rows_layout.addWidget(row)

            line = QFrame()

            line.setFrameShape(QFrame.HLine)

            line.setStyleSheet(f"""
                color: {BORDER};
            """)

            self.rows_layout.addWidget(line)

    def handle_search(self):

        keyword = self.search_input.text().strip()

        if not keyword:

            flights = get_all_flights()

        else:

            flights = search_flights(keyword)

        self.load_flights(flights)