#import RPi.GPIO as gpio
import sys, os

from time import sleep
from gpiopin import Pin

# BCM     Assignment
#  22      Menu Button
#  27      Up Button
#  17      Ok Button
#  25      USB 5V1
#  13      Batt 1


USB_STATUS  = 0
BATT_STATUS = 0

pwr  = Pin(22) # To CNL Pwr/Menu buttuon
up   = Pin(27) # To CNL Pwr/Menu buttuon
ok   = Pin(17) # To CNL Pwr/Menu buttuon
usbp = Pin(25) # To USB +5V
usbg = Pin( 6) # To USB GND
batt = Pin(13) # To Batt +5V

#batt.on()

def logger(txt):
    print(txt)

def press_button(btn, seconds=0.1, wait=0.3):
    sleep(seconds)
    btn.off()
    #print('Waiting {} seconds ...'.format(wait))
    vw(wait)


def turn_usb_off():
    global USB_STATUS
    global usbp
    global usbg

    usbp.off()
    usbg.off()
    USB_STATUS = 0


def turn_usb_on():
    global USB_STATUS
    global usbp
    global usbg

    if USB_STATUS == 1:
        return

    usbp.on()
    usbg.on()
    USB_STATUS = 1
    press_button(ok)
    sleep(5)


def turn_batt_on():
    global BATT_STATUS
    global batt

    logger('  Turning on battery')
    batt.on()
    BATT_STATUS = 1
    #sleep(0.5)


def turn_batt_off():
    global BATT_STATUS
    global batt

    logger('  Turning off battery') 
    batt.off()
    BATT_STATUS = 0


def vw(sec=1):
    if sec < 1.0:
        sleep(sec)
        return

    logger('Waiting {} seconds'.format(sec))
    sleep(sec)
    #print 'Waiting   ', 
    #sys.stdout.flush()
    #for i in range(int(sec),0,-1):
        #print '\b\b\b{:02d}'.format(i), 
        #sys.stdout.flush()
        #sleep(1)
    #print ''


def press_button(btn, seconds=0.1, wait=0.3):
    btn.on()
    sleep(seconds)
    btn.off()
    vw(wait)


def apply_bolus(bolus_amount=0.0):

    if bolus_amount == 0.0:
        logger('No Bolus required')
        return

    #print 50 * '='
    logger('APPLYING {} BOLUS'.format(str(bolus_amount)))

    logger('  Turning Off USB Power')
    turn_usb_off()
    press_button(ok)

    #turn_batt_on()
    logger('  Pressing POWER')
    press_button(pwr, 3, 5)
    logger('  Select BOLUS')
    press_button(ok)
    logger('  Select MANUAL')
    press_button(ok, 0.1, 20)

    for i in range(int(bolus_amount * 10)):
        logger('    Pressing UP')
        press_button(up)

    logger('   Sending Bolus to Pump ...')
    for i in range(10):
        press_button(ok, 0.2, 0.5)
        print('.', end='', flush=True)

    logger('  Bolus sent Done !')
    turn_usb_on()
    turn_usb_off()
    #turn_batt_off()




