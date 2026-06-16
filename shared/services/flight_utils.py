from datetime import timedelta
from database.init_db import get_connection
from shared.api.weather_api import get_weather_by_airport
from shared.mock_data import FLIGHT_DURATION  # centralised in shared/mock_data.py


def generate_flight_code(dep,dst):

    conn=get_connection()
    cursor=conn.cursor()

    prefix=f"JJ{dep}{dst}"

    cursor.execute("""
    SELECT COUNT(*)
    FROM flights
    WHERE flight_number LIKE ?
    """,(f"{prefix}%",))

    count=cursor.fetchone()[0]+1
    conn.close()

    return f"{prefix}{count:03d}"


def calculate_duration(dep,dst):

    return FLIGHT_DURATION.get(
        (dep,dst),
        120
    )


def get_delay(dep):

    weather=get_weather_by_airport(dep)

    risk=weather["delay_risk"]

    if risk=="Medium":
        return 15

    if risk=="High":
        return 30

    if risk=="Critical":
        return 60

    return 0

def calculate_price(dep: str, dst: str) -> float:
    """Tự động tính giá vé dựa vào quốc gia và độ dài chuyến bay."""
    duration = calculate_duration(dep, dst)
    # Xác định bay quốc tế hay nội địa
    vietnam_airports = ("SGN", "HAN", "DAD", "CXR", "PQC")
    is_intl = dep not in vietnam_airports or dst not in vietnam_airports
    
    # Base fee (Giá gốc): Quốc tế $120, Nội địa $40
    base_fee = 120.0 if is_intl else 40.0
    
    # Tính thêm tiền theo số phút bay ($0.5 mỗi phút)
    return round(base_fee + (duration * 0.5), 2)