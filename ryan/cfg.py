import os
#  APP = os.path.dirname(os.path.realpath(__file__))
#  f = APP + "config.ini"

import configparser
parser = configparser.ConfigParser()

import logging

def w():
    logging.warning("-> writing %s", f)
    with open(f, 'w') as FILE:
        parser.write(FILE)

import sys
if getattr( sys, 'frozen', False ) :
	app_path = sys.executable
else :
	import __main__ as main
	app_path = main.__file__
app_name = os.path.splitext(os.path.basename(app_path))[0]
app_dir = os.path.dirname(app_path)

app_ini = "%s/%s.ini" % (app_dir, app_name)
#  app_ini = "%s/%s.ini" % ('.', app)
#  print("file=",main.__file__)
#  print("argv=",sys.argv[0])
#  print(app_path)
#  print(app_dir)
#  print(app_name)
#  print(app_ini)

read_before = False
def r(ff=app_ini, refresh=False):
    global f
    if ff is not None:
        f = ff
    global read_before
    if refresh or not read_before:
        read_before = True
        if os.path.exists(f):
            logging.info("-> reading %s", f)
            parser.read(f)
        else:
            logging.warning("-> init %s ", f)

def rw(read=1):
    if read:
        read_cfg()
    else:
        write_cfg()

class Section :
    name = 'DEFAULT'
    def __init__(self, name='DEFAULT'):
        self.name = name
    def get(self, k, fallback=None):
        return get(self.name, k,fallback)
    def set(self, k, v):
        return set(self.name, k,v)
    def __getattr__(self, k): # self.attr
        if k in ('name',) :
            super().__getattr__(k)
        else:
            return get(self.name, k)
    def __setattr__(self, k, v): # self.attr
        if k in ('name',) :
            super().__setattr__(k,v)
        else:
            set(self.name, k,v)
    def __repr__(self):
        return f"[{self.name}]"
    def w(self):
        w()

from functools import partial
def get_section(section):
    #  if section != "DEFAULT" and not parser.has_section(section):
    #      parser.add_section(section)
    return Section(section)

DATA = {} # hold correct dtype
def get(section='DEFAULT', k=None, fallback=None, prompt=""):
    if section != "DEFAULT" and not parser.has_section(section):
        parser.add_section(section)
    if k is None: # need setion
        return get_section(section)

    if isinstance(k, dict):
        for kk, kf in k.items():
            k[kk] = get(section, kk, kf)
        return k

    if k in DATA.get(section, {}):
        return DATA[section][k]

    if parser.has_option(section,k):
        v = parser.get(section, k)
        logging.debug(f"<- [{section}] {k}={v}")
        if fallback is not None:
            t = type(fallback)
            if t == list:
                v = v.split(',')
            elif t == bool:
                v = True if v=='True' else False
            else:
                v = t(v)
        if section not in DATA: DATA[section] = {}
        DATA[section][k] = v
    else:
        if prompt != "":
            v = input(prompt)
        else:
            v = fallback
        set(section, k, v)
        w()
    return v

def set(section, k, v=None):
    if section not in DATA: DATA[section] = {}
    if isinstance(k, dict):
        for kk, kv in k.items():
            set(section, kk, kv)
        return

    DATA[section][k] = v
    logging.debug(f"-> [{section}] {k}={v}")
    if type(v)==list :
        vt = ','.join(v)
    #  elif type(v)==bool :
    #      vt = str(1 if vt else 0) # bool('False')=>True, so use 0/1 instead
    else:
        vt = str(v)
    parser.set(section,k,vt)

#  from contextlib import contextmanager
#  @contextmanager
#  def cfg(action="run", func, w):
#      kwargs = dict(k='call', v=(-10,10))
#      yield #  w = RangeSlider(title='CALL RANGE', value=call_range(None,None,None,**kwargs), start=-20, end=20, step=1, width=200)
#      self.w['call_range'].on_change('value', partial(call_range,**kwargs))
#      func("(%.2fs) %s" %( time.time() - t0, action))

if __name__ == '__main__':
    #  cfg = globals()
    f = 'test.ini'
    r(f)
    s = 'section1'
    opt = dict(
        option1_int =1,
        option2_int =2,
        option3_bool=True
        )
    for k,vdef in opt.items():
        v = get(s, k, vdef)
        #  print(f'{k}={v}, type={type(v)}')
    cc = get(s)
    cc.option2_int = 3
    w()
    with open(f) as F:
        print(F.read())
else:
    #  r()
    pass # Work as a module
