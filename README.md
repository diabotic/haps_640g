# haps_640g

Half Artificial Pancreas System - Only does automatic bolus - NO bolus suspension

Effort to create a Hardware/Software solution to mimic the OpenAPS Project for the 640g Pump. 


# What You Need

1 - Raspberry Pi with Wifi

2 - A Contour Next Link 2.4 to command your 640 Pump

3 - An eletronic board with optocouplers to command the CNL

4 - A Nightscout account


# Installation

Download driver cnl24lib.py from https://github.com/mvp/uhubctl#raspberry-pi-b2b3b 

Put it in the lib directory 

Adjust your nightscout credentials on ns_uploader.py

Adjust your diabetes settings on diabetes.py

Run haps.py



# Thanks

First, I want to thanks for pazaan (https://github.com/pazaan) and oldsterIL (https://github.com/oldsterIL) for all the shared code and knowledge about all IO with medtronic devices. 
Also greate thanks for Ball00 (https://github.com/Bal00) for the 640g integration insights and the electrical scheme
Thanks too for all friends from Brazil, Poland, Russia and the world for helping to brainstorming for other ways to talk to the 640g or Veo


# References 

CNL Driver:
https://github.com/oldsterIL/600SeriesDriver

HW Concept Inspiration:
https://github.com/Bal00/operating-contour-next-link

Command USB of Raspberry Pi:
https://github.com/mvp/uhubctl#raspberry-pi-b2b3b




# Other References 

https://github.com/pazaan/decoding-contour-next-link

https://github.com/galaviz-lip/cgm-remote-monitor

https://github.com/pazaan/600SeriesAndroidUploader

https://github.com/sarunia/MED-LINK-v.4

https://github.com/cjo20/ns-api-uploader/blob/master/uploader.py

https://github.com/dirceusemighini/AndroidAPS

https://github.com/szpaku80/reverse-engineering-contour-next-link-24

https://github.com/openaps/decocare

https://nbviewer.jupyter.org/gist/mariusae/18a62db9cc32d09dc691fd4f78dcdbfa

