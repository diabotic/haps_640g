# based on https://github.com/cjo20/ns-api-uploader

import time
from datetime import datetime as dt
from dateutil.tz import gettz
from dateutil.parser import parse
import calendar
import requests
import json
import hashlib

import shutil
from multiprocessing.pool import ThreadPool


# ToDo: use a config file to save this
NS_URL = 'https://xxxxxxxxxxxxxxx.herokuapp.com'
API_SECRET = 'YourPassword'.encode('utf-8')
hashed_secret = hashlib.sha1(API_SECRET).hexdigest()

url = "%s/api/v1/entries" % NS_URL



def to_seconds(date):
    return time.mktime(date.timetuple())



def upload_bg(bg=-1, str_pump_time=dt.now(), iob=0.0,  verbose=True ):

    try: 
        if int(bg) < 0 or int(bg) > 600:
            return False

        bg = int(bg)

        now_dt = dt.strptime(str_pump_time, '%Y-%m-%d %H:%M:%S')
        now_tz = now_dt.replace(tzinfo=gettz())    
        now_ts = to_seconds(now_tz)
        #datetime.fromtimestamp(current_time).replace(tzinfo=args.timezone)    
        
        if verbose:
            print("Uploading BG %d at %s" %(bg,  now_tz.isoformat( )))

        payload = dict(type='sgv', sgv=bg, date=int(now_ts * 1000), dateString=now_tz.isoformat( ))

        headers = {'API-SECRET' : hashed_secret,
            'Content-Type': "application/json",
            'Accept': 'application/json'
        }
        r = requests.post(url, headers=headers, data=json.dumps(payload))

        # ToDo: Include IoB and Pump/Sensor Status

        if (r.status_code == 200):
            if verbose:
                print("Uploaded successfully")
            return True
        else:
            if verbose:
                print('ERROR uploading: ' + str(r.status_code ) + ':' + str(r.text))
            return False

    except Exception as e:
        print('ERROR uploading: ' + str(e))
        return False

    return True





