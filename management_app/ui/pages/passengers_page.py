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
)

from shared.services.passenger_service import (
    get_all_passengers,
    search_passengers,
)


RED = "#FF3B4A"
RED_LIGHT = "#FFF1F2"
WHITE = "#FFFFFF"
BG_MAIN = "#F6F7FB"
GRAY_TEXT = "#9AA4B2"
GRAY_BG = "#F3F4F7"
TEXT_DARK = "#0F172A"
TEXT_MED = "#475569"
BORDER = "#ECEEF2"


class MemberRow(QWidget):

    def __init__(self, passenger):
        super().__init__()

        self.setFixedHeight(78)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(24, 0, 24, 0)

        avatar = passenger.full_name[0].upper()

        avatar_box = QLabel(avatar)

        avatar_box.setFixedSize(36, 36)

        avatar_box.setAlignment(Qt.AlignCenter)

        avatar_box.setStyleSheet(f"""
            background: {GRAY_BG};
            border-radius: 18px;
            font-size: 14px;
            font-weight: bold;
            color: {TEXT_MED};
        """)

        name_layout = QVBoxLayout()

        name_lbl = QLabel(passenger.full_name)

        name_lbl.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        email_lbl = QLabel(passenger.email)

        email_lbl.setStyleSheet(f"""
            font-size: 11px;
            color: {GRAY_TEXT};
        """)

        name_layout.addWidget(name_lbl)
        name_layout.addWidget(email_lbl)

        passport_layout = QVBoxLayout()

        pass_lbl = QLabel(passenger.passport_number)

        pass_lbl.setStyleSheet(f"""
            font-size: 13px;
            font-weight: bold;
            color: {TEXT_MED};
        """)

        country_lbl = QLabel(passenger.nationality)

        country_lbl.setStyleSheet(f"""
            font-size: 11px;
            color: {GRAY_TEXT};
        """)

        passport_layout.addWidget(pass_lbl)
        passport_layout.addWidget(country_lbl)

        rank = passenger.member_rank

        rank_lbl = QLabel(rank.upper())

        rank_lbl.setAlignment(Qt.AlignCenter)

        rank_lbl.setFixedHeight(24)

        if rank.lower() == "bạch kim":

            bg = "#0F172A"
            color = WHITE

        elif rank.lower() == "vàng":

            bg = "#FEF3C7"
            color = "#92400E"

        else:

            bg = RED_LIGHT
            color = RED

        rank_lbl.setStyleSheet(f"""
            background: {bg};
            color: {color};
            border-radius: 12px;
            padding-left: 12px;
            padding-right: 12px;
            font-size: 11px;
            font-weight: bold;
        """)

        spending = f"${passenger.total_spending:,.0f}"

        spending_lbl = QLabel(spending)

        spending_lbl.setStyleSheet(f"""
            font-size: 15px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        action_lbl = QLabel("⋯")

        action_lbl.setStyleSheet(f"""
            font-size: 18px;
            color: {GRAY_TEXT};
        """)

        layout.addWidget(avatar_box, 1)
        layout.addLayout(name_layout, 4)
        layout.addLayout(passport_layout, 3)
        layout.addWidget(rank_lbl, 2)
        layout.addWidget(spending_lbl, 2)
        layout.addWidget(action_lbl, 1)


class PassengerPage(QWidget):

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

        self.layout = QVBoxLayout(content)

        self.layout.setContentsMargins(32, 28, 32, 24)

        self.layout.setSpacing(20)

        self.build_header()

        self.build_table()

        self.load_passengers()

    def build_header(self):

        header = QHBoxLayout()

        title_layout = QVBoxLayout()

        title = QLabel("Khách hàng & Thành viên")

        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        subtitle = QLabel(
            "Hồ sơ hành khách và hạng thành viên"
        )

        subtitle.setStyleSheet(f"""
            font-size: 13px;
            color: {GRAY_TEXT};
        """)

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        self.search = QLineEdit()

        self.search.setPlaceholderText(
            "Tìm kiếm hành khách..."
        )

        self.search.setFixedSize(280, 42)

        self.search.textChanged.connect(
            self.on_search
        )

        self.search.setStyleSheet(f"""
            QLineEdit {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 20px;
                padding-left: 16px;
                font-size: 13px;
            }}
        """)

        add_btn = QPushButton("+  Thêm hành khách")

        add_btn.setFixedHeight(42)

        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {RED};
                border: none;
                border-radius: 20px;
                color: white;
                padding-left: 20px;
                padding-right: 20px;
                font-size: 13px;
                font-weight: bold;
            }}
        """)

        right = QHBoxLayout()

        right.addWidget(self.search)
        right.addWidget(add_btn)

        header.addLayout(title_layout)
        header.addStretch()
        header.addLayout(right)

        self.layout.addLayout(header)

    def build_table(self):

        self.table = QFrame()

        self.table.setStyleSheet(f"""
            background: {WHITE};
            border-radius: 24px;
            border: 1px solid {BORDER};
        """)

        self.table_layout = QVBoxLayout(self.table)

        self.table_layout.setContentsMargins(0, 0, 0, 0)

        self.rows_layout = QVBoxLayout()

        self.table_layout.addLayout(self.rows_layout)

        self.layout.addWidget(self.table)

    def load_passengers(self):

        passengers = get_all_passengers()

        self.render_rows(passengers)

    def render_rows(self, passengers):

        while self.rows_layout.count():

            item = self.rows_layout.takeAt(0)

            widget = item.widget()

            if widget:

                widget.deleteLater()

        if not passengers:

            empty = QLabel(
                "Không có hành khách nào."
            )

            empty.setAlignment(Qt.AlignCenter)

            empty.setStyleSheet(f"""
                padding: 40px;
                color: {GRAY_TEXT};
                font-size: 14px;
            """)

            self.rows_layout.addWidget(empty)

            return

        for passenger in passengers:

            row = MemberRow(passenger)

            self.rows_layout.addWidget(row)

            line = QFrame()

            line.setFrameShape(QFrame.HLine)

            line.setStyleSheet(f"""
                color: {BORDER};
            """)

            self.rows_layout.addWidget(line)

    def on_search(self):

        keyword = self.search.text().strip()

        if not keyword:

            passengers = get_all_passengers()

        else:

            passengers = search_passengers(keyword)

        self.render_rows(passengers)