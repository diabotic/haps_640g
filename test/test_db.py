import sys
import os
import traceback
sys.path.append('lib')

from db import *


print(get_ns_records(10))
