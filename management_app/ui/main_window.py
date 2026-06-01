from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPen,
    QFont,
    QPainterPath,
)

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QStackedWidget,
    QLineEdit,
)

from shared.models.account import Account

from management_app.ui.pages.dashboard_page import DashboardPage
from management_app.ui.pages.flights_page import FlightsPage
from management_app.ui.pages.passengers_page import PassengerPage
from management_app.ui.pages.bookings_page import BookingsPage
from management_app.ui.pages.statistics_page import StatisticsPage
from management_app.ui.pages.settings_page import SettingsPage


# COLORS
RED = "#E53935"
RED_LIGHT = "#FFEBEE"
WHITE = "#FFFFFF"
BG_MAIN = "#F8F9FB"
SIDEBAR_BG = "#FFFFFF"
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


class AvatarCircle(QWidget):

    def __init__(
        self,
        initials,
        color=RED,
        size=36,
        parent=None
    ):
        super().__init__(parent)

        self.initials = initials[:2].upper()

        self.color = color

        self.setFixedSize(size, size)

    def paintEvent(self, event):

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing
        )

        path = QPainterPath()

        path.addEllipse(
            1,
            1,
            self.width() - 2,
            self.height() - 2
        )

        painter.fillPath(
            path,
            QBrush(QColor(self.color))
        )

        painter.setPen(
            QPen(QColor(WHITE))
        )

        font = QFont()

        font.setPointSize(11)

        font.setBold(True)

        painter.setFont(font)

        painter.drawText(
            self.rect(),
            Qt.AlignCenter,
            self.initials
        )


class Sidebar(QWidget):

    def __init__(
        self,
        on_navigate,
        on_logout,
        parent=None
    ):
        super().__init__(parent)

        self.setFixedWidth(230)

        self.setStyleSheet(f"""
            background: {SIDEBAR_BG};
            border-right: 1px solid {BORDER};
        """)

        layout = QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        layout.setSpacing(0)

        # LOGO
        logo_frame = QWidget()

        logo_frame.setFixedHeight(80)

        logo_layout = QHBoxLayout(logo_frame)

        logo_layout.setContentsMargins(
            20,
            0,
            20,
            0
        )

        logo = AvatarCircle("✈")

        brand_col = QVBoxLayout()

        brand_col.setSpacing(0)

        title = QLabel("JETJET")

        title.setStyleSheet(f"""
            font-size: 16px;
            font-weight: 900;
            color: {RED};
        """)

        subtitle = QLabel("MANAGEMENT")

        subtitle.setStyleSheet(f"""
            font-size: 9px;
            color: {GRAY_TEXT};
            letter-spacing: 2px;
        """)

        brand_col.addWidget(title)

        brand_col.addWidget(subtitle)

        logo_layout.addWidget(logo)

        logo_layout.addLayout(brand_col)

        logo_layout.addStretch()

        layout.addWidget(logo_frame)

        layout.addWidget(h_line())

        layout.addSpacing(12)

        # NAVIGATION
        nav_items = [
            ("📊", "Dashboard", 0),
            ("✈", "Flights", 1),
            ("👥", "Passengers", 2),
            ("🎫", "Bookings", 3),
            ("📈", "Statistics", 4),
            ("⚙", "Settings", 5),
        ]

        self.buttons = {}

        for icon, text, index in nav_items:

            btn = QPushButton(
                f"  {icon}   {text}"
            )

            btn.setFixedHeight(46)

            btn.setCursor(Qt.PointingHandCursor)

            btn.clicked.connect(
                lambda checked=False, i=index:
                on_navigate(i)
            )

            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 12px;
                    text-align: left;
                    padding-left: 18px;
                    font-size: 13px;
                    color: {TEXT_MED};
                    font-weight: 500;
                    margin: 2px 12px;
                }}

                QPushButton:hover {{
                    background: {GRAY_BG};
                }}
            """)

            self.buttons[index] = btn

            layout.addWidget(btn)

        layout.addStretch()

        layout.addWidget(h_line())

        logout_btn = QPushButton(
            "  ⬅  Logout System"
        )

        logout_btn.setFixedHeight(50)

        logout_btn.clicked.connect(on_logout)

        logout_btn.setCursor(Qt.PointingHandCursor)

        logout_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                text-align: left;
                padding-left: 18px;
                font-size: 13px;
                color: {GRAY_TEXT};
            }}

            QPushButton:hover {{
                background: {RED_LIGHT};
                color: {RED};
            }}
        """)

        layout.addWidget(logout_btn)

        self.set_active(0)

    def set_active(self, index):

        for i, btn in self.buttons.items():

            if i == index:

                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {RED_LIGHT};
                        border: none;
                        border-radius: 12px;
                        text-align: left;
                        padding-left: 18px;
                        font-size: 13px;
                        color: {RED};
                        font-weight: bold;
                        margin: 2px 12px;
                    }}
                """)

            else:

                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        border: none;
                        border-radius: 12px;
                        text-align: left;
                        padding-left: 18px;
                        font-size: 13px;
                        color: {TEXT_MED};
                        font-weight: 500;
                        margin: 2px 12px;
                    }}

                    QPushButton:hover {{
                        background: {GRAY_BG};
                    }}
                """)


class TopBar(QWidget):

    def __init__(
        self,
        account: Account,
        parent=None
    ):
        super().__init__(parent)

        self.setFixedHeight(70)

        self.setStyleSheet(f"""
            background: {WHITE};
            border-bottom: 1px solid {BORDER};
        """)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            24,
            0,
            24,
            0
        )

        self.page_title = QLabel("Dashboard")

        self.page_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        search = QLineEdit()

        search.setPlaceholderText(
            "Search flights, passengers or bookings..."
        )

        search.setFixedWidth(320)

        search.setFixedHeight(38)

        search.setStyleSheet(f"""
            QLineEdit {{
                background: {GRAY_BG};
                border: 1px solid {BORDER};
                border-radius: 19px;
                padding-left: 16px;
                font-size: 13px;
            }}

            QLineEdit:focus {{
                border: 1px solid {RED};
            }}
        """)

        display_name = account.display_name or "JetJet User"

        initials = "".join([
            x[0]
            for x in display_name.split()
        ][:2])

        name = QLabel(display_name)

        avatar = AvatarCircle(initials)

        name.setStyleSheet(f"""
            font-size: 13px;
            font-weight: bold;
            color: {TEXT_DARK};
        """)

        role_text = (account.role or "staff").upper()
        role = QLabel(role_text)

        role.setStyleSheet(f"""
            font-size: 9px;
            color: {GRAY_TEXT};
            letter-spacing: 1px;
        """)

        profile_col = QVBoxLayout()

        profile_col.setSpacing(0)

        profile_col.addWidget(name)

        profile_col.addWidget(role)

        layout.addWidget(self.page_title)

        layout.addStretch()

        layout.addWidget(search)

        layout.addSpacing(18)

        layout.addWidget(avatar)

        layout.addLayout(profile_col)


class MainWindow(QMainWindow):

    def __init__(
        self,
        account: Account
    ):
        super().__init__()

        self.account = account

        self.setWindowTitle(
            "JetJet Air Management"
        )

        self.resize(1450, 850)
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # TOPBAR
        self.topbar = TopBar(account)
        root.addWidget(self.topbar)

        # BODY
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # SIDEBAR
        self.sidebar = Sidebar(
            self.navigate,
            self.logout
        )
        body.addWidget(self.sidebar)

        # PAGES
        self.pages = QStackedWidget()

        self.pages.setStyleSheet(f"""
            background: {BG_MAIN};
        """)
        self.pages.addWidget(
            DashboardPage()
        )

        self.pages.addWidget(
            FlightsPage()
        )

        self.pages.addWidget(
            PassengerPage()
        )

        self.pages.addWidget(
            BookingsPage()
        )

        self.pages.addWidget(
            StatisticsPage()
        )

        self.pages.addWidget(
            SettingsPage(account)
        )
        
        body.addWidget(self.pages)
        root.addLayout(body)

    def navigate(self, index):
        self.pages.setCurrentIndex(index)
        self.sidebar.set_active(index)
        labels = [
            "Dashboard",
            "Flights",
            "Passengers",
            "Bookings",
            "Statistics",
            "Settings"
        ]
        self.topbar.page_title.setText(
            labels[index]
        )
        # Live-refresh data-heavy pages on every tab switch
        page = self.pages.widget(index)
        if hasattr(page, 'refresh'):
            try:
                page.refresh()
            except Exception as exc:
                print(f"[MainWindow.navigate] refresh error on page {index}: {exc}")

    def logout(self):
        from management_app.ui.dialogs.login_dialog import LoginDialog
        self.login = LoginDialog()
        self.login.show()
        self.close()