import datetime 
import sys
import traceback
sys.path.append('lib')

from decoding.read_minimed_next24 import *


def fetchPumpData(downloadOperations, history=False):
    mt = Medtronic600SeriesDriver()
    mt.openDevice()

    pump_data = {}

    try:
        mt.getDeviceInfo()
        logger.info("Device serial: {0}".format(mt.deviceSerial))
        mt.enterControlMode()
        try:
            mt.enterPassthroughMode()
            try:
                mt.openConnection()
                try:
                    mt.readInfo()
                    mt.readLinkKey()
                    try:
                        mt.negotiateChannel()
                    except:
                        logger.error("downloadPumpSession: Cannot connect to the pump. Abandoning")
                        return {}
                    mt.beginEHSM()
                    try:    
                        # We need to read always the pump time to store the offset for later messeging
                        mt.getPumpTime()
                        try:
                            pump_data = downloadOperations(mt,history)
                        except Exception as err:
                            logger.error("Unexpected error in client downloadOperations", exc_info = True)
                            traceback.print_exc()
                    finally:
                        mt.finishEHSM()
                finally:
                    mt.closeConnection()
            finally:
                mt.exitPassthroughMode()
        finally:
            mt.exitControlMode()
    finally:
        mt.closeDevice()

    return pump_data


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



def pumpDownloadData(mt, history_mode=False):

    status = mt.getPumpStatus()
    pump_data = {} 

    logger.info(binascii.hexlify( status.responsePayload ))
    logger.info ("Active Insulin: {0:.3f}U".format( status.activeInsulin ))
    pump_data['active_insulin'] = status.activeInsulin
    
    logger.info ("Sensor BGL: {0} mg/dL ({1:.1f} mmol/L) at {2}".format( status.sensorBGL,
             status.sensorBGL / 18.016,
             status.sensorBGLTimestamp.strftime( "%c" ) ))
    pump_data['bgl_mg'] = status.sensorBGL
    pump_data['bgl_mmol'] = status.sensorBGL / 18.016
    pump_data['bgl_time'] = status.sensorBGLTimestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    # If is calibrating, get pred bgl instead
    # if pump_data['bgl_mg'] > 600:
    #     history_mode = True

    logger.info("BGL trend: {0}".format( status.trendArrow ))
    print('BGL trend:', str(status.trendArrow)) 
    pump_data['bgl_trend'] = parse_arrows(status.trendArrow)

    logger.info("Current basal rate: {0:.3f}U".format( status.currentBasalRate ))
    pump_data['basal_rate'] = status.currentBasalRate

    logger.info("Temp basal rate: {0:.3f}U".format( status.tempBasalRate ))
    logger.info("Temp basal percentage: {0}%".format( status.tempBasalPercentage ))
    pump_data['temp_basal_rate'] = status.tempBasalRate
    pump_data['temp_basal_perc'] = status.tempBasalPercentage
    
    logger.info("Units remaining: {0:.3f}U".format( status.insulinUnitsRemaining ))
    logger.info("Battery remaining: {0}%".format( status.batteryLevelPercentage ))
    pump_data['pump_battery_perc'] = status.batteryLevelPercentage
    pump_data['units_remaining']= status.insulinUnitsRemaining


    if history_mode:
        logger.info("Getting Pump history info")
    else:
        return pump_data 

    start_date = datetime.datetime.now() - datetime.timedelta(days=1)
    historyInfo = mt.getPumpHistoryInfo(start_date, datetime.datetime.max, HISTORY_DATA_TYPE.PUMP_DATA)
    # print (binascii.hexlify( historyInfo.responsePayload,  ))
    #print (" Pump Start: {0}".format(historyInfo.datetimeStart))
    #print (" Pump End: {0}".format(historyInfo.datetimeEnd));
    #print (" Pump Size: {0}".format(historyInfo.historySize));
    
    print ("Getting Pump history")
    history_pages = mt.getPumpHistory(historyInfo.historySize, start_date, datetime.datetime.max, HISTORY_DATA_TYPE.PUMP_DATA)

    events = mt.processPumpHistory(history_pages, HISTORY_DATA_TYPE.PUMP_DATA)
    print ("# All Pump events:")
    for ev in events:
        print (" Pump: ", ev)
    print ("# End Pump events")
    
    print ("Getting sensor history info")
    sensHistoryInfo = mt.getPumpHistoryInfo(start_date, datetime.datetime.max, HISTORY_DATA_TYPE.SENSOR_DATA)
    #print (binascii.hexlify( historyInfo.responsePayload,  ))
    #print (" Sensor Start: {0}".format(sensHistoryInfo.datetimeStart))
    #print (" Sensor End: {0}".format(sensHistoryInfo.datetimeEnd));
    #print (" Sensor Size: {0}".format(sensHistoryInfo.historySize));
    
    print ("Getting Sensor history")
    sensor_history_pages = mt.getPumpHistory(sensHistoryInfo.historySize, start_date, datetime.datetime.max, HISTORY_DATA_TYPE.SENSOR_DATA)

    # Uncomment to save events for testing without Pump (use: tests/process_saved_history.py)
    #with open('sensor_history_data.dat', 'wb') as output:
    #    pickle.dump(sensor_history_pages, output)
    
    sensor_data = []
    last_isig = 0
    sensorEvents = mt.processPumpHistory(sensor_history_pages, HISTORY_DATA_TYPE.SENSOR_DATA)
    #print ("# All Sensor events:")
    for ev in sensorEvents:
        #print (" Sensor", ev)
        single_data = str(ev).split(' ') 
        if len(single_data) > 7:
            s_event = {}
            s_event['date'      ] = single_data[ 2] + ' ' + single_data[3][:8]
            s_event['bgl'       ] = clear_value(single_data[ 4])
            s_event['pred_bgl'  ] = clear_value(single_data[ 5])
            s_event['isig'      ] = clear_value(single_data[ 6])
            s_event['changert'  ] = clear_value(single_data[ 7])
            s_event['noisy'     ] = clear_value(single_data[ 8])
            s_event['discard'   ] = clear_value(single_data[ 9])
            s_event['sensor_err'] = clear_value(single_data[10])

            print('Got Event at ', s_event['date'])
            sensor_data.append(s_event)
             
    print ("# End Sensor events")
  
    try:
        pump_data['isig'    ] = sensor_data[-1]['isig'] 
        pump_data['pred_bgl'] = sensor_data[-1]['pred_bgl'] 
        pump_data['history' ] = sensor_data
    except:
        pass

    return pump_data
    
    

