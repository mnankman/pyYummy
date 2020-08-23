
class Log:
    VERBOSITY_NONE = 0
    VERBOSITY_ERROR = 1
    VERBOSITY_VERBOSE = 2
    VERBOSITY_DEBUG = 3
    VERBOSITY_PREFIXES = ["", "ERROR:", "", "DEBUG:"]
    class __Log:
        def __init__(self, verbosity):
            self.verbosity = verbosity

        def debug(self, *args, **kwargs):
            if self.verbosity>=Log.VERBOSITY_DEBUG:
                self.trace(*args, **kwargs)

        def error(self, *args, **kwargs):
            if self.verbosity>=Log.VERBOSITY_ERROR:
                self.trace(*args, **kwargs)

        def trace(self, *args, **kwargs):
            if self.verbosity>=Log.VERBOSITY_VERBOSE: 
                func = None
                fargs = None
                returns = None
                kwargs2 = {}
                args2 = (Log.VERBOSITY_PREFIXES[self.verbosity],) + args
                for k,v in kwargs.items():
                    if k=="function": func = v
                    elif k=="args": fargs = v
                    elif k=="returns": returns = v
                    else: kwargs2[k] = v
                if func:
                    args2 += (func, fargs if fargs else "()")
                    if returns: 
                        args2 += ("-->", returns)
                    print(*args2, **kwargs2)
                else:
                    print(*args2, **kwargs2)

        def setVerbosity(self, verbosity):
            self.verbosity = verbosity

    instance = None
    def __init__(self):
        if not Log.instance:
            Log.instance = Log.__Log(Log.VERBOSITY_NONE)
    
    def debug(self, *args, **kwargs):
        self.trace(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.trace(*args, **kwargs)

    def trace(self, *args, **kwargs):
        if Log.instance:
            Log.instance.trace(*args, **kwargs)

    def setVerbosity(self, verbosity):
        if Log.instance:
            Log.instance.setVerbosity(verbosity)

