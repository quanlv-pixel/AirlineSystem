import hashlib
import sys
import os
import sqlite3

from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import (
    QColor, QFont, QPainter, QBrush, QPen,
    QPainterPath, QLinearGradient
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QGraphicsDropShadowEffect, QFrame
)

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
        self.setFixedHeight(50)
        if password:
            self.setEchoMode(QLineEdit.Password)
        self.setStyleSheet(f"QLineEdit {{ background: {INPUT_BG}; border: 1px solid #ECECF1; border-radius: 12px; padding: 0 15px; color: {TEXT_DARK}; }} QLineEdit:focus {{ border: 1px solid {RED_PRIMARY}; background: {WHITE}; }}")

class RegisterWindow(QMainWindow):
    go_login = Signal()

    def __init__(self, pos=None):
        super().__init__()
        self.setWindowTitle("JetJet Air - Đăng ký")
        self.setFixedSize(450, 680)
        if pos: self.move(pos)
        else: self._center()

        self.bg = GradientBackground()
        self.setCentralWidget(self.bg)

        layout = QVBoxLayout(self.bg)
        layout.setContentsMargins(40, 40, 40, 40)

        self.card = QFrame()
        self.card.setStyleSheet(f"background: {WHITE}; border-radius: 24px;")
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(40); card_shadow.setColor(QColor(0,0,0,60)); card_shadow.setOffset(0,10)
        self.card.setGraphicsEffect(card_shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(30, 35, 30, 35)
        card_layout.setSpacing(12)

        logo = QLabel("✈")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(f"font-size: 40px; color: {RED_PRIMARY};")
        
        title = QLabel("TẠO TÀI KHOẢN")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size: 22px; font-weight: 900; color: {TEXT_DARK};")

        self.name_input = StyledInput("Họ và tên")
        self.email_input = StyledInput("Địa chỉ Email")
        self.pwd_input = StyledInput("Mật khẩu (tối thiểu 6 ký tự)", password=True)

        self.msg_label = QLabel("")
        self.msg_label.setAlignment(Qt.AlignCenter)
        self.msg_label.setWordWrap(True)
        self.msg_label.setStyleSheet("font-size: 12px; color: #E53935;")

        reg_btn = QPushButton("ĐĂNG KÝ NGAY")
        reg_btn.setFixedHeight(54)
        reg_btn.setCursor(Qt.PointingHandCursor)
        reg_btn.setStyleSheet(f"QPushButton {{ background: {RED_PRIMARY}; color: white; border-radius: 12px; font-weight: 800; font-size: 14px; margin-top: 10px; }} QPushButton:hover {{ background: #D32F2F; }}")
        reg_btn.clicked.connect(self._handle_register)

        back_btn = QPushButton("Đã có tài khoản? Đăng nhập")
        back_btn.setFixedHeight(40)
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("QPushButton { background:transparent; color:#666; font-weight:700; border:none; } QPushButton:hover { color:#FF1632; }")
        back_btn.clicked.connect(lambda: self.go_login.emit())

        card_layout.addWidget(logo)
        card_layout.addWidget(title)
        card_layout.addWidget(self.name_input)
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(self.pwd_input)
        card_layout.addWidget(self.msg_label)
        card_layout.addWidget(reg_btn)
        card_layout.addWidget(back_btn)

        layout.addWidget(self.card)

    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def _handle_register(self):
        name, email, pwd = self.name_input.text(), self.email_input.text(), self.pwd_input.text()
        if not name or not email or not pwd:
            self.msg_label.setText("Vui lòng điền đủ thông tin")
            return
        
        ok, res = _db_register(name, email, pwd)
        if ok:
            self.msg_label.setStyleSheet("color: #2E7D32;")
            self.msg_label.setText("Thành công! Đang chuyển hướng...")
            QTimer.singleShot(1500, self.go_login.emit)
        else:
            self.msg_label.setText(res)

def _hash(p): return hashlib.sha256(p.encode()).hexdigest()

def _db_register(name, email, pwd):
    try:
        conn = sqlite3.connect(_get_db_path())
        cur = conn.cursor()
        
        username = email.split("@")[0].lower()
        cur.execute("INSERT INTO accounts (username, email, password_hash, full_name, role) VALUES (?,?,?,?,'customer')",
                   (username, email.lower(), _hash(pwd), name))
        
        cur.execute("""
            INSERT INTO passengers (full_name, email, gender, date_of_birth, phone, nationality)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email.lower(), "N/A", "1990-01-01", "", "Vietnam"))
        
        conn.commit()
        conn.close()
        return True, "Thành công"
    except Exception as e:
        return False, "Email đã tồn tại" if "UNIQUE" in str(e) else str(e)

def _get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    while not os.path.exists(os.path.join(project_root, 'database')) and project_root != os.path.dirname(project_root):
        project_root = os.path.dirname(project_root)
    return os.path.join(project_root, "database", "airline.db")