# settings_page.py
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QColor,
    QPainter,
    QBrush,
    QPainterPath,
    QFont,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QComboBox,
    QLineEdit,
    QMessageBox,
)

from shared.services.account_service import update_account

# ─────────────────────────────────────────────
# COLORS
# ─────────────────────────────────────────────
C_BG = "#F4F6FA"
C_WHITE = "#FFFFFF"
C_BORDER = "#E4E6F0"

C_TEXT = "#111827"
C_MID = "#4B5563"
C_GRAY = "#9CA3AF"

C_RED = "#E53935"
C_RED_LIGHT = "#FFEBEE"

C_BLUE = "#2563EB"
C_GREEN = "#22C55E"

C_SOFT = "#F3F4F6"


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def hline():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"""
        background: {C_BORDER};
        border: none;
        max-height: 1px;
    """)
    return line


def label(text, size=13, weight=400, color=C_TEXT):
    w = {
        400: "normal",
        500: "500",
        600: "600",
        700: "bold",
        800: "800",
    }.get(weight, "normal")

    lbl = QLabel(text)

    lbl.setStyleSheet(f"""
        font-size: {size}px;
        font-weight: {w};
        color: {color};
        background: transparent;
        border: none;
    """)

    return lbl


def card_style(radius=18):
    return f"""
        background: {C_WHITE};
        border: 1px solid {C_BORDER};
        border-radius: {radius}px;
    """


# ─────────────────────────────────────────────
# TOGGLE
# ─────────────────────────────────────────────
class ToggleSwitch(QWidget):

    toggled = Signal(bool)

    def __init__(self, checked=False):
        super().__init__()

        self.checked = checked

        self.setFixedSize(50, 28)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        self.checked = not self.checked
        self.toggled.emit(self.checked)
        self.update()

    def paintEvent(self, event):

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        bg = QColor(C_RED if self.checked else "#D1D5DB")

        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(bg))

        path = QPainterPath()
        path.addRoundedRect(rect, 14, 14)

        p.drawPath(path)

        knob_x = 24 if self.checked else 4

        p.setBrush(QBrush(QColor("white")))

        p.drawEllipse(knob_x, 4, 20, 20)


# ─────────────────────────────────────────────
# APPEARANCE PICKER
# ─────────────────────────────────────────────
class AppearancePicker(QWidget):

    mode_changed = Signal(str)

    def __init__(self):
        super().__init__()

        self.mode = "light"

        self.setFixedHeight(36)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.light_btn = QPushButton("☀")
        self.dark_btn = QPushButton("🌙")

        for btn in [self.light_btn, self.dark_btn]:

            btn.setFixedSize(42, 32)

            btn.setCursor(Qt.PointingHandCursor)

        self.light_btn.clicked.connect(
            lambda: self.set_mode("light")
        )

        self.dark_btn.clicked.connect(
            lambda: self.set_mode("dark")
        )

        layout.addWidget(self.light_btn)
        layout.addWidget(self.dark_btn)

        self.set_mode("light")

    def set_mode(self, mode):

        self.mode = mode

        active = f"""
            QPushButton {{
                background: {C_WHITE};
                border: 1px solid {C_BORDER};
                border-radius: 10px;
                font-size: 15px;
            }}
        """

        inactive = f"""
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 10px;
                color: {C_GRAY};
                font-size: 15px;
            }}

            QPushButton:hover {{
                color: {C_TEXT};
            }}
        """

        self.light_btn.setStyleSheet(
            active if mode == "light" else inactive
        )

        self.dark_btn.setStyleSheet(
            active if mode == "dark" else inactive
        )

        self.mode_changed.emit(mode)


# ─────────────────────────────────────────────
# PROFILE CARD
# ─────────────────────────────────────────────
class ProfileCard(QWidget):

    def __init__(self, name, email, initials):

        super().__init__()

        self.setFixedHeight(110)

        self.setStyleSheet(card_style())

        layout = QHBoxLayout(self)

        layout.setContentsMargins(22, 0, 22, 0)

        avatar = QLabel(initials)

        avatar.setFixedSize(62, 62)

        avatar.setAlignment(Qt.AlignCenter)

        avatar.setStyleSheet(f"""
            background: {C_RED_LIGHT};
            color: {C_RED};
            border-radius: 31px;
            font-size: 22px;
            font-weight: bold;
        """)

        info = QVBoxLayout()

        info.setSpacing(4)

        info.addWidget(label(name, 16, 700))
        info.addWidget(label(email, 12, 400, C_GRAY))

        layout.addWidget(avatar)
        layout.addLayout(info)

        layout.addStretch()


# ─────────────────────────────────────────────
# SETTINGS ROW
# ─────────────────────────────────────────────
class SettingsRow(QWidget):

    def __init__(self, icon, title, subtitle, checked=True):

        super().__init__()

        self.setFixedHeight(74)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        icon_lbl = QLabel(icon)

        icon_lbl.setFixedSize(42, 42)

        icon_lbl.setAlignment(Qt.AlignCenter)

        icon_lbl.setStyleSheet(f"""
            background: {C_SOFT};
            border: 1px solid {C_BORDER};
            border-radius: 12px;
            font-size: 18px;
        """)

        texts = QVBoxLayout()

        texts.setSpacing(3)

        texts.addWidget(label(title, 14, 700))
        texts.addWidget(label(subtitle, 12, 400, C_GRAY))

        toggle = ToggleSwitch(checked)

        layout.addWidget(icon_lbl)
        layout.addLayout(texts)

        layout.addStretch()

        layout.addWidget(toggle)


# ─────────────────────────────────────────────
# SETTINGS PAGE
# ─────────────────────────────────────────────
class SettingsPage(QWidget):

    def __init__(self, account=None):

        super().__init__()
        self.account = account

        self.setStyleSheet(f"""
            background: {C_BG};
        """)

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(QFrame.NoFrame)

        scroll.setStyleSheet("""
            border: none;
            background: transparent;
        """)

        outer = QVBoxLayout(self)

        outer.setContentsMargins(0, 0, 0, 0)

        outer.addWidget(scroll)

        content = QWidget()

        scroll.setWidget(content)

        root = QVBoxLayout(content)

        root.setContentsMargins(28, 22, 28, 22)

        root.setSpacing(18)

        # HEADER
        header = QHBoxLayout()

        titles = QVBoxLayout()

        titles.setSpacing(4)

        titles.addWidget(
            label("Cài đặt Hệ thống", 26, 800)
        )

        titles.addWidget(
            label(
                "Cấu hình môi trường vận hành JetJet Air",
                13,
                400,
                C_GRAY
            )
        )

        save_btn = QPushButton("LƯU THAY ĐỔI")

        save_btn.setFixedHeight(42)

        save_btn.setCursor(Qt.PointingHandCursor)

        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_RED};
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 13px;
                font-weight: bold;
                padding-left: 20px;
                padding-right: 20px;
            }}

            QPushButton:hover {{
                background: #C62828;
            }}
        """)

        save_btn.clicked.connect(self.save_profile)

        header.addLayout(titles)
        header.addStretch()
        header.addWidget(save_btn)

        root.addLayout(header)

        # ACCOUNT
        name = getattr(account, "display_name", None) \
            or getattr(account, "username", None) \
            or "JetJet Admin"

        email = getattr(account, "email", None) \
            or "console@jetjet-air.com"

        initials = "".join(
            word[0] for word in name.split()[:2]
        ).upper()

        root.addWidget(
            ProfileCard(name, email, initials)
        )

        # MAIN
        cols = QHBoxLayout()

        cols.setSpacing(18)

        # LEFT
        left = QVBoxLayout()

        # ADMIN PROFILE SECTION
        admin_card = QWidget()
        admin_card.setStyleSheet(card_style())
        al = QVBoxLayout(admin_card)
        al.setContentsMargins(22, 20, 22, 20)
        al.setSpacing(18)

        al.addWidget(label("ADMIN PROFILE", 10, 700, C_GRAY))

        # Full Name Input
        fn_lbl = label("Full Name", 13, 600)
        self.name_input = QLineEdit()
        self.name_input.setText(getattr(self.account, "full_name", "") or "")
        self.name_input.setStyleSheet(f"border: 1px solid {C_BORDER}; border-radius: 8px; padding: 8px; background: {C_SOFT};")
        al.addWidget(fn_lbl)
        al.addWidget(self.name_input)

        # Email Input
        em_lbl = label("Email", 13, 600)
        self.email_input = QLineEdit()
        self.email_input.setText(getattr(self.account, "email", "") or "")
        self.email_input.setStyleSheet(f"border: 1px solid {C_BORDER}; border-radius: 8px; padding: 8px; background: {C_SOFT};")
        al.addWidget(em_lbl)
        al.addWidget(self.email_input)

        # Phone Input
        ph_lbl = label("Phone", 13, 600)
        self.phone_input = QLineEdit()
        self.phone_input.setText(getattr(self.account, "phone", "") or "")
        self.phone_input.setStyleSheet(f"border: 1px solid {C_BORDER}; border-radius: 8px; padding: 8px; background: {C_SOFT};")
        al.addWidget(ph_lbl)
        al.addWidget(self.phone_input)

        left.addWidget(admin_card)

        # INTERFACE SETTINGS (Only Appearance)
        interface_card = QWidget()
        interface_card.setStyleSheet(card_style())
        il = QVBoxLayout(interface_card)
        il.setContentsMargins(22, 20, 22, 20)
        il.setSpacing(18)
        il.addWidget(label("INTERFACE SETTINGS", 10, 700, C_GRAY))

        # Appearance
        appearance_row = QHBoxLayout()
        appearance_row.addWidget(label("☀", 18))
        appearance_row.addWidget(label("Appearance", 14, 600))
        appearance_row.addStretch()
        appearance_row.addWidget(AppearancePicker())
        il.addLayout(appearance_row)

        left.addWidget(interface_card)
        left.addStretch()

        cols.addLayout(left, 55)

        # RIGHT
        right = QVBoxLayout()

        status = QWidget()

        status.setStyleSheet(card_style())

        st = QVBoxLayout(status)

        st.setContentsMargins(22, 20, 22, 20)

        st.setSpacing(14)

        st.addWidget(
            label("SYSTEM STATUS", 10, 700, C_GRAY)
        )

        st.addWidget(
            label(
                "All JetJet core services operating normally.",
                13,
                400,
                C_MID
            )
        )

        dot = QLabel("● ONLINE")

        dot.setStyleSheet(f"""
            font-size: 12px;
            font-weight: bold;
            color: {C_GREEN};
        """)

        st.addWidget(dot)

        right.addWidget(status)

        right.addStretch()

        cols.addLayout(right, 45)

        root.addLayout(cols)

        # FOOTER
        footer = QHBoxLayout()

        left_txt = label(
            "© 2026 HỆ THỐNG QUẢN TRỊ JETJET AIR",
            10,
            400,
            C_GRAY
        )

        right_txt = label(
            "● PHIÊN BẢN 2.5.0 ỔN ĐỊNH",
            10,
            700,
            C_RED
        )

        footer.addWidget(left_txt)
        footer.addStretch()
        footer.addWidget(right_txt)

        root.addLayout(footer)

    def save_profile(self):
        if not self.account:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin tài khoản.")
            return

        full_name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()

        success = update_account(
            account_id=self.account.account_id,
            full_name=full_name,
            email=email,
            phone=phone
        )

        if success:
            QMessageBox.information(self, "Thành công", "Cập nhật thông tin thành công!")
            # Update the account object locally
            self.account.full_name = full_name
            self.account.email = email
            self.account.phone = phone
        else:
            QMessageBox.warning(self, "Lỗi", "Đã có lỗi xảy ra khi lưu thông tin.")