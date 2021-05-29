import datetime as dtt
import pandas as pd
import os

from datetime import datetime as dt

BASE_PATH = '/opt/haps/'
LOG_PATH  = BASE_PATH + 'logs/haps.log'
SIG_PATH  = BASE_PATH + 'signal/bolus.sig' 


def delete_file(filename):
    try:
        os.remove(filename)
        return True
    except:
        return True


def clear_bolus_signal():
    delete_file(SIG_PATH)


def read_last_lines(filename, n=1):
    try:
        with open(filename, 'r') as f:
            lines = f.read().splitlines()
            last_lines = lines[n*-1:]   
        return last_lines
    except:
        return []


def read_last_line(filename):
    res = read_last_lines(filename,1)
    if len(res) == 0: 
        return ''
    else:
        return res[0]


def append_line(filename, str_line):
    with open(filename, 'a') as f:
        f.write(str(str_line) + '\n')



def set_bolus_signal(bolus):
    append_line(SIG_PATH, str(bolus))


def get_bolus_signal():
    try:
        bolus = float(read_last_line(SIG_PATH))
        return float(bolus)
    except:
        return 0


def valid_bg(bg):
    try:
        if bg is not None:
            if len(str(bg).strip()) > 0:
                if int(bg) > 0 and int(bg) < 600:
                    return True
    except:
        return False
    return False


def dt2str(dt_obj):
    if isinstance(dt_obj,str):
        return dt_obj
    else:
        dt_str = dt.strftime(dt_obj, '%Y-%m-%d %H:%M:%S')
        return dt_str


def str2dt(dt_str):
    if isinstance(dt_str,dt):
        return(dt_str)
    else:
        dt_obj = dt.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        return dt_obj


def valid_time(dt_obj):
    try:
        dto = str2dt(dt_obj)
        return True
    except Exception as e:
        print('ERROR validating datetime', e, str(dt_obj), 'is not in format YYYY-MM-DD HH:mm:SS')
        return False



def logger(input_str):
    print(input_str)

    ts_input_str = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    ts_input_str += ' ' + str(input_str)
    
    append_line(LOG_PATH, ts_input_str)



