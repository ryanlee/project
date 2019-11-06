COLOR = {
    "reset"     : "\x1b[0m",                 
    "bold"      : "\x1b[01m",                

    "turquoise" : "\x1b[36;01m",             
    "teal"      : "\x1b[36;06m",             
    "fuscia"    : "\x1b[35;01m",             
    "purple"    : "\x1b[35;06m",             
    "blue"      : "\x1b[34;01m",             
    "darkblue"  : "\x1b[34;06m",             
    "yellow"    : "\x1b[33;01m",             
    "brown"     : "\x1b[33;06m",             
    "green"     : "\x1b[32;01m",             
    "darkgreen" : "\x1b[32;06m",             
    "red"       : "\x1b[31;01m",             
    "darkred"   : "\x1b[31;06m",             
}
COLOR_BG = "\x1b[48;5;0m"

import sys
def cprint (color, s, *args, **kwargs) :
    if   args : s = s % args                 
    if kwargs : s = s % kwargs               
    sys.stdout.write(COLOR[color])           
    sys.stdout.write(s)                      
    sys.stdout.write(COLOR['reset'])


import logging

COLOR_LEVELS = {
    logging.CRITICAL : COLOR['purple'],          # CRITICAL 50    
    logging.ERROR    : COLOR['red'],             # ERROR    40    
    logging.WARNING  : COLOR['teal'],            # WARNING  30    
    logging.INFO     : COLOR['darkgreen'],       # INFO     20    
    logging.DEBUG    : COLOR['darkblue'],        # DEBUG    10    
    logging.NOTSET   : COLOR['bold'],            # NOTSET    0     
}
class ColorStreamHandler(logging.StreamHandler):
    def emit(self, record):
        s = self.format(record) + '\n'
        c = COLOR_LEVELS[record.levelno]
        # sys.stdout.write(COLOR_BG)           
        # sys.stdout.write(COLOR['bold'])           
        sys.stdout.write(c)
        sys.stdout.write(s)
        sys.stdout.write(COLOR['reset'])

import os
def set(stream=0, level='', format=''):
    """add a log handler, default to console"""
    logger = logging.getLogger('')
    handlers = logger.handlers
    handler  = stream if isinstance(stream,logging.Handler) else None
    if isinstance(stream,int) or isinstance(stream,logging.StreamHandler): # 0 means stdout
        for h in logger.handlers :
            if isinstance(h,logging.StreamHandler) :
                logger.removeHandler(h) # remove old, otherwise there will be multiple active stream, duplicated output 
        if handler is None:
            if os.getenv('TERM') in ("screen", "screen-256color", "tmux", "tmux-256color", "xterm", "xterm-256color") :
                handler = ColorStreamHandler()
            else:
                handler = logging.StreamHandler()
        if format == '' : format = '[%(levelname)-8s] %(message)s'
        if level  == '' : level = logging.INFO
    elif isinstance(stream,str) : # string means file
        for h in logger.handlers :
            if isinstance(h,logging.FileHandler) :
                handler = h
                break
        else :
            handler = logging.FileHandler(stream,'w')
        if format == '' : format = '%(asctime)s @ %(filename)16s,%(lineno)04d [%(levelname)-8s] %(message)s'
        if level  == '' : level = logging.DEBUG
    elif isinstance(stream,logging.Handler) : # custom handler
        if format == '' : format = '%(asctime)s @ %(filename)16s,%(lineno)04d [%(levelname)-8s] %(message)s'
        if level  == '' : level = logging.DEBUG
    else:
        return

    # logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG) # this must below all handler's level, otherwise will override them

    handler.setLevel(level)

    datefmt='%Y/%m/%d %H:%M:%S'
    formatter = logging.Formatter(format, datefmt)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    # return handler.getLevel()

#  set_log() # default to console

# # show all info in log
# logging.basicConfig(
#     level=logging.DEBUG,
#     # format='%(asctime)s @ %(filename)16s,%(lineno)04d %(name)-8s: [%(levelname)-8s] %(message)s',
#     format='%(asctime)s @ %(filename)16s,%(lineno)04d [%(levelname)-8s] %(message)s',
#     datefmt='%Y/%m/%d %H:%M:%S',
#     filename=f,
#     filemode='w')

# # show only ERROR/CRITICAL on console
# console = logging.StreamHandler()
# console.setLevel(logging.WARNING)
# formatter = logging.Formatter('[%(levelname)-8s] %(message)s')
# console.setFormatter(formatter)
# logging.getLogger('').addHandler(console)

