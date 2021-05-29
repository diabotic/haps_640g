import sys
import os
import traceback
sys.path.append('../lib')

from rpi_cnl import *
from diabetes import * 
from utils import *

turn_usb_off()
turn_usb_on()


while True: 
    sleep(10)


