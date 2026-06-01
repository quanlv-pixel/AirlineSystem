"""
shared/services/member_service.py
-----------------------------------
Tier calculation logic and live spending aggregation
shared between booking_app and management_app.
"""
from database.db import get_connection


# ─────────────────────────────────────────────────────────────────────────────
# Tier thresholds (USD)
# ─────────────────────────────────────────────────────────────────────────────
TIER_THRESHOLDS = [
    (3000, "BẠCH KIM"),
    (1500, "HẠNG VÀNG"),
    (500,  "HẠNG BẠC"),
    (0,    "THÀNH VIÊN"),
]

PROMO_CODES: dict[str, tuple[str, float]] = {
    "JETJET20":   ("percent", 20.0),   # 20% off base price
    "HELLOFIRST": ("flat",    15.0),   # $15 flat discount
    "ROUNDTRIP10":("percent", 10.0),   # 10% off
    "WEEKEND5":   ("percent",  5.0),   # 5% off
}

# Tier-exclusive promo codes (only visible when activated + matching tier)
TIER_PROMOS: dict[str, list[dict]] = {
    "BẠCH KIM": [
        {"code": "PLATINUM30", "label": "Ưu đãi Bạch Kim độc quyền",
         "desc": "Giảm ngay 30% toàn bộ hành trình — đặc quyền hội viên cao nhất.",
         "exp": "31/12/2026"},
    ],
    "HẠNG VÀNG": [
        {"code": "GOLD15", "label": "Ưu đãi Hội Viên Vàng",
         "desc": "Giảm 15% cho mọi chuyến bay quốc tế khi giữ hạng Vàng.",
         "exp": "31/12/2026"},
    ],
    "HẠNG BẠC": [
        {"code": "SILVER10", "label": "Ưu đãi Hội Viên Bạc",
         "desc": "Giảm 10% cho chuyến bay nội địa — dành riêng hội viên Bạc.",
         "exp": "31/10/2026"},
    ],
}

# Register all tier-exclusive codes into PROMO_CODES for validation
PROMO_CODES["PLATINUM30"] = ("percent", 30.0)
PROMO_CODES["GOLD15"]     = ("percent", 15.0)
PROMO_CODES["SILVER10"]   = ("percent", 10.0)


def get_tier_for_spending(spending: float) -> str:
    """Return tier label based on total_spending (USD)."""
    for threshold, tier in TIER_THRESHOLDS:
        if spending > threshold:
            return tier
    return "THÀNH VIÊN"


def get_user_spending_from_db(username: str) -> float:
    """
    Dynamically sum total_amount of Confirmed/Paid bookings
    for the given username. Returns 0.0 on any error.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT COALESCE(SUM(total_amount), 0)
            FROM bookings
            WHERE created_by = ?
              AND (payment_status = 'Paid' OR booking_status = 'Confirmed')
            """,
            (username,),
        )
        result = cursor.fetchone()[0]
        conn.close()
        return float(result) if result else 0.0
    except Exception as e:
        print(f"[member_service] get_user_spending_from_db error: {e}")
        return 0.0


def get_tier_for_user(username: str) -> str:
    """Convenience: fetch spending from DB, then map to tier."""
    spending = get_user_spending_from_db(username)
    return get_tier_for_spending(spending)


def apply_promo(code: str, base_price: float, seat_fee: float,
                tax: float, fee: float) -> tuple[bool, str, float]:
    """
    Validate a promo code and return (valid, message, discounted_total).
    Discount is applied only to base_price; taxes/fees remain unchanged.
    """
    code = code.strip().upper()
    if code not in PROMO_CODES:
        return False, "Mã không hợp lệ hoặc đã hết hạn.", base_price + seat_fee + tax + fee

    kind, value = PROMO_CODES[code]
    if kind == "percent":
        discount = round(base_price * value / 100, 2)
        new_base = max(0.0, base_price - discount)
        msg = f"Giảm {int(value)}% giá vé cơ bản (−${discount:.0f})"
    else:  # flat
        discount = min(value, base_price)
        new_base = max(0.0, base_price - discount)
        msg = f"Giảm thẳng ${int(value)}"

    total = new_base + seat_fee + tax + fee
    return True, msg, round(total, 2)
