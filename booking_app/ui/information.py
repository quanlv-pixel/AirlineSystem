"""
information.py
--------------
Trang Thông Tin Tài Khoản — JetJet Air Booking Portal
Hiển thị avatar, stats (tổng chi tiêu, số chuyến bay),
thông tin tài khoản, và nút kích hoạt hội viên.
"""
from __future__ import annotations
import sys
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QColor, QPainter, QBrush, QPen,
    QPainterPath, QLinearGradient, QFont
)
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QScrollArea, QSizePolicy, QLabel,
    QMessageBox, QDialog, QFormLayout, QLineEdit
)

from booking_app.ui.pages.booking_shared import (
    lbl, card_style, h_sep,
    C_RED, C_RED2, C_DARK, C_WHITE, C_BG,
    C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY,
    C_GREEN, C_ORANGE, C_BLUE
)

from shared.services.booking_service import get_booking_history_by_user
from shared.services.account_service import get_is_activated, update_account


# ─────────────────────────────────────────────────────────────────────────────
# 1. AVATAR WIDGET — Hình tròn icon người dùng nền đỏ gradient
# ─────────────────────────────────────────────────────────────────────────────
class AvatarWidget(QWidget):
    def __init__(self, size: int = 120, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Nền gradient đỏ bo tròn (bo góc lớn như ảnh)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor("#FF5252"))
        grad.setColorAt(1, QColor("#C62828"))

        r = w * 0.30          # border-radius ≈ 30% → bo góc mạnh
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, r, r)
        p.fillPath(path, QBrush(grad))

        # Icon người (vòng tròn đầu + thân hình bán cầu)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(C_WHITE)))

        head_r = w * 0.17
        head_cx = w / 2
        head_cy = h * 0.37
        p.drawEllipse(
            int(head_cx - head_r), int(head_cy - head_r),
            int(head_r * 2),       int(head_r * 2)
        )

        # Thân (nửa ellipse dưới)
        body_w = w * 0.52
        body_h = h * 0.28
        body_x = (w - body_w) / 2
        body_y = h * 0.60
        body_path = QPainterPath()
        body_path.moveTo(body_x, body_y + body_h)
        body_path.arcTo(body_x, body_y, body_w, body_h * 2, 0, 180)
        body_path.closeSubpath()
        p.fillPath(body_path, QBrush(QColor(C_WHITE)))


# ─────────────────────────────────────────────────────────────────────────────
# 2. PROFILE CARD — Card trái: avatar + tên + email + tier
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
# 2. PROFILE CARD — Card trái: avatar + tên + email + tier
# ─────────────────────────────────────────────────────────────────────────────
class ProfileCard(QWidget):
    def __init__(self, account: dict, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.setStyleSheet(
            f"background:{C_WHITE}; border:1px solid {C_BORDER}; border-radius:20px;"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 36, 28, 36)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignHCenter)

        self.avatar = AvatarWidget(size=110)
        lay.addWidget(self.avatar, 0, Qt.AlignHCenter)
        lay.addSpacing(20)

        # Tên
        name = account.get("full_name") or account.get("username") or "Khách"
        self.name_lbl = lbl(name.upper(), 20, 800, C_TEXT)
        self.name_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.name_lbl)
        lay.addSpacing(6)

        # Email
        email = account.get("email", "---")
        self.email_lbl = lbl(email, 13, 400, C_GRAY)
        self.email_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.email_lbl)
        lay.addSpacing(24)

        # Tier badge
        tier = account.get("tier", "KHÁCH VÃNG LAI").upper()
        self.tier_lbl = lbl(tier, 11, 800, C_BLUE, spacing=1.0)
        self.tier_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.tier_lbl)

    def update_info(self, account: dict):
        """Hàm cập nhật thông tin hiển thị trên Card"""
        name = account.get("full_name") or account.get("username") or "Khách"
        self.name_lbl.setText(name.upper())
        self.email_lbl.setText(account.get("email", "---"))
        self.tier_lbl.setText(account.get("tier", "KHÁCH VÃNG LAI").upper())


# ─────────────────────────────────────────────────────────────────────────────
# 3. STAT CARD — Card nhỏ: Tổng chi tiêu / Số chuyến bay
# ─────────────────────────────────────────────────────────────────────────────
class StatCard(QWidget):
    def __init__(self, label: str, value: str, color: str = C_TEXT, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(16))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(106)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 18, 24, 18)
        lay.setSpacing(8)

        lbl_w = lbl(label.upper(), 11, 600, C_GRAY, spacing=0.8)
        lay.addWidget(lbl_w)

        # Thêm biến color vào val_w
        val_w = lbl(value, 30, 800, color)
        lay.addWidget(val_w)


# ─────────────────────────────────────────────────────────────────────────────
# 4. ACCOUNT INFO CARD — Card tối: thông tin tài khoản dạng rows
# ─────────────────────────────────────────────────────────────────────────────
class AccountInfoCard(QWidget):
    def __init__(self, account: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background:{C_DARK}; border-radius:20px;"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 26, 28, 26)
        lay.setSpacing(0)

        title = lbl("Thông tin Tài khoản", 17, 700, C_WHITE)
        lay.addWidget(title)
        lay.addSpacing(24)

        # Tính các giá trị hiển thị
        passport = account.get("passport_number") or "---"
        phone    = account.get("phone") or "---"
        provider = account.get("provider", "MOCK AUTH").upper()

        uid_raw = account.get("account_id") or account.get("user_id") or ""
        if uid_raw:
            uid_str = str(uid_raw)
            uid = f"user-{uid_str[:5]}..." if len(uid_str) > 5 else f"user-{uid_str}"
        else:
            uid = "user----"

        joined = account.get("created_at", "")
        if joined:
            try:
                dt = datetime.strptime(str(joined)[:10], "%Y-%m-%d")
                joined = dt.strftime("%d/%m/%Y")
            except Exception:
                joined = str(joined)[:10]
        else:
            joined = "---"

        rows = [
            ("HỘ CHIẾU",      passport),
            ("ĐIỆN THOẠI",    phone),
            ("PROVIDER",      provider),
            ("USER ID",       uid),
            ("NGÀY GIA NHẬP", joined),
        ]

        for i, (key, val) in enumerate(rows):
            row_lay = QHBoxLayout()
            row_lay.setContentsMargins(0, 0, 0, 0)
            row_lay.setSpacing(8)

            key_lbl = lbl(key, 12, 600, "#8888AA", spacing=0.5)
            val_lbl = lbl(str(val), 13, 600, C_WHITE)
            val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            row_lay.addWidget(key_lbl)
            row_lay.addStretch()
            row_lay.addWidget(val_lbl)
            lay.addLayout(row_lay)

            if i < len(rows) - 1:
                lay.addSpacing(12)
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet("background:rgba(255,255,255,0.07); border:none;")
                sep.setFixedHeight(1)
                lay.addWidget(sep)
                lay.addSpacing(12)


# ─────────────────────────────────────────────────────────────────────────────
# DIALOG CHỈNH SỬA THÔNG TIN
# ─────────────────────────────────────────────────────────────────────────────
class EditProfileDialog(QDialog):
    def __init__(self, account, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chỉnh sửa thông tin")
        self.setFixedSize(350, 200)
        self.setStyleSheet(f"background: {C_WHITE}; color: {C_TEXT};")
        
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        input_style = f"border: 1px solid {C_BORDER}; border-radius: 6px; padding: 8px; font-size: 13px;"
        
        # Lấy dữ liệu cũ (Xử lý cả 2 trường hợp biến là Dictionary hoặc Object)
        if isinstance(account, dict):
            old_name = account.get("full_name", "")
            old_phone = account.get("phone", "")
        else:
            old_name = getattr(account, "full_name", "")
            old_phone = getattr(account, "phone", "")

        self.name_input = QLineEdit(old_name)
        self.name_input.setStyleSheet(input_style)
        self.phone_input = QLineEdit(old_phone)
        self.phone_input.setStyleSheet(input_style)
        
        layout.addRow(lbl("Họ và tên:", 13, 600), self.name_input)
        layout.addRow(lbl("Số điện thoại:", 13, 600), self.phone_input)
        
        save_btn = QPushButton("Lưu thay đổi")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet(f"background: {C_RED}; color: {C_WHITE}; border: none; border-radius: 8px; padding: 10px; font-weight: bold; margin-top: 10px;")
        save_btn.clicked.connect(self.accept)
        layout.addRow(save_btn)


# ─────────────────────────────────────────────────────────────────────────────
# 5. INFORMATION PAGE (Main)
# ─────────────────────────────────────────────────────────────────────────────
class InformationPage(QWidget):
    activate_member_clicked = Signal()

    def __init__(self, account: dict | None = None, parent=None):
        super().__init__(parent)
        self.account = account or {}
        self.setStyleSheet(f"background:{C_BG};")
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)
        self._build_ui()

    # ── Public API ────────────────────────────────────────────────────────────
    def update_account(self, account: dict):
        if account: self.account = account
        
        username = getattr(self.account, "username", None) or (self.account.get("username") if isinstance(self.account, dict) else "")
        
        # FETCH LIVE BALANCE
        acc_balance = 0.0
        try:
            from shared.services.account_service import connect_db
            conn = connect_db()
            c = conn.cursor()
            c.execute("SELECT balance FROM accounts WHERE username=?", (username,))
            res = c.fetchone()
            if res: acc_balance = res[0]
            conn.close()
        except: pass

        # 1. Update Profile Card Trái
        acc_dict = self.account if isinstance(self.account, dict) else self.account.__dict__
        if hasattr(self, 'profile_card'):
            self.profile_card.update_info(acc_dict)

        # 2. Update Các ô thống kê Phải
        history = get_booking_history_by_user(username)
        acc_spent = sum(r.get("total_amount", 0) for r in history if r.get("booking_status") != "Cancelled")
        acc_flights = len(history)

        if hasattr(self, 'stats_layout'):
            # Xóa các ô cũ
            for i in reversed(range(self.stats_layout.count())):
                widget = self.stats_layout.itemAt(i).widget()
                if widget: widget.deleteLater()

            # Thêm 3 ô mới với class StatCard chuẩn
            self.stats_layout.addWidget(StatCard("TỔNG CHI TIÊU", f"${acc_spent:,.0f}", C_GREEN))
            self.stats_layout.addWidget(StatCard("SỐ DƯ VÍ", f"${acc_balance:,.2f}", C_ORANGE))
            self.stats_layout.addWidget(StatCard("CHUYẾN BAY", f"{acc_flights}", C_BLUE))

    # ── Private ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent; border:none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._root_layout.addWidget(scroll, 1)

        container = QWidget()
        container.setStyleSheet(f"background:{C_BG};")
        scroll.setWidget(container)

        lay = QVBoxLayout(container)
        lay.setContentsMargins(40, 36, 40, 40)
        lay.setSpacing(20)

        username = self.account.get("username", "")
        try:
            history = get_booking_history_by_user(username)
            paid_statuses = {"paid", "confirmed"}
            total_spent   = sum(
                row.get("total_amount", 0) or 0
                for row in history
                if str(row.get("status", "")).lower() in paid_statuses
            )
            total_flights = len({
                row.get("booking_reference", "").split("-")[0]
                for row in history
                if str(row.get("status", "")).lower() in paid_statuses
                and row.get("booking_reference")
            })
        except Exception:
            total_spent   = self.account.get("total_spent", 0)
            total_flights = self.account.get("total_flights", 0)

        try:
            is_activated = get_is_activated(username)
        except Exception:
            is_activated = self.account.get("is_activated", 0)

        body = QHBoxLayout()
        body.setSpacing(28)
        body.setAlignment(Qt.AlignTop)

        # Cột trái (Gán biến self.profile_card)
        self.profile_card = ProfileCard(self.account)
        body.addWidget(self.profile_card, 0, Qt.AlignTop)

        # Cột phải
        right_col = QVBoxLayout()
        right_col.setSpacing(16)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        page_title = lbl("Hồ sơ cá nhân", 18, 700, C_TEXT)
        header_row.addWidget(page_title)
        header_row.addStretch()

        edit_btn = QPushButton("Chỉnh sửa thông tin ✏️")
        edit_btn.setFixedHeight(38)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C_WHITE}; color: {C_TEXT}; border: 1.5px solid {C_BORDER};
                border-radius: 10px; font-size: 13px; font-weight: 600; padding: 0 16px;
            }}
            QPushButton:hover {{ background: {C_BG}; border-color: {C_RED}; color: {C_RED}; }}
            QPushButton:pressed {{ background: #FFEBEE; }}
        """)
        edit_btn.clicked.connect(self._on_edit_clicked)
        header_row.addWidget(edit_btn)
        right_col.addLayout(header_row)

        # Stats row (Gán biến self.stats_layout)
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(16)

        spent_str   = f"${total_spent:,.0f}" if total_spent else "$0"
        flights_str = str(total_flights) if total_flights else "0"

        self.stats_layout.addWidget(StatCard("Tổng Chi Tiêu", spent_str, C_GREEN))
        self.stats_layout.addWidget(StatCard("Chuyến Bay", flights_str, C_BLUE))
        right_col.addLayout(self.stats_layout)

        info_card = AccountInfoCard(self.account)
        right_col.addWidget(info_card)

        if not is_activated:
            activate_btn = QPushButton("KÍCH HOẠT QUYỀN LỢI HỘI VIÊN")
            activate_btn.setFixedHeight(54)
            activate_btn.setCursor(Qt.PointingHandCursor)
            activate_btn.setStyleSheet(f"""
                QPushButton {{ background: {C_RED}; color: {C_WHITE}; border: none; border-radius: 27px; font-size: 14px; font-weight: 800; }}
                QPushButton:hover {{ background: {C_RED2}; }}
                QPushButton:pressed {{ background: #B71C1C; }}
            """)
            activate_btn.clicked.connect(self.activate_member_clicked.emit)
            right_col.addWidget(activate_btn)

        right_widget = QWidget()
        right_widget.setStyleSheet("background:transparent;")
        right_widget.setLayout(right_col)
        body.addWidget(right_widget, 1)

        lay.addLayout(body)
        lay.addStretch()
        
        # Mở lên là fetch data luôn cho 3 ô khớp
        self.update_account(self.account)

    def _on_edit_clicked(self):
        dialog = EditProfileDialog(self.account, self)
        if dialog.exec() == QDialog.Accepted:
            new_name = dialog.name_input.text()
            new_phone = dialog.phone_input.text()
            
            if isinstance(self.account, dict):
                acc_id = self.account.get("account_id") or self.account.get("user_id")
                self.account["full_name"] = new_name
                self.account["phone"] = new_phone
            else:
                acc_id = getattr(self.account, "account_id", None) or getattr(self.account, "user_id", None)
                self.account.full_name = new_name
                self.account.phone = new_phone
                
            if acc_id:
                try:
                    from shared.services.account_service import update_account
                    update_account(account_id=acc_id, full_name=new_name, phone=new_phone)
                except Exception as e:
                    print(f"Lỗi cập nhật DB: {e}")

            self.update_account(self.account)
            QMessageBox.information(self, "Thành công", "Cập nhật thông tin thành công!")

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    MOCK_ACCOUNT = {
        "account_id":      "hi2f9a",
        "full_name":       "a",
        "username":        "a",
        "email":           "a@gmail.com",
    }
    from PySide6.QtWidgets import QMainWindow
    win = QMainWindow()
    win.setWindowTitle("Information Page — Test")
    win.resize(1200, 800)
    page = InformationPage(account=MOCK_ACCOUNT)
    win.setCentralWidget(page)
    win.show()
    sys.exit(app.exec())