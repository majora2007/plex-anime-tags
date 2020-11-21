import time




def RateLimited(maxPerSecond):
    """
    A rate limiter that limits the times per second a function can be called.
    :param maxPerSecond: Max times per second the function should be called
    :return: Function this wraps
    """
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rateLimitedFunction(*args, **kargs):
            elapsed = time.perf_counter() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.perf_counter()
            return ret

        return rateLimitedFunction

    return decorate

from .anidb import *