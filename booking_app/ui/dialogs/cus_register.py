"""
register.py
-----------
Giao diện Đăng ký — JetJet Air Booking App (dành cho khách hàng)
Chạy độc lập: python register.py
"""
from __future__ import annotations
import hashlib
import sys

from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import (
    QColor, QFont, QPainter, QBrush, QPen,
    QPainterPath, QLinearGradient
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QGraphicsDropShadowEffect
)

# ─────────────────────────────────────────────────────────────────────────────
# Màu sắc (giữ nhất quán với login.py)
# ─────────────────────────────────────────────────────────────────────────────
C_RED      = "#E53935"
C_RED2     = "#C62828"
C_RED_BG1  = "#EF5350"
C_RED_BG2  = "#C62828"
C_WHITE    = "#FFFFFF"
C_TEXT     = "#1A1A2E"
C_GRAY     = "#AAAACC"
C_INPUT_BG = "#F2F3F7"
C_ERROR    = "#C62828"
C_SUCCESS  = "#22C55E"


# ─────────────────────────────────────────────────────────────────────────────
# Nền gradient đỏ
# ─────────────────────────────────────────────────────────────────────────────
class RedBackground(QWidget):
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0, QColor(C_RED_BG1))
        grad.setColorAt(1.0, QColor(C_RED_BG2))
        p.fillRect(self.rect(), QBrush(grad))


# ─────────────────────────────────────────────────────────────────────────────
# Logo badge (giống login.py)
# ─────────────────────────────────────────────────────────────────────────────
class LogoBadge(QWidget):
    def __init__(self, size: int = 76, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        r = w * 0.28

        # Shadow
        p.setPen(Qt.NoPen)
        sh_path = QPainterPath()
        sh_path.addRoundedRect(4, 6, w - 8, h - 6, r, r)
        p.fillPath(sh_path, QBrush(QColor(0, 0, 0, 40)))

        # Badge gradient
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor("#FF5252"))
        grad.setColorAt(1.0, QColor("#C62828"))
        badge = QPainterPath()
        badge.addRoundedRect(0, 0, w - 4, h - 6, r, r)
        p.fillPath(badge, QBrush(grad))

        # Icon
        p.setPen(QPen(QColor(C_WHITE), 1.5))
        f = QFont(); f.setPointSize(int(w * 0.36))
        p.setFont(f)
        p.drawText(0, 0, w - 4, h - 6, Qt.AlignCenter, "✈")


# ─────────────────────────────────────────────────────────────────────────────
# Input với icon
# ─────────────────────────────────────────────────────────────────────────────
class IconInput(QWidget):
    def __init__(self, placeholder: str, icon: str,
                 password: bool = False, parent=None):
        super().__init__(parent)
        self.setFixedHeight(54)
        self.setStyleSheet(f"""
            IconInput {{
                background: {C_INPUT_BG};
                border-radius: 14px;
                border: none;
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        ic = QLabel(icon)
        ic.setFixedWidth(22)
        ic.setAlignment(Qt.AlignCenter)
        ic.setStyleSheet(f"font-size:17px; color:{C_GRAY};"
                         " background:transparent; border:none;")

        self.field = QLineEdit()
        self.field.setPlaceholderText(placeholder)
        self.field.setFrame(False)
        self.field.setStyleSheet(f"""
            QLineEdit {{
                background: transparent; border: none;
                font-size: 14px; color: {C_TEXT};
            }}
        """)
        if password:
            self.field.setEchoMode(QLineEdit.Password)

        lay.addWidget(ic)
        lay.addWidget(self.field)

    def text(self) -> str:
        return self.field.text().strip()

    def clear(self):
        self.field.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Tab bar ĐĂNG NHẬP | ĐĂNG KÝ  (active = 1)
# ─────────────────────────────────────────────────────────────────────────────
class TabBar(QWidget):
    tab_changed = Signal(int)

    def __init__(self, active: int = 1, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)
        self.setStyleSheet(f"""
            TabBar {{
                background: {C_INPUT_BG};
                border-radius: 14px;
                border: none;
            }}
        """)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(5, 5, 5, 5)
        lay.setSpacing(4)

        self._btn0 = QPushButton("ĐĂNG NHẬP")
        self._btn1 = QPushButton("ĐĂNG KÝ")

        for i, btn in enumerate((self._btn0, self._btn1)):
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self.tab_changed.emit(idx))
            lay.addWidget(btn)

        self._set_active(active)

    def _set_active(self, idx: int):
        on  = f"""QPushButton {{
                    background: {C_WHITE}; border: none; border-radius: 10px;
                    font-size: 12px; font-weight: 700; color: {C_TEXT};
                    letter-spacing: 1px;
                }}"""
        off = f"""QPushButton {{
                    background: transparent; border: none; border-radius: 10px;
                    font-size: 12px; font-weight: 600; color: {C_GRAY};
                    letter-spacing: 1px;
                }}
                QPushButton:hover {{ color: {C_TEXT}; }}"""
        self._btn0.setStyleSheet(on  if idx == 0 else off)
        self._btn1.setStyleSheet(on  if idx == 1 else off)


# ─────────────────────────────────────────────────────────────────────────────
# Register Card
# ─────────────────────────────────────────────────────────────────────────────
class RegisterCard(QWidget):
    register_success = Signal(object)  # phát account sau khi đăng ký OK
    go_login         = Signal()        # phát khi bấm tab Đăng nhập

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C_WHITE}; border-radius:28px;")

        sh = QGraphicsDropShadowEffect(self)
        sh.setBlurRadius(50); sh.setXOffset(0); sh.setYOffset(12)
        sh.setColor(QColor(0, 0, 0, 55))
        self.setGraphicsEffect(sh)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(0)

        # ── Back button ──────────────────────────────────────────────────────
        back = QPushButton("<")
        back.setFixedSize(34, 34)
        back.setCursor(Qt.PointingHandCursor)
        back.clicked.connect(lambda: QApplication.quit())
        back.setStyleSheet(f"""
            QPushButton {{
                background: {C_INPUT_BG}; border: none; border-radius: 17px;
                font-size: 14px; font-weight: 700; color: {C_GRAY};
            }}
            QPushButton:hover {{ background: #E0E1EC; }}
        """)
        back_row = QHBoxLayout()
        back_row.addWidget(back)
        back_row.addStretch()
        root.addLayout(back_row)
        root.addSpacing(8)

        # ── Logo ─────────────────────────────────────────────────────────────
        logo_row = QHBoxLayout()
        logo_row.setAlignment(Qt.AlignCenter)
        logo_row.addWidget(LogoBadge(76))
        root.addLayout(logo_row)
        root.addSpacing(16)

        # ── Tiêu đề ──────────────────────────────────────────────────────────
        title = QLabel()
        title.setTextFormat(Qt.RichText)
        title.setText(
            "<span style='font-size:30px; font-weight:900; color:#1A1A2E;'>JETJET</span>"
            "<span style='font-size:30px; font-weight:400; color:#1A1A2E;'> AIR</span>"
        )
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("background:transparent; border:none;")
        root.addWidget(title)
        root.addSpacing(6)

        sub = QLabel("DÀNH CHO KHÁCH HÀNG")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(f"""
            font-size:10px; font-weight:700; color:{C_RED};
            letter-spacing:2.5px; background:transparent; border:none;
        """)
        root.addWidget(sub)
        root.addSpacing(20)

        # ── Tab bar (active = ĐĂNG KÝ) ───────────────────────────────────────
        tabs = TabBar(active=1)
        tabs.tab_changed.connect(self._on_tab)
        root.addWidget(tabs)
        root.addSpacing(18)

        # ── Inputs ───────────────────────────────────────────────────────────
        self._name  = IconInput("Họ và tên khách hàng", "◎")
        self._email = IconInput("Email khách hàng",      "✉")
        self._pwd   = IconInput("Mật khẩu truy cập",    "🔒", password=True)

        root.addWidget(self._name)
        root.addSpacing(10)
        root.addWidget(self._email)
        root.addSpacing(10)
        root.addWidget(self._pwd)
        root.addSpacing(6)

        # ── Thông báo ────────────────────────────────────────────────────────
        self._msg = QLabel("")
        self._msg.setAlignment(Qt.AlignCenter)
        self._msg.setWordWrap(True)
        self._msg.setStyleSheet(f"font-size:12px; color:{C_ERROR};"
                                " background:transparent; border:none;")
        root.addWidget(self._msg)
        root.addSpacing(6)

        # ── Nút đăng ký ──────────────────────────────────────────────────────
        btn_reg = QPushButton("  →]  TẠO TÀI KHOẢN JETJET")
        btn_reg.setFixedHeight(56)
        btn_reg.setCursor(Qt.PointingHandCursor)
        btn_reg.clicked.connect(self._handle_register)
        btn_reg.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C_RED}, stop:1 #FF5252);
                border: none; border-radius: 28px;
                font-size: 14px; font-weight: 800; color: {C_WHITE};
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C_RED2}, stop:1 {C_RED});
            }}
            QPushButton:pressed {{ background: {C_RED2}; }}
        """)
        root.addWidget(btn_reg)
        root.addSpacing(16)

        # ── Footer ───────────────────────────────────────────────────────────
        footer = QLabel("TRẢI NGHIỆM BAY ĐẲNG CẤP CÙNG JETJET AIR.")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"font-size:10px; font-weight:600; color:{C_GRAY};"
                             " letter-spacing:1px; background:transparent; border:none;")
        root.addWidget(footer)

    # ── Tab switch ───────────────────────────────────────────────────────────
    def _on_tab(self, idx: int):
        if idx == 0:
            self.go_login.emit()

    # ── Xử lý đăng ký ────────────────────────────────────────────────────────
    def _handle_register(self):
        self._msg.setStyleSheet(f"font-size:12px; color:{C_ERROR};"
                                " background:transparent; border:none;")
        name  = self._name.text()
        email = self._email.text()
        pwd   = self._pwd.text()

        # Validate
        if not name or not email or not pwd:
            self._msg.setText("Vui lòng điền đầy đủ tất cả các trường.")
            return
        if "@" not in email or "." not in email:
            self._msg.setText("Địa chỉ email không hợp lệ.")
            return
        if len(pwd) < 6:
            self._msg.setText("Mật khẩu phải có ít nhất 6 ký tự.")
            return

        ok, result = _db_register(name, email, pwd)
        if ok:
            self._msg.setStyleSheet(f"font-size:12px; color:{C_SUCCESS};"
                                    " background:transparent; border:none;")
            self._msg.setText("✅ Đăng ký thành công! Đang chuyển sang đăng nhập…")
            # Delay rồi chuyển về login
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1500, self.go_login.emit)
        else:
            self._msg.setText(result)


# ─────────────────────────────────────────────────────────────────────────────
# Database helpers
# ─────────────────────────────────────────────────────────────────────────────
def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _db_register(full_name: str, email: str,
                 password: str) -> tuple[bool, str]:
    """
    Tạo tài khoản mới với role='customer'.
    Trả về (True, account_dict) hoặc (False, error_message).
    """
    try:
        import os, sqlite3
        db = os.path.join(os.path.dirname(__file__), "database", "airline.db")
        conn = sqlite3.connect(db)
        cur  = conn.cursor()

        # Username = phần trước @ của email
        username = email.split("@")[0].lower().replace(".", "_")

        cur.execute("""
            INSERT INTO accounts
                (username, email, password_hash, full_name, role)
            VALUES (?, ?, ?, ?, 'customer')
        """, (username, email.lower(), _hash(password), full_name))

        account_id = cur.lastrowid
        conn.commit()
        conn.close()

        return True, {"account_id": account_id, "username": username,
                      "email": email, "full_name": full_name, "role": "customer"}

    except Exception as e:
        err = str(e)
        if "UNIQUE constraint failed: accounts.email" in err:
            return False, "Email này đã được đăng ký. Vui lòng dùng email khác."
        if "UNIQUE constraint failed: accounts.username" in err:
            return False, "Tên người dùng đã tồn tại. Vui lòng thử email khác."
        return False, f"Lỗi hệ thống: {err}"


# ─────────────────────────────────────────────────────────────────────────────
# Main Window
# ─────────────────────────────────────────────────────────────────────────────
class RegisterWindow(QMainWindow):
    """
    Cửa sổ đăng ký khách hàng.

    Tích hợp:
        from register import RegisterWindow
        win = RegisterWindow()
        win.card.register_success.connect(on_register)
        win.show()
    """
    go_login = Signal()

    def __init__(self, pos: QPoint | None = None):
        super().__init__()
        self.setWindowTitle("JetJet Air — Đăng ký")
        self.setFixedSize(540, 730)
        if pos:
            self.move(pos)
        else:
            self._center()

        # Nền đỏ
        bg = RedBackground()
        self.setCentralWidget(bg)

        lay = QVBoxLayout(bg)
        lay.setContentsMargins(20, 20, 20, 20)

        self.card = RegisterCard()
        self.card.go_login.connect(self._open_login)
        lay.addWidget(self.card)

    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width()  - self.width())  // 2,
                  (screen.height() - self.height()) // 2)

    def _open_login(self):
        from booking_app.ui.dialogs.cus_login import LoginWindow
        self._login_win = LoginWindow(pos=self.pos())
        self._login_win.login_success.connect(self._on_login_success)
        self._login_win.show()
        self.hide()
        self.go_login.emit()

    def _on_login_success(self, account):
        try:
            from booking_app import JetBookWindow
            w = JetBookWindow(account=account)
            w.show()
            self._login_win.hide()
            self.close()
        except ImportError:
            print(f"[Register→Login OK] {account}")


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = RegisterWindow()
    win.show()
    sys.exit(app.exec())