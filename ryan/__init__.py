"""
support library for ryan
"""
__all__ = [ 'tracer', 'trace', 'date', 'RUNTIME', 'dump', 'timer']

################################################################################
# support functions
################################################################################
import time
def date(format="%(year)04d-%(month)02d-%(mday)02d %(hour)02d:%(minute)02d:%(second)02d", t=""):
    """docstring for date"""
    if t == "": t = time.localtime()
    dict_date = dict(zip(("year", "month", "mday", "hour", "minute", "second", "wday", "yday"), t))
    date =  format % dict_date
    return date

import logging
from contextlib import contextmanager
import time
@contextmanager
def timer(action="run", func=logging.debug):
    if action is not None and action != '' and func is not None:
        t0 = time.time()
    yield
    if action is not None and action != '' and func is not None:
        func("(%.2fs) %s" %( time.time() - t0, action))

import pprint
pp = pprint.PrettyPrinter(indent=2,width=100,depth=3)
def dump(obj):
    pp.pprint(obj)
    #print(obj.__name__, "=", repr(obj.__dict__))
    #for key,val in obj.__dict__.items():
    #    print("\t", key, "=>", val)

import os
def ENV(name, value=None, only_set_if_none=0):
    old = os.getenv(name,None)
    if value != None and (only_set_if_none and old!=None):
        os.putenv(name,value)
    return old if old is not None else ""

def size_fmt(num, suffix=''):
    for unit in ['B','K','M','G','T','P','E','Z']: # 
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def time_fmt(num, suffix=''):
    for unit in ['second(s)','minute(s)','hour(s)']: # 
        if abs(num) < 60:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 60

import pwd
def user_fmt(uid):
    try:
        user_pw = pwd.getpwuid(uid)
        user = user_pw.pw_name # login name (ID)
        uname = user_pw.pw_gecos #user full name
    except KeyError as e:
        uname = "UNKNOWN-%d"% (uid,)
    return uname

################################################################################
# global variable
################################################################################
import sys
RUNTIME = date()
pwd = os.getcwd()
script     = os.path.abspath(sys.argv[0])
scriptdir  = os.path.dirname(sys.argv[0])
scriptname = os.path.basename(sys.argv[0])

################################################################################
##  support 
################################################################################
class no_re_enter:
    def __init__(self, func):
        self.calls = 0
        self.func  = func
    def __call__(self, *args):
        if self.calls > 0 :
            print("calls '%s' to '%s' already run before(%d), so pass this time" % (self.calls, self.func.__name__, self.calls))
        else :
            self.func(*args)
        self.calls += 1

if __name__ == '__main__':
    print(pwd, script, scriptdir, scriptname)
    print(date())
else:
    pass
