"""
seat_selection.py
-----------------
Seat Selection Page for the booking application.
Fixed: Dynamic data loading via update_page(), removed eager loading in __init__,
and corrected the OCCUPIED_FALLBACK logic.
"""
from __future__ import annotations
import random, sys, re
from PySide6.QtCore import Qt, Signal, QRect, QRectF
from PySide6.QtGui import (QColor, QPainter, QBrush, QPen, QPainterPath,
                            QFont, QLinearGradient)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QScrollArea, QAbstractButton,
    QSizePolicy, QSpacerItem
)
from booking_app.ui.pages.booking_shared import (lbl, h_sep, card_style, red_btn, page_header,
                             NavBar, C_RED, C_RED2, C_DARK, C_WHITE,
                             C_BG, C_BORDER, C_TEXT, C_MID, C_GRAY,
                             C_LGRAY, C_GREEN, C_ORANGE)

SEAT_PRICE = 25          # USD / ghế
MAX_SEATS  = 1           # Strict: 1 seat per checkout to prevent multi-row DB duplicates
COLS       = ["A","B","C","D","E","F"]

# Fallback data ONLY for database errors
def _gen_occupied() -> set[tuple[int,str]]:
    occ: set[tuple[int,str]] = set()
    rng = random.Random(42)
    for r in range(1, 36):
        for c in COLS:
            if rng.random() < 0.3:
                occ.add((r, c))
    return occ

OCCUPIED_FALLBACK: set[tuple[int,str]] = _gen_occupied()
EXIT_ROWS = {11, 12}

class SeatBtn(QAbstractButton):
    ST_EMPTY    = 0
    ST_OCCUPIED = 1
    ST_SELECTED = 2
    ST_PENDING  = 3

    seat_toggled = Signal(int, str, bool)

    _COLORS = {
        ST_EMPTY:    ("#F0F1F8", "#DDE0ED", "#9B9BB4"),
        ST_OCCUPIED: (C_DARK,   "none",    C_WHITE),
        ST_SELECTED: (C_RED,    "none",    C_WHITE),
        ST_PENDING:  (C_ORANGE, "none",    C_WHITE),
    }

    def __init__(self, row: int, col: str, status: int = ST_EMPTY, parent=None):
        super().__init__(parent)
        self._row    = row
        self._col    = col
        self._status = status
        self.setFixedSize(42, 46)
        if status != self.ST_OCCUPIED:
            self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, e):
        if self._status == self.ST_OCCUPIED:
            return
        if self._status == self.ST_SELECTED:
            self._status = self.ST_EMPTY
            self.seat_toggled.emit(self._row, self._col, False)
        elif self._status == self.ST_EMPTY:
            self._status = self.ST_SELECTED
            self.seat_toggled.emit(self._row, self._col, True)
        self.update()

    def force_status(self, st: int):
        self._status = st
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        bg_hex, bdr_hex, fg_hex = self._COLORS[self._status]

        p.setPen(QPen(QColor(bdr_hex), 1.5) if bdr_hex != "none" else Qt.NoPen)
        p.setBrush(QBrush(QColor(bg_hex)))
        pp = QPainterPath(); pp.addRoundedRect(1, 1, w-2, h-2, 9, 9)
        p.drawPath(pp)

        fg = QColor(fg_hex)
        p.setPen(QPen(fg, 1.5)); p.setBrush(Qt.NoBrush)
        bx, by = int(w*0.21), int(h*0.06)
        bw, bh = int(w*0.58), int(h*0.42)
        p.drawRoundedRect(bx, by, bw, bh, 3, 3)
        sx, sy = int(w*0.14), int(h*0.53)
        sw, sh = int(w*0.72), int(h*0.22)
        p.drawRoundedRect(sx, sy, sw, sh, 3, 3)
        f = QFont(); f.setPointSize(8); f.setWeight(QFont.Bold)
        p.setFont(f); p.setPen(QPen(fg))
        p.drawText(0, int(h*0.77), w, int(h*0.22), Qt.AlignCenter, self._col)

class SeatRow(QWidget):
    seat_toggled = Signal(int, str, bool)

    def __init__(self, row: int, parent=None):
        super().__init__(parent)
        self._row   = row
        self._btns: dict[str, SeatBtn] = {}
        self.setFixedHeight(52)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 4, 8, 4)
        lay.setSpacing(6)

        rn = QLabel(str(row)); rn.setFixedWidth(24); rn.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        rn.setStyleSheet(f"font-size:12px;font-weight:600;color:{C_GRAY};")
        lay.addWidget(rn); lay.addSpacing(4)

        for col in ["A","B","C"]:
            btn = SeatBtn(row, col, SeatBtn.ST_EMPTY)
            btn.seat_toggled.connect(self.seat_toggled)
            self._btns[col] = btn
            lay.addWidget(btn)

        aisle = QLabel(str(row)); aisle.setFixedWidth(28); aisle.setAlignment(Qt.AlignCenter)
        aisle.setStyleSheet(f"font-size:11px;color:#D0D1E0;")
        lay.addSpacing(8); lay.addWidget(aisle); lay.addSpacing(8)

        for col in ["D","E","F"]:
            btn = SeatBtn(row, col, SeatBtn.ST_EMPTY)
            btn.seat_toggled.connect(self.seat_toggled)
            self._btns[col] = btn
            lay.addWidget(btn)

    def update_seats(self, occupied: set, selected: set):
        for col, btn in self._btns.items():
            if (self._row, col) in occupied:
                btn.force_status(SeatBtn.ST_OCCUPIED)
            elif (self._row, col) in selected:
                btn.force_status(SeatBtn.ST_SELECTED)
            else:
                btn.force_status(SeatBtn.ST_EMPTY)

class SelectedItem(QWidget):
    removed = Signal(int, str)

    def __init__(self, row: int, col: str, price: int, parent=None):
        super().__init__(parent)
        self._row, self._col = row, col
        self.setFixedHeight(72)
        self.setStyleSheet(f"background:{C_LGRAY};border-radius:12px;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        seat_lbl = lbl(f"{row}{col}", 22, 900, C_RED)
        seat_lbl.setFixedWidth(52)
        lay.addWidget(seat_lbl)

        info_col = QVBoxLayout(); info_col.setSpacing(3)
        info_col.addWidget(lbl("HẠNG PHỔ THÔNG", 11, 600, C_GRAY, 0.5))
        info_col.addWidget(lbl("Tiêu chuẩn", 13, 600, C_TEXT))
        lay.addLayout(info_col)
        lay.addStretch()

        price_lbl = lbl(f"${price}", 14, 700, C_TEXT)
        lay.addWidget(price_lbl)

        rm = QPushButton("✕"); rm.setFixedSize(26, 26)
        rm.setCursor(Qt.PointingHandCursor)
        rm.setStyleSheet(f"QPushButton{{background:#E0E1ED;border:none;border-radius:13px;"
                         f"font-size:12px;color:{C_GRAY};}}"
                         f"QPushButton:hover{{background:#FFCDD2;color:{C_RED};}}")
        rm.clicked.connect(lambda: self.removed.emit(self._row, self._col))
        lay.addWidget(rm)

class SelectedPanel(QWidget):
    confirm  = Signal(list)
    deselect = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(card_style(20))
        self._items: dict[tuple, SelectedItem] = {}

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(22, 22, 22, 22)
        self._root.setSpacing(0)

        self._root.addWidget(lbl("Ghế đã chọn", 18, 800, C_TEXT))
        self._root.addSpacing(16)

        self._list_w = QWidget(); self._list_w.setStyleSheet("background:transparent;")
        self._list_l = QVBoxLayout(self._list_w)
        self._list_l.setContentsMargins(0,0,0,0); self._list_l.setSpacing(10)
        self._root.addWidget(self._list_w)

        self._ph = lbl("Chưa chọn ghế nào.\nClick vào ghế để chọn.", 13, 400, C_GRAY)
        self._ph.setAlignment(Qt.AlignCenter)
        self._ph.setContentsMargins(0, 20, 0, 20)
        self._list_l.addWidget(self._ph)

        self._root.addSpacing(16)
        self._root.addWidget(h_sep())
        self._root.addSpacing(14)

        total_row = QHBoxLayout()
        total_row.addWidget(lbl("PHỤ PHÍ GHẾ NGỒI", 11, 700, C_GRAY, 1.0))
        total_row.addStretch()
        self._total_lbl = lbl("$0", 22, 800, C_TEXT)
        total_row.addWidget(self._total_lbl)
        self._root.addLayout(total_row)
        self._root.addSpacing(16)

        self._confirm_btn = red_btn("XÁC NHẬN CHỖ NGỒI  →", 50)
        self._confirm_btn.setEnabled(False)
        self._confirm_btn.clicked.connect(lambda: self.confirm.emit(list(self._items.keys())))
        self._root.addWidget(self._confirm_btn)
        self._root.addSpacing(16)

        warn = QWidget()
        warn.setStyleSheet("background:#FFFBEB;border:1px solid #FDE68A;border-radius:10px;")
        wl = QHBoxLayout(warn); wl.setContentsMargins(14,12,14,12); wl.setSpacing(10)
        wl.addWidget(lbl("⚠", 14, 400, C_ORANGE))
        wl.addWidget(lbl("Ghế lối thoát hiểm yêu cầu hành khách có sức khỏe và khả năng hỗ trợ trong trường hợp khẩn cấp.", 11, 400, C_MID))
        self._root.addWidget(warn)
        self._root.addStretch()

    def add_seat(self, row: int, col: str):
        key = (row, col)
        if key in self._items or len(self._items) >= MAX_SEATS: return
        self._ph.hide()
        item = SelectedItem(row, col, SEAT_PRICE)
        item.removed.connect(self.remove_seat)
        self._items[key] = item
        self._list_l.addWidget(item)
        self._refresh_total()

    def remove_seat(self, row: int, col: str):
        key = (row, col)
        if key not in self._items: return
        item = self._items.pop(key)
        self._list_l.removeWidget(item)
        item.deleteLater()
        if not self._items: self._ph.show()
        self._refresh_total()
        self.deselect.emit(row, col)

    def clear(self):
        for key, item in list(self._items.items()):
            self._list_l.removeWidget(item)
            item.deleteLater()

        self._items.clear()

        self._ph.show()
        self._refresh_total()

    def _refresh_total(self):
        total = len(self._items) * SEAT_PRICE
        self._total_lbl.setText(f"${total}")
        self._confirm_btn.setEnabled(len(self._items) > 0)

    def selected_seats(self) -> list[tuple[int,str]]:
        return list(self._items.keys())

class SeatMapWidget(QWidget):
    seat_toggled = Signal(int, str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{C_WHITE};border-radius:16px;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)

        hdr_w = QWidget(); hdr_w.setStyleSheet("background:transparent;")
        hdr_l = QVBoxLayout(hdr_w); hdr_l.setContentsMargins(20,20,20,12); hdr_l.setSpacing(12)

        cockpit = QLabel("TỔ LÁI / COCKPIT")
        cockpit.setAlignment(Qt.AlignCenter)
        cockpit.setFixedHeight(44)
        cockpit.setStyleSheet(f"font-size:11px;font-weight:600;color:{C_GRAY};"
                              f"background:{C_LGRAY};border:1.5px solid {C_BORDER};"
                              f"border-radius:22px;letter-spacing:2px;")
        hdr_l.addWidget(cockpit)

        legend_row = QHBoxLayout(); legend_row.setSpacing(20)
        legend_row.setAlignment(Qt.AlignCenter)
        for color, label in [("#F0F1F8", "TRỐNG"), (C_ORANGE, "ĐANG CHỜ"), (C_RED, "ĐANG CHỌN"), (C_DARK, "ĐÃ ĐẶT")]:
            row = QHBoxLayout(); row.setSpacing(6)
            dot = QWidget(); dot.setFixedSize(14,14)
            dot.setStyleSheet(f"background:{color};border-radius:7px;{'border:1.5px solid #DDE0ED;' if color=='#F0F1F8' else ''}")
            row.addWidget(dot)
            row.addWidget(lbl(label, 11, 600, C_MID))
            legend_row.addLayout(row)
        hdr_l.addLayout(legend_row)
        outer.addWidget(hdr_w)
        outer.addWidget(h_sep())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent;border:none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        outer.addWidget(scroll, 1)

        grid_w = QWidget(); grid_w.setStyleSheet("background:transparent;")
        grid_l = QVBoxLayout(grid_w)
        grid_l.setContentsMargins(10,12,10,20); grid_l.setSpacing(0)

        self._rows: dict[int, SeatRow] = {}

        for row_num in range(1, 36):
            if row_num in EXIT_ROWS:
                ex = QLabel("✦  LỐI THOÁT HIỂM / EXIT ROW  ✦")
                ex.setAlignment(Qt.AlignCenter)
                ex.setFixedHeight(28)
                ex.setStyleSheet(f"font-size:10px;font-weight:700;color:{C_ORANGE};background:#FFF8E1;letter-spacing:1px;border-radius:6px;")
                grid_l.addSpacing(4); grid_l.addWidget(ex); grid_l.addSpacing(4)

            seat_row = SeatRow(row_num)
            seat_row.seat_toggled.connect(self.seat_toggled)
            self._rows[row_num] = seat_row
            grid_l.addWidget(seat_row)

        grid_l.addStretch()
        scroll.setWidget(grid_w)

    def update_map(self, occupied: set, selected: set):
        for row in self._rows.values():
            row.update_seats(occupied, selected)

    def force_deselect(self, row:int, col:str, occupied:set, selected:set):
        self.update_map(occupied, selected) 

class SeatMapPage(QWidget):
    proceed  = Signal(dict)
    go_back  = Signal()

    def __init__(self, ctx: dict | None = None, parent=None):
        super().__init__(parent)
        self.ctx = ctx or {}
        self.setStyleSheet(f"background:{C_BG};")
        self._occupied=set()

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 28)
        root.setSpacing(20)

        root.addLayout(page_header(
            "Sơ đồ Chỗ ngồi",
            "Bước 5: Lựa chọn vị trí yêu thích",
            on_back=self.go_back,
        ))

        body = QHBoxLayout(); body.setSpacing(20)

        self._map = SeatMapWidget()
        self._map.seat_toggled.connect(self._on_toggle)
        body.addWidget(self._map, 62)

        right_w = QWidget(); right_w.setStyleSheet("background:transparent;")
        rl = QVBoxLayout(right_w); rl.setContentsMargins(0,0,0,0)
        self._panel = SelectedPanel()
        self._panel.confirm.connect(self._on_confirm)
        self._panel.deselect.connect(self._on_panel_deselect)
        rl.addWidget(self._panel); rl.addStretch()
        body.addWidget(right_w, 38)

        root.addLayout(body, 1)

    def update_page(self):
        flight_info = self.ctx.get("flight")
        flight_id = None

        if flight_info:
            flight_id = (
                flight_info.get("flight_id")
                or flight_info.get("fid")
            )

        self._panel.clear()

        self._occupied = self._get_occupied_seats(flight_id)

        self._map.update_map(
            self._occupied,
            set()
        )

    def _get_occupied_seats(self, flight_id: int | None) -> set[tuple[int, str]]:
        """
        Build the full occupied-seat set for the seat map.

        Strategy:
        1. Fetch ACTUAL reserved seats from the DB via get_seats_by_flight().
        2. Calculate how many seats SHOULD look occupied based on the flight's
           occupancy percentage (drawn from ctx), spread across ~210 seats.
        3. Use random.Random(flight_id) for a *deterministic* fake-occupancy
           pattern so the map looks identical on every load for the same flight.
        4. Merge the fake set with the real DB set and return the union.
        """
        TOTAL_SEATS = 35 * 6  # 35 rows × 6 cols = 210 seats

        # ── Step 1: real reserved seats from DB ──────────────────────────────
        db_occ: set[tuple[int, str]] = set()
        if flight_id is not None:
            try:
                from shared.services.seat_service import get_seats_by_flight
                seats = get_seats_by_flight(flight_id)
                if seats is not None:
                    for s in seats:
                        if s.is_reserved:
                            match = re.match(r"(\d+)([A-F])", s.seat_number)
                            if match:
                                db_occ.add((int(match.group(1)), match.group(2)))
            except Exception as e:
                print(f"[SeatMap] DB error: {e}")

        # ── Step 2: determine target occupancy count ──────────────────────────
        flight_info = self.ctx.get("flight", {}) or {}
        occupancy_pct = flight_info.get("occupancy_percent", 0)
        target_occupied = int(TOTAL_SEATS * occupancy_pct / 100)

        # ── Step 3: deterministic fake-occupied set seeded by flight_id ───────
        fake_occ: set[tuple[int, str]] = set()
        if flight_id is not None and target_occupied > 0:
            rng = random.Random(flight_id)
            all_seats = [(r, c) for r in range(1, 36) for c in COLS]
            rng.shuffle(all_seats)
            for seat in all_seats:
                if len(fake_occ) >= target_occupied:
                    break
                fake_occ.add(seat)

        # ── Step 4: merge fake + real ─────────────────────────────────────────
        return fake_occ | db_occ

    def _on_toggle(self, row: int, col: str, selected: bool):
        if selected:
            if len(self._panel.selected_seats()) >= MAX_SEATS:
                self._map.update_map(
                    self._occupied,
                    set(self._panel.selected_seats())
                )
                return
            self._panel.add_seat(row, col)
        else:
            self._panel.remove_seat(row, col)

    def _on_panel_deselect(self, row: int, col: str):
        self._map.update_map(
            self._occupied,
            set(self._panel.selected_seats())
        )

    def _on_confirm(self, seats: list):
        self.ctx["seats"]      = seats
        self.ctx["seat_fee"]   = len(seats) * SEAT_PRICE
        self.ctx["seat_labels"] = [f"{r}{c}" for r, c in seats]
        self.proceed.emit(self.ctx)


if __name__ == "__main__":
    app = QApplication(sys.argv); app.setStyle("Fusion")
    win = QMainWindow()
    win.setWindowTitle("JetJet Air — Sơ đồ Chỗ ngồi")
    win.resize(1380, 860)
    w = QWidget(); lay = QVBoxLayout(w); lay.setContentsMargins(0,0,0,0); lay.setSpacing(0)
    nav = NavBar(0)
    page = SeatMapPage()
    lay.addWidget(nav)
    lay.addWidget(page)
    win.setCentralWidget(w); win.show()
    page.update_page() # Call manually for demo
    sys.exit(app.exec())