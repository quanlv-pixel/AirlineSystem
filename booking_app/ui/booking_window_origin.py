"""
booking_window.py  [FIXED — 11 lỗi đã sửa]
--------------------------------------------
Danh sách fix:
  [F1]  NavBar(self.account) → NavBar(active_tab=0)          (CRITICAL)
  [F2]  SELECT flights: r["id"]               → r["flight_id"]     (CRITICAL)
  [F3]  SELECT flights: r["flight_code"]      → r["flight_number"] (CRITICAL)
  [F4]  SELECT flights: r["departure_airport"]→ r["departure"]     (CRITICAL)
  [F5]  SELECT flights: r["arrival_airport"]  → r["destination"]   (CRITICAL)
  [F6]  SELECT flights: r["base_price"]       → r["ticket_price"]  (CRITICAL)
  [F7]  INSERT bookings: cột 'status'         → 'booking_status'   (CRITICAL)
  [F8]  INSERT bookings: cột 'booking_pnr'    → 'booking_reference'(CRITICAL)
  [F9]  step8_ticket.proceed                  → .go_home           (HIGH)
  [F10] go_back signals step2-step7 chưa connect → đã thêm        (HIGH)
  [F11] NavBar trong booking_shared cũng đã sửa tab_changed emit   (HIGH)
"""
from __future__ import annotations
import sys, os, sqlite3, random, string
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QFrame, QScrollArea, QComboBox,
    QStackedWidget, QMessageBox
)

# Import từ booking_shared (đã fix NavBar)
from booking_app.ui.pages.booking_shared import (
    NavBar, lbl, h_sep, card_style, red_btn, page_header,
    C_BG, C_RED, C_DARK, C_WHITE, C_BORDER, C_TEXT, C_MID, C_GRAY
)

# Import các bước
from booking_app.ui.pages.flight_detailed  import FlightDetailPage
from booking_app.ui.pages.passenger_info   import PassengerInfoPage
from booking_app.ui.pages.seat_selection   import SeatMapPage
from booking_app.ui.pages.confirmation     import ConfirmPage
from booking_app.ui.pages.payment          import PaymentPage
from booking_app.ui.pages.ticket           import TicketPage

# ── Dữ liệu mặc định ─────────────────────────────────────────────────────────
AIRPORTS = ["SGN (TP.HCM)", "HAN (Hà Nội)", "DAD (Đà Nẵng)",
            "CXR (Nha Trang)", "PQC (Phú Quốc)"]

SAMPLE_FLIGHTS = [
    {"fid":1,"code":"JJ101","aircraft":"AIRBUS A321 NEO",
     "dep":"SGN","dst":"HAN","dep_t":"08:00","arr_t":"10:15","dur":"2H 15M","price":120},
    {"fid":2,"code":"JJ103","aircraft":"BOEING 787 DREAMLINER",
     "dep":"SGN","dst":"HAN","dep_t":"13:30","arr_t":"15:45","dur":"2H 15M","price":150},
    {"fid":3,"code":"JJ105","aircraft":"AIRBUS A321 NEO",
     "dep":"SGN","dst":"HAN","dep_t":"18:15","arr_t":"20:30","dur":"2H 15M","price":110},
]


def get_db_path() -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for base in (current_dir, os.path.dirname(current_dir)):
        p = os.path.join(base, "database", "airline.db")
        if os.path.exists(p):
            return p
    return os.path.join(current_dir, "database", "airline.db")


# ── Flight Card (trang tìm kiếm) ─────────────────────────────────────────────
class FlightCard(QFrame):
    selected = Signal(dict)

    def __init__(self, flight_data: dict):
        super().__init__()
        self.flight = flight_data
        self.setStyleSheet(card_style())

        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 18, 22, 18)

        v1 = QVBoxLayout()
        v1.addWidget(lbl(flight_data["code"], size=16, weight=700, color=C_RED))
        v1.addWidget(lbl(flight_data.get("aircraft","—"), size=11, color=C_GRAY))
        lay.addLayout(v1, 2)

        v2 = QVBoxLayout()
        v2.addWidget(lbl(f"{flight_data['dep_t']}  ➔  {flight_data['arr_t']}",
                         size=16, weight=600))
        v2.addWidget(lbl(f"{flight_data['dep']} tới {flight_data['dst']}"
                         f" ({flight_data.get('dur','—')})", size=12, color=C_MID))
        lay.addLayout(v2, 4)

        v3 = QVBoxLayout()
        v3.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        v3.addWidget(lbl(f"${flight_data['price']}", size=20, weight=700, color=C_DARK))
        btn = red_btn("CHỌN")
        btn.setFixedWidth(110)
        btn.clicked.connect(lambda: self.selected.emit(self.flight))
        v3.addWidget(btn)
        lay.addLayout(v3, 2)


# ── Flights Page (bước 1) ─────────────────────────────────────────────────────
class FlightsPage(QWidget):
    flight_selected = Signal(dict)

    def __init__(self):
        super().__init__()
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(30, 20, 30, 20)
        main_lay.setSpacing(20)

        main_lay.addLayout(
            page_header("TÌM KIẾM CHUYẾN BAY",
                        "Hệ thống tìm kiếm hành trình bay trực tuyến")
        )

        # Search bar
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

        # Scroll area kết quả
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background:transparent;border:none;")
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background:transparent;")
        self.list_layout = QVBoxLayout(self.scroll_widget)
        self.list_layout.setSpacing(15)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.scroll_widget)
        main_lay.addWidget(self.scroll, 1)

        self.search_flights()

    def search_flights(self):
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
                cursor.execute("""
                    SELECT flight_id, flight_number, aircraft,
                           departure, destination,
                           departure_time, arrival_time,
                           ticket_price, available_seats, gate, terminal
                    FROM flights
                    WHERE available_seats > 0
                """)
                for r in cursor.fetchall():
                    # ── [F2-F6] Dùng đúng tên cột của init_db.py ──────────────
                    try:
                        dep_t = str(r["departure_time"])[:5]
                        arr_t = str(r["arrival_time"])[:5]
                    except Exception:
                        dep_t = arr_t = "—"

                    flights.append({
                        "fid":      r["flight_id"],           # [F2] đã fix
                        "code":     r["flight_number"],        # [F3] đã fix
                        "aircraft": r["aircraft"] or "—",
                        "dep":      r["departure"][:3].upper(),# [F4] đã fix
                        "dst":      r["destination"][:3].upper(),# [F5] đã fix
                        "dep_t":    dep_t,
                        "arr_t":    arr_t,
                        "dur":      "—",
                        "price":    int(r["ticket_price"] or 0),# [F6] đã fix
                        "gate":     r["gate"] or "TBA",
                        "terminal": r["terminal"] or "T1",
                    })
                conn.close()
            except Exception as e:
                print(f"[DB Warning] {e} — dùng SAMPLE_FLIGHTS")

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
        lay.addWidget(lbl(f"{title} — Tính năng đang phát triển",
                          size=18, weight=600, color=C_MID))


# ═════════════════════════════════════════════════════════════════════════════
# BookingWindow
# ═════════════════════════════════════════════════════════════════════════════
class BookingWindow(QMainWindow):
    def __init__(self, account=None):
        super().__init__()
        self.account = account or {"name": "Khách hàng", "username": "guest"}
        self.setWindowTitle("JetJet Air — Hệ thống Quản lý Đặt vé Máy bay")
        self.resize(1300, 850)

        self.ctx: dict = {
            "account":     self.account,
            "flight":      None,
            "passenger":   None,
            "seats":       [],
            "seat_labels": [],
            "seat_fee":    0,
            "base_price":  0,
            "tax":         45,
            "fee":         12,
            "total":       0,
        }

        central = QWidget()
        central.setStyleSheet(f"background:{C_BG};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── [F1] NavBar nhận active_tab=0 (int), KHÔNG phải account dict ──────
        self.nav = NavBar(active_tab=0, on_logout=self._logout)
        self.nav.tab_changed.connect(self._handle_nav_tab)
        root.addWidget(self.nav)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background:{C_BG};")
        root.addWidget(self.stack, 1)

        self._init_all_pages()

    def _init_all_pages(self):
        # Trang tab Navbar (index 0-3)
        self.step1_search    = FlightsPage()
        self.page_history    = PlaceholderPage("📜", "Lịch Sử")
        self.page_promo      = PlaceholderPage("🎁", "Khuyến Mãi")
        self.page_info       = PlaceholderPage("◎",  "Thông Tin")

        # Trang luồng đặt vé (index 4-9)
        self.step2_detail    = FlightDetailPage(self.ctx.get("flight"))
        self.step3_passenger = PassengerInfoPage(self.ctx, self.account)
        self.step4_seats     = SeatMapPage(self.ctx)
        self.step6_confirm   = ConfirmPage(self.ctx)
        self.step7_payment   = PaymentPage(self.ctx)
        self.step8_ticket    = TicketPage(self.ctx)

        for page in [self.step1_search, self.page_history, self.page_promo,
                     self.page_info,    self.step2_detail, self.step3_passenger,
                     self.step4_seats,  self.step6_confirm, self.step7_payment,
                     self.step8_ticket]:
            self.stack.addWidget(page)
        # Indexes: 0-3 = tabs, 4=detail, 5=pax, 6=seats, 7=confirm, 8=pay, 9=ticket

        # ── Signal pipeline ──────────────────────────────────────────────────
        # Bước 1 → 2
        self.step1_search.flight_selected.connect(self.open_flight_detail)

        # Bước 2 → 3  |  back 2 → 1
        self.step2_detail.proceed.connect(self._to_step3_passenger)
        # ── [F10] Kết nối go_back ────────────────────────────────────────────
        self.step2_detail.go_back.connect(lambda: self.stack.setCurrentIndex(0))

        # Bước 3 → 4  |  back 3 → 2
        self.step3_passenger.proceed.connect(self._to_step4_seats)
        self.step3_passenger.go_back.connect(lambda: self.stack.setCurrentIndex(4))

        # Bước 4 → 6  |  back 4 → 3
        self.step4_seats.proceed.connect(self._to_step6_confirm)
        self.step4_seats.go_back.connect(lambda: self.stack.setCurrentIndex(5))

        # Bước 6 → 7  |  back 6 → 4
        self.step6_confirm.proceed.connect(self._to_step7_payment)
        self.step6_confirm.go_back.connect(lambda: self.stack.setCurrentIndex(6))

        # Bước 7 → 8  |  back 7 → 6
        self.step7_payment.payment_complete.connect(self._to_step8_ticket)
        self.step7_payment.go_back.connect(lambda: self.stack.setCurrentIndex(7))

        # ── [F9] TicketPage dùng signal 'go_home', KHÔNG phải 'proceed' ─────
        self.step8_ticket.go_home.connect(self._reset_to_home)

    # ── Điều phối context ────────────────────────────────────────────────────
    def open_flight_detail(self, flight_data: dict):
        self.ctx["flight"]     = flight_data
        self.ctx["base_price"] = flight_data.get("price", 0)
        self.ctx["total"]      = (self.ctx["base_price"]
                                  + self.ctx["tax"]
                                  + self.ctx["fee"])
        # Rebuild FlightDetailPage với dữ liệu mới
        self.stack.removeWidget(self.step2_detail)
        self.step2_detail.deleteLater()
        self.step2_detail = FlightDetailPage(flight_data)
        self.step2_detail.proceed.connect(self._to_step3_passenger)
        self.step2_detail.go_back.connect(lambda: self.stack.setCurrentIndex(0))
        self.stack.insertWidget(4, self.step2_detail)
        self.stack.setCurrentIndex(4)

    def _to_step3_passenger(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        self.step3_passenger.ctx = self.ctx
        self.nav.set_active_tab(0)
        self.stack.setCurrentIndex(5)

    def _to_step4_seats(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        # Rebuild SeatMapPage để nhận đúng flight_id
        self.stack.removeWidget(self.step4_seats)
        self.step4_seats.deleteLater()
        self.step4_seats = SeatMapPage(self.ctx)
        self.step4_seats.proceed.connect(self._to_step6_confirm)
        self.step4_seats.go_back.connect(lambda: self.stack.setCurrentIndex(5))
        self.stack.insertWidget(6, self.step4_seats)
        self.stack.setCurrentIndex(6)

    def _to_step6_confirm(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        self.step6_confirm.ctx = self.ctx
        self.stack.setCurrentIndex(7)

    def _to_step7_payment(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        self.step7_payment.ctx = self.ctx
        self.stack.setCurrentIndex(8)

    def _to_step8_ticket(self, final_ctx: dict):
        self.ctx.update(final_ctx)
        self._save_booking_to_db()
        self.step8_ticket.ctx = self.ctx
        self.stack.setCurrentIndex(9)

    def _reset_to_home(self):
        self.ctx = {
            "account":     self.account,
            "flight":      None, "passenger": None,
            "seats":       [], "seat_labels": [],
            "seat_fee":    0,  "base_price":  0,
            "tax":         45, "fee":         12, "total": 0,
        }
        self.nav.set_active_tab(0)
        self.step1_search.search_flights()
        self.stack.setCurrentIndex(0)

    def _handle_nav_tab(self, index: int):
        if 0 <= index <= 3:
            self.stack.setCurrentIndex(index)

    def _logout(self):
        self._reset_to_home()
        self.close()

    # ── Ghi DB ───────────────────────────────────────────────────────────────
    def _save_booking_to_db(self):
        db_path = get_db_path()
        if not os.path.exists(os.path.dirname(db_path)):
            return
        try:
            conn   = sqlite3.connect(db_path)
            cursor = conn.cursor()

            pax    = self.ctx.get("passenger", {})
            flight = self.ctx.get("flight", {})

            # Tạo/lấy PNR
            pnr = self.ctx.get("pnr")
            if not pnr:
                pnr = "JJ" + "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=4)
                )
                self.ctx["pnr"] = pnr

            # 1. INSERT passengers (khớp với schema init_db.py)
            cursor.execute("""
                INSERT INTO passengers
                    (full_name, gender, date_of_birth, nationality,
                     passport_number, email, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pax.get("name"),
                pax.get("gender", "N/A"),
                pax.get("dob",    "N/A"),
                pax.get("nationality", "Việt Nam"),
                pax.get("passport"),
                pax.get("email"),
                pax.get("phone"),
            ))
            passenger_id = cursor.lastrowid

            # 2. INSERT bookings — một booking/ghế
            # ── [F7] 'status' → 'booking_status'
            # ── [F8] 'booking_pnr' → 'booking_reference'
            for seat in self.ctx.get("seat_labels", []):
                cursor.execute("""
                    INSERT INTO bookings
                        (booking_reference, passenger_id, flight_id,
                         seat_number, booking_class, total_amount,
                         payment_status, booking_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pnr,
                    passenger_id,
                    flight.get("fid", 1),
                    seat,
                    "Economy",
                    self.ctx.get("total", 0),
                    "Paid",         # payment_status
                    "Confirmed",    # booking_status  [F7]
                ))

            # 3. INSERT payments
            cursor.execute("""
                INSERT INTO payments
                    (booking_id, payment_method, payment_status,
                     amount, transaction_code, paid_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (
                cursor.lastrowid,
                "Card",
                "Completed",
                self.ctx.get("total", 0),
                pnr + "-TX",
            ))

            conn.commit()
            conn.close()
            print(f"[DB ✅] Đặt vé thành công — PNR: {pnr}")

        except Exception as e:
            print(f"[DB ❌] {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    session_user = {"name": "Lê Văn Quân", "username": "quanlv",
                    "full_name": "Lê Văn Quân",
                    "email": "quanle19112007@gmail.com"}
    window = BookingWindow(account=session_user)
    window.show()
    sys.exit(app.exec())