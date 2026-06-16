from __future__ import annotations
import sys
from collections import defaultdict
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QPainterPath
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy,
    QGraphicsOpacityEffect
)
from booking_app.ui.pages.booking_shared import (lbl, h_sep, card_style,
                             C_RED, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY,
                             C_GREEN, C_BLUE, C_ORANGE)

from shared.services.booking_service import get_booking_history_by_user, cancel_booking
from PySide6.QtWidgets import QMessageBox


# ─────────────────────────────────────────────────────────────────────────────
# Helper: group raw rows by base PNR
# ─────────────────────────────────────────────────────────────────────────────
def _group_by_pnr(raw_rows: list[dict]) -> list[dict]:
    """
    Collapse individual seat-rows into grouped order dicts keyed by base PNR.
    A PNR like 'JJ1A2B-2' strips to base 'JJ1A2B'.
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in raw_rows:
        ref = str(row.get("booking_reference", "")).strip()
        base_pnr = ref.split("-")[0] if ref else str(row.get("booking_id", "?"))
        groups[base_pnr].append(row)

    result: list[dict] = []
    for base_pnr, rows in groups.items():
        first = rows[0]
        ticket_count = len(rows)
        total_group_amount = sum(r.get("total_amount", 0) for r in rows)
        seats = [str(r.get("seats", "")).strip() for r in rows if r.get("seats")]
        result.append({
            "base_pnr":          base_pnr,
            "booking_ids":       [r.get("booking_id") for r in rows],
            "booking_date":      first.get("booking_date", "—"),
            "status":            first.get("status", "pending"),
            "flight_code":       first.get("flight_code", "—"),
            "departure":         first.get("departure", "—"),
            "destination":       first.get("destination", "—"),
            "departure_time":    first.get("departure_time", "—"),
            "arrival_time":      first.get("arrival_time", "—"),
            "ticket_count":      ticket_count,
            "total_amount":      total_group_amount,
            "seats":             seats,
        })
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Thẻ Thống Kê Nhỏ
# ─────────────────────────────────────────────────────────────────────────────
class StatsCard(QWidget):
    def __init__(self, title: str, value: str, icon: str, color: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(12))
        self.setFixedHeight(80)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(18, 12, 18, 12)

        ico_lbl = lbl(icon, 22, 400, color)
        ico_lbl.setFixedWidth(32)
        lay.addWidget(ico_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.addWidget(lbl(title.upper(), 10, 700, C_GRAY, 0.5))
        text_col.addWidget(lbl(value, 20, 800, C_TEXT))
        lay.addLayout(text_col)
        lay.addStretch()


# ─────────────────────────────────────────────────────────────────────────────
# Expandable Order Card (grouped tickets)
# ─────────────────────────────────────────────────────────────────────────────
class OrderCard(QWidget):
    """
    Displays a grouped booking order.  Clicking 'Xem chi tiết' toggles an
    inline detail section that shows PNR + all seat labels.
    """

    def __init__(self, order: dict, cancel_callback=None, parent=None):
        super().__init__(parent)
        self._expanded = False
        self._order = order
        self._cancel_callback = cancel_callback
        self.setStyleSheet(card_style(16))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(0, 0, 0, 0)
        self._root.setSpacing(0)

        # ── Main summary row ────────────────────────────────────────────────
        top_w = QWidget()
        top_w.setStyleSheet("background:transparent;")
        top_lay = QHBoxLayout(top_w)
        top_lay.setContentsMargins(22, 18, 22, 18)
        top_lay.setSpacing(16)

        # 1. Status badge + booking-id
        status = str(order.get("status", "pending")).lower()
        st_text, st_color, st_bg = " CHỜ THANH TOÁN ", C_ORANGE, "#FFF8E1"
        if status in ("confirmed", "đã xác nhận", "completed", "paid"):
            st_text, st_color, st_bg = " ĐÃ XÁC NHẬN ", C_GREEN, "#E8F5E9"
        elif status in ("cancelled", "đã hủy"):
            st_text, st_color, st_bg = " ĐÃ HỦY VÉ ", C_RED, "#FFEBEE"

        status_col = QVBoxLayout()
        status_col.setSpacing(6)
        status_col.setAlignment(Qt.AlignVCenter)

        st_lbl = lbl(st_text, 10, 800, st_color)
        st_lbl.setStyleSheet(f"background:{st_bg}; border-radius:6px; padding:4px 8px;")
        st_lbl.setAlignment(Qt.AlignCenter)
        status_col.addWidget(st_lbl)
        status_col.addWidget(lbl(f"#{order.get('base_pnr', '—')}", 11, 700, C_GRAY))
        top_lay.addLayout(status_col)

        # 2. Route
        route_col = QVBoxLayout()
        route_col.setSpacing(4)
        route_col.setAlignment(Qt.AlignVCenter)

        route_row = QHBoxLayout()
        route_row.setSpacing(8)
        route_row.addWidget(lbl(order.get("departure", "—")[:3].upper(), 22, 800, C_TEXT))
        route_row.addWidget(lbl("➔", 14, 400, C_RED))
        route_row.addWidget(lbl(order.get("destination", "—")[:3].upper(), 22, 800, C_TEXT))
        route_row.addStretch()
        route_col.addLayout(route_row)
        route_col.addWidget(lbl(f"✈  {order.get('flight_code', '—')}", 12, 500, C_MID))
        top_lay.addLayout(route_col, 2)

        # 3. Date & time
        dep_t = str(order.get("departure_time", "—"))
        dep_short = dep_t[11:16] if len(dep_t) > 10 else dep_t
        date_str = str(order.get("booking_date", "—"))[:10]

        time_col = QVBoxLayout()
        time_col.setSpacing(4)
        time_col.setAlignment(Qt.AlignVCenter)
        time_col.addWidget(lbl(f"📅  Khởi hành: {dep_short}", 12, 600, C_TEXT))
        time_col.addWidget(lbl(f"Ngày đặt: {date_str}", 11, 400, C_GRAY))
        top_lay.addLayout(time_col, 2)

        # 4. Ticket count chip
        count = order.get("ticket_count", 1)
        ticket_col = QVBoxLayout()
        ticket_col.setAlignment(Qt.AlignVCenter)
        count_lbl = lbl(f"🎫  {count} vé", 13, 700, C_RED)
        count_lbl.setStyleSheet(
            f"background:#FFF0F0; border-radius:10px; padding:6px 14px; color:{C_RED};"
        )
        ticket_col.addWidget(count_lbl)
        top_lay.addLayout(ticket_col)

        # 5. Price + detail button
        price_col = QVBoxLayout()
        price_col.setSpacing(6)
        price_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        price_col.addWidget(lbl(f"${order.get('total_amount', 0):,.0f}", 22, 900, C_RED))
        price_col.addWidget(lbl("Tổng hóa đơn", 10, 500, C_GRAY))

        self._detail_btn = QPushButton("Xem chi tiết  ▾")
        self._detail_btn.setFixedHeight(30)
        self._detail_btn.setCursor(Qt.PointingHandCursor)
        self._detail_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: 1.5px solid {C_BORDER};
                border-radius: 8px; font-size: 11px; font-weight: 700;
                color: {C_MID}; padding: 0 10px;
            }}
            QPushButton:hover {{
                background: {C_LGRAY}; border-color: {C_RED}; color: {C_RED};
            }}
        """)
        self._detail_btn.clicked.connect(self._toggle_details)
        price_col.addWidget(self._detail_btn)

        # Cancel ticket button — only for pending / confirmed orders
        if status in ("pending", "confirmed", "chờ thanh toán", "đã xác nhận"):
            booking_ids = order.get("booking_ids", [])
            cancel_ticket_btn = QPushButton("🚫  Hủy vé")
            cancel_ticket_btn.setFixedHeight(30)
            cancel_ticket_btn.setCursor(Qt.PointingHandCursor)
            cancel_ticket_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: 1.5px solid {C_RED};
                    border-radius: 8px;
                    font-size: 11px;
                    font-weight: 700;
                    color: {C_RED};
                    padding: 0 10px;
                }}
                QPushButton:hover {{
                    background: #FFEBEE;
                }}
            """)
            if self._cancel_callback and booking_ids:
                cancel_ticket_btn.clicked.connect(
                    lambda checked=False, bids=booking_ids: self._cancel_callback(bids)
                )
            price_col.addWidget(cancel_ticket_btn)

        top_lay.addLayout(price_col)

        self._root.addWidget(top_w)

        # ── Expandable detail section (hidden by default) ────────────────────
        self._detail_w = QWidget()
        self._detail_w.setStyleSheet(
            f"background:#F8F9FE; border-top:1px solid {C_BORDER};"
            f"border-bottom-left-radius:14px; border-bottom-right-radius:14px;"
        )
        self._detail_w.setVisible(False)

        detail_lay = QVBoxLayout(self._detail_w)
        detail_lay.setContentsMargins(24, 16, 24, 18)
        detail_lay.setSpacing(12)

        # PNR row
        pnr_row = QHBoxLayout()
        pnr_row.addWidget(lbl("🔖  Mã đặt chỗ (PNR):", 12, 600, C_GRAY))
        pnr_val = lbl(order.get("base_pnr", "—"), 13, 800, C_DARK)
        pnr_val.setStyleSheet(
            f"background:{C_WHITE}; border:1.5px solid {C_BORDER};"
            f"border-radius:8px; padding:4px 12px; color:{C_DARK};"
        )
        pnr_row.addWidget(pnr_val)
        pnr_row.addStretch()
        detail_lay.addLayout(pnr_row)

        # Seat chips row
        seats: list[str] = order.get("seats", [])
        if seats:
            seat_row = QHBoxLayout()
            seat_row.setSpacing(8)
            seat_row.addWidget(lbl("🪑  Ghế đã chọn:", 12, 600, C_GRAY))
            chips_w = QWidget()
            chips_w.setStyleSheet("background:transparent;")
            chips_lay = QHBoxLayout(chips_w)
            chips_lay.setContentsMargins(0, 0, 0, 0)
            chips_lay.setSpacing(6)
            for seat in seats:
                chip = lbl(seat, 12, 800, C_WHITE)
                chip.setAlignment(Qt.AlignCenter)
                chip.setFixedHeight(28)
                chip.setStyleSheet(
                    f"background:{C_DARK}; border-radius:8px;"
                    f"padding:0 10px; color:{C_WHITE};"
                )
                chips_lay.addWidget(chip)
            chips_lay.addStretch()
            seat_row.addWidget(chips_w, 1)
            detail_lay.addLayout(seat_row)
        else:
            detail_lay.addWidget(lbl("Chưa có thông tin ghế.", 12, 400, C_GRAY))

        # Per-ticket breakdown
        if count > 1:
            breakdown = lbl(
                f"Mỗi vé: ${order.get('total_amount', 0) / count:,.1f}  ·  "
                f"{count} vé  ·  Tổng: ${order.get('total_amount', 0):,.0f}",
                11, 500, C_GRAY
            )
            detail_lay.addWidget(breakdown)

        self._root.addWidget(self._detail_w)

    # ── Toggle expand / collapse ─────────────────────────────────────────────
    def _toggle_details(self):
        self._expanded = not self._expanded
        self._detail_w.setVisible(self._expanded)
        if self._expanded:
            self._detail_btn.setText("Ẩn chi tiết  ▴")
            self._detail_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {C_RED}; border: none;
                    border-radius: 8px; font-size: 11px; font-weight: 700;
                    color: {C_WHITE}; padding: 0 10px;
                }}
                QPushButton:hover {{ background: #C0392B; }}
            """)
        else:
            self._detail_btn.setText("Xem chi tiết  ▾")
            self._detail_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: 1.5px solid {C_BORDER};
                    border-radius: 8px; font-size: 11px; font-weight: 700;
                    color: {C_MID}; padding: 0 10px;
                }}
                QPushButton:hover {{
                    background: {C_LGRAY}; border-color: {C_RED}; color: {C_RED};
                }}
            """)
        # Let parent scroll area recalculate size
        self.adjustSize()
        if self.parent():
            self.parent().adjustSize()


# ─────────────────────────────────────────────────────────────────────────────
# HistoryPage Layout Chính
# ─────────────────────────────────────────────────────────────────────────────
class HistoryPage(QWidget):
    def __init__(self, account: dict | None = None, parent=None):
        super().__init__(parent)
        self.account = account or {"account_id": 1, "full_name": "Khách hàng"}
        self.all_orders:  list[dict] = []   # grouped order objects
        self.current_filter = "all"

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(16)

        # Header
        header_lay = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title_col.addWidget(lbl("Lịch sử Đặt vé của bạn", 24, 800, C_DARK))
        title_col.addWidget(lbl("Quản lý danh sách chuyến bay và trạng thái vé điện tử", 13, 400, C_GRAY))
        header_lay.addLayout(title_col)
        header_lay.addStretch()
        root.addLayout(header_lay)

        # Stats bar
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(16)
        root.addLayout(self.stats_layout)

        # Filter + search bar
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(12)

        self.btn_all     = QPushButton("Tất cả đơn hàng")
        self.btn_done    = QPushButton("Đã xác nhận")
        self.btn_pending = QPushButton("Chờ thanh toán")

        for b in [self.btn_all, self.btn_done, self.btn_pending]:
            b.setFixedHeight(36)
            b.setCursor(Qt.PointingHandCursor)

        ctrl_row.addWidget(self.btn_all)
        ctrl_row.addWidget(self.btn_done)
        ctrl_row.addWidget(self.btn_pending)
        ctrl_row.addSpacing(20)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm theo mã bay, điểm đi, điểm đến, mã PNR...")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background: {C_WHITE}; border: 1.5px solid {C_BORDER};
                border-radius: 10px; padding: 0 14px; font-size: 13px; color: {C_TEXT};
            }}
            QLineEdit:focus {{ border-color: {C_RED}; }}
        """)
        self.search_input.textChanged.connect(self._apply_filter_and_search)
        ctrl_row.addWidget(self.search_input, 1)
        root.addLayout(ctrl_row)

        # Scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background:transparent; border:none;")
        root.addWidget(self.scroll, 1)

        self.list_container = QWidget()
        self.list_container.setStyleSheet("background:transparent;")
        self.list_lay = QVBoxLayout(self.list_container)
        self.list_lay.setContentsMargins(0, 4, 0, 10)
        self.list_lay.setSpacing(12)
        self.scroll.setWidget(self.list_container)

        self.empty_lbl = lbl("Chưa có đơn đặt vé nào phù hợp.", 14, 500, C_GRAY)
        self.empty_lbl.setAlignment(Qt.AlignCenter)
        self.empty_lbl.setContentsMargins(0, 60, 0, 60)
        self.list_lay.addWidget(self.empty_lbl)

        self.btn_all.clicked.connect(lambda: self._set_filter("all"))
        self.btn_done.clicked.connect(lambda: self._set_filter("confirmed"))
        self.btn_pending.clicked.connect(lambda: self._set_filter("pending"))

        self.refresh()

    # ─────────────────────────────────────────────────────────────────────────
    def refresh(self, current_account: dict | None = None):
        """Re-fetch raw rows, group by PNR, rebuild UI."""
        if current_account:
            self.account = current_account

        username = self.account.get("username", "guest")
        raw_rows = get_booking_history_by_user(username)

        # Group individual seat rows into consolidated order objects
        self.all_orders = _group_by_pnr(raw_rows)

        self._update_stats_header()
        self._set_filter("all")

    # ─────────────────────────────────────────────────────────────────────────
    def _update_stats_header(self):
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        confirmed_orders = [
            o for o in self.all_orders
            if str(o.get("status", "")).lower() in ("confirmed", "completed", "paid")
        ]
        total_orders  = len(confirmed_orders)
        total_tickets = sum(o.get("ticket_count", 1) for o in confirmed_orders)
        total_spent   = sum(o.get("total_amount", 0) for o in confirmed_orders)
        pending_pay   = len([
            o for o in self.all_orders
            if str(o.get("status", "")).lower() == "pending"
        ])

        self.stats_layout.addWidget(StatsCard("Đơn hàng thành công", f"{total_orders} đơn", "✈", C_GREEN))
        self.stats_layout.addWidget(StatsCard("Tổng vé đã mua", f"{total_tickets} vé", "🎫", C_BLUE))
        self.stats_layout.addWidget(StatsCard("Tổng tiền tích lũy", f"${total_spent:,.0f}", "🪪", C_RED))
        self.stats_layout.addWidget(StatsCard("Chờ xử lý", f"{pending_pay} giao dịch", "⏳", C_ORANGE))

    # ─────────────────────────────────────────────────────────────────────────
    def _set_filter(self, filter_type: str):
        self.current_filter = filter_type

        active_style = (f"background:{C_RED}; color:{C_WHITE}; border:none;"
                        f"border-radius:8px; font-weight:700; padding:0 14px;")
        normal_style = (f"background:{C_WHITE}; color:{C_MID};"
                        f"border:1.5px solid {C_BORDER}; border-radius:8px;"
                        f"font-weight:500; padding:0 14px;")

        self.btn_all.setStyleSheet(    active_style if filter_type == "all"       else normal_style)
        self.btn_done.setStyleSheet(   active_style if filter_type == "confirmed" else normal_style)
        self.btn_pending.setStyleSheet(active_style if filter_type == "pending"   else normal_style)

        self._apply_filter_and_search()

    # ─────────────────────────────────────────────────────────────────────────
    def _apply_filter_and_search(self):
        # Clear existing order cards
        for i in reversed(range(self.list_lay.count())):
            item = self.list_lay.takeAt(i)
            if item.widget():
                w = item.widget()
                if w != self.empty_lbl:
                    w.deleteLater()

        search_txt = self.search_input.text().strip().lower()
        visible_count = 0

        for order in self.all_orders:
            status = str(order.get("status", "pending")).lower()

            # Status filter
            if self.current_filter == "confirmed" and status not in ("confirmed", "completed", "paid"):
                continue
            if self.current_filter == "pending" and status != "pending":
                continue

            # Text search: PNR, flight code, departure, destination
            haystack = " ".join([
                str(order.get("base_pnr", "")),
                str(order.get("flight_code", "")),
                str(order.get("departure", "")),
                str(order.get("destination", "")),
                " ".join(order.get("seats", [])),
            ]).lower()

            if search_txt and search_txt not in haystack:
                continue

            card = OrderCard(order, cancel_callback=self.handle_cancel_ticket)
            self.list_lay.addWidget(card)
            visible_count += 1

        self.list_lay.addStretch()
        self.empty_lbl.setVisible(visible_count == 0)

    # ─────────────────────────────────────────────────────────────────────────────
    def handle_cancel_ticket(self, booking_ids: list[int]): # <--- NHẬN MẢNG ID
        """Ask for confirmation, cancel the booking, then refresh the list."""
        reply = QMessageBox.question(
            self, "Xác nhận hủy vé",
            "Bạn có chắc muốn hủy đơn hàng này? Tất cả ghế trong đơn sẽ bị hủy.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            success = True
            for bid in booking_ids:                     # <--- VÒNG LẶP HỦY TỪNG VÉ
                if not cancel_booking(bid):
                    success = False
            
            if success:
                QMessageBox.information(self, "Thành công", "Đã hủy toàn bộ vé thành công.")
            else:
                QMessageBox.warning(self, "Lỗi", "Có lỗi xảy ra khi hủy một số vé.")
            self.refresh()


# ─────────────────────────────────────────────────────────────────────────────
# Standalone test
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    test_account = {
        "account_id": 1,
        "full_name":  "Lê Văn Quân",
        "username":   "quanlv",
        "email":      "quanle@gmail.com",
    }

    window = QWidget()
    window.setWindowTitle("JetJet Air — Kiểm tra Lịch sử đặt chỗ")
    window.resize(1100, 750)
    window.setStyleSheet(f"background: {C_BG};")

    layout = QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(HistoryPage(account=test_account))

    window.show()
    sys.exit(app.exec())