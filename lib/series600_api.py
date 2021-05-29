#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
# logging.basicConfig has to be before astm import, otherwise logs don't appear
logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# Log Level:
# CRITICAL
# ERROR
# WARNING
# INFO
# DEBUG

import cnl24lib as cnl24lib
import binascii
from datetime import datetime as dt
from datetime import timedelta

import pickle # needed for local history export
import subprocess

def set_time(str_dt):
    print('Updating system time to', str_dt)
    upt = subprocess.call(['sudo', 'date', '-s ' + str_dt  ])


def parse_arrows(input_str):
   
    arrows_str = str(input_str).lower()
    intensity = 0
    signal = 1

    if 'down' in arrows_str:
        signal = -1

    if 'three' in arrows_str or '3' in arrows_str:
        intensity = 3
    elif 'two' in arrows_str or '2' in arrows_str:
        intensity = 2
    elif 'one' in arrows_str or '1' in arrows_str:
        intensity = 1 
    
    return intensity * signal


def clear_value(str_input):

    res = str(str_input).strip().split(':')[-1]
    res = str(res).replace(',', '').strip()

    return res



def pump_simple_download(mt):

    status = mt.get_pump_status()

    #print('All Pump Commands:')
    #for m in dir(status):
    #    print('  ', m)

    pump_data = {} 

    logger.info(100 * '-')
    logger.info(binascii.hexlify( status.response_payload ))
    logger.info(100 * '-')

    # Status

    pump_data['pump_battery_perc'      ] = status.battery_level_percentage
    pump_data['units_remaining'        ] = status.insulin_units_remaining 
    pump_data['pump_suspended'         ] = status.is_pump_status_suspended
    pump_data['pump_delivering_insulin'] = status.is_pump_status_delivering_insulin

    # Insulin
    pump_data['active_insulin'           ] = status.active_insulin
    pump_data['active_basal_pattern'     ] = status.active_basal_pattern
    pump_data['active_temp_basal_pattern'] = status.active_temp_basal_pattern
    pump_data['basal_rate'               ] = status.current_basal_rate
    pump_data['temp_basal_rate'          ] = status.temp_basal_rate
    pump_data['temp_basal_perc'          ] = status.temp_basal_percentage

    # BGL
    pump_data['bgl_mg'   ] = status.sensor_bgl
    pump_data['bgl_mmol' ] = status.sensor_bgl / 18.016
    pump_data['bgl_time' ] = status.sensor_bgl_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    pump_data['bgl_trend'] = parse_arrows(status.trend_arrow)

    # Calibration
    pump_data['cgm_calibrating'         ] = status.is_sensor_status_calibrating
    pump_data['cgm_calibration_complete'] = status.is_sensor_status_calibration_complete
    pump_data['cgm_exception'           ] = status.is_sensor_status_exception
   
    mt.get_pump_time()
    pump_data['pump_time'] = mt.pump_time.strftime('%Y-%m-%d %H:%M:%S')

    for m in pump_data.keys():
        logger.info(m + ' : ' + str(pump_data[m]))

    return pump_data

   
def fetch_sensor_history(mt, delta_h=24):

    sensor_data = []

    # !!! Max timedelta = 10 days
    #start_date = dt.now() - timedelta(days=1)
    start_date = dt.now() - timedelta(hours=24)
    end_date = dt.max

    # Sensor history = cnl24lib.HistoryDataType.SENSOR_DATA
    # Pump history = cnl24lib.HistoryDataType.PUMP_DATA
    #history_type = cnl24lib.HistoryDataType.PUMP_DATA
    history_type = cnl24lib.HistoryDataType.SENSOR_DATA

    history_info = mt.get_pump_history_info(start_date, end_date, history_type)

    logger.info("ReadHistoryInfo Start : {0}".format(history_info.from_date))
    logger.info("ReadHistoryInfo End   : {0}".format(history_info.to_date))
    logger.info("ReadHistoryInfo Size  : {0}".format(history_info.length))
    logger.info("ReadHistoryInfo Block : {0}".format(history_info.blocks))
    
    try:
        logger.info('PROCESSING HISTORY PAGES')
        history_pages = mt.get_pump_history(start_date, end_date, history_type)
        logger.info('PROCESSING EVENTS')
        events = mt.process_pump_history(history_pages, history_type)
    except Exception as e:
        print('ERROR downloading history pages', e)
        return []
    
    for ev in events:
        try:
            single_data = str(ev).split(' ') 
            if len(single_data) > 10:
                s_event = {}
                s_event['date'      ] = single_data[ 2] + ' ' + single_data[3][:8]
                s_event['bgl'       ] = clear_value(single_data[ 4])
                s_event['pred_bgl'  ] = clear_value(single_data[ 6])
                s_event['isig'      ] = clear_value(single_data[ 7])
                s_event['changert'  ] = clear_value(single_data[ 8])
                s_event['noisy'     ] = clear_value(single_data[ 9])
                s_event['discard'   ] = clear_value(single_data[10])
                s_event['sensor_err'] = clear_value(single_data[11])

                print('RAW SENSOR EVNT::', single_data)
                print('SENSOR EVENT   :', s_event)
                sensor_data.append(s_event)
            else:
                unhandled = True
                single_data = str(ev).split(' ') 
                print('UNDANDLED EVENT:', str(ev))
        except Exception as e:
            print('ERROR Parsing events:', e)
            return []

    return sensor_data




def fetch_pump_data(last_bg_dt=dt.now(), history_mode=False, update_sys_clock=False):

    mt = cnl24lib.Medtronic600SeriesDriver()

    pump_data = {}

    if mt.open_device():
        logger.info("Open USB")

        try:
            mt.request_device_info()
            logger.info("CNL Device serial: {0}".format(mt.device_serial))
            logger.info("CNL Device model: {0}".format(mt.device_model))
            logger.info("CNL Device sn: {0}".format(mt.device_sn))
            mt.enter_control_mode()

            try:
                mt.enter_passthrough_mode()
                try:

                    mt.open_connection()
                    try:
                        mt.request_read_info()
                        mt.read_link_key()

                        #logger.info("pump_mac: 0x{0:X}".format(mt.session.pump_mac))
                        #logger.info("link_mac: 0x{0:X}".format(mt.session.link_mac))
                        #logger.info("encryption key from pump: {0}".format(binascii.hexlify( mt.session.key)))

                        if mt.negotiate_channel():
                            # logger.info("Channel: 0x{0:X}".format(mt.session.radio_channel))
                            # logger.info("Channel RSSI Perc: {0}%".format(mt.session.radio_rssi_percent))
                            mt.begin_ehsm()
                            try:

                                pump_data = pump_simple_download(mt)
                                current_bg = pump_data['bgl_mg'] 
                                current_bg_dt = dt.strptime(pump_data['bgl_time'], '%Y-%m-%d %H:%M:%S')
                                delta = (current_bg_dt - last_bg_dt).seconds 

                                # If bg is valid and last measure is longer than 5 minutes, get history
                                print('LAST BG RECORDED TIME  :', last_bg_dt)
                                print('CURRENT BG FETCHED TIME:', current_bg_dt)
                                print('Difference:', delta, 'minutes') 

                                if delta > 310 and current_bg > 0 and current_bg < 600: 
                                    print('Forcing History mode to fetch data gap')
                                    history_mode = True 
                                    update_sys_clock = True

                                if update_sys_clock:
                                    set_time(pump_data['pump_time'])

                                # check if the last bg time is more than 6 minutes behind the current bg time. 
                                # if it is then download from history

                                if history_mode:
                                    sensor_data = fetch_sensor_history(mt)
                                    pump_data['history'] = sensor_data


                            finally:
                                mt.finish_ehsm()
                        else:
                            logger.error("Cannot connect to the pump.")
                    finally:
                        mt.close_connection()
                finally:
                    mt.exit_passthrough_mode()
            finally:
                mt.exit_control_mode()
        finally:
            mt.close_device()
    else:
        logger.info("Error open USB")

    return pump_data


