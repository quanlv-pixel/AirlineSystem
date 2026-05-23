from datetime import timedelta
from database.init_db import get_connection
from shared.api.weather_api import get_weather_by_airport


FLIGHT_DURATION={

("HAN","SGN"):125,
("SGN","HAN"):125,

("HAN","DAD"):80,
("DAD","HAN"):80,

("SGN","DAD"):90,
("DAD","SGN"):90,

("SGN","SIN"):130,
("SIN","SGN"):130,

("HAN","ICN"):300,
("ICN","HAN"):300

}


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