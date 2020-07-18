
class Log:
    VERBOSITY_NONE = 0
    VERBOSITY_VERBOSE = 1
    class __Log:
        def __init__(self, verbosity):
            self.verbosity = verbosity

        def trace(self, *args, **kwargs):
            if self.verbosity>0: print(*args, **kwargs)

        def setVerbosity(self, verbosity):
            self.verbosity = verbosity

    instance = None
    def __init__(self):
        if not Log.instance:
            Log.instance = Log.__Log(Log.VERBOSITY_NONE)
    

    def trace(self, *args, **kwargs):
        if Log.instance:
            Log.instance.trace(*args, **kwargs)

    def setVerbosity(self, verbosity):
        if Log.instance:
            Log.instance.setVerbosity(verbosity)

