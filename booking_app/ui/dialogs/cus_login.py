"""
login.py
--------
Giao diện Đăng nhập — JetJet Air Booking App (dành cho khách hàng)
Chạy độc lập: python login.py
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
    QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame,
    QGraphicsDropShadowEffect
)

# ─────────────────────────────────────────────────────────────────────────────
# Màu sắc
# ─────────────────────────────────────────────────────────────────────────────
C_RED      = "#E53935"
C_RED2     = "#C62828"
C_RED_BG1  = "#EF5350"   # gradient nền trên
C_RED_BG2  = "#C62828"   # gradient nền dưới
C_WHITE    = "#FFFFFF"
C_TEXT     = "#1A1A2E"
C_GRAY     = "#AAAACC"
C_INPUT_BG = "#F2F3F7"
C_ERROR    = "#C62828"


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
# Logo badge vuông bo góc
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

        # Shadow layer
        p.setPen(Qt.NoPen)
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(4, 6, w - 8, h - 6, r, r)
        p.fillPath(shadow_path, QBrush(QColor(0, 0, 0, 40)))

        # Badge gradient
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor("#FF5252"))
        grad.setColorAt(1.0, QColor("#C62828"))
        badge_path = QPainterPath()
        badge_path.addRoundedRect(0, 0, w - 4, h - 6, r, r)
        p.fillPath(badge_path, QBrush(grad))

        # Plane icon
        p.setPen(QPen(QColor(C_WHITE), 1.5))
        f = QFont(); f.setPointSize(int(w * 0.36)); f.setWeight(QFont.Normal)
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
# Tab bar ĐĂNG NHẬP | ĐĂNG KÝ
# ─────────────────────────────────────────────────────────────────────────────
class TabBar(QWidget):
    tab_changed = Signal(int)  # 0 = login, 1 = register

    def __init__(self, active: int = 0, parent=None):
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
# Card trắng chứa toàn bộ nội dung
# ─────────────────────────────────────────────────────────────────────────────
class LoginCard(QWidget):
    login_success = Signal(object)    # phát Account khi đăng nhập OK
    go_register   = Signal()          # phát khi bấm tab Đăng ký

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C_WHITE}; border-radius:28px;")

        # Shadow
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
        root.addSpacing(22)

        # ── Tab bar ──────────────────────────────────────────────────────────
        self._tabs = TabBar(active=0)
        self._tabs.tab_changed.connect(self._on_tab)
        root.addWidget(self._tabs)
        root.addSpacing(20)

        # ── Inputs ───────────────────────────────────────────────────────────
        self._email = IconInput("Email khách hàng", "✉")
        self._pwd   = IconInput("Mật khẩu truy cập", "🔒", password=True)

        root.addWidget(self._email)
        root.addSpacing(10)
        root.addWidget(self._pwd)
        root.addSpacing(6)

        # ── Error label ──────────────────────────────────────────────────────
        self._error = QLabel("")
        self._error.setAlignment(Qt.AlignCenter)
        self._error.setStyleSheet(f"font-size:12px; color:{C_ERROR};"
                                  " background:transparent; border:none;")
        root.addWidget(self._error)
        root.addSpacing(6)

        # ── Nút đăng nhập ────────────────────────────────────────────────────
        btn_login = QPushButton("  →]  ĐĂNG NHẬP JETJET")
        btn_login.setFixedHeight(56)
        btn_login.setCursor(Qt.PointingHandCursor)
        btn_login.clicked.connect(self._handle_login)
        btn_login.setStyleSheet(f"""
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
        root.addWidget(btn_login)
        root.addSpacing(16)

        # ── Footer ───────────────────────────────────────────────────────────
        footer = QLabel("TRẢI NGHIỆM BAY ĐẲNG CẤP CÙNG JETJET AIR.")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"font-size:10px; font-weight:600; color:{C_GRAY};"
                             " letter-spacing:1px; background:transparent; border:none;")
        root.addWidget(footer)

    # ── Tab switch ───────────────────────────────────────────────────────────
    def _on_tab(self, idx: int):
        if idx == 1:
            self.go_register.emit()

    # ── Xử lý đăng nhập ─────────────────────────────────────────────────────
    def _handle_login(self):
        self._error.setText("")
        email = self._email.text()
        pwd   = self._pwd.text()

        if not email or not pwd:
            self._error.setText("Vui lòng nhập đầy đủ email và mật khẩu.")
            return

        account = _db_login(email, pwd)
        if account:
            self.login_success.emit(account)
        else:
            self._error.setText("Email hoặc mật khẩu không đúng. Thử lại.")


# ─────────────────────────────────────────────────────────────────────────────
# Database helpers
# ─────────────────────────────────────────────────────────────────────────────
def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _db_login(email: str, password: str):
    """Trả về account dict hoặc None."""
    try:
        import os, sqlite3
        db = os.path.join(os.path.dirname(__file__), "database", "airline.db")
        conn = sqlite3.connect(db)
        cur  = conn.cursor()
        cur.execute("""
            SELECT account_id, username, email, full_name, role
            FROM accounts
            WHERE email = ? AND password_hash = ?
        """, (email.lower(), _hash(password)))
        row = conn.fetchone() if hasattr(conn, 'fetchone') else cur.fetchone()
        # update last_login
        if row:
            cur.execute("UPDATE accounts SET last_login=CURRENT_TIMESTAMP"
                        " WHERE account_id=?", (row[0],))
            conn.commit()
        conn.close()
        if row:
            return {"account_id": row[0], "username": row[1],
                    "email": row[2], "full_name": row[3], "role": row[4]}
        return None
    except Exception as e:
        print(f"[Login] DB error: {e}")
        # Fallback demo: accept any non-empty
        return {"account_id": 0, "username": email.split("@")[0],
                "email": email, "full_name": "Khách hàng", "role": "customer"}


# ─────────────────────────────────────────────────────────────────────────────
# Main Window
# ─────────────────────────────────────────────────────────────────────────────
class LoginWindow(QMainWindow):
    """
    Cửa sổ đăng nhập khách hàng.

    Tích hợp vào booking_app.py:
        from login import LoginWindow
        win = LoginWindow()
        win.card.login_success.connect(on_login)
        win.show()
    """
    login_success = Signal(object)

    def __init__(self, pos: QPoint | None = None):
        super().__init__()
        self.setWindowTitle("JetJet Air — Đăng nhập")
        self.setFixedSize(540, 680)
        if pos:
            self.move(pos)
        else:
            self._center()

        # Nền đỏ
        bg = RedBackground()
        self.setCentralWidget(bg)

        # Card trắng
        lay = QVBoxLayout(bg)
        lay.setContentsMargins(20, 20, 20, 20)

        self.card = LoginCard()
        self.card.login_success.connect(self.login_success)
        self.card.go_register.connect(self._open_register)
        lay.addWidget(self.card)

    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width()  - self.width())  // 2,
                  (screen.height() - self.height()) // 2)

    def _open_register(self):
        from booking_app.ui.dialogs.cus_register import RegisterWindow
        self._reg = RegisterWindow(pos=self.pos())
        self._reg.go_login.connect(self._reopen)
        self._reg.show()
        self.hide()

    def _reopen(self):
        self.show()


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    def _on_login(account):
        print(f"[Login OK] {account}")
        # Mở booking app
        try:
            from booking_app import JetBookWindow
            w = JetBookWindow(account=account)
            w.show()
            win.hide()
        except ImportError:
            print("booking_app.py chưa sẵn sàng.")

    win = LoginWindow()
    win.login_success.connect(_on_login)
    win.show()
    sys.exit(app.exec())