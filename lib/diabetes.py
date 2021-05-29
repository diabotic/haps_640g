import json

from utils import *

BOLUS_PATTERN = '/home/pi/Projects/haps/config/bolus.json'
BOLUS_JSON = {} 

# How many mg/dl 1 unit lowers
BG_TARGET = 120
IS_SLEEP  = 40
IS_BRFAST = 40
IS_LUNCH  = 40
IS_NORM   = 40
MAX_BOLUS = 1.0


def valid_bg(bg):
    try:
        if bg is not None:
            if len(str(bg).strip()) > 0:
                if int(bg) > 0 and int(bg) < 600:
                    return True
    except:
        return False
    return False



try:
    with open(BOLUS_PATTERN) as json_file:
        BOLUS_JSON = json.load(json_file)
        #print('Bolus loaded:', BOLUS_JSON)
except:
        BOLUS_JSON = {}


def calculateBolus(bg, arrows, active_insulin, p_time ):
    bolus = 0.0
    max_bolus = MAX_BOLUS
    bg_target=BG_TARGET

    if arrows < 0:
        return 0.0

    p_hour = int(p_time[11:13])
    if p_hour > 12 and p_hour < 16:
        logger('Lunch correction for ' + str( p_time[10:])) 
        insulin_sensivity = IS_LUNCH
    elif p_hour > 22 and p_hour < 8:
        logger('Early morning correction for ' + str( p_time[10:])) 
        insulin_sensivity = IS_SLEEP
    else:
        logger('Normal correction for ' + str( p_time[10:]))
        insulin_sensivity=IS_NORM

    precision = 0.1

    try:
        current_bg = float(bg)
        trend = arrows * 15
        active_insulin = float(active_insulin)
        amount_to_correct = current_bg + trend - bg_target

        if amount_to_correct > 0:
            # Calculate needed insulin for correction
            bolus = amount_to_correct / insulin_sensivity

            # Discounts active insulin
            bolus = bolus - active_insulin

            # Uses 0.1 precision
            bolus = float(int(bolus * 10))/10

            if bolus < 0: bolus = 0.0
    except Exception as e:
        error_msg = 'ERROR CALCULATING BOLUS' + str(e) + ' Traceback: ' + str(traceback.format_exc())
        logger(msg_error)
        bolus = 0
    
    if bolus > max_bolus:
        bolus = max_bolus

    return bolus


def apply_correction(pump_data):

    bolus_c = 0
    if pump_data is None or len(pump_data) == 0:
        return False

    try:
        bg = pump_data['bgl_mg']
        if not valid_bg(bg):
            return False

        logger('=======')
        logger('BG: ' + str(bg))
        logger('=======')
        arrows = pump_data['bgl_trend']
        active_insulin = pump_data['active_insulin']
        p_hour = pump_data['bgl_time']

        bolus_c = calculateBolus(bg, arrows, active_insulin, p_hour)

    except Exception as e:
        msg_error = 'ERROR CALCULATING BOLUS:' + str(e) + ' Traceback: ' + str(traceback.format_exc())
        logger(msg_error)
        return False

    logger('Calculated correction: ' + str(bolus_c) )

    if bolus_c > 0:
        return bolus_c

    return 0.0


