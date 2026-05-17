"""
booking_window.py
-----------------
Giao diện chính điều khiển luồng đặt vé (Booking Flow) — JetJet Air
Tích hợp trực tiếp trang tìm kiếm gốc và điều phối qua các file tính năng riêng biệt.
"""
from __future__ import annotations
import sys
import os
import sqlite3
import random
import string
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QFrame, QScrollArea, QComboBox,
                             QStackedWidget, QMessageBox)

# Import các thành phần dùng chung từ file style của bạn
from booking_app.ui.pages.booking_shared import (NavBar, lbl, h_sep, card_style, red_btn, page_header,
                            C_BG, C_RED, C_DARK, C_WHITE, C_BORDER, C_TEXT, C_MID, C_GRAY)

# Import các bước trong luồng đặt vé từ các file riêng biệt của bạn
from booking_app.ui.pages.flight_detailed import FlightDetailPage   # Bước 2: Chi tiết chuyến bay
from booking_app.ui.pages.passenger_info import PassengerInfoPage   # Bước 3: Thông tin hành khách
from booking_app.ui.pages.seat_selection import SeatMapPage        # Bước 4 & 5: Sơ đồ chỗ ngồi
from booking_app.ui.pages.confirmation import ConfirmPage           # Bước 6: Xác nhận thông tin
from booking_app.ui.pages.payment import PaymentPage                # Bước 7: Thanh toán an toàn
from booking_app.ui.pages.ticket import TicketPage                  # Bước 8: Hiển thị vé điện tử thành công

# ─────────────────────────────────────────────────────────────────────────────
# Cấu hình dữ liệu mặc định hệ thống
# ─────────────────────────────────────────────────────────────────────────────
AIRPORTS = ["SGN (TP.HCM)", "HAN (Hà Nội)", "DAD (Đà Nẵng)", "CXR (Nha Trang)", "PQC (Phú Quốc)"]

SAMPLE_FLIGHTS = [
    {"fid": 1, "code": "JJ101", "aircraft": "AIRBUS A321 NEO", "dep": "SGN", "dst": "HAN", "dep_t": "08:00", "arr_t": "10:15", "dur": "2H 15M", "price": 120},
    {"fid": 2, "code": "JJ103", "aircraft": "BOEING 787 DREAMLINER", "dep": "SGN", "dst": "HAN", "dep_t": "13:30", "arr_t": "15:45", "dur": "2H 15M", "price": 150},
    {"fid": 3, "code": "JJ105", "aircraft": "AIRBUS A321 NEO", "dep": "SGN", "dst": "HAN", "dep_t": "18:15", "arr_t": "20:30", "dur": "2H 15M", "price": 110}
]

def get_db_path():
    """Lấy đường dẫn tuyệt đối đến cơ sở dữ liệu an toàn tránh lỗi directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "database", "airline.db")
    if not os.path.exists(db_path):
        parent_dir = os.path.dirname(current_dir)
        db_path = os.path.join(parent_dir, "database", "airline.db")
    return db_path

# ─────────────────────────────────────────────────────────────────────────────
# Các thành phần giao diện tìm kiếm chuyến bay ban đầu
# ─────────────────────────────────────────────────────────────────────────────
class FlightCard(QFrame):
    selected = Signal(dict)
    
    def __init__(self, flight_data: dict):
        super().__init__()
        self.flight = flight_data
        self.setStyleSheet(card_style())
        
        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 18, 22, 18)
        
        # Mã chuyến bay & Máy bay
        v1 = QVBoxLayout()
        v1.addWidget(lbl(flight_data["code"], size=16, weight=700, color=C_RED))
        v1.addWidget(lbl(flight_data["aircraft"], size=11, color=C_GRAY))
        lay.addLayout(v1, 2)
        
        # Tuyển bay & Thời gian
        v2 = QVBoxLayout()
        v2.addWidget(lbl(f"{flight_data['dep_t']}  ➔  {flight_data['arr_t']}", size=16, weight=600))
        v2.addWidget(lbl(f"{flight_data['dep']} tới {flight_data['dst']} ({flight_data['dur']})", size=12, color=C_MID))
        lay.addLayout(v2, 4)
        
        # Giá tiền & Nút chọn
        v3 = QVBoxLayout()
        v3.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        v3.addWidget(lbl(f"${flight_data['price']}", size=20, weight=700, color=C_DARK))
        
        btn = red_btn("CHỌN")
        btn.setFixedWidth(110)
        btn.clicked.connect(lambda: self.selected.emit(self.flight))
        v3.addWidget(btn)
        lay.addLayout(v3, 2)


class FlightsPage(QWidget):
    flight_selected = Signal(dict)
    
    def __init__(self):
        super().__init__()
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(30, 20, 30, 20)
        main_lay.setSpacing(20)
        
        main_lay.addWidget(page_header("TÌM KIẾM CHUYẾN BAY", "Hệ thống tìm kiếm hành trình bay trực tuyến cùng JetJet Air"))
        
        # Thanh tìm kiếm nhanh (Search Panel)
        search_box = QFrame()
        search_box.setStyleSheet(card_style())
        spanel = QHBoxLayout(search_box)
        spanel.setContentsMargins(20, 15, 20, 15)
        spanel.setSpacing(15)
        
        self.cb_dep = QComboBox()
        self.cb_dep.addItems(AIRPORTS)
        self.cb_dep.setFixedHeight(42)
        
        self.cb_dst = QComboBox()
        self.cb_dst.addItems(AIRPORTS)
        self.cb_dst.setCurrentIndex(1)
        self.cb_dst.setFixedHeight(42)
        
        btn_search = red_btn("TÌM KIẾM")
        btn_search.setFixedWidth(140)
        btn_search.setFixedHeight(42)
        btn_search.clicked.connect(self.search_flights)
        
        spanel.addWidget(lbl("Điểm đi:", weight=600))
        spanel.addWidget(self.cb_dep, 1)
        spanel.addWidget(lbl("Điểm đến:", weight=600))
        spanel.addWidget(self.cb_dst, 1)
        spanel.addWidget(btn_search)
        
        main_lay.addWidget(search_box)
        
        # Khu vực danh sách kết quả (Scroll Area)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background:transparent; border:none;")
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background:transparent;")
        self.list_layout = QVBoxLayout(self.scroll_widget)
        self.list_layout.setSpacing(15)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll.setWidget(self.scroll_widget)
        main_lay.addWidget(self.scroll, 1)
        
        self.search_flights()
        
    def search_flights(self):
        # Làm sạch danh sách cũ
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        flights = []
        db_path = get_db_path()
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM flights")
                for r in cursor.fetchall():
                    flights.append({
                        "fid": r["id"],
                        "code": r["flight_code"],
                        "aircraft": "AIRBUS A321 NEO",
                        "dep": r["departure_airport"],
                        "dst": r["arrival_airport"],
                        "dep_t": r["departure_time"],
                        "arr_t": r["arrival_time"],
                        "dur": "2H 15M",
                        "price": r["base_price"]
                    })
                conn.close()
            except Exception as e:
                print(f"[DB Warning] Không thể kết nối cơ sở dữ liệu: {e}. Chuyển sang dữ liệu mẫu.")
        
        if not flights:
            flights = SAMPLE_FLIGHTS
            
        for f in flights:
            card = FlightCard(f)
            card.selected.connect(self.flight_selected.emit)
            self.list_layout.addWidget(card)
        self.list_layout.addStretch()


class PlaceholderPage(QWidget):
    def __init__(self, icon: str, title: str):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl(icon, size=48))
        lay.addWidget(lbl(f"{title} - Tính năng đang phát triển", size=18, weight=600, color=C_MID))


# ─────────────────────────────────────────────────────────────────────────────
# Lớp điều khiển chính toàn bộ hệ thống (Main Application Window)
# ─────────────────────────────────────────────────────────────────────────────
class JetBookWindow(QMainWindow):
    def __init__(self, account=None):
        super().__init__()
        self.account = account or {"name": "Khách hàng"}
        self.setWindowTitle("JetJet Air — Hệ thống Quản lý Đặt vé Máy bay")
        self.resize(1300, 850)
        
        # Đối tượng quản lý dữ liệu toàn phiên đặt vé (Context State)
        self.ctx = {
            "account": self.account,
            "flight": None,
            "passenger": None,
            "seats": [],
            "seat_labels": [],
            "seat_fee": 0,
            "base_price": 0,
            "tax": 45,
            "fee": 12,
            "total": 0
        }

        central = QWidget()
        central.setStyleSheet(f"background:{C_BG};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Thanh điều hướng dùng chung NavBar
        self.nav = NavBar(self.account)
        self.nav.tab_changed.connect(self._handle_nav_tab)
        root.addWidget(self.nav)

        # Trình quản lý các trang hiển thị StackedWidget
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{C_BG};")
        root.addWidget(self.stack, 1)

        self._init_all_pages()

    def _init_all_pages(self):
        # Thiết lập các trang chính tương ứng các Tab của Navbar (Index 0 -> 3)
        self.step1_search = FlightsPage()                     # Index 0
        self.page_history = PlaceholderPage("📜", "Lịch Sử")   # Index 1
        self.page_promo   = PlaceholderPage("🎁", "Khuyến Mãi") # Index 2
        self.page_info    = PlaceholderPage("◎", "Thông Tín")   # Index 3
        
        # Thiết lập các trang xử lý luồng đặt vé (Index 4 -> 9)
        self.step2_detail    = FlightDetailPage(self.ctx["flight"])
        self.step3_passenger = PassengerInfoPage(self.ctx)
        self.step4_seats     = SeatMapPage(self.ctx)
        self.step6_confirm   = ConfirmPage(self.ctx)
        self.step7_payment   = PaymentPage(self.ctx)
        self.step8_ticket    = TicketPage(self.ctx)

        # Đẩy toàn bộ vào Stack điều hướng
        self.stack.addWidget(self.step1_search)    # 0
        self.stack.addWidget(self.page_history)    # 1
        self.stack.addWidget(self.page_promo)      # 2
        self.stack.addWidget(self.page_info)       # 3
        self.stack.addWidget(self.step2_detail)     # 4
        self.stack.addWidget(self.step3_passenger)  # 5
        self.stack.addWidget(self.step4_seats)      # 6
        self.stack.addWidget(self.step6_confirm)    # 7
        self.stack.addWidget(self.step7_payment)    # 8
        self.stack.addWidget(self.step8_ticket)     # 9

        # ── KẾT NỐI TOÀN BỘ ĐƯỜNG ĐI LOGIC (SIGNAL PIPELINE) ──────────────────
        
        # Bước 1 -> Chọn chuyến bay -> Sang Bước 2 (Chi tiết)
        self.step1_search.flight_selected.connect(self.open_flight_detail)
        
        # Bước 2 -> Nhấn tiến hành -> Sang Bước 3 (Điền thông tin hành khách)
        self.step2_detail.proceed.connect(self._to_step3_passenger)
        
        # Bước 3 -> Điền xong thông tin -> Sang Bước 4 & 5 (Sơ đồ ghế)
        self.step3_passenger.proceed.connect(self._to_step4_seats)
        
        # Bước 4 & 5 -> Chọn xong vị trí ghế -> Sang Bước 6 (Xác nhận hóa đơn)
        self.step4_seats.proceed.connect(self._to_step6_confirm)
        
        # Bước 6 -> Đồng ý điều khoản -> Sang Bước 7 (Cổng thanh toán bảo mật)
        self.step6_confirm.proceed.connect(self._to_step7_payment)
        
        # Bước 7 -> Xác thực OTP/SSL thành công -> Sang Bước 8 (In vé điện tử)
        self.step7_payment.payment_complete.connect(self._to_step8_ticket)
        
        # Bước 8 -> Nhấn Hoàn tất trên Ticket Page -> Reset luồng về Trang chủ
        if hasattr(self.step8_ticket, "proceed"):
            self.step8_ticket.proceed.connect(self._reset_to_home)

    # ── HÀM ĐIỀU PHỐI VÀ ĐỒNG BỘ CONTEXT QUA TỪNG TRANG ─────────────────────

    def open_flight_detail(self, flight_data: dict):
        self.ctx["flight"] = flight_data
        self.ctx["base_price"] = flight_data.get("price", 0)
        self.ctx["total"] = self.ctx["base_price"] + self.ctx["tax"] + self.ctx["fee"]
        
        self.step2_detail.flight = flight_data
        if hasattr(self.step2_detail, "_build_ui"):
            self.step2_detail._build_ui()
        self.stack.setCurrentIndex(4)

    def _to_step3_passenger(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        self.step3_passenger.ctx = self.ctx
        if hasattr(self.step3_passenger, "_build_ui"):
            self.step3_passenger._build_ui()
        self.stack.setCurrentIndex(5)

    def _to_step4_seats(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        self.step4_seats.ctx = self.ctx
        if hasattr(self.step4_seats, "_build_ui"):
            self.step4_seats._build_ui()
        self.stack.setCurrentIndex(6)

    def _to_step6_confirm(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        self.step6_confirm.ctx = self.ctx
        if hasattr(self.step6_confirm, "_build_ui"):
            self.step6_confirm._build_ui()
        self.stack.setCurrentIndex(7)

    def _to_step7_payment(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        self.step7_payment.ctx = self.ctx
        if hasattr(self.step7_payment, "_build_ui"):
            self.step7_payment._build_ui()
        self.stack.setCurrentIndex(8)

    def _to_step8_ticket(self, final_ctx: dict):
        self.ctx.update(final_ctx)
        
        # Ghi nhận thông tin xuống SQLite Database trước khi in vé hiển thị cho khách hàng
        self._save_booking_transaction_to_db()
        
        if hasattr(self.step8_ticket, "ctx"):
            self.step8_ticket.ctx = self.ctx
        if hasattr(self.step8_ticket, "_build_ui"):
            self.step8_ticket._build_ui()
        self.stack.setCurrentIndex(9)

    def _reset_to_home(self):
        self.ctx = {
            "account": self.account, "flight": None, "passenger": None,
            "seats": [], "seat_labels": [], "seat_fee": 0, "base_price": 0,
            "tax": 45, "fee": 12, "total": 0
        }
        self.step1_search.search_flights()
        self.stack.setCurrentIndex(0)

    def _handle_nav_tab(self, index: int):
        if index in [0, 1, 2, 3]:
            self.stack.setCurrentIndex(index)

    def _save_booking_transaction_to_db(self):
        db_path = get_db_path()
        if not os.path.exists(os.path.dirname(db_path)):
            return
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            pax = self.ctx.get("passenger", {})
            flight = self.ctx.get("flight", {})
            pnr = self.ctx.get("pnr")
            
            if not pnr:
                pnr = "JJ" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
                self.ctx["pnr"] = pnr
            
            # 1. Thêm bản ghi thông tin vào bảng passengers
            cursor.execute("""
                INSERT INTO passengers (full_name, date_of_birth, gender, nationality, passport_number, email, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (pax.get("name"), pax.get("dob"), pax.get("gender"), pax.get("nationality"), 
                  pax.get("passport"), pax.get("email"), pax.get("phone")))
            
            passenger_id = cursor.lastrowid
            
            # 2. Thêm thông tin đặt chỗ ghế tương ứng vào bảng bookings
            for seat in self.ctx.get("seat_labels", []):
                cursor.execute("""
                    INSERT INTO bookings (passenger_id, flight_id, seat_number, status, booking_pnr)
                    VALUES (?, ?, ?, ?, ?)
                """, (passenger_id, flight.get("fid", 1), seat, "CONFIRMED", pnr))
                
            conn.commit()
            conn.close()
            print(f"[SQLite Success] Lưu giao dịch đặt vé mã PNR: {pnr} hoàn tất!")
        except Exception as e:
            print(f"[SQLite Error] Không thể đồng bộ dữ liệu đặt chỗ: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Tài khoản phiên làm việc mock-up
    session_user = {"name": "Lê Văn Quân", "username": "quanlv"}
    
    window = JetBookWindow(account=session_user)
    window.show()
    sys.exit(app.exec())