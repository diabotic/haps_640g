import logging
logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

import sys
import traceback
sys.path.append('../lib')

from minimed_next24_api import*
from rpi_cnl import *
from diabetes import * 


def apply_correction(pump_data):

    bolus_c = 0 
    if pump_data is None or len(pump_data) == 0:
        return False

    try:
        bg = pump_data['bgl_mg']
        if bg > 600:
            bg = pump_data['pred_bgl'] 
            print('PUMP NOT CALIBRATED - ESTIMATING BG IN', bg) 
        arrows = pump_data['bgl_trend']
        active_insulin = pump_data['active_insulin']
        p_hour = pump_data['bgl_time']
        
        bolus_c = calculateBolus(bg, arrows, active_insulin, p_hour)
    except Exception as e:
        msg_error = 'ERROR CALCULATING BOLUS:' + str(e) + ' Traceback: ' + str(traceback.format_exc())
        logger.error(msg_error)
        return False

        
    logger.info('Calculated correction: ' + str(bolus_c) )

    if bolus_c > 0:
        apply_bolus(bolus_c)
        return True

    return False


if __name__ == '__main__':
    apply_bolus(0.3)
