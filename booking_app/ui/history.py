from __future__ import annotations
import sys
import os
from datetime import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QPainterPath
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QFrame, QSizePolicy
)
from booking_app.ui.pages.booking_shared import (lbl, h_sep, card_style, 
                             C_RED, C_DARK, C_WHITE, C_BG,
                             C_BORDER, C_TEXT, C_MID, C_GRAY, C_LGRAY,
                             C_GREEN, C_BLUE, C_ORANGE)

from shared.services.booking_service import get_booking_history_by_user


# ─────────────────────────────────────────────────────────────────────────────
# Thẻ Thống Kê Nhỏ (Điểm cộng nâng cao)
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
# Thẻ Lịch Sử Từng Vé Chuyến Bay (Booking History Row Card)
# ─────────────────────────────────────────────────────────────────────────────
class HistoryTicketCard(QWidget):
    def __init__(self, booking: dict, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(14))
        self.setFixedHeight(105)
        
        main_lay = QHBoxLayout(self)
        main_lay.setContentsMargins(20, 15, 20, 15)
        main_lay.setSpacing(15)
        
        # 1. Trạng thái & Mã đặt chỗ
        status_col = QVBoxLayout()
        status_col.setSpacing(6)
        status_col.setAlignment(Qt.AlignVCenter)
        
        status = str(booking.get("status", "pending")).lower()
        st_text, st_color, st_bg = " CHỜ THANH TOÁN ", C_ORANGE, "#FFF8E1"
        if status in ("confirmed", "đã xác nhận", "completed"):
            st_text, st_color, st_bg = " ĐÃ XÁC NHẬN ", C_GREEN, "#E8F5E9"
        elif status in ("cancelled", "đã hủy"):
            st_text, st_color, st_bg = " ĐÃ HỦY VÉ ", C_RED, "#FFEBEE"
            
        st_lbl = lbl(st_text, 10, 800, st_color)
        st_lbl.setStyleSheet(f"background:{st_bg}; border-radius:6px; padding:4px 6px;")
        st_lbl.setAlignment(Qt.AlignCenter)
        
        status_col.addWidget(st_lbl)
        status_col.addWidget(lbl(f"Mã: #{booking.get('booking_id', '000')}", 12, 700, C_TEXT))
        main_lay.addLayout(status_col)
        
        main_lay.addSpacing(10)
        
        # 2. Thông tin chặng bay chính
        route_col = QVBoxLayout()
        route_col.setSpacing(4)
        route_col.setAlignment(Qt.AlignVCenter)
        
        route_title = QHBoxLayout()
        route_title.setSpacing(8)
        route_title.addWidget(lbl(booking.get("departure", "SGN"), 18, 800, C_TEXT))
        route_title.addWidget(lbl("➔", 14, 400, C_RED))
        route_title.addWidget(lbl(booking.get("destination", "HAN"), 18, 800, C_TEXT))
        route_title.addStretch()
        
        route_col.addLayout(route_title)
        route_col.addWidget(lbl(f"Chuyến bay: {booking.get('flight_code', 'JJ-—')}  |  Ghế: {booking.get('seats') or 'Chưa chọn'}", 12, 500, C_MID))
        main_lay.addLayout(route_col, 2)
        
        # 3. Thời gian bay & Đặt chỗ
        time_col = QVBoxLayout()
        time_col.setSpacing(4)
        time_col.setAlignment(Qt.AlignVCenter)
        time_col.addWidget(lbl(f"📅 Khởi hành: {booking.get('departure_time', '—')}", 12, 600, C_TEXT))
        time_col.addWidget(lbl(f"Ngày đặt: {booking.get('booking_date', '—')}", 11, 400, C_GRAY))
        main_lay.addLayout(time_col, 2)
        
        # 4. Giá tiền thanh toán
        price_col = QVBoxLayout()
        price_col.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        price_col.addWidget(lbl(f"${booking.get('total_amount', 0)}", 22, 900, C_RED))
        price_col.addWidget(lbl("Tổng hóa đơn", 10, 500, C_GRAY))
        main_lay.addLayout(price_col)


# ─────────────────────────────────────────────────────────────────────────────
# HistoryPage Layout Chính
# ─────────────────────────────────────────────────────────────────────────────
class HistoryPage(QWidget):
    def __init__(self, account: dict | None = None, parent=None):
        super().__init__(parent)
        self.account = account or {"account_id": 1, "full_name": "Khách hàng"}
        self.all_bookings: list[dict] = []
        self.current_filter = "all"
        
        # Giao diện chính
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(16)
        
        # Tiêu đề trang (Bỏ chữ thoát portal hoàn toàn)
        header_lay = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(4)
        title_col.addWidget(lbl("Lịch sử Đặt vé của bạn", 24, 800, C_DARK))
        title_col.addWidget(lbl("Quản lý danh sách chuyến bay và trạng thái vé điện tử", 13, 400, C_GRAY))
        header_lay.addLayout(title_col)
        header_lay.addStretch()
        root.addLayout(header_lay)
        
        # Thanh Thống Kê Đỉnh Đầu
        self.stats_layout = QHBoxLayout()
        self.stats_layout.setSpacing(16)
        root.addLayout(self.stats_layout)
        
        # Thanh Điều Khiển: Gồm bộ lọc trạng thái + Thanh tìm kiếm (Search)
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(12)
        
        # Nhóm Nút Bộ Lọc (Filter)
        self.btn_all = QPushButton("Tất cả chuyến")
        self.btn_done = QPushButton("Đã xác nhận")
        self.btn_pending = QPushButton("Chờ thanh toán")
        
        for b in [self.btn_all, self.btn_done, self.btn_pending]:
            b.setFixedHeight(36)
            b.setCursor(Qt.PointingHandCursor)
        
        ctrl_row.addWidget(self.btn_all)
        ctrl_row.addWidget(self.btn_done)
        ctrl_row.addWidget(self.btn_pending)
        ctrl_row.addSpacing(20)
        
        # Hộp tìm kiếm (Search box)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Tìm theo mã bay, điểm đi, điểm đến...")
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
        
        # Khu vực Scroll Area hiển thị danh sách vé
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background:transparent; border:none;")
        root.addWidget(self.scroll, 1)
        
        # Widget chứa danh sách bên trong Scroll
        self.list_container = QWidget()
        self.list_container.setStyleSheet("background:transparent;")
        self.list_lay = QVBoxLayout(self.list_container)
        self.list_lay.setContentsMargins(0, 4, 0, 10)
        self.list_lay.setSpacing(12)
        self.scroll.setWidget(self.list_container)
        
        # Nhãn thông báo rỗng dạng Card lớn ẩn mặc định
        self.empty_lbl = lbl("Chưa có dữ liệu đặt vé nào phù hợp với tìm kiếm của bạn.", 14, 500, C_GRAY)
        self.empty_lbl.setAlignment(Qt.AlignCenter)
        self.empty_lbl.setContentsMargins(0, 60, 0, 60)
        self.list_lay.addWidget(self.empty_lbl)
        
        # Kết nối sự kiện bộ lọc
        self.btn_all.clicked.connect(lambda: self._set_filter("all"))
        self.btn_done.clicked.connect(lambda: self._set_filter("confirmed"))
        self.btn_pending.clicked.connect(lambda: self._set_filter("pending"))
        
        # Đọc dữ liệu lần đầu tiên
        self.refresh()

    def refresh(self, current_account: dict | None = None):
        """Hàm đồng bộ và tải lại toàn bộ dữ liệu từ Service Layer"""
        if current_account:
            self.account = current_account
            
        username = self.account.get("username", "guest")
        self.all_bookings = get_booking_history_by_user(username)

        # Cập nhật Widgets thống kê đỉnh đầu
        self._update_stats_header()
        # Áp dụng hiển thị danh sách lọc lên màn hình
        self._set_filter("all")

    def _update_stats_header(self):
        """Xóa và dựng lại bảng thống kê nâng cao thực tế"""
        # Xóa các widget cũ trong thanh thống kê
        while self.stats_layout.count():
            item = self.stats_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        total_trips = len([b for b in self.all_bookings if str(b.get("status")).lower() in ("confirmed", "completed", "paid")])
        total_spent = sum(b.get("total_amount", 0) for b in self.all_bookings if str(b.get("status")).lower() in ("confirmed", "completed", "paid"))
        pending_pay = len([b for b in self.all_bookings if str(b.get("status")).lower() == "pending"])
        
        self.stats_layout.addWidget(StatsCard("Chuyến bay thành công", f"{total_trips} chuyến", "✈", C_GREEN))
        self.stats_layout.addWidget(StatsCard("Tổng tiền tích lũy", f"${total_spent}", "🪪", C_RED))
        self.stats_layout.addWidget(StatsCard("Chờ xử lý thanh toán", f"{pending_pay} giao dịch", "⏳", C_ORANGE))

    def _set_filter(self, filter_type: str):
        self.current_filter = filter_type
        
        # Đồng bộ đổi màu style cho 3 nút bấm trạng thái giống hệt CSS chuyên nghiệp
        active_style = f"background:{C_RED}; color:{C_WHITE}; border:none; border-radius:8px; font-weight:700; padding:0 14px;"
        normal_style = f"background:{C_WHITE}; color:{C_MID}; border:1.5px solid {C_BORDER}; border-radius:8px; font-weight:500; padding:0 14px;"
        
        self.btn_all.setStyleSheet(active_style if filter_type == "all" else normal_style)
        self.btn_done.setStyleSheet(active_style if filter_type == "confirmed" else normal_style)
        self.btn_pending.setStyleSheet(active_style if filter_type == "pending" else normal_style)
        
        self._apply_filter_and_search()

    def _apply_filter_and_search(self):
        """Hành động lọc danh sách và tìm kiếm text song song"""
        # Xóa toàn bộ các card cũ ra khỏi Layout (Trừ nhãn empty_lbl)
        for i in reversed(range(self.list_lay.count())):
            item = self.list_lay.itemAt(i)
            if item and item.widget() and item.widget() != self.empty_lbl:
                w = item.widget()
                w.setParent(None)
                w.deleteLater()
                
        search_txt = self.search_input.text().strip().lower()
        visible_count = 0
        
        for b in self.all_bookings:
            status = str(b.get("status", "pending")).lower()
            
            # Khớp điều kiện bộ lọc nút bấm trước
            if self.current_filter == "confirmed" and status not in ("confirmed", "completed", "paid"):
                continue
            if self.current_filter == "pending" and status != "pending":
                continue
                
            # Khớp tiếp điều kiện thanh tìm kiếm (Mã bay, Điểm đi, Điểm đến)
            match_search = (
                search_txt in str(b.get("flight_code", "")).lower() or
                search_txt in str(b.get("departure", "")).lower() or
                search_txt in str(b.get("destination", "")).lower() or
                search_txt in str(b.get("booking_id", "")).lower()
            )
            
            if not match_search and search_txt != "":
                continue
                
            # Đạt mọi điều kiện -> Tiến hành vẽ Card lên giao diện
            card = HistoryTicketCard(b)
            self.list_lay.addWidget(card)
            visible_count += 1
            
        # Thêm khoảng đệm co dãn tự động ở đáy danh sách
        self.list_lay.addStretch()
        
        # Ẩn/Hiện thông báo rỗng nếu không tìm thấy vé nào
        self.empty_lbl.setVisible(visible_count == 0)


# ─────────────────────────────────────────────────────────────────────────────
# Kiểm thử độc lập trang History
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Tạo Tk ảo của khách hàng đăng nhập thử nghiệm
    test_account = {"account_id": 1, "full_name": "Lê Văn Quân", "username": "quanlv", "email": "quanle@gmail.com"}
    
    window = QWidget()
    window.setWindowTitle("JetJet Air — Kiểm tra Lịch sử đặt chỗ")
    window.resize(1100, 750)
    window.setStyleSheet(f"background: {C_BG};")
    
    layout = QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)
    
    page = HistoryPage(account=test_account)
    layout.addWidget(page)
    
    window.show()
    sys.exit(app.exec())