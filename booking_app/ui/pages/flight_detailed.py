from __future__ import annotations
import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QSizePolicy, QPushButton
)
from booking_app.ui.pages.booking_shared import (
    lbl, h_sep, card_style, red_btn, page_header,
    C_RED, C_DARK, C_WHITE, C_BG, C_BORDER, C_TEXT, C_MID, C_GRAY
)

class FlightDetailCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style())
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(24, 24, 24, 24)
        self._lay.setSpacing(16)

    def update_data(self, ctx: dict):
        while self._lay.count():
            child = self._lay.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        
        # SỬA LỖI Ở ĐÂY: Dùng `or {}` để đảm bảo luôn là một Dictionary, tránh bị None
        flight = ctx.get("flight") or {}
        ret_flight = ctx.get("flight_return") or {}
        is_rt = ctx.get("is_roundtrip", False)

        title = lbl("Chi tiết Hành trình", 18, 800, C_TEXT)
        self._lay.addWidget(title)
        self._lay.addWidget(h_sep())

        # Render Chuyến đi (Chỉ render khi thực sự đã chọn chuyến bay)
        if flight:
            self._build_flight_info(flight, "CHUYẾN ĐI")

        # Render Chuyến về nếu là Khứ hồi
        if is_rt and ret_flight:
            self._lay.addSpacing(10)
            self._lay.addWidget(h_sep())
            self._lay.addSpacing(10)
            self._build_flight_info(ret_flight, "CHUYẾN VỀ")
        
        self._lay.addStretch()

    def _build_flight_info(self, f: dict, title: str):
        self._lay.addWidget(lbl(title, 14, 800, C_RED))
        
        row1 = QHBoxLayout()
        row1.addWidget(lbl(f.get("code", "N/A"), 16, 800, C_DARK))
        row1.addStretch()
        row1.addWidget(lbl(f.get("aircraft", "AIRBUS"), 12, 500, C_GRAY))
        self._lay.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(lbl(f"{f.get('dep_t', '--:--')} ➔ {f.get('arr_t', '--:--')}", 20, 800, C_TEXT))
        row2.addStretch()
        self._lay.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(lbl(f"Từ {f.get('dep')} đến {f.get('dst')}", 13, 500, C_MID))
        row3.addStretch()
        self._lay.addLayout(row3)

class CostCard(QFrame):
    proceed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ctx = {}
        self.setStyleSheet(card_style())
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(24, 24, 24, 24)
        self._lay.setSpacing(12)

    def update_data(self, ctx: dict):
        self.ctx = ctx
        while self._lay.count():
            child = self._lay.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_layout(child.layout())

        self._lay.addWidget(lbl("Tóm tắt Chi phí", 18, 800, C_TEXT))
        self._lay.addSpacing(8)

        is_rt = ctx.get("is_roundtrip", False)
        multiplier = 2 if is_rt else 1

        base_avg = ctx.get("base_price", 0)
        base_total = base_avg * multiplier
        tax_total = 45 * multiplier
        fee_total = 12 * multiplier
        grand_total = base_total + tax_total + fee_total

        def _row(k, v, b=False, c=C_TEXT):
            r = QHBoxLayout()
            r.addWidget(lbl(k, 13, 600 if b else 400, C_MID if not b else c))
            r.addStretch()
            r.addWidget(lbl(v, 13, 700 if b else 500, c))
            return r

        trip_type = "Giá vé (Khứ hồi)" if is_rt else "Giá vé (Một chiều)"
        self._lay.addLayout(_row(trip_type, f"${base_total:.0f}"))
        self._lay.addLayout(_row("Thuế sân bay", f"${tax_total:.0f}"))
        self._lay.addLayout(_row("Phí dịch vụ", f"${fee_total:.0f}"))

        self._lay.addSpacing(10)
        self._lay.addWidget(h_sep())
        self._lay.addSpacing(10)

        tot_r = QHBoxLayout()
        tot_r.addWidget(lbl("TỔNG CỘNG", 14, 800, C_DARK))
        tot_r.addStretch()
        tot_r.addWidget(lbl(f"${grand_total:.0f}", 24, 800, C_RED))
        self._lay.addLayout(tot_r)

        self._lay.addSpacing(16)
        btn = red_btn("TIẾP TỤC ➔", 46)
        btn.clicked.connect(self._on_proceed)
        self._lay.addWidget(btn)

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_layout(child.layout())

    def _on_proceed(self):
        # Tính toán lại tổng để pass đi
        mult = 2 if self.ctx.get("is_roundtrip") else 1
        self.ctx["total"] = (self.ctx.get("base_price", 0) + 45 + 12) * mult
        self.proceed.emit(self.ctx)

class FlightDetailPage(QWidget):
    proceed = Signal(dict)
    go_back = Signal()

    def __init__(self, ctx: dict | None = None, parent=None):
        super().__init__(parent)
        self.ctx = ctx or {}
        self.setStyleSheet(f"background:{C_BG};")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(20)
        
        root.addLayout(page_header("Chi tiết Hành trình", "Bước 2: Xác nhận lịch trình và chi phí", on_back=self.go_back))
        
        body = QHBoxLayout()
        body.setSpacing(20)
        
        self._card = FlightDetailCard()
        body.addWidget(self._card, 63)
        
        self._cost = CostCard()
        self._cost.proceed.connect(self.proceed.emit)
        body.addWidget(self._cost, 37)
        
        root.addLayout(body)
        root.addStretch()
        if self.ctx: self.update_page(self.ctx)

    def update_page(self, ctx: dict | None = None):
        if ctx: self.ctx = ctx
        if self.ctx:
            self._card.update_data(self.ctx)
            self._cost.update_data(self.ctx)