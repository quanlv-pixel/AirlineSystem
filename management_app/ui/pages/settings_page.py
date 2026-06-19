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
    line.setStyleSheet(f"background: {C_BORDER}; border: none; max-height: 1px;")
    return line

def label(text, size=13, weight=400, color=C_TEXT):
    w = {400: "normal", 500: "500", 600: "600", 700: "bold", 800: "800"}.get(weight, "normal")
    lbl = QLabel(text)
    lbl.setStyleSheet(f"font-size: {size}px; font-weight: {w}; color: {color}; background: transparent; border: none;")
    return lbl

def card_style(radius=18):
    return f"background: {C_WHITE}; border: 1px solid {C_BORDER}; border-radius: {radius}px;"

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

        self.avatar = QLabel(initials)
        self.avatar.setFixedSize(62, 62)
        self.avatar.setAlignment(Qt.AlignCenter)
        self.avatar.setStyleSheet(f"""
            background: {C_RED_LIGHT}; color: {C_RED};
            border-radius: 31px; font-size: 22px; font-weight: bold;
        """)

        info = QVBoxLayout()
        info.setSpacing(4)
        self.name_lbl = label(name, 16, 700)
        self.email_lbl = label(email, 12, 400, C_GRAY)
        info.addWidget(self.name_lbl)
        info.addWidget(self.email_lbl)

        layout.addWidget(self.avatar)
        layout.addLayout(info)
        layout.addStretch()

    def update_info(self, name, email, initials):
        """Hàm dùng để vẽ lại thẻ sau khi lưu thành công"""
        self.name_lbl.setText(name)
        self.email_lbl.setText(email)
        self.avatar.setText(initials)

# ─────────────────────────────────────────────
# SETTINGS PAGE
# ─────────────────────────────────────────────
class SettingsPage(QWidget):
    # Tín hiệu phát ra khi cập nhật thành công để Sidebar/Header bắt lấy
    account_updated = Signal(object) 

    def __init__(self, account=None):
        super().__init__()
        self.account = account
        self.setStyleSheet(f"background: {C_BG};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("border: none; background: transparent;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        self.content_widget = content

        root = QVBoxLayout(content)
        root.setContentsMargins(28, 22, 28, 22)
        root.setSpacing(18)

        # HEADER
        header = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(4)
        titles.addWidget(label("Cài đặt Hệ thống", 26, 800))
        titles.addWidget(label("Cấu hình môi trường vận hành JetJet Air", 13, 400, C_GRAY))

        save_btn = QPushButton("LƯU THAY ĐỔI")
        save_btn.setFixedHeight(42)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{ background: {C_RED}; border: none; border-radius: 12px; color: white; font-size: 13px; font-weight: bold; padding: 0 20px; }}
            QPushButton:hover {{ background: #C62828; }}
        """)
        save_btn.clicked.connect(self.save_profile)

        header.addLayout(titles)
        header.addStretch()
        header.addWidget(save_btn)
        root.addLayout(header)

        # ACCOUNT CARD
        name = getattr(account, "display_name", None) or getattr(account, "username", None) or "JetJet Admin"
        email = getattr(account, "email", None) or "console@jetjet-air.com"
        initials = "".join(word[0] for word in name.split()[:2]).upper() if name else "JA"

        self.profile_card = ProfileCard(name, email, initials)
        root.addWidget(self.profile_card)

        # MAIN
        cols = QHBoxLayout()
        cols.setSpacing(18)

        # LEFT - ADMIN PROFILE
        left = QVBoxLayout()
        admin_card = QWidget()
        admin_card.setStyleSheet(card_style())
        al = QVBoxLayout(admin_card)
        al.setContentsMargins(22, 20, 22, 20)
        al.setSpacing(18)
        al.addWidget(label("HỒ SƠ QUẢN TRỊ", 10, 700, C_GRAY))

        # Full Name Input
        self.name_input = QLineEdit()
        self.name_input.setText(getattr(self.account, "full_name", "") or "")
        self.name_input.setStyleSheet(f"border: 1px solid {C_BORDER}; border-radius: 8px; padding: 8px; background: {C_SOFT};")
        al.addWidget(label("Họ và tên", 13, 600))
        al.addWidget(self.name_input)

        # Email Input
        self.email_input = QLineEdit()
        self.email_input.setText(getattr(self.account, "email", "") or "")
        self.email_input.setStyleSheet(f"border: 1px solid {C_BORDER}; border-radius: 8px; padding: 8px; background: {C_SOFT};")
        al.addWidget(label("Email", 13, 600))
        al.addWidget(self.email_input)

        left.addWidget(admin_card)
        left.addStretch()
        cols.addLayout(left, 55)

        # RIGHT - SYSTEM STATUS
        right = QVBoxLayout()
        status = QWidget()
        status.setStyleSheet(card_style())
        st = QVBoxLayout(status)
        st.setContentsMargins(22, 20, 22, 20)
        st.setSpacing(14)
        st.addWidget(label("TRẠNG THÁI HỆ THỐNG", 10, 700, C_GRAY))
        st.addWidget(label("Tất cả dịch vụ cốt lõi JetJet đang hoạt động bình thường.", 13, 400, C_MID))
        
        dot = QLabel("● TRỰC TUYẾN")
        dot.setStyleSheet(f"font-size: 12px; font-weight: bold; color: {C_GREEN};")
        st.addWidget(dot)

        right.addWidget(status)
        right.addStretch()
        cols.addLayout(right, 45)

        root.addLayout(cols)

        # FOOTER
        footer = QHBoxLayout()
        footer.addWidget(label("© 2026 HỆ THỐNG QUẢN TRỊ JETJET AIR", 10, 400, C_GRAY))
        footer.addStretch()
        footer.addWidget(label("● PHIÊN BẢN 2.5.0 ỔN ĐỊNH", 10, 700, C_RED))
        root.addLayout(footer)

    def save_profile(self):
        if not self.account:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin tài khoản.")
            return

        full_name = self.name_input.text().strip()
        email = self.email_input.text().strip()

        # Bỏ tham số phone vì đã xoá trường này
        success = update_account(
            account_id=self.account.account_id,
            full_name=full_name,
            email=email
        )

        if success:
            # 1. Cập nhật object
            self.account.full_name = full_name
            self.account.email = email
            
            # 2. Cập nhật thẻ Profile trên màn hình hiện tại
            initials = "".join(word[0] for word in full_name.split()[:2]).upper() if full_name else "JA"
            self.profile_card.update_info(full_name, email, initials)

            # 3. Phóng tín hiệu ra bên ngoài để Menu/Sidebar cập nhật
            self.account_updated.emit(self.account)
            
            QMessageBox.information(self, "Thành công", "Cập nhật thông tin thành công!")
        else:
            QMessageBox.warning(self, "Lỗi", "Đã có lỗi xảy ra khi lưu thông tin.")