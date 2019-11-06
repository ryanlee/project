from argparse import RawTextHelpFormatter, RawDescriptionHelpFormatter, ArgumentParser
class my_formater (RawTextHelpFormatter,RawDescriptionHelpFormatter) :
    pass

global _parser
global opt
_parser = None
def new_parser(app, desc=""):
    global _parser
    _parser = ArgumentParser(
            prog=app,
            formatter_class=my_formater,
            description=desc,
            epilog="===================================="
            )
    _parser.add_argument('-quiet', '--quiet', default=0, action='store_true', help="only show warnings messages")
    _parser.add_argument('-d', '--debug', default=0, action='store_true',help="enable debug message") 
    _parser.add_argument('-l', '-log', '--log', nargs='?',  metavar='logfile(disko.log)', const="disko.log", help="save log file") # default="disko.log",
    return _parser

from ryan import log
import logging
def parse(opt):
    if opt.quiet :
        log.set(0,logging.WARNING)
    elif opt.debug :
        log.set(0,logging.DEBUG)
    else:
        log.set(0,logging.INFO)
    if opt.log is not None :
        log.set(opt.log)
    logging.debug("opt=%s", opt)

from contextlib import contextmanager

class parser:
    def __init__(self, *args, **kwargs):
        self.p = new_parser(*args, **kwargs)

    def __enter__(self):
        # Do some other stuff
        return self

    def add(self, *args, **kwargs):
        #  print("add",args,kwargs)
        self.p.add_argument(*args, **kwargs)

    def help(self): self.p.print_help()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Do some tear down action, process some data that is 
        # created in __enter__ and log those results
        self.opt = self.p.parse_args()
        parse(self.opt)
        # returning None, we don't want to suppress exceptions
        return None

#  @contextmanager
#  def parser_func(*args, **kwds):
#      p = new_parser(*args, **kwds)
#      try:
#          yield p
#      finally:
#          global opt
#          opt = p.parse_args()
#          parse(opt)
#          logging.debug("opt=%s", opt)

# TODO, add to snip
################################################################################
##  parse options
################################################################################
#  logger = logging.getLogger('')
#  #  logger.setLevel(logging.INFO) # this must below all handler's level, otherwise will override them
#  formatter = logging.Formatter('[%(levelname)-8s] %(message)s' , '%Y/%m/%d %H:%M:%S')
#  handler = logging.StreamHandler()
#  logger.addHandler(handler)
#  handler.setFormatter(formatter)
#  if opt.quiet :
#      logger.setLevel(logging.WARNING)
#  elif opt.debug :
#      logger.setLevel(logging.DEBUG)
#  else:
#      logger.setLevel(logging.INFO)
#  if opt.log is not None :
#      ryan.set_log(opt.log)
#  logging.debug("opt=%s", opt)
