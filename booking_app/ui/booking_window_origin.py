"""
booking_window_origin.py [REFACTORED + FEATURE-LINKED]
------------------------------------------------------------
Main Window for the Booking Application.
Updated:
  - VIP activation state read from DB on startup & persisted on activation
  - Promo tab shows PromotionPage or CurrentMemberPage based on is_activated
  - promo_used passed through ctx to _save_booking_to_db
  - MembersPage and CurrentMemberPage receive live account context
"""
from __future__ import annotations
import sys, os, random, string
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QFrame, QScrollArea, QComboBox,
    QStackedWidget, QMessageBox
)

# Centralized Services
from shared.services.flight_service import get_all_flights, sync_mock_flight_to_db
from shared.services.passenger_service import create_passenger
from shared.services.booking_service import create_booking
from shared.services.seat_service import reserve_seat
from shared.services.payment_service import create_payment
from shared.services.account_service import get_is_activated, set_is_activated
from shared.services.member_service import get_tier_for_user

# Centralized APIs
from shared.api.aviation_api import *
from shared.api.weather_api import *

# Import from booking_shared
from booking_app.ui.pages.booking_shared import (
    NavBar, lbl, h_sep, card_style, red_btn, page_header,
    C_BG, C_RED, C_DARK, C_WHITE, C_BORDER, C_TEXT, C_MID, C_GRAY
)

# Import steps
from booking_app.ui.pages.flight_detailed  import FlightDetailPage
from booking_app.ui.pages.passenger_info   import PassengerInfoPage
from booking_app.ui.pages.seat_selection   import SeatMapPage
from booking_app.ui.pages.confirmation     import ConfirmPage
from booking_app.ui.pages.payment          import PaymentPage
from booking_app.ui.pages.ticket           import TicketPage

# Feature pages
from booking_app.ui.history                import HistoryPage
from booking_app.ui.promotion              import PromotionPage
from booking_app.ui.members                import MembersPage
from booking_app.ui.cur_mem                import CurrentMemberPage
from booking_app.ui.information            import InformationPage

AIRPORTS = ["SGN (TP.HCM)", "HAN (Hà Nội)", "DAD (Đà Nẵng)",
            "CXR (Nha Trang)", "PQC (Phú Quốc)"]


class FlightCard(QFrame):
    selected = Signal(dict)

    def __init__(self, flight_data: dict):
        super().__init__()
        self.flight = flight_data
        self.setStyleSheet(card_style())

        lay = QHBoxLayout(self)
        lay.setContentsMargins(22, 18, 22, 18)

        v1 = QVBoxLayout()
        v1.addWidget(lbl(flight_data.get("code", "N/A"), size=16, weight=700, color=C_RED))
        v1.addWidget(lbl(flight_data.get("aircraft","—"), size=11, color=C_GRAY))
        lay.addLayout(v1, 2)

        v2 = QVBoxLayout()
        v2.addWidget(lbl(f"{flight_data.get('dep_t','--:--')}  ➔  {flight_data.get('arr_t','--:--')}",
                         size=16, weight=600))
        v2.addWidget(lbl(f"{flight_data.get('dep','')} tới {flight_data.get('dst','')}"
                         f" ({flight_data.get('dur','—')})", size=12, color=C_MID))
        lay.addLayout(v2, 4)

        v3 = QVBoxLayout()
        v3.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        v3.addWidget(lbl(f"${flight_data.get('price', 0)}", size=20, weight=700, color=C_DARK))
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
        main_lay.setContentsMargins(30, 20, 30, 20); main_lay.setSpacing(20)

        main_lay.addLayout(page_header("TÌM KIẾM CHUYẾN BAY", "Hệ thống tìm kiếm hành trình bay trực tuyến"))

        search_box = QFrame(); search_box.setStyleSheet(card_style())
        spanel = QHBoxLayout(search_box); spanel.setContentsMargins(20, 15, 20, 15); spanel.setSpacing(15)

        self.cb_dep = QComboBox(); self.cb_dep.addItems(AIRPORTS); self.cb_dep.setFixedHeight(42)
        self.cb_dst = QComboBox(); self.cb_dst.addItems(AIRPORTS); self.cb_dst.setCurrentIndex(1); self.cb_dst.setFixedHeight(42)

        btn_search = red_btn("TÌM KIẾM"); btn_search.setFixedWidth(140); btn_search.setFixedHeight(42)
        btn_search.clicked.connect(self.search_flights)

        spanel.addWidget(lbl("Điểm đi:", weight=600)); spanel.addWidget(self.cb_dep, 1)
        spanel.addWidget(lbl("Điểm đến:", weight=600)); spanel.addWidget(self.cb_dst, 1)
        spanel.addWidget(btn_search)
        main_lay.addWidget(search_box)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background:transparent;border:none;")
        self.scroll_widget = QWidget(); self.scroll_widget.setStyleSheet("background:transparent;")
        self.list_layout = QVBoxLayout(self.scroll_widget); self.list_layout.setSpacing(15); self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll.setWidget(self.scroll_widget)
        main_lay.addWidget(self.scroll, 1)
        self.search_flights()

    def search_flights(self):
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

        try:
            from shared.api.mock_api import MOCK_FLIGHTS, STATUSES_NOT_BOOKABLE
            flights = []
            for f in MOCK_FLIGHTS:
                status    = f.get("status", "Scheduled")
                occupancy = f.get("occupancy_percent", 0)
                if status in STATUSES_NOT_BOOKABLE: continue
                if occupancy >= 95:                 continue
                flights.append({
                    "fid":      f["flight_id"],
                    "flight_id":f["flight_id"],
                    "code":     f["flight_number"],
                    "aircraft": f.get("aircraft", "—"),
                    "dep":      f["departure"][:3].upper(),
                    "dst":      f["destination"][:3].upper(),
                    "dep_t":    str(f["departure_time"])[11:16],
                    "arr_t":    str(f["arrival_time"])[11:16],
                    "dur":      "—",
                    "price":    int(f.get("ticket_price", 0)),
                    "status":   status,
                    "occupancy_percent": occupancy,
                })
            if not flights:
                flights = [
                    {"fid":1,"flight_id":1,"code":"JJ201","aircraft":"AIRBUS A321 NEO",
                     "dep":"HAN","dst":"SGN","dep_t":"09:00","arr_t":"11:15",
                     "dur":"2H 15M","price":120,"status":"Scheduled","occupancy_percent":20},
                ]
            for f in flights:
                card = FlightCard(f)
                card.selected.connect(self.flight_selected.emit)
                self.list_layout.addWidget(card)
        except Exception as e:
            print(f"[FlightsPage Error] {e}")

        self.list_layout.addStretch()


class PlaceholderPage(QWidget):
    def __init__(self, icon: str, title: str):
        super().__init__()
        lay = QVBoxLayout(self); lay.setAlignment(Qt.AlignCenter)
        lay.addWidget(lbl(icon, size=48))
        lay.addWidget(lbl(f"{title} — Tính năng đang phát triển", size=18, weight=600, color=C_MID))


class BookingWindow(QMainWindow):
    def __init__(self, account=None):
        super().__init__()
        self.account = account or {"name": "Khách hàng", "username": "guest"}
        self.setWindowTitle("JetJet Air — Hệ thống Quản lý Đặt vé Máy bay")
        self.resize(1300, 850)

        # ── Load activation state from DB on startup ──────────────────────────
        username = self.account.get("username", "")
        is_activated = get_is_activated(username) if username else 0

        self.ctx: dict = {
            "account":      self.account,
            "flight":       None,
            "passenger":    None,
            "seats":        [],
            "seat_labels":  [],
            "seat_fee":     0,
            "base_price":   0,
            "tax":          45,
            "fee":          12,
            "total":        0,
            "is_activated": is_activated,
            "promo_used":   None,
        }

        central = QWidget(); central.setStyleSheet(f"background:{C_BG};")
        self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)

        self.nav = NavBar(active_tab=0, on_logout=self._logout)
        self.nav.tab_changed.connect(self._handle_nav_tab)
        root.addWidget(self.nav)

        self.stack = QStackedWidget(); self.stack.setStyleSheet(f"background:{C_BG};")
        root.addWidget(self.stack, 1)

        self._init_all_pages()

    def _init_all_pages(self):
        # Compute user tier for promotion page
        username = self.account.get("username", "")
        tier = get_tier_for_user(username) if self.ctx.get("is_activated") else None

        self.step1_search    = FlightsPage()
        self.page_history    = HistoryPage(account=self.account)
        self.page_promo      = PromotionPage(tier=tier)
        self.page_info       = InformationPage(account=self.account)

        self.page_members    = MembersPage(account=self.account)
        self.page_cur_mem    = CurrentMemberPage(account=self.account)

        self.step2_detail    = FlightDetailPage(None)
        self.step3_passenger = PassengerInfoPage(self.ctx)
        self.step4_seats     = SeatMapPage(self.ctx)
        self.step6_confirm   = ConfirmPage(self.ctx)
        self.step7_payment   = PaymentPage(self.ctx)
        self.step8_ticket    = TicketPage(self.ctx)

        # Stack indices:
        # 0: Search, 1: History, 2: Promotion, 3: Info
        # 4: Detail, 5: Passenger, 6: Seats, 7: Confirm, 8: Payment, 9: Ticket
        # 10: Members, 11: Current Member
        for page in [self.step1_search, self.page_history, self.page_promo, self.page_info,
                     self.step2_detail, self.step3_passenger, self.step4_seats,
                     self.step6_confirm, self.step7_payment, self.step8_ticket,
                     self.page_members, self.page_cur_mem]:
            self.stack.addWidget(page)

        # ── Signal connections for booking flow ───────────────────────────────
        self.step1_search.flight_selected.connect(self._to_step2_detail)
        self.step2_detail.proceed.connect(self._to_step3_passenger)
        self.step2_detail.go_back.connect(lambda: self.stack.setCurrentIndex(0))
        self.step3_passenger.proceed.connect(self._to_step4_seats)
        self.step3_passenger.go_back.connect(lambda: self.stack.setCurrentIndex(4))
        self.step4_seats.proceed.connect(self._to_step6_confirm)
        self.step4_seats.go_back.connect(lambda: self.stack.setCurrentIndex(5))
        self.step6_confirm.proceed.connect(self._to_step7_payment)
        self.step6_confirm.go_back.connect(lambda: self.stack.setCurrentIndex(6))
        self.step7_payment.payment_complete.connect(self._to_step8_ticket)
        self.step7_payment.go_back.connect(lambda: self.stack.setCurrentIndex(7))

        # ── VIP activation flow ───────────────────────────────────────────────
        self.page_promo.activate_member_clicked.connect(self._go_to_members)
        self.page_members.register_success.connect(self._on_member_activated)
        self.page_info.activate_member_clicked.connect(self._go_to_promotion)

        if hasattr(self.step8_ticket, 'go_home'):
            self.step8_ticket.go_home.connect(self._reset_to_home)

    # ─────────────────────────────────────────────────────────────────────────
    # Navigation helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _call_update_and_switch(self, page_widget, index):
        if hasattr(page_widget, 'update_page'):
            try: page_widget.update_page()
            except TypeError: page_widget.update_page(self.ctx)
        self.stack.setCurrentIndex(index)

    def _go_to_members(self):
        """Navigate to the membership activation form."""
        self.page_members.set_account(self.account)
        self.stack.setCurrentIndex(10)

    def _on_member_activated(self):
        """Called after MembersPage persists is_activated=1 to DB."""
        self.ctx["is_activated"] = 1

        # Refresh tier and update promo page
        username = self.account.get("username", "")
        tier = get_tier_for_user(username)
        self.page_promo.set_tier(tier)

        # Refresh CurrentMemberPage with new account context
        self.page_cur_mem.update_member(self.account)

        self.stack.setCurrentIndex(11)

    def _go_to_promotion(self):
        """Navigate to Promotion tab, showing the right sub-page."""
        self.nav.set_active_tab(2)
        self._show_promo_or_member()

    def _show_promo_or_member(self):
        """Show CurrentMemberPage if activated, else PromotionPage."""
        if self.ctx.get("is_activated"):
            self.page_cur_mem.update_member(self.account)
            self.stack.setCurrentIndex(11)
        else:
            self.stack.setCurrentIndex(2)

    def _handle_nav_tab(self, index: int):
        if 0 <= index <= 3:
            if index == 1:
                self.page_history.refresh(self.account)
            elif index == 2:
                # Always check activation state from DB before showing promo tab
                username = self.account.get("username", "")
                self.ctx["is_activated"] = get_is_activated(username)
                self._show_promo_or_member()
                return
            elif index == 3:
                self.page_info.update_account(self.account)

            self.stack.setCurrentIndex(index)

    # ─────────────────────────────────────────────────────────────────────────
    # Booking flow steps
    # ─────────────────────────────────────────────────────────────────────────
    def _to_step2_detail(self, flight_data: dict):
        self.ctx["flight"]     = flight_data
        self.ctx["base_price"] = flight_data.get("price", 0)
        self.ctx["total"]      = self.ctx["base_price"] + self.ctx["tax"] + self.ctx["fee"]
        self.ctx["promo_used"] = None    # reset promo each new booking
        if hasattr(self.step2_detail, 'flight'): self.step2_detail.flight = flight_data
        self._call_update_and_switch(self.step2_detail, 4)

    def _to_step3_passenger(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        self._call_update_and_switch(self.step3_passenger, 5)

    def _to_step4_seats(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        self._call_update_and_switch(self.step4_seats, 6)

    def _to_step6_confirm(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        self._call_update_and_switch(self.step6_confirm, 7)

    def _to_step7_payment(self, updated_ctx: dict):
        self.ctx.update(updated_ctx)
        self._call_update_and_switch(self.step7_payment, 8)

    def _to_step8_ticket(self, final_ctx: dict):
        self.ctx.update(final_ctx)

        self.ctx["pnr"]      = self.ctx.get("pnr") or ("JJ" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4)))
        self.ctx["gate"]     = random.choice(["B21", "B22", "A10", "A12", "C05"])
        self.ctx["terminal"] = "Nhà ga T1"
        self.ctx["zone"]     = random.choice(["Khu A", "Khu B", "Khu C"])

        if self._save_booking_to_db():
            self.page_history.refresh(self.account)
            self._call_update_and_switch(self.step8_ticket, 9)
        else:
            QMessageBox.critical(self, "Lỗi", "Không thể lưu thông tin đặt vé thông qua service layer.")

    def _reset_to_home(self):
        username = self.account.get("username", "")
        self.ctx = {
            "account":      self.account,
            "flight":       None,
            "passenger":    None,
            "seats":        [],
            "seat_labels":  [],
            "seat_fee":     0,
            "base_price":   0,
            "tax":          45,
            "fee":          12,
            "total":        0,
            "is_activated": get_is_activated(username),
            "promo_used":   None,
        }
        self.page_history.refresh(self.account)
        self.nav.set_active_tab(0)
        self.step1_search.search_flights()
        self.stack.setCurrentIndex(0)

    def _logout(self):
        self.close()

    # ─────────────────────────────────────────────────────────────────────────
    # DB persistence
    # ─────────────────────────────────────────────────────────────────────────
    def _save_booking_to_db(self) -> bool:
        """
        Saves the booking to DB including promo_used from ctx.
        """
        try:
            pax_data  = self.ctx.get("passenger", {})
            flight    = self.ctx.get("flight", {})
            pnr       = self.ctx.get("pnr") or ("JJ" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4)))
            self.ctx["pnr"] = pnr
            promo_used = self.ctx.get("promo_used")

            fid = flight.get("fid", 1)
            if not sync_mock_flight_to_db(fid):
                print(f"[Sync Error] Could not sync flight {fid} to database.")
                return False

            dob = pax_data.get("dob")
            if not dob or dob == "DD/MM/YYYY":
                dob = "1990-01-01"

            success, msg, passenger_id = create_passenger(
                full_name=pax_data.get("name"),
                gender=pax_data.get("gender", "N/A"),
                date_of_birth=dob,
                phone=pax_data.get("phone"),
                passport_number=pax_data.get("passport"),
                email=pax_data.get("email"),
                nationality=pax_data.get("nationality", "Vietnam")
            )
            if not success or not passenger_id:
                print(f"[Service Error] create_passenger: {msg}"); return False

            first_booking_id = None
            for i, seat_label in enumerate(self.ctx.get("seat_labels", [])):
                unique_pnr = pnr if len(self.ctx.get("seat_labels", [])) == 1 else f"{pnr}-{i+1}"
                success, msg, booking_id = create_booking(
                    booking_reference=unique_pnr,
                    passenger_id=passenger_id,
                    flight_id=fid,
                    seat_number=seat_label,
                    total_amount=self.ctx.get("total", 0),
                    payment_status="Paid",
                    booking_status="Confirmed",
                    created_by=self.account.get("username"),
                    promo_used=promo_used,
                )
                if not success:
                    print(f"[Service Error] create_booking: {msg}"); return False
                if first_booking_id is None: first_booking_id = booking_id

                success, msg = reserve_seat(
                    flight_id=fid,
                    seat_number=seat_label,
                    passenger_id=passenger_id
                )
                if not success:
                    print(f"[Service Error] reserve_seat: {msg}")

            if first_booking_id:
                success, msg = create_payment(
                    booking_id=first_booking_id,
                    payment_method="Card",
                    amount=self.ctx.get("total", 0),
                    transaction_code=pnr + "-TX"
                )
                if not success:
                    print(f"[Service Error] create_payment: {msg}")

            return True
        except Exception as e:
            print(f"[Refactor Error] _save_booking_to_db: {e}"); return False


if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    session_user = {"name": "Lê Văn Quân", "username": "quanlv", "email": "quanle@example.com"}
    window = BookingWindow(account=session_user)
    window.show()
    sys.exit(app.exec())