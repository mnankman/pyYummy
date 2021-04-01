import logging
import inspect
import util

loggers = {}

def log(logger_method, msg, *args, **kwargs):
    func = None
    fargs = None
    returns = None
    var=None
    kwargs2 = {}
    args2 = args
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
    logger_method(msg + util.collectionToString(args2))

def getLogger():
    frm = inspect.stack()[2]
    modName = inspect.getmodule(frm[0]).__name__
    if modName in loggers:
        logger = loggers[modName]
    else:
        logger = logging.getLogger(modName)
        loggers[modName] = logger
        #logging.debug('new logger:', modName)
    return logger

def debug(*args, **kwargs):
    log(getLogger().debug, "", *args, **kwargs)

def warning(*args, **kwargs):
    log(getLogger().warning, "", *args, **kwargs)

def error(*args, **kwargs):
    log(getLogger().error, "", *args, **kwargs)

def trace(*args, **kwargs):
    log(getLogger().info, "", *args, **kwargs)


