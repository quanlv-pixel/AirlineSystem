from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QBrush, QPainterPath
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QLineEdit, QScrollArea, QSizePolicy,
)

from shared.services.passenger_service import (
    get_all_passengers_enriched,
    search_passengers_enriched,
)
from shared.services.member_service import get_tier_for_spending, get_user_spending_from_db

# ── Màu sắc ──────────────────────────────────────────────────────────────────
RED       = "#E53935"
RED_LIGHT = "#FFEBEE"
WHITE     = "#FFFFFF"
BG_MAIN   = "#F6F7FB"
GRAY_TEXT = "#9AA4B2"
GRAY_BG   = "#F3F4F7"
TEXT_DARK = "#0F172A"
TEXT_MED  = "#475569"
BORDER    = "#ECEEF2"

_AVATAR_COLORS = [
    ("#E0E7FF", "#3730A3"),
    ("#FCE7F3", "#9D174D"),
    ("#D1FAE5", "#065F46"),
    ("#FEF3C7", "#92400E"),
    ("#F3E8FF", "#6B21A8"),
    ("#FFEDD5", "#9A3412"),
    ("#CFFAFE", "#155E75"),
]

# Tier badge style definitions
_TIER_BADGE = {
    "BẠCH KIM":   (TEXT_DARK, WHITE,     "Bạch Kim badge — dark bg white text"),
    "HẠNG VÀNG":  ("#AA7C11", "#FFF8DC", "Vàng badge — gold"),
    "HẠNG BẠC":   ("#4A5568", "#E2E8F0", "Bạc badge — silver"),
    "THÀNH VIÊN": ("#065F46", "#D1FAE5", "Thành viên badge — green"),
}

# Active session username for live spending (matches seeded account)
SESSION_USERNAME = "quanlv"


# ─────────────────────────────────────────────────────────────────────────────
# Progress bar tuỳ chỉnh
# ─────────────────────────────────────────────────────────────────────────────
class _ProgressBar(QWidget):
    def __init__(self, percent: int, color: str = RED, parent=None):
        super().__init__(parent)
        self._pct   = max(0, min(100, percent))
        self._color = QColor(color)
        self.setFixedHeight(6)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, _):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.Antialiasing)
            w, h = self.width(), self.height()
            r = h / 2
            track = QPainterPath()
            track.addRoundedRect(0, 0, w, h, r, r)
            p.fillPath(track, QBrush(QColor("#EEEEEE")))
            fw = int(w * self._pct / 100)
            if fw > 0:
                fill = QPainterPath()
                fill.addRoundedRect(0, 0, fw, h, r, r)
                p.fillPath(fill, QBrush(self._color))
        finally:
            p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Medal Icon
# ─────────────────────────────────────────────────────────────────────────────
class _MedalIcon(QWidget):
    def __init__(self, size: int = 64, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _):
        p = QPainter(self)
        try:
            p.setRenderHint(QPainter.Antialiasing)
            w, h = self.width(), self.height()
            red   = QColor(RED)
            red_l = QColor(RED_LIGHT)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(red_l))
            p.drawEllipse(0, 0, w, h)
            pen_red = __import__("PySide6.QtGui", fromlist=["QPen"]).QPen(red, 3)
            p.setPen(pen_red)
            p.setBrush(Qt.NoBrush)
            margin = int(w * 0.14)
            p.drawEllipse(margin, margin, w - margin * 2, h - margin * 2)
            p.setPen(__import__("PySide6.QtGui", fromlist=["QPen"]).QPen(red))
            f = __import__("PySide6.QtGui", fromlist=["QFont"]).QFont()
            f.setPointSize(max(1, int(w * 0.28)))
            f.setBold(True)
            p.setFont(f)
            p.drawText(0, 0, w, h, Qt.AlignCenter, "★")
        finally:
            p.end()


# ─────────────────────────────────────────────────────────────────────────────
# Member Row — with tier logic based on is_activated + spending
# ─────────────────────────────────────────────────────────────────────────────
class MemberRow(QWidget):
    _instance_count = 0

    def __init__(self, passenger):
        super().__init__()
        self.setFixedHeight(72)
        self.setStyleSheet("background: transparent;")

        idx = MemberRow._instance_count % len(_AVATAR_COLORS)
        MemberRow._instance_count += 1
        av_bg, av_fg = _AVATAR_COLORS[idx]

        lay = QHBoxLayout(self)
        lay.setContentsMargins(20, 0, 20, 0)
        lay.setSpacing(0)

        # ── Avatar ───────────────────────────────────────────────────────────
        first = (passenger.full_name[0].upper() if passenger.full_name else "?")
        av = QLabel(first)
        av.setFixedSize(34, 34)
        av.setAlignment(Qt.AlignCenter)
        av.setStyleSheet(f"""
            background: {av_bg};
            border-radius: 10px;
            font-size: 13px;
            font-weight: 700;
            color: {av_fg};
        """)
        lay.addWidget(av)
        lay.addSpacing(14)

        # ── HỌ VÀ TÊN ────────────────────────────────────────────────────────
        name_w = QWidget(); name_w.setStyleSheet("background: transparent;")
        name_l = QVBoxLayout(name_w)
        name_l.setContentsMargins(0, 0, 0, 0); name_l.setSpacing(3)
        name_l.setAlignment(Qt.AlignVCenter)

        # Live spending for the session user; static for others
        display_spending = passenger.total_spending
        if getattr(passenger, '_is_session_user', False):
            display_spending = get_user_spending_from_db(SESSION_USERNAME)

        name_lbl = QLabel(passenger.full_name or "—")
        name_lbl.setStyleSheet(f"font-size:14px; font-weight:700; color:{TEXT_DARK};")
        email_lbl = QLabel(passenger.email or "")
        email_lbl.setStyleSheet(f"font-size:11px; color:{GRAY_TEXT};")
        name_l.addWidget(name_lbl); name_l.addWidget(email_lbl)
        lay.addWidget(name_w, 34)

        # ── GIẤY TỜ ──────────────────────────────────────────────────────────
        pass_w = QWidget(); pass_w.setStyleSheet("background: transparent;")
        pass_l = QVBoxLayout(pass_w)
        pass_l.setContentsMargins(0, 0, 0, 0); pass_l.setSpacing(3)
        pass_l.setAlignment(Qt.AlignVCenter)
        pass_lbl = QLabel(passenger.passport_number or "—")
        pass_lbl.setStyleSheet(f"font-size:13px; font-weight:600; color:{TEXT_MED};")
        nat = (passenger.nationality or "").upper()
        nat_lbl = QLabel(nat)
        nat_lbl.setStyleSheet(f"font-size:10px; color:{GRAY_TEXT}; letter-spacing:0.5px;")
        pass_l.addWidget(pass_lbl); pass_l.addWidget(nat_lbl)
        lay.addWidget(pass_w, 22)

        # ── HẠNG ─────────────────────────────────────────────────────────────
        rank_wrap = QWidget(); rank_wrap.setStyleSheet("background: transparent;")
        rank_wrap_l = QHBoxLayout(rank_wrap)
        rank_wrap_l.setContentsMargins(0, 0, 0, 0)
        rank_wrap_l.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        is_activated = getattr(passenger, 'is_activated', 0)

        if is_activated:
            # Compute tier from spending
            spending_val = display_spending
            tier = get_tier_for_spending(spending_val)
            fg, bg, _ = _TIER_BADGE.get(tier, (TEXT_DARK, WHITE, ""))

            rank_lbl = QLabel(tier)
            rank_lbl.setFixedHeight(26)
            rank_lbl.setAlignment(Qt.AlignCenter)
            rank_lbl.setContentsMargins(12, 0, 12, 0)
            rank_lbl.setStyleSheet(f"""
                background: {bg};
                color: {fg};
                border-radius: 13px;
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.5px;
            """)
            rank_wrap_l.addWidget(rank_lbl)
        else:
            # Not activated → leave tier column blank
            rank_wrap_l.addStretch()

        rank_wrap_l.addStretch()
        lay.addWidget(rank_wrap, 14)

        # ── CHI TIÊU ─────────────────────────────────────────────────────────
        spending_str = f"${display_spending:,.0f}"
        sp_lbl = QLabel(spending_str)
        sp_lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        sp_lbl.setStyleSheet(f"font-size:14px; font-weight:700; color:{TEXT_DARK};")
        lay.addWidget(sp_lbl, 16)

        # ── THAO TÁC ─────────────────────────────────────────────────────────
        action_lbl = QLabel("···")
        action_lbl.setAlignment(Qt.AlignCenter)
        action_lbl.setStyleSheet(f"font-size:16px; color:{GRAY_TEXT}; letter-spacing:2px;")
        lay.addWidget(action_lbl, 10)


# ─────────────────────────────────────────────────────────────────────────────
# Analytics Card
# ─────────────────────────────────────────────────────────────────────────────
class _AnalyticsCard(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"""
            _AnalyticsCard {{
                background: {WHITE};
                border-radius: 20px;
                border: 1px solid {BORDER};
            }}
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 28, 24, 28)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        lay.addWidget(_MedalIcon(64), 0, Qt.AlignHCenter)
        lay.addSpacing(16)

        title = QLabel("Phân tích Hội viên")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"font-size:18px; font-weight:800; color:{TEXT_DARK};")
        lay.addWidget(title)
        lay.addSpacing(8)

        desc = QLabel("Hệ thống tự động xếp hạng dựa trên chi tiêu thực tế và trạng thái kích hoạt tài khoản.")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size:12px; color:{GRAY_TEXT}; line-height:1.5;")
        lay.addWidget(desc)
        lay.addSpacing(24)

        # Tier distribution bars
        tiers = [
            ("BẠCH KIM",   "#1A1A2E", 18),
            ("HẠNG VÀNG",  "#D4AF37", 28),
            ("HẠNG BẠC",   "#8E9EAB", 35),
            ("THÀNH VIÊN", "#2E7D32", 19),
        ]
        for tier_name, color, pct in tiers:
            row_lay = QHBoxLayout()
            t_lbl = QLabel(tier_name)
            t_lbl.setStyleSheet(f"font-size:10px; font-weight:600; color:{GRAY_TEXT}; letter-spacing:1px;")
            p_lbl = QLabel(f"{pct}%")
            p_lbl.setStyleSheet(f"font-size:11px; font-weight:700; color:{TEXT_MED};")
            row_lay.addWidget(t_lbl); row_lay.addStretch(); row_lay.addWidget(p_lbl)
            lay.addLayout(row_lay)
            lay.addSpacing(4)
            bar = _ProgressBar(pct, color)
            lay.addWidget(bar)
            lay.addSpacing(10)

        lay.addStretch()


# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
class _Footer(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(52)
        self.setStyleSheet(f"background:{BG_MAIN}; border-top:1px solid {BORDER};")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(28, 0, 28, 0)
        lay.setSpacing(0)

        def _lbl(text, size=10, weight=400, color=GRAY_TEXT, spacing=0):
            l = QLabel(text)
            w = {400:"normal",600:"600",700:"bold"}.get(weight,"normal")
            sp = f"letter-spacing:{spacing}px;" if spacing else ""
            l.setStyleSheet(f"font-size:{size}px;font-weight:{w};color:{color};background:transparent;border:none;{sp}")
            return l

        lay.addWidget(_lbl("© 2026 HỆ THỐNG QUẢN TRỊ JETJET / LƯU HÀNH NỘI BỘ", spacing=0.3))
        lay.addStretch()
        lay.addWidget(_lbl("CHÍNH SÁCH BẢO MẬT", weight=600))
        lay.addSpacing(24)
        dot = QLabel("●")
        dot.setStyleSheet(f"font-size:10px;color:{RED};background:transparent;border:none;")
        lay.addWidget(dot)
        lay.addSpacing(5)
        lay.addWidget(_lbl("PHIÊN BẢN 2.5.0 ỔN ĐỊNH", weight=700, color=RED, spacing=0.3))


# ─────────────────────────────────────────────────────────────────────────────
# Passenger Page
# ─────────────────────────────────────────────────────────────────────────────
class PassengerPage(QWidget):
    def __init__(self):
        super().__init__()
        MemberRow._instance_count = 0

        self.setStyleSheet(f"background:{BG_MAIN};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background:transparent; border:none;")

        content = QWidget()
        content.setStyleSheet(f"background:{BG_MAIN};")
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(28, 24, 28, 0)
        self.layout.setSpacing(20)

        self.build_header()

        body = QHBoxLayout()
        body.setSpacing(16)
        self.build_table()
        body.addWidget(self.table, 70)
        body.addWidget(_AnalyticsCard(), 30)
        self.layout.addLayout(body)
        self.layout.addWidget(_Footer())

        self.load_passengers()

    # ── Header ───────────────────────────────────────────────────────────────
    def build_header(self):
        header = QHBoxLayout(); header.setSpacing(0)

        title_col = QVBoxLayout(); title_col.setSpacing(4)
        title = QLabel("Khách hàng & Thành viên")
        title.setStyleSheet(f"font-size:24px; font-weight:800; color:{TEXT_DARK};")
        subtitle = QLabel("Hồ sơ hành khách và hạng thành viên thân thiết")
        subtitle.setStyleSheet(f"font-size:13px; color:{GRAY_TEXT};")
        title_col.addWidget(title); title_col.addWidget(subtitle)
        header.addLayout(title_col)
        header.addStretch()

        search_row = QHBoxLayout(); search_row.setSpacing(8)
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet(f"font-size:14px; color:{GRAY_TEXT};")
        self.search = QLineEdit()
        self.search.setPlaceholderText("Tìm kiếm hành khách...")
        self.search.setFixedSize(230, 38)
        self.search.textChanged.connect(self.on_search)
        self.search.setStyleSheet(f"""
            QLineEdit {{
                background:{WHITE}; border:1px solid {BORDER};
                border-radius:19px; padding-left:14px;
                font-size:13px; color:{TEXT_DARK};
            }}
            QLineEdit:focus {{ border-color:{RED}; }}
        """)
        search_row.addWidget(search_icon); search_row.addWidget(self.search)
        header.addLayout(search_row)
        self.layout.addLayout(header)

    # ── Table card ───────────────────────────────────────────────────────────
    def build_table(self):
        self.table = QFrame()
        self.table.setStyleSheet(f"""
            QFrame {{
                background:{WHITE}; border-radius:20px; border:1px solid {BORDER};
            }}
        """)
        self.table_layout = QVBoxLayout(self.table)
        self.table_layout.setContentsMargins(0, 0, 0, 8)
        self.table_layout.setSpacing(0)

        card_top = QWidget(); card_top.setFixedHeight(52)
        card_top.setStyleSheet("background:transparent;")
        card_top_l = QHBoxLayout(card_top)
        card_top_l.setContentsMargins(22, 0, 18, 0)

        danh_ba = QLabel("DANH BẠ THÀNH VIÊN")
        danh_ba.setStyleSheet(f"font-size:11px; font-weight:700; color:{GRAY_TEXT}; letter-spacing:1.5px;")
        refresh = QLabel("↺")
        refresh.setFixedSize(28, 28); refresh.setAlignment(Qt.AlignCenter)
        refresh.setStyleSheet(f"font-size:14px; color:{GRAY_TEXT}; border:1.5px solid {BORDER}; border-radius:14px;")
        card_top_l.addWidget(danh_ba); card_top_l.addStretch(); card_top_l.addWidget(refresh)
        self.table_layout.addWidget(card_top)
        self.table_layout.addWidget(self._sep())

        col_hdr_w = QWidget(); col_hdr_w.setFixedHeight(42)
        col_hdr_w.setStyleSheet("background:transparent;")
        col_hdr_l = QHBoxLayout(col_hdr_w)
        col_hdr_l.setContentsMargins(20, 0, 20, 0); col_hdr_l.setSpacing(0)
        col_hdr_l.addSpacing(48)

        for text, stretch in [
            ("HỌ VÀ TÊN", 34), ("GIẤY TỜ", 22),
            ("HẠNG",      14), ("CHI TIÊU", 16), ("THAO TÁC", 10),
        ]:
            lbl_w = QLabel(text)
            lbl_w.setStyleSheet(f"font-size:10px; font-weight:700; color:{GRAY_TEXT}; letter-spacing:0.8px;")
            col_hdr_l.addWidget(lbl_w, stretch)

        self.table_layout.addWidget(col_hdr_w)
        self.table_layout.addWidget(self._sep())

        self.rows_layout = QVBoxLayout()
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(0)
        self.table_layout.addLayout(self.rows_layout)

    @staticmethod
    def _sep():
        f = QFrame(); f.setFrameShape(QFrame.HLine); f.setFixedHeight(1)
        f.setStyleSheet(f"background:{BORDER}; border:none;"); return f

    # ── Load & render ─────────────────────────────────────────────────────────
    def load_passengers(self):
        MemberRow._instance_count = 0
        passengers = get_all_passengers_enriched()
        # Mark the session user row for live spending
        for p in passengers:
            p._is_session_user = (p.email and "quanle@example.com" in p.email.lower())
        self.render_rows(passengers)

    def render_rows(self, passengers):
        MemberRow._instance_count = 0
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        if not passengers:
            empty = QLabel("Không có hành khách nào.")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(f"padding:40px; color:{GRAY_TEXT}; font-size:14px;")
            self.rows_layout.addWidget(empty)
            return

        for i, passenger in enumerate(passengers):
            row = MemberRow(passenger)
            self.rows_layout.addWidget(row)
            if i < len(passengers) - 1:
                self.rows_layout.addWidget(self._sep())

    # ── Search ────────────────────────────────────────────────────────────────
    def on_search(self):
        keyword = self.search.text().strip()
        if not keyword:
            passengers = get_all_passengers_enriched()
        else:
            passengers = search_passengers_enriched(keyword)
        for p in passengers:
            p._is_session_user = (p.email and "quanle@example.com" in p.email.lower())
        self.render_rows(passengers)