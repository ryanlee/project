import inspect

indent_text = '--'

def _indent(offset=0):
    return indent_text * (len(inspect.stack()) - 3 - offset)

def indent(offset=0):
    return indent_text * (len(inspect.stack()) - 3 - offset) + "-"

def trace_logger(prefix, func, args, file, line, verbose):
    s = "%s+ %s(%s)" % (prefix, func, args)
    if verbose :
        s += " @ %s(%d)" % (file, line)
    if isinstance(verbose,str): 
        s = s + "\n" + prefix + "  " + verbose
    logging.debug(s) # show more details in log
    return s

# sys._getframe(stackdepth)
def trace(verbose=1): # [ryan] verbose can be string too, 1 just add file line info
    """trace function call stack, printwith indent"""
    stacks = inspect.stack()
    (frame, file, line, fname, code, index) = stacks[1]
    mod = os.path.splitext(os.path.basename(file))[0]

    if frame.f_locals.has_key('self') :
        obj = frame.f_locals['self']
        #mod = obj.__class__.__module__ + "." + obj.__class__.__name__
        mod = mod + "." + obj.__class__.__name__

    #grand_parent = stacks[2][0].f_locals
    #if grand_parent.has_key(fname):
    #    func = grand_parent[fname]
    #else :
    #        "\n\tstacks[1]=", stacks[1], stacks[1][0].f_locals,\
    #        "\n\tstacks[2]=", stacks[2], stacks[2][0].f_locals

    prefix = _indent(1)

    (args, varargs, varkw, locals) = inspect.getargvalues(frame)
    argstr = ", ".join([ "%s=%s"%(key,locals[key]) for key in args if key!="self"])

    return trace_logger(prefix, mod+"."+fname, argstr, file, line, verbose)

def log(format, *args):
    logging.info(format,*args)
    print(format % args)

class tracer:
    verbose = 1
    def __init__(self, func, trace_args=[]):
        self.calls = 0
        self.func  = func
        code = func.func_code
        self.file, self.line = code.co_filename, code.co_firstlineno
        arg_count = code.co_argcount
        self.args = code.co_varnames[:arg_count]

    def __call__(self, *args, **kw):
        self.calls += 1
        argstr = ",".join([ "%s=%s"%(x[0],x[1]) for x in zip(self.args,args) ])
        trace_logger(indent(), self.func.__module__+"."+self.func.__name__, argstr, self.file, self.line, self.verbose)

        self.func(*args)

################################################################################
# main
################################################################################
class TestClass (   ):
    """docstring for TestClass"""
    def __init__(self):
        pass
    def test_func2(self):
        trace("test %d %d %d"%(1,2,3))
        trace("test2 %d %d %d"%(1,2,3))
    def test_func1(self):
        trace()
        self.test_func2()
    def test(self):
        trace()
        self.test_func1()

if __name__ == '__main__':
    log("test%s%d","a",2)
    # print(pwd, script, scriptdir, scriptname)
    # print(date())

    TestClass().test()
else:
    pass
