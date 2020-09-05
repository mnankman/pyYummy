import util

class Log:
    VERBOSITY_NONE = 0
    VERBOSITY_ERROR = 1
    VERBOSITY_WARNING = 2
    VERBOSITY_VERBOSE = 3
    VERBOSITY_DEBUG = 4
    VERBOSITY_PREFIXES = ["", "ERROR:", "WARNING:", "TRACE:", "DEBUG:"]
    class __Log:
        def __init__(self, verbosity):
            self.verbosity = verbosity

        def debug(self, *args, **kwargs):
            if self.verbosity>=Log.VERBOSITY_DEBUG:
                self.print(Log.VERBOSITY_DEBUG, *args, **kwargs)

        def warning(self, *args, **kwargs):
            if self.verbosity>=Log.VERBOSITY_WARNING:
                self.print(Log.VERBOSITY_WARNING, *args, **kwargs)

        def error(self, *args, **kwargs):
            if self.verbosity>=Log.VERBOSITY_ERROR:
                self.print(Log.VERBOSITY_ERROR, *args, **kwargs)

        def trace(self, *args, **kwargs):
            if self.verbosity>=Log.VERBOSITY_VERBOSE:
                self.print(Log.VERBOSITY_VERBOSE, *args, **kwargs)

        def print(self, verbosityLevel, *args, **kwargs):
            if self.verbosity>=Log.VERBOSITY_VERBOSE: 
                func = None
                fargs = None
                returns = None
                var=None
                kwargs2 = {}
                args2 = (Log.VERBOSITY_PREFIXES[verbosityLevel],) + args
                for k,v in kwargs.items():
                    if k=="function": 
                        try:
                            func = v.__qualname__
                        finally:
                            pass
                        if not func: func = v
                    elif k=="args": 
                        fargs = util.collectionToString(v) if isinstance(v, (tuple,list)) else "(" + util.toString(v) + ")"
                    elif k=="returns": 
                        returns = util.collectionToString(v) if isinstance(v, (tuple,list)) else util.toString(v)
                    elif k=="var":
                        assert isinstance(v, tuple) and len(v)==2
                        varName, varValue = v
                        args2 += (varName, "=", varValue)
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
            self.trace(function=self.setVerbosity, args=(verbosity,))

    instance = None
    def __init__(self):
        if not Log.instance:
            Log.instance = Log.__Log(Log.VERBOSITY_NONE)
    
    def debug(self, *args, **kwargs):
        if Log.instance:
            Log.instance.debug(*args, **kwargs)

    def warning(self, *args, **kwargs):
        if Log.instance:
            Log.instance.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        if Log.instance:
            Log.instance.error(*args, **kwargs)

    def trace(self, *args, **kwargs):
        if Log.instance:
            Log.instance.trace(*args, **kwargs)

    def setVerbosity(self, verbosity):
        if Log.instance:
            Log.instance.setVerbosity(verbosity)

log = Log()
log.setVerbosity(Log.VERBOSITY_DEBUG)

def debug(*args, **kwargs):
    log.debug(*args, **kwargs)

def warning(*args, **kwargs):
    log.warning(*args, **kwargs)

def error(*args, **kwargs):
    log.error(*args, **kwargs)

def trace(*args, **kwargs):
    log.trace(*args, **kwargs)

def setVerbosity(verbosity):
    log.setVerbosity(verbosity)

