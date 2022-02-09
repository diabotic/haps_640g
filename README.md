# haps_640g

Half Artificial Pancreas System - Only does automatic bolus - NO bolus suspension

Effort to create a Hardware/Software solution to mimic the OpenAPS Project for the 640g Pump. 
          

&emsp; 

# What You Need

1 - Raspberry Pi with Wifi

2 - A Contour Next Link 2.4 to command your 640 Pump

3 - An eletronic board with optocouplers to command the CNL

4 - A Nightscout account


&emsp; 

# Installation

Download driver cnl24lib.py from https://github.com/oldsterIL/600SeriesDriver

Put it in the lib directory 

Adjust your nightscout credentials on ns_uploader.py

Adjust your diabetes settings on diabetes.py

Run haps.py


&emsp; 

# Thanks

First, I want to thanks for pazaan (https://github.com/pazaan) and oldsterIL (https://github.com/oldsterIL) for all the shared code and knowledge about all IO with medtronic devices. 
Also greate thanks for Ball00 (https://github.com/Bal00) for the 640g integration insights and the electrical scheme
Thanks too for all friends from Brazil, Poland, Russia and the world for helping to brainstorming for other ways to talk to the 640g or Veo


&emsp; 

# References 

CNL Driver:
https://github.com/oldsterIL/600SeriesDriver

HW Concept Inspiration:
https://github.com/Bal00/operating-contour-next-link

Command USB of Raspberry Pi:
https://github.com/mvp/uhubctl#raspberry-pi-b2b3b


&emsp; 

&emsp; 


# Other References 

http://www.nightscout.info/

https://github.com/benceszasz/minimed-connect-to-nightscout

https://github.com/pazaan/decoding-contour-next-link

https://github.com/galaviz-lip/cgm-remote-monitor

https://github.com/pazaan/600SeriesAndroidUploader

https://github.com/sarunia/MED-LINK-v.4

https://github.com/cjo20/ns-api-uploader/blob/master/uploader.py

https://github.com/dirceusemighini/AndroidAPS

https://github.com/szpaku80/reverse-engineering-contour-next-link-24

https://github.com/openaps/decocare

https://nbviewer.jupyter.org/gist/mariusae/18a62db9cc32d09dc691fd4f78dcdbfa

https://github.com/nightscout/AndroidAPS

https://androidaps.readthedocs.io/en/latest/Installing-AndroidAPS/Building-APK.html

https://www.diabettech.com/looping-a-guide/

https://github.com/LilDucky/Medtronic-6xx

https://jensheuschkel.wordpress.com/2017/08/27/contour-next-link-link-2-4-teardown/?fbclid=IwAR2c099oM8qqQmjtrqf-OwLVuBRgllDe6fH1Qwozvow4-i-nKoK7GAeUIDQ

https://github.com/JoernL/LimiTTer

https://www.intechopen.com/books/gluconeogenesis/blood-glucose-prediction-for-artificial-pancreas-system

https://github.com/szpaku80/reverse-engineering-contour-next-link-24

