import hashlib, sys, os, sqlite3, random, smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import (
    QColor, QFont, QPainter, QBrush, QPen,
    QPainterPath, QLinearGradient
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QGraphicsDropShadowEffect, QFrame, QDialog, QMessageBox
)

RED_PRIMARY = "#FF1632"
RED_GRADIENT = ["#FF1632", "#FF2942", "#FF4B5F"]
TEXT_DARK = "#1A1A2E"
INPUT_BG = "#F3F4F7"
WHITE = "#FFFFFF"

# =====================================================================
# EMAIL SENDER CONFIGURATION (Bạn điền thông tin thật vào đây)
# =====================================================================
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_APP_PASSWORD = os.getenv("SMTP_APP_PASSWORD")

def send_otp_email(to_email, otp_code):
    try:
        msg = MIMEText(f"Mã OTP để đặt lại mật khẩu JetJet Air của bạn là: {otp_code}\nMã có hiệu lực trong 5 phút.")
        msg['Subject'] = 'JetJet Air - Phục hồi mật khẩu'
        msg['From'] = SMTP_EMAIL
        msg['To'] = to_email

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Lỗi gửi email: {e}")
        return False

# =====================================================================
# POPUP QUÊN MẬT KHẨU
# =====================================================================
class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Quên mật khẩu")
        self.setFixedSize(350, 250)
        self.setStyleSheet(f"background: {WHITE}; border-radius: 12px;")
        
        self.otp_code = None
        self.user_email = None
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        
        self.title = QLabel("PHỤC HỒI MẬT KHẨU")
        self.title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {RED_PRIMARY};")
        self.layout.addWidget(self.title, 0, Qt.AlignCenter)
        
        self.input_field = StyledInput("Nhập email đã đăng ký")
        self.layout.addWidget(self.input_field)
        
        self.action_btn = QPushButton("GỬI MÃ OTP")
        self.action_btn.setFixedHeight(45)
        self.action_btn.setStyleSheet(f"background: {TEXT_DARK}; color: {WHITE}; border-radius: 8px; font-weight: bold;")
        self.action_btn.clicked.connect(self.handle_action)
        self.layout.addWidget(self.action_btn)
        
        self.step = 1 # 1: Nhập email, 2: Nhập OTP, 3: Nhập pass mới
        
    def handle_action(self):
        text = self.input_field.text().strip()
        if not text:
            return
            
        if self.step == 1:
            # Kiểm tra email tồn tại không
            conn = sqlite3.connect(_get_db_path())
            cur = conn.cursor()
            cur.execute("SELECT email FROM accounts WHERE email=?", (text.lower(),))
            row = cur.fetchone()
            conn.close()
            
            if not row:
                QMessageBox.warning(self, "Lỗi", "Email không tồn tại trong hệ thống!")
                return
                
            self.user_email = text.lower()
            self.otp_code = str(random.randint(100000, 999999))
            
            self.action_btn.setText("ĐANG GỬI...")
            self.action_btn.setEnabled(False)
            QApplication.processEvents()
            
            if send_otp_email(self.user_email, self.otp_code):
                self.step = 2
                self.input_field.clear()
                self.input_field.setPlaceholderText("Nhập mã OTP 6 số")
                self.action_btn.setText("XÁC NHẬN OTP")
                QMessageBox.information(self, "Thành công", f"Mã OTP đã được gửi đến {self.user_email}")
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể gửi email. Vui lòng kiểm tra lại cấu hình SMTP.")
            
            self.action_btn.setEnabled(True)
            
        elif self.step == 2:
            if text == self.otp_code:
                self.step = 3
                self.input_field.clear()
                self.input_field.setEchoMode(QLineEdit.Password)
                self.input_field.setPlaceholderText("Nhập mật khẩu mới")
                self.action_btn.setText("ĐỔI MẬT KHẨU")
            else:
                QMessageBox.warning(self, "Lỗi", "Mã OTP không chính xác!")
                
        elif self.step == 3:
            if len(text) < 6:
                QMessageBox.warning(self, "Lỗi", "Mật khẩu phải từ 6 ký tự trở lên!")
                return
            _db_update_password(self.user_email, text)
            QMessageBox.information(self, "Thành công", "Đổi mật khẩu thành công! Vui lòng đăng nhập lại.")
            self.accept()

# =====================================================================
# CÁC CLASS UI CHÍNH
# =====================================================================
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
        if password: self.setEchoMode(QLineEdit.Password)
        self.setStyleSheet(f"""
            QLineEdit {{ background: {INPUT_BG}; border: 1px solid #ECECF1; border-radius: 12px; padding: 0 15px; color: {TEXT_DARK}; font-size: 14px; }}
            QLineEdit:focus {{ border: 1px solid {RED_PRIMARY}; background: {WHITE}; }}
        """)

class LoginWindow(QMainWindow):
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

        self.email_input = StyledInput("Email hoặc Tên đăng nhập")
        self.pwd_input = StyledInput("Mật khẩu", password=True)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #E53935; font-size: 12px;")

        # Quên mật khẩu
        forgot_btn = QPushButton("Quên mật khẩu?")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.setStyleSheet(f"background: transparent; color: {TEXT_DARK}; border: none; text-align: right; font-weight: bold;")
        forgot_btn.clicked.connect(self._handle_forgot_pwd)

        self.login_btn = QPushButton("ĐĂNG NHẬP")
        self.login_btn.setFixedHeight(54)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setStyleSheet(f"QPushButton {{ background: {RED_PRIMARY}; color: white; border-radius: 12px; font-weight: 800; font-size: 14px; margin-top: 10px; }} QPushButton:hover {{ background: #D32F2F; }}")
        self.login_btn.clicked.connect(self._handle_login)

        register_btn = QPushButton("Chưa có tài khoản? Đăng ký ngay")
        register_btn.setFixedHeight(40)
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.setStyleSheet(f"QPushButton {{ background: transparent; color: #666; font-weight: 700; font-size: 13px; border: none; }} QPushButton:hover {{ color: {RED_PRIMARY}; }}")
        register_btn.clicked.connect(lambda: self.go_register.emit())

        card_layout.addWidget(logo)
        card_layout.addWidget(title)
        card_layout.addWidget(self.email_input)
        card_layout.addWidget(self.pwd_input)
        card_layout.addWidget(forgot_btn)
        card_layout.addWidget(self.error_label)
        card_layout.addWidget(self.login_btn)
        card_layout.addWidget(register_btn)

        layout.addWidget(self.card)

    def _center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def _handle_forgot_pwd(self):
        dlg = ForgotPasswordDialog(self)
        dlg.exec()

    def _handle_login(self):
        self.login_btn.setEnabled(False)
        self.login_btn.setText("ĐANG XỬ LÝ...")

        email_or_user = self.email_input.text().strip()
        pwd = self.pwd_input.text().strip()
        
        if not email_or_user or not pwd:
            self.error_label.setText("Vui lòng nhập đầy đủ thông tin")
            self.login_btn.setEnabled(True)
            self.login_btn.setText("ĐĂNG NHẬP")
            return

        account = _db_login(email_or_user, pwd)
        if account:
            self.login_success.emit(account)
        else:
            self.error_label.setText("Sai tài khoản hoặc mật khẩu")
            self.login_btn.setEnabled(True)
            self.login_btn.setText("ĐĂNG NHẬP")

def _hash(p): return hashlib.sha256(p.encode()).hexdigest()

def _get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    while not os.path.exists(os.path.join(project_root, 'database')) and project_root != os.path.dirname(project_root):
        project_root = os.path.dirname(project_root)
    return os.path.join(project_root, "database", "airline.db")

def _db_login(email_or_user, password):
    try:
        conn = sqlite3.connect(_get_db_path())
        cur = conn.cursor()
        # Hỗ trợ login bằng email HOẶC username
        cur.execute("SELECT account_id, username, email, full_name, role FROM accounts WHERE (email=? OR username=?) AND password_hash=?", 
                   (email_or_user.lower(), email_or_user.lower(), _hash(password)))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE accounts SET last_login=CURRENT_TIMESTAMP WHERE account_id=?", (row[0],))
            conn.commit()
        conn.close()
        return {"account_id": row[0], "username": row[1], "email": row[2], "full_name": row[3], "role": row[4]} if row else None
    except: return None

def _db_update_password(email, new_pwd):
    try:
        conn = sqlite3.connect(_get_db_path())
        cur = conn.cursor()
        cur.execute("UPDATE accounts SET password_hash=? WHERE email=?", (_hash(new_pwd), email.lower()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(e)