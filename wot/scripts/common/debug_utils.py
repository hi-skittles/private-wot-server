# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/debug_utils.py
# Compiled at: 2015-03-09 10:16:07
from collections import defaultdict
import sys
from functools import wraps
from warnings import warn_explicit
from constants import IS_DEVELOPMENT, IS_CLIENT, IS_CELLAPP, IS_BASEAPP
import BigWorld
_src_file_trim_to = ('res/wot/scripts/', len('res/wot/scripts/'))
_g_logMapping = {}

class CriticalError(BaseException):
    pass


def init():
    global _g_logMapping
    if not IS_CLIENT:

        def splitMessageIntoChunks(prefix, msg, func):
            if prefix not in ('EXCEPTION', 'CRITICAL'):
                msg = msg[:8960]
            blockSize = 1792
            for m in msg.splitlines(False)[:100]:
                idx = 0
                while idx < len(m):
                    func(prefix, m[idx:idx + blockSize], None)
                    idx += blockSize

            return

        bwLogTrace = BigWorld.logTrace
        BigWorld.logTrace = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogTrace)
        bwLogDebug = BigWorld.logDebug
        BigWorld.logDebug = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogDebug)
        bwLogInfo = BigWorld.logInfo
        BigWorld.logInfo = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogInfo)
        bwLogNotice = BigWorld.logNotice
        BigWorld.logNotice = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogNotice)
        bwLogWarning = BigWorld.logWarning
        BigWorld.logWarning = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogWarning)
        bwLogError = BigWorld.logError
        BigWorld.logError = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogError)
        bwLogCritical = BigWorld.logCritical
        BigWorld.logCritical = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogCritical)
        bwLogHack = BigWorld.logHack
        BigWorld.logHack = lambda prefix, msg, *args: splitMessageIntoChunks(prefix, msg, bwLogHack)
    _g_logMapping = {'TRACE': BigWorld.logTrace,
     'DEBUG': BigWorld.logDebug,
     'INFO': BigWorld.logInfo,
     'NOTE': BigWorld.logNotice,
     'NOTICE': BigWorld.logNotice,
     'WARNING': BigWorld.logWarning,
     'ERROR': BigWorld.logError,
     'CRITICAL': BigWorld.logCritical,
     'HACK': BigWorld.logHack}


def CRITICAL_ERROR(msg, *kargs):
    msg = '{0}:{1}:{2}'.format(_makeMsgHeader(sys._getframe(1)), msg, kargs)
    BigWorld.logCritical('CRITICAL', msg, None)
    if IS_CLIENT:
        import BigWorld
        BigWorld.quit()
    elif IS_CELLAPP or IS_BASEAPP:
        import BigWorld
        BigWorld.shutDownApp()
        raise CriticalError, msg
    else:
        sys.exit()
    return


def LOG_CURRENT_EXCEPTION():
    from traceback import format_exc
    msg = _makeMsgHeader(sys._getframe(1)) + '\n' + format_exc()
    BigWorld.logError('EXCEPTION', msg, None)
    return


def LOG_WRAPPED_CURRENT_EXCEPTION(wrapperName, orgName, orgSource, orgLineno):
    sys.stderr.write('[%s] (%s, %d):' % ('EXCEPTION', orgSource, orgLineno))
    from sys import exc_info
    from traceback import format_tb, format_exception_only
    etype, value, tb = exc_info()
    if tb:
        list = ['Traceback (most recent call last):\n']
        list = list + format_tb(tb)
    else:
        list = []
    list = list
    for ln in list:
        if ln.find(wrapperName) == -1:
            sys.stderr.write(ln)

    list = format_exception_only(etype, value)
    for ln in list:
        sys.stderr.write(ln.replace(wrapperName, orgName))


def LOG_CODEPOINT_WARNING(*kargs):
    _doLog('WARNING', 'this code point should have never been reached', kargs)


def LOG_ERROR(msg, *kargs):
    _doLog('ERROR', msg, kargs)


def LOG_ERROR_DEV(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('ERROR', msg, kargs)


def LOG_WARNING(msg, *kargs):
    _doLog('WARNING', msg, kargs)


def LOG_NOTE(msg, *kargs):
    _doLog('NOTE', msg, kargs)


def LOG_DEBUG(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('DEBUG', msg, kargs)


def LOG_DEBUG_DEV(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('DEBUG', msg, kargs)


def LOG_NESTE(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('NESTE', msg, kargs)


def LOG_MX(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('MX', msg, kargs)


def LOG_MX_DEV(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('MX', msg, kargs)


def LOG_DZ(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('DZ', msg, kargs)


def LOG_TU(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('TU', msg, kargs)


def LOG_RF(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('RF', msg, kargs)


def LOG_DAN(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('DAN', msg, kargs)


def LOG_DAN_DEV(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('DAN', msg, kargs)


def LOG_VLK_DEV(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('VLK', msg, kargs)


def LOG_VLK(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('VLK', msg, kargs)


def LOG_SK_DEV(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('SK', msg, kargs)


def LOG_SK(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('SK', msg, kargs)


def LOG_OGNICK_DEV(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('OGNICK', msg, kargs)


def LOG_OGNICK(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('OGNICK', msg, kargs)


def LOG_MK(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('MK', msg, kargs)


def LOG_EZ(msg, *kargs):
    if IS_DEVELOPMENT:
        _doLog('JKqq', msg, kargs)


def LOG_IG(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('IG', msg, kargs)


if IS_DEVELOPMENT:

    def LOG_SVAN_DEV(fmt, *args):
        _doLogFmt('SVAN', fmt, *args)


else:

    def LOG_SVAN_DEV(*args, **kwargs):
        pass


def LOG_GUI(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('GUI', msg, kargs)


def LOG_VOIP(msg, *kargs):
    if IS_DEVELOPMENT or not IS_CLIENT:
        _doLog('VOIP', msg, kargs)


def FLUSH_LOG():
    import BigWorld
    BigWorld.flushPythonLog()


def LOG_UNEXPECTED(msg, *kargs):
    _doLog('LOG_UNEXPECTED', msg, kargs)


def LOG_WRONG_CLIENT(entity, *kargs):
    if hasattr(entity, 'id'):
        entity = entity.id
    BigWorld.logError('WRONG_CLIENT', ' '.join(map(str, [_makeMsgHeader(sys._getframe(1)), entity, kargs])), None)
    return


def _doLog(category, msg, args=None):
    header = _makeMsgHeader(sys._getframe(2))
    logFunc = _g_logMapping.get(category, None)
    if not logFunc:
        logFunc = BigWorld.logInfo
    if args:
        output = ' '.join(map(str, [header, msg, args]))
    else:
        output = ' '.join(map(str, [header, msg]))
    logFunc(category, output, None)
    return


def _makeMsgHeader(frame):
    return '(%s, %d):' % (frame.f_code.co_filename, frame.f_lineno)


def _doLogFmt(prefix, fmt, *args):
    msg = _makeMsgHeader(sys._getframe(2))
    msg += fmt.format(*args) if args else fmt
    BigWorld.logInfo(prefix, msg, None)
    return


def trace(func):
    argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
    fname = func.func_name
    frame = sys._getframe(1)

    @wraps(func)
    def wrapper(*args, **kwds):
        BigWorld.logDebug(' '.join('(%s, %d) call %s:' % (frame.f_code.co_filename, frame.f_lineno, fname), ':', ', '.join(('%s=%r' % entry for entry in zip(argnames, args) + kwds.items()))))
        ret = func(*args, **kwds)
        BigWorld.logDebug(' '.join('(%s, %d) return from %s:' % (frame.f_code.co_filename, frame.f_lineno, fname), ':', repr(ret)))
        return ret

    return wrapper


def deprecated(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        warn_explicit('Call to deprecated function %(funcname)s.' % {'funcname': func.__name__}, category=DeprecationWarning, filename=func.func_code.co_filename, lineno=func.func_code.co_firstlineno + 1)
        return func(*args, **kwargs)

    return wrapper


def disabled(func):

    def empty_func(*args, **kargs):
        pass

    return empty_func


def disabled_if(flag, msg=''):
    if flag:

        def disable_func(func):
            LOG_SVAN_DEV('Method ({}) disabled. {} ', func.__name__, msg)
            return disabled(func)

    else:

        def disable_func(func):
            return func

    return disable_func


def dump_garbage(source=False):
    """
    show us what's the garbage about
    """
    import inspect, gc
    print '\nCollecting GARBAGE:'
    gc.collect()
    print '\nCollecting GARBAGE:'
    gc.collect()
    print '\nGARBAGE OBJECTS:'
    for x in gc.garbage:
        try:
            s = str(x)
            if len(s) > 80:
                s = '%s...' % s[:80]
            print '::', s
            print '        type:', type(x)
            print '   referrers:', len(gc.get_referrers(x))
            print '    is class:', inspect.isclass(type(x))
            print '      module:', inspect.getmodule(x)
            if source:
                lines, line_num = inspect.getsourcelines(type(x))
                print '    line num:', line_num
                for l in lines:
                    print '        line:', l.rstrip('\n')

        except:
            pass


def dump_garbage_2(verbose=True, generation=2):
    import gc
    from weakref import ProxyType, ReferenceType
    gc.set_debug(gc.DEBUG_LEAK | gc.DEBUG_STATS)
    if generation is None:
        gc.collect()
    elif generation in xrange(0, 3):
        gc.collect(generation)
    else:
        LOG_ERROR('Value of generation is invalid. Generation may be an integer specifying which generation to collect (from 0 to 2)')
        return
    if verbose:
        print '========================================='
        print '##DUMPSTART'
    del gc.garbage[:]
    d = defaultdict(lambda : 0)
    for i in gc.get_objects():
        if not isinstance(i, ProxyType) and not isinstance(i, ReferenceType):
            if hasattr(i, '__class__'):
                t = i.__class__
            else:
                t = type(i)
            d[t] += 1

    if verbose:
        for t, cnt in d.iteritems():
            print '%d %s' % (cnt, t)

    d.clear()
    del gc.garbage[:]
    del d
    if verbose:
        print '##DUMPEND'
        print '========================================='
    return


def verify(expression):
    try:
        assert expression
    except AssertionError:
        LOG_CURRENT_EXCEPTION()


init()
