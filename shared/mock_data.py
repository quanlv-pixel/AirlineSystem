"""
shared/mock_data.py
===================
Single Source of Truth for all hard-coded / mock / seed data used
across the JetJet Air application.

Sections
--------
1. FLIGHT_DURATION      - route-pair duration map (minutes)
2. SEED_AIRPORTS        - airport master records for DB seeding
3. SEED_PASSENGERS      - realistic Vietnamese passenger profiles
4. SEED_ACCOUNTS        - matching customer accounts for DB seeding
5. MOCK_VIP_PASSENGERS  - rich mock passenger objects for UI analytics
"""

from __future__ import annotations
from types import SimpleNamespace


# =============================================================================
# 1. FLIGHT DURATION
#    Key  : (departure_code, destination_code)
#    Value: flight duration in minutes
#    Used by: shared/services/flight_utils.py
# =============================================================================
FLIGHT_DURATION: dict = {
    ("HAN", "SGN"): 125,
    ("SGN", "HAN"): 125,

    ("HAN", "DAD"): 80,
    ("DAD", "HAN"): 80,

    ("SGN", "DAD"): 90,
    ("DAD", "SGN"): 90,

    ("SGN", "SIN"): 130,
    ("SIN", "SGN"): 130,

    ("HAN", "ICN"): 300,
    ("ICN", "HAN"): 300,
}


# =============================================================================
# 2. SEED AIRPORTS
#    Tuple layout: (airport_code, airport_name, city, country)
#    Used by: database/init_db.py  ->  cursor.executemany(airports)
# =============================================================================
SEED_AIRPORTS: list = [
    ("SGN", "Tan Son Nhat Airport", "Ho Chi Minh", "Vietnam"),
    ("HAN", "Noi Bai Airport",      "Ha Noi",      "Vietnam"),
    ("DAD", "Da Nang Airport",      "Da Nang",     "Vietnam"),
    ("PQC", "Phu Quoc Airport",     "Phu Quoc",    "Vietnam"),
    ("CXR", "Cam Ranh Airport",     "Nha Trang",   "Vietnam"),
    ("SIN", "Changi Airport",       "Singapore",   "Singapore"),
    ("BKK", "Suvarnabhumi Airport", "Bangkok",     "Thailand"),
    ("ICN", "Incheon Airport",      "Seoul",       "Korea"),
    ("NRT", "Narita Airport",       "Tokyo",       "Japan"),
]


# =============================================================================
# 3. SEED PASSENGERS
#    Tuple layout:
#      (full_name, gender, date_of_birth, nationality, phone,
#       email, member_rank, passport_number, total_spending)
#    Used by: database/init_db.py  ->  _seed_passengers_and_accounts()
# =============================================================================
SEED_PASSENGERS: list = [
    ("Le Van Quan",         "Male",   "2007-11-19", "Vietnam", "0912345678",
     "quanle@example.com",       "member", "B12345678",  0.0),
    ("Nguyen Thi Thu Ha",   "Female", "1995-03-15", "Vietnam", "0908123456",
     "thuha.nguyen@gmail.com",   "member", "B23456789",  2750.0),
    ("Tran Minh Khoa",      "Male",   "1988-07-22", "Vietnam", "0976543210",
     "minhkhoa.tran@email.vn",   "member", "B34567890",  4200.0),
    ("Pham Thi Lan Anh",    "Female", "1992-12-01", "Vietnam", "0934567890",
     "lananh.pham@outlook.com",  "member", "B45678901",  1100.0),
    ("Hoang Duc Thang",     "Male",   "1985-05-30", "Vietnam", "0967890123",
     "thang.hoang@company.vn",   "member", "B56789012",  3600.0),
    ("Vu Thi My Linh",      "Female", "2000-09-10", "Vietnam", "0945678901",
     "mylinh.vu@gmail.com",      "member", "B67890123",  320.0),
    ("Dang Quoc Bao",       "Male",   "1979-01-25", "Vietnam", "0923456789",
     "quocbao.dang@vip.vn",      "member", "B78901234",  5100.0),
    ("Bui Thi Hong Nhung",  "Female", "1997-06-18", "Vietnam", "0956789012",
     "hongnhung.bui@gmail.com",  "member", "B89012345",  870.0),
    ("Ly Thanh Trung",      "Male",   "1983-11-05", "Vietnam", "0912567890",
     "thanhtung.ly@email.vn",    "member", "B90123456",  1800.0),
    ("Ngo Thi Bich Phuong", "Female", "2002-04-14", "Vietnam", "0978901234",
     "bichphuong.ngo@gmail.com", "member", "B01234567",  450.0),
    ("Dinh Van Hung",       "Male",   "1975-08-28", "Vietnam", "0901234567",
     "vanhung.dinh@corp.vn",     "member", "C12345678",  2200.0),
    ("Phan Thi Dieu Linh",  "Female", "1999-02-11", "Vietnam", "0965432109",
     "dieulinh.phan@gmail.com",  "member", "C23456789",  680.0),
]


# =============================================================================
# 4. SEED ACCOUNTS
#    Tuple layout: (username, email, full_name, password_plain, is_activated)
#    NOTE: passwords are hashed by SHA-256 at insert time inside init_db.py
#    Used by: database/init_db.py  ->  _seed_passengers_and_accounts()
# =============================================================================
SEED_ACCOUNTS: list = [
    ("quanlv",       "quanle@example.com",       "Le Van Quan",         "jetjet123", 0),
    ("thuha95",      "thuha.nguyen@gmail.com",   "Nguyen Thi Thu Ha",   "jetjet123", 1),
    ("minhkhoa88",   "minhkhoa.tran@email.vn",   "Tran Minh Khoa",      "jetjet123", 1),
    ("lananh92",     "lananh.pham@outlook.com",  "Pham Thi Lan Anh",    "jetjet123", 1),
    ("thang85",      "thang.hoang@company.vn",   "Hoang Duc Thang",     "jetjet123", 1),
    ("mylinh00",     "mylinh.vu@gmail.com",      "Vu Thi My Linh",      "jetjet123", 0),
    ("quocbao79",    "quocbao.dang@vip.vn",      "Dang Quoc Bao",       "jetjet123", 1),
    ("hongnhung97",  "hongnhung.bui@gmail.com",  "Bui Thi Hong Nhung",  "jetjet123", 0),
    ("thanhtung83",  "thanhtung.ly@email.vn",    "Ly Thanh Trung",      "jetjet123", 1),
    ("bichphuong02", "bichphuong.ngo@gmail.com", "Ngo Thi Bich Phuong", "jetjet123", 0),
    ("vanhung75",    "vanhung.dinh@corp.vn",     "Dinh Van Hung",       "jetjet123", 1),
    ("dieulinh99",   "dieulinh.phan@gmail.com",  "Phan Thi Dieu Linh",  "jetjet123", 0),
]


# =============================================================================
# 5. MOCK VIP PASSENGERS
#    SimpleNamespace objects consumed by the Passengers page analytics card.
#    Fields:
#      full_name       - display name
#      email           - unique key used to deduplicate against DB passengers
#      passport_number - unique document number
#      nationality     - country string
#      total_spending  - lifetime spend in USD (determines tier badge)
#      is_activated    - 1 = activated account, 0 = not activated
#      month           - registration month (1-12), used by the month filter
#    Used by: management_app/ui/pages/passengers_page.py
# =============================================================================
MOCK_VIP_PASSENGERS: list = [
    SimpleNamespace(full_name="Pham Minh Duc",    email="duc.pm@elite.vn",     passport_number="B1234567", nationality="Vietnam", total_spending=3800.0, is_activated=1, month=1),
    SimpleNamespace(full_name="Nguyen Lan Anh",   email="lananh@platinum.vn",  passport_number="C2345678", nationality="Vietnam", total_spending=5200.0, is_activated=1, month=1),
    SimpleNamespace(full_name="Tran Viet Hung",   email="hung.tv@goldvip.vn",  passport_number="D3456789", nationality="Vietnam", total_spending=1750.0, is_activated=1, month=2),
    SimpleNamespace(full_name="Le Thi Bich Van",  email="van.ltb@silver.vn",   passport_number="E4567890", nationality="Vietnam", total_spending=780.0,  is_activated=1, month=2),
    SimpleNamespace(full_name="Vu Quang Khai",    email="khai.vq@member.vn",   passport_number="F5678901", nationality="Vietnam", total_spending=320.0,  is_activated=1, month=3),
    SimpleNamespace(full_name="Do Thi Huong",     email="huong.dt@gold.vn",    passport_number="G6789012", nationality="Vietnam", total_spending=1620.0, is_activated=1, month=3),
    SimpleNamespace(full_name="Hoang Anh Tuan",   email="tuan.ha@platinum.vn", passport_number="H7890123", nationality="Vietnam", total_spending=4900.0, is_activated=1, month=4),
    SimpleNamespace(full_name="Bui Thi Ngoc",     email="ngoc.bt@silver.vn",   passport_number="I8901234", nationality="Vietnam", total_spending=860.0,  is_activated=1, month=4),
    SimpleNamespace(full_name="Dinh Van Phuc",    email="phuc.dv@member.vn",   passport_number="J9012345", nationality="Vietnam", total_spending=410.0,  is_activated=1, month=5),
    SimpleNamespace(full_name="Pham Thi Thu",     email="thu.pt@gold.vn",      passport_number="K0123456", nationality="Vietnam", total_spending=1900.0, is_activated=1, month=5),
    SimpleNamespace(full_name="Cao Van Lam",      email="lam.cv@platinum.vn",  passport_number="L1234568", nationality="Vietnam", total_spending=6100.0, is_activated=1, month=6),
    SimpleNamespace(full_name="Trinh Thi Mai",    email="mai.tt@silver.vn",    passport_number="M2345679", nationality="Vietnam", total_spending=950.0,  is_activated=1, month=6),
    SimpleNamespace(full_name="Ngo Xuan Hai",     email="hai.nx@gold.vn",      passport_number="N3456780", nationality="Vietnam", total_spending=2100.0, is_activated=1, month=7),
    SimpleNamespace(full_name="Ly Thi Cam",       email="cam.lt@member.vn",    passport_number="O4567891", nationality="Vietnam", total_spending=270.0,  is_activated=1, month=7),
    SimpleNamespace(full_name="Phan Van Dat",     email="dat.pv@platinum.vn",  passport_number="P5678902", nationality="Vietnam", total_spending=5500.0, is_activated=1, month=8),
    SimpleNamespace(full_name="Duong Thi Ha",     email="ha.dt@silver.vn",     passport_number="Q6789013", nationality="Vietnam", total_spending=700.0,  is_activated=1, month=8),
    SimpleNamespace(full_name="Tran Quoc Toan",   email="toan.tq@gold.vn",     passport_number="R7890124", nationality="Vietnam", total_spending=1450.0, is_activated=1, month=9),
    SimpleNamespace(full_name="Ha Thi Loan",      email="loan.ht@member.vn",   passport_number="S8901235", nationality="Vietnam", total_spending=190.0,  is_activated=1, month=9),
    SimpleNamespace(full_name="Vuong Minh Tam",   email="tam.vm@platinum.vn",  passport_number="T9012346", nationality="Vietnam", total_spending=7200.0, is_activated=1, month=10),
    SimpleNamespace(full_name="Nong Thi Bao",     email="bao.nt@silver.vn",    passport_number="U0123457", nationality="Vietnam", total_spending=830.0,  is_activated=1, month=10),
    SimpleNamespace(full_name="Kieu Van Nam",     email="nam.kv@gold.vn",      passport_number="V1234569", nationality="Vietnam", total_spending=2400.0, is_activated=1, month=11),
    SimpleNamespace(full_name="Truong Thi Yen",   email="yen.tt@member.vn",    passport_number="W2345670", nationality="Vietnam", total_spending=460.0,  is_activated=1, month=11),
    SimpleNamespace(full_name="Mac Van Toan",     email="toan.mv@platinum.vn", passport_number="X3456781", nationality="Vietnam", total_spending=8900.0, is_activated=1, month=12),
    SimpleNamespace(full_name="Banh Thi Kim",     email="kim.bt@gold.vn",      passport_number="Y4567892", nationality="Vietnam", total_spending=1800.0, is_activated=1, month=12),
]
