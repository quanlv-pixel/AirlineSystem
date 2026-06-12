import hashlib
import sys
import os
import sqlite3

from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import (
    QColor, QFont, QPainter, QBrush, QPen,
    QPainterPath, QLinearGradient
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QGraphicsDropShadowEffect, QFrame
)

# Style Constants
RED_PRIMARY = "#FF1632"
RED_GRADIENT = ["#FF1632", "#FF2942", "#FF4B5F"]
TEXT_DARK = "#1A1A2E"
INPUT_BG = "#F3F4F7"
WHITE = "#FFFFFF"

class GradientBackground(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(RED_GRADIENT[0]))
        gradient.setColorAt(0.5, QColor(RED_GRADIENT[1]))
        gradient.setColorAt(1, QColor(RED_GRADIENT[2]))
        painter.fillRect(self.rect(), QBrush(gradient))

class StyledInput(QLineEdit):
    def __init__(self, placeholder, password=False):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(54)
        if password:
            self.setEchoMode(QLineEdit.Password)
        self.setStyleSheet(f"""
            QLineEdit {{
                background: {INPUT_BG};
                border: 1px solid #ECECF1;
                border-radius: 12px;
                padding: 0 15px;
                color: {TEXT_DARK};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {RED_PRIMARY};
                background: {WHITE};
            }}
        """)

class LoginWindow(QMainWindow):
    # Đưa các signal ra đây để main.py có thể kết nối trực tiếp vào window
    login_success = Signal(object)
    go_register = Signal() 

    def __init__(self, pos=None):
        super().__init__()
        self.setWindowTitle("JetJet Air - Đăng nhập")
        self.setFixedSize(450, 620)
        if pos: self.move(pos)
        else: self._center()

        self.bg = GradientBackground()
        self.setCentralWidget(self.bg)

        layout = QVBoxLayout(self.bg)
        layout.setContentsMargins(40, 40, 40, 40)

        # Card (Bọc UI)
        self.card = QFrame()
        self.card.setStyleSheet(f"background: {WHITE}; border-radius: 24px;")
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(40)
        card_shadow.setColor(QColor(0, 0, 0, 60))
        card_shadow.setOffset(0, 10)
        self.card.setGraphicsEffect(card_shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 40, 30, 40)
        card_layout.setSpacing(15)

        logo = QLabel("✈")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(f"font-size: 48px; color: {RED_PRIMARY}; margin-bottom: 5px;")
        
        title = QLabel("JETJET AIR")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 26px; font-weight: 900; color: {TEXT_DARK}; letter-spacing: 1px;")

        subtitle = QLabel("Đăng nhập để đặt vé ngay")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #666; margin-bottom: 10px;")

        self.email_input = StyledInput("Email của bạn")
        self.pwd_input = StyledInput("Mật khẩu", password=True)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #E53935; font-size: 12px;")

        self.login_btn = QPushButton("ĐĂNG NHẬP")
        self.login_btn.setFixedHeight(54)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet(f"QPushButton {{ background: {RED_PRIMARY}; color: white; border-radius: 12px; font-weight: 800; font-size: 14px; margin-top: 10px; }} QPushButton:hover {{ background: #D32F2F; }}")
        self.login_btn.clicked.connect(self._handle_login)

        # Nút chuyển sang Đăng ký
        register_btn = QPushButton("Chưa có tài khoản? Đăng ký ngay")
        register_btn.setFixedHeight(40)
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: #666; font-weight: 700; font-size: 13px; border: none; }} QPushButton:hover {{ color: {RED_PRIMARY}; }}")
        register_btn.clicked.connect(lambda: self.go_register.emit())

        card_layout.addWidget(logo)
        card_layout.addWidget(title)
        card_layout.addWidget(subtitle)
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(self.pwd_input)
        card_layout.addWidget(self.error_label)
        card_layout.addWidget(self.login_btn)
        card_layout.addWidget(register_btn)

        layout.addWidget(self.card)

    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def _handle_login(self):
        # Immediately disable to block any double-click from re-emitting login_success
        self.login_btn.setEnabled(False)
        self.login_btn.setText("ĐANG XỬ LÝ...")

        email = self.email_input.text().strip()
        pwd = self.pwd_input.text().strip()
        if not email or not pwd:
            self.error_label.setText("Vui lòng nhập đầy đủ thông tin")
            self.login_btn.setEnabled(True)
            self.login_btn.setText("ĐĂNG NHẬP")
            return

        account = _db_login(email, pwd)
        if account:
            # Keep button disabled — window will close shortly after signal fires
            self.login_success.emit(account)
        else:
            self.error_label.setText("Email hoặc mật khẩu không chính xác")
            self.login_btn.setEnabled(True)
            self.login_btn.setText("ĐĂNG NHẬP")

def _hash(p): return hashlib.sha256(p.encode()).hexdigest()

def _get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    while not os.path.exists(os.path.join(project_root, 'database')) and project_root != os.path.dirname(project_root):
        project_root = os.path.dirname(project_root)
    return os.path.join(project_root, "database", "airline.db")

def _db_login(email, password):
    try:
        conn = sqlite3.connect(_get_db_path())
        cur = conn.cursor()
        cur.execute("SELECT account_id, username, email, full_name, role FROM accounts WHERE email=? AND password_hash=?", (email.lower(), _hash(password)))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE accounts SET last_login=CURRENT_TIMESTAMP WHERE account_id=?", (row[0],))
            conn.commit()
        conn.close()
        return {"account_id": row[0], "username": row[1], "email": row[2], "full_name": row[3], "role": row[4]} if row else None
    except: return None