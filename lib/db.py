import sqlite3
import traceback

from datetime import datetime as dt
from utils import *

DB_PATH = 'db/haps.db'


def get_connection():
    conn=sqlite3.connect(DB_PATH)
    return conn


def close_connection(conn):
    conn.close


def create_table():
    conn = get_connection()
    c = conn.cursor()

    query = """
            CREATE TABLE bg_history (
                    time text,
                    bgl integer, 
                    arrows integer,
                    active_insulin real,
                    ns_status integer,
                    UNIQUE(time)
            )
    """
    
    c.execute(query)
    conn.commit()
    conn.close()



def get_ns_records(n=100):
    conn = get_connection()
    c = conn.cursor()

    q = "SELECT * FROM (SELECT * FROM bg_history where ns_status == 0 ORDER BY time DESC LIMIT " + str(n) + ") ORDER BY time"

    c.execute(q)
    results = c.fetchall()
    conn.close()

    return results


def get_bg_records(n=10):
    conn = get_connection()
    c = conn.cursor()

    q = "SELECT * FROM bg_history ORDER BY time DESC LIMIT " + str(n)

    c.execute(q)
    results = c.fetchall()
    conn.close()

    return results



def get_last_bg_datetime():
    last_result = get_bg_records(1)

    last_dt = str2dt(last_result[0][0])

    return last_dt


def record_bg(time_obj, bgl, arrows=0, active_insulin=0.0, ns_status=False):
    try:
        #print('Saving Data')
        conn = get_connection()
        c = conn.cursor()

        if not valid_bg(bgl):
            print('ERROR saving (invalid BG):', bgl)
            return False

        if not valid_time(time_obj):
            print('ERROR saving (invalid time):', time_obj)
            return False

        q = "INSERT INTO bg_history VALUES ('{}', {}, '{}','{}',{})".format(
            dt2str(time_obj),
            bgl,
            arrows,
            active_insulin,
            1.0 * ns_status
        )
        #print('QUERY: ', q)

        c.execute(q)
        conn.commit()
        conn.close()
        
        return True

    except Exception as e:
        if 'UNIQUE' not in str(e):
            print('ERROR:', e)
        return False


def update_ns_status(str_time, ns_status=0):
    conn = get_connection()
    c = conn.cursor()
    
    ns_status = int(ns_status)
    str_dt = str(str_time)
    str_dt = dt2str(str_dt)
    #print('Saving', str_dt, ns_status)

    q = 'UPDATE bg_history set ns_status = {} where time = "{}"'.format(ns_status, str_dt)
    #print('QUERY:', q)

    c.execute(q)
    conn.commit()
    conn.close()


def calc_rpi_time(pump_datetime):
    # Diference in seconds from the RPi to the Pump
    # If Rpi date is earlier(lesser) than 640g, use negative values
    # If RPi date is later (greater) than 640g, use positive values
    DELTA_TIME = 0

    rpi_dt = pump_datetime + dtt.timedelta(seconds=DELTA_TIME)

    return rpi_dt



def estimate_next_bg_read_time():

    CGM_DELAY = 10

    last_time = get_last_bg_datetime()

    pump_dt = str2dt(last_time)
    rpi_dt = calc_rpi_time(pump_dt)
    rpi_dt = rpi_dt + dtt.timedelta(seconds=CGM_DELAY)

    #print('Last BG Time:', rpi_dt)
    min = rpi_dt.minute
    sec = rpi_dt.second

    # Calculate all minutes where the BG will me measured
    next_minutes = [min + (m * 5) for m in range(12) ]
    next_minutes = sorted([m - 60 if m >= 60 else m for m in next_minutes])
    next_dts = [dt(dt.now().year,  dt.now().month, dt.now().day, dt.now().hour, m, sec) for m in next_minutes]

    # Get the next minute in calculated BG time intervals
    next_bg_time = list(filter(lambda x: x > dt.now(), next_dts))[0]
    return next_bg_time



def calc_next_read():

    # Prime > 60
    difference = 73

    try:
        next_bg_time = estimate_next_bg_read_time()
        difference = (next_bg_time - dt.now()).total_seconds()
        #logger(difference)
        if difference < 0:
            difference = 7
    except Exception as e:
        logger('ERROR calculating next read: ' + str(e))
        traceback.print_exc()
        difference = 73

    logger('Next BG read: ' + str(dt.now() + dtt.timedelta(seconds=difference)))

    return difference



        
