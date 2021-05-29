import sys
import os
import traceback
sys.path.append('lib')

import numpy as np

from series600_api import *
from rpi_cnl import *
from diabetes import * 
from utils import *
from db import *
from haps_threads import run_thread
from ns_uploader import upload_bg

turn_usb_off()


def ns_update():

    # Fetch all logged history
    logger('Uploading to Nightscout...')
    records = get_ns_records(1000)

    for r in records:
        str_time = r[0]
        bgl = r[1]
        #print(str_time, bgl)

        ns_status = upload_bg(bgl, str_time)
        if ns_status == True:
            update_ns_status(str_time, ns_status)
    logger('Upload to Nightscout Done')



def wait_for_bolus(time_seconds):
    # Look at the signal file to see if a manual bolus was sent 
    for i in range(int(time_seconds)):
        bolus = get_bolus_signal()
        if bolus > 0:
            clear_bolus_signal()
            apply_bolus(bolus)
            turn_usb_on()
        else:
            sleep(1)


def save_pump_history(all_pump_data):

    p_hour = all_pump_data['bgl_time']

    if 'history' in all_pump_data.keys() and all_pump_data['history'] != []:
        logger('Saving Pump History')

        bgs = []
        isigs = []

        for event in all_pump_data['history']:
            dt_bg = event['date']
            try:
                bg    = event['bgl']
                isig  = event['isig']
                logger('Recording BG {} and ISIG {}'.format(str(bg), str(isig))) 

                bg   = float(bg)
                isig = float(isig)

            except Exception as e:
                logger('Invalid BG {} or ISIG {}'.format(event['bgl'], event['isig']))
                continue

            if valid_bg(bg):
                prop = float(bg) / float(isig)
                bgs.append(bg)
                isigs.append(isig) 
            else:
                logger('Trying to calculate BG from ISIG {}'.format(str(bgs)))
                if len(bgs) > 20: 
                    bg = int(np.interp(isig, isigs, bgs))
                    logger('Inferring BG {} from ISIG {}'.format(bg, isig))
                

            if dt2str(p_hour) != dt2str(dt_bg):
                logger('Saving BG {} at {}'.format(bg, dt_bg))
                record_bg(dt_bg, bg)



def control_cgm_data(update_clock=False, history=False):
    turn_usb_on()
    last_bg_dt = get_last_bg_datetime()
    logger('Last BG Time: {}'.format(last_bg_dt))
    
    bg = 0
    try:
        all_pump_data  = fetch_pump_data(last_bg_dt, history, update_clock)
        bg             = all_pump_data['bgl_mg']
        p_hour         = all_pump_data['bgl_time']
        arrows         = all_pump_data['bgl_trend']
        active_insulin = all_pump_data['active_insulin']
    except:
        turn_usb_off()
        return False
    turn_usb_off()
    
    #if not valid_bg(bg):
    #    return False

    # Save History to DB
    save_pump_history(all_pump_data)
    record_bg(str(p_hour), bg, arrows, active_insulin,0.0)

    # Upload to NightScout
    run_thread(ns_update)
    
    correction = apply_correction(all_pump_data)
    if correction > 0:
        apply_bolus(correction)



if __name__ == '__main__':

    # On first run, fetch history and sync clock with Pump
    control_cgm_data(True, True)

    while True: 
        sleep_time = calc_next_read()
        
        if sleep_time > 300:
            sleep_time = 60
        
        wait_for_bolus(sleep_time)

        try:
            control_cgm_data(True)

        except Exception as e:
            msg_error = 'ERROR:' + str(e) + ' Traceback: ' + str(traceback.format_exc())
            print(msg_error)
            #logger('Rebooting system')
            #os.system('sudo reboot')


        # Leave USB on for charging external battery
        turn_usb_on()
        turn_usb_off()
        print('')


