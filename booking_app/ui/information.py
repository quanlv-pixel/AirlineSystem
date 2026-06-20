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
# 4. ACCOUNT INFO CARD — Giao diện mới (Nền sáng, chữ màu, rút gọn thông tin)
# ─────────────────────────────────────────────────────────────────────────────
class AccountInfoCard(QWidget):
    def __init__(self, account: dict, parent=None):
        super().__init__(parent)
        # Đổi nền thành trắng, viền xám để sáng sủa và dễ nhìn hơn
        self.setStyleSheet(
            f"background:{C_WHITE}; border: 1px solid {C_BORDER}; border-radius:20px;"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 26, 28, 26)
        lay.setSpacing(0)

        # Tiêu đề màu Đỏ nổi bật
        title = lbl("Thông tin Tài khoản", 17, 800, C_RED)
        lay.addWidget(title)
        lay.addSpacing(24)

        passport = account.get("passport_number") or "---"
        phone    = account.get("phone") or "---"

        # Label chứa giá trị (Màu đen/xanh đậm)
        self.passport_lbl = lbl(str(passport), 13, 700, C_TEXT)
        self.phone_lbl = lbl(str(phone), 13, 700, C_TEXT)
        self.passport_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.phone_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        rows = [
            ("HỘ CHIẾU", self.passport_lbl),
            ("ĐIỆN THOẠI", self.phone_lbl),
        ]

        for i, (key, val_widget) in enumerate(rows):
            row_lay = QHBoxLayout()
            row_lay.setContentsMargins(0, 0, 0, 0)
            row_lay.setSpacing(8)

            # Chữ tiêu đề mục (Màu xám đậm)
            key_lbl = lbl(key, 12, 600, C_MID, spacing=0.5)

            row_lay.addWidget(key_lbl)
            row_lay.addStretch()
            row_lay.addWidget(val_widget)
            lay.addLayout(row_lay)

            if i < len(rows) - 1:
                lay.addSpacing(14)
                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet(f"background:{C_BORDER}; border:none;")
                sep.setFixedHeight(1)
                lay.addWidget(sep)
                lay.addSpacing(14)

    def update_info(self, account: dict):
        """Cập nhật lại text khi lưu chỉnh sửa"""
        self.passport_lbl.setText(str(account.get("passport_number") or "---"))
        self.phone_lbl.setText(str(account.get("phone") or "---"))

# ─────────────────────────────────────────────────────────────────────────────
# DIALOG CHỈNH SỬA THÔNG TIN - Thêm ô Hộ chiếu
# ─────────────────────────────────────────────────────────────────────────────
class EditProfileDialog(QDialog):
    def __init__(self, account, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chỉnh sửa thông tin")
        self.setFixedSize(350, 260)  # Tăng chiều cao để chứa thêm ô Hộ chiếu
        self.setStyleSheet(f"background: {C_WHITE}; color: {C_TEXT};")
        
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        input_style = f"border: 1px solid {C_BORDER}; border-radius: 6px; padding: 8px; font-size: 13px;"
        
        if isinstance(account, dict):
            old_name = account.get("full_name", "")
            old_phone = account.get("phone", "")
            old_passport = account.get("passport_number", "")
        else:
            old_name = getattr(account, "full_name", "")
            old_phone = getattr(account, "phone", "")
            old_passport = getattr(account, "passport_number", "")

        self.name_input = QLineEdit(old_name)
        self.name_input.setStyleSheet(input_style)
        self.phone_input = QLineEdit(old_phone)
        self.phone_input.setStyleSheet(input_style)
        self.passport_input = QLineEdit(old_passport)
        self.passport_input.setStyleSheet(input_style)
        
        layout.addRow(lbl("Họ và tên:", 13, 600), self.name_input)
        layout.addRow(lbl("Số điện thoại:", 13, 600), self.phone_input)
        layout.addRow(lbl("Hộ chiếu:", 13, 600), self.passport_input)
        
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
        if hasattr(self, 'info_card'):
            self.info_card.update_info(acc_dict)

        # ── ĐÃ FIX: Lọc chính xác trạng thái và cộng tiền chuẩn ──
        history = get_booking_history_by_user(username)
        
        unique_pnrs = set()
        acc_spent = 0
        for r in history:
            # Sửa lỗi lấy nhầm key 'booking_status', hỗ trợ đọc cả 2 phòng hờ
            status = str(r.get("status", r.get("booking_status", ""))).lower()
            
            # Lọc toàn bộ các từ khóa báo hiệu đã hủy
            if status not in ["cancelled", "canceled", "đã hủy", "đã hủy vé"]:
                pnr_base = str(r.get("booking_reference", r.get("pnr", ""))).split("-")[0]
                unique_pnrs.add(pnr_base)
                # Cộng tất cả tiền của mọi vé (không bị sót khi 1 chuyến đặt nhiều ghế)
                acc_spent += float(r.get("total_amount", 0))
                
        acc_flights = len(unique_pnrs)

        if hasattr(self, 'stats_layout'):
            # Xóa các ô cũ
            for i in reversed(range(self.stats_layout.count())):
                widget = self.stats_layout.itemAt(i).widget()
                if widget: widget.deleteLater()

            # Thêm 3 ô mới
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
            is_activated = get_is_activated(username)
        except Exception:
            is_activated = self.account.get("is_activated", 0)

        body = QHBoxLayout()
        body.setSpacing(28)
        body.setAlignment(Qt.AlignTop)

        # Cột trái
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

        # Tạm thời tạo layout rỗng, hàm update_account phía dưới sẽ tự động tính toán và vẽ lại cho chuẩn
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(16)
        right_col.addLayout(self.stats_layout)

        self.info_card = AccountInfoCard(self.account)
        right_col.addWidget(self.info_card)

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
        
        # Mở trang lên là hệ thống tự động chốt sổ sách (Cập nhật Data luôn)
        self.update_account(self.account)

    def _on_edit_clicked(self):
        dialog = EditProfileDialog(self.account, self)
        if dialog.exec() == QDialog.Accepted:
            new_name = dialog.name_input.text()
            new_phone = dialog.phone_input.text()
            new_passport = dialog.passport_input.text() 
            
            if isinstance(self.account, dict):
                acc_id = self.account.get("account_id") or self.account.get("user_id")
                self.account["full_name"] = new_name
                self.account["phone"] = new_phone
                self.account["passport_number"] = new_passport
            else:
                acc_id = getattr(self.account, "account_id", None) or getattr(self.account, "user_id", None)
                self.account.full_name = new_name
                self.account.phone = new_phone
                self.account.passport_number = new_passport
                
            if acc_id:
                try:
                    from shared.services.account_service import update_account, connect_db
                    update_account(account_id=acc_id, full_name=new_name, phone=new_phone)
                    
                    # Tự động cập nhật Hộ chiếu vào Database
                    conn = connect_db()
                    c = conn.cursor()
                    try:
                        c.execute("ALTER TABLE accounts ADD COLUMN passport_number TEXT")
                        conn.commit()
                    except Exception:
                        pass 
                        
                    c.execute("UPDATE accounts SET passport_number = ? WHERE account_id = ?", (new_passport, acc_id))
                    conn.commit()
                    conn.close()
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