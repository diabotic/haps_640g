import sys
import os
import traceback
sys.path.append('../lib')

from minimed_next24_api import*
from rpi_cnl import *
from diabetes import * 
from utils import *

turn_usb_off()


if __name__ == '__main__':

    while True: 
        try:
            print('USB on')
            turn_usb_on()
            sleep(5)
            pump_data = fetchPumpData(pumpDownloadData)
            logger('Pump Data:' + str(pump_data) )
           
        except Exception as e:
            msg_error = 'ERROR:' + str(e) + ' Traceback: ' + str(traceback.format_exc())
            logger(msg_error)
            #logger('Rebooting system')
            #os.system('sudo reboot')


        # Leave USB on for charging external battery
        #turn_usb_on()
        print('USB off')
        turn_usb_off()
        sleep(10)


