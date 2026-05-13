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

    def __init__(
        self,
        avatar,
        name,
        email,
        passport_id,
        country,
        rank,
        spending
    ):
        super().__init__()

        self.setFixedHeight(78)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(24, 0, 24, 0)

        layout.setSpacing(10)

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

        name_layout.setSpacing(2)

        name_lbl = QLabel(name)

        name_lbl.setStyleSheet(f"""
            font-size: 14px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        email_lbl = QLabel(email)

        email_lbl.setStyleSheet(f"""
            font-size: 11px;
            color: {GRAY_TEXT};
        """)

        name_layout.addWidget(name_lbl)
        name_layout.addWidget(email_lbl)

        passport_layout = QVBoxLayout()

        passport_layout.setSpacing(2)

        pass_lbl = QLabel(passport_id)

        pass_lbl.setStyleSheet(f"""
            font-size: 13px;
            font-weight: bold;
            color: {TEXT_MED};
        """)

        country_lbl = QLabel(country)

        country_lbl.setStyleSheet(f"""
            font-size: 11px;
            color: {GRAY_TEXT};
        """)

        passport_layout.addWidget(pass_lbl)
        passport_layout.addWidget(country_lbl)

        rank_lbl = QLabel(rank.upper())

        rank_lbl.setFixedHeight(22)

        rank_lbl.setAlignment(Qt.AlignCenter)

        if rank.lower() == "bạch kim":

            bg = "#0F172A"
            color = WHITE

        elif rank.lower() == "vàng":

            bg = "#FFF5F5"
            color = RED

        elif rank.lower() == "bạc":

            bg = "#FFF5F5"
            color = RED

        else:

            bg = "#FFF5F5"
            color = RED

        rank_lbl.setStyleSheet(f"""
            background: {bg};
            color: {color};
            border-radius: 11px;
            padding-left: 10px;
            padding-right: 10px;
            font-size: 11px;
            font-weight: bold;
        """)

        spending_lbl = QLabel(spending)

        spending_lbl.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        action_lbl = QLabel("⋯")

        action_lbl.setStyleSheet(f"""
            font-size: 20px;
            color: {GRAY_TEXT};
        """)

        layout.addWidget(avatar_box, 1)
        layout.addLayout(name_layout, 4)
        layout.addLayout(passport_layout, 3)
        layout.addWidget(rank_lbl, 2)
        layout.addWidget(spending_lbl, 2)
        layout.addWidget(action_lbl, 1)

        layout.setAlignment(action_lbl, Qt.AlignCenter)


class UpgradeCard(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedWidth(230)

        self.setStyleSheet(f"""
            background: {WHITE};
            border-radius: 24px;
            border: 1px solid {BORDER};
        """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(30, 30, 30, 30)

        layout.setSpacing(18)

        icon = QLabel("🎖")

        icon.setAlignment(Qt.AlignCenter)

        icon.setStyleSheet("""
            font-size: 42px;
        """)

        title = QLabel("Nâng hạng\nThành viên")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        desc = QLabel(
            "Xử lý nâng hạng hàng loạt cho\nkhách hàng thân thiết."
        )

        desc.setAlignment(Qt.AlignCenter)

        desc.setStyleSheet(f"""
            font-size: 12px;
            color: {GRAY_TEXT};
            line-height: 18px;
        """)

        button = QPushButton("CHẠY QUY TRÌNH")

        button.setFixedHeight(44)

        button.setCursor(Qt.PointingHandCursor)

        button.setStyleSheet(f"""
            QPushButton {{
                background: #0F172A;
                border: none;
                border-radius: 22px;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background: #1E293B;
            }}
        """)

        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addStretch()
        layout.addWidget(button)


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

        scroll.setStyleSheet("""
            border: none;
            background: transparent;
        """)

        content = QWidget()

        scroll.setWidget(content)

        outer.addWidget(scroll)

        layout = QVBoxLayout(content)

        layout.setContentsMargins(32, 28, 32, 24)

        layout.setSpacing(22)

        # HEADER
        header = QHBoxLayout()

        title_layout = QVBoxLayout()

        title_layout.setSpacing(2)

        title = QLabel("Khách hàng & Thành viên")

        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        subtitle = QLabel(
            "Hồ sơ hành khách và hạng thành viên thân thiết"
        )

        subtitle.setStyleSheet(f"""
            font-size: 14px;
            color: {GRAY_TEXT};
        """)

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        search = QLineEdit()

        search.setPlaceholderText(
            "Tìm kiếm hành khách..."
        )

        search.setFixedWidth(280)

        search.setFixedHeight(40)

        search.setStyleSheet(f"""
            QLineEdit {{
                background: {WHITE};
                border: 1px solid {BORDER};
                border-radius: 20px;
                padding-left: 16px;
                font-size: 13px;
                color: {TEXT_MED};
            }}

            QLineEdit:focus {{
                border: 1px solid {RED};
            }}
        """)

        add_btn = QPushButton("+  Đăng Ký Chương trình")

        add_btn.setFixedHeight(40)

        add_btn.setCursor(Qt.PointingHandCursor)

        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {RED};
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding-left: 20px;
                padding-right: 20px;
            }}

            QPushButton:hover {{
                background: #E53935;
            }}
        """)

        right = QHBoxLayout()

        right.setSpacing(12)

        right.addWidget(search)
        right.addWidget(add_btn)

        header.addLayout(title_layout)
        header.addStretch()
        header.addLayout(right)

        layout.addLayout(header)

        # CONTENT
        body = QHBoxLayout()

        body.setSpacing(20)

        # TABLE CARD
        table_card = QWidget()

        table_card.setStyleSheet(f"""
            background: {WHITE};
            border-radius: 24px;
            border: 1px solid {BORDER};
        """)

        table_layout = QVBoxLayout(table_card)

        table_layout.setContentsMargins(0, 0, 0, 0)

        table_layout.setSpacing(0)

        top = QHBoxLayout()

        top.setContentsMargins(24, 24, 24, 20)

        table_title = QLabel("DANH BẠ THÀNH VIÊN")

        table_title.setStyleSheet(f"""
            font-size: 13px;
            font-weight: bold;
            color: {GRAY_TEXT};
            letter-spacing: 1px;
        """)

        refresh = QLabel("↻")

        refresh.setStyleSheet(f"""
            font-size: 18px;
            color: {GRAY_TEXT};
        """)

        top.addWidget(table_title)
        top.addStretch()
        top.addWidget(refresh)

        table_layout.addLayout(top)

        # TABLE HEADER
        table_header = QHBoxLayout()

        table_header.setContentsMargins(24, 10, 24, 10)

        headers = [
            ("HỌ VÀ TÊN", 5),
            ("GIẤY TỜ", 3),
            ("HẠNG", 2),
            ("CHI TIÊU", 2),
            ("THAO TÁC", 1),
        ]

        for text, stretch in headers:

            lbl = QLabel(text)

            lbl.setStyleSheet(f"""
                font-size: 12px;
                font-weight: bold;
                color: {GRAY_TEXT};
            """)

            table_header.addWidget(lbl, stretch)

        table_layout.addLayout(table_header)

        members = [
            (
                "L",
                "Lê Văn Quân",
                "quanle@jj-air.com",
                "C1234567",
                "VIỆT NAM",
                "Bạch kim",
                "$2,400"
            ),
            (
                "J",
                "James Wilson",
                "james.w@sky.com",
                "K9821332",
                "ANH",
                "Bạc",
                "$850"
            ),
            (
                "N",
                "Nguyễn Thu Hà",
                "ha.nt@jj-air.com",
                "B8821102",
                "VIỆT NAM",
                "Vàng",
                "$1,200"
            ),
            (
                "Y",
                "Yoo Si Jin",
                "yoosj@mail.com",
                "M3342001",
                "HÀN QUỐC",
                "Bạch kim",
                "$5,100"
            ),
            (
                "E",
                "Emma Watson",
                "emma.w@jj-air.com",
                "U1123382",
                "MỸ",
                "Thành viên",
                "$120"
            ),
        ]

        for member in members:

            row = MemberRow(*member)

            table_layout.addWidget(row)

            line = QFrame()

            line.setFrameShape(QFrame.HLine)

            line.setStyleSheet(f"""
                color: {BORDER};
            """)

            table_layout.addWidget(line)

        body.addWidget(table_card, 1)

        # SIDE CARD
        side = UpgradeCard()

        body.addWidget(side)

        layout.addLayout(body)

        # FOOTER
        footer = QHBoxLayout()

        left = QLabel(
            "© 2026 HỆ THỐNG QUẢN TRỊ JETJET / LƯU HÀNH NỘI BỘ"
        )

        left.setStyleSheet(f"""
            font-size: 11px;
            color: {GRAY_TEXT};
            font-weight: bold;
            letter-spacing: 2px;
        """)

        right = QLabel(
            "●  PHIÊN BẢN 2.5.0 ỔN ĐỊNH"
        )

        right.setStyleSheet(f"""
            font-size: 11px;
            color: {RED};
            font-weight: bold;
        """)

        footer.addWidget(left)
        footer.addStretch()
        footer.addWidget(right)

        layout.addLayout(footer)