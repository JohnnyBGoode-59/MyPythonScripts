#-------------------------------------------------------------------------------
# Name: Logging
# Purpose: Read and write Json files.
#
# Author: John Eichenberger
#
# Created:     25/08/2020
# Copyright:   (c) John Eichenberger 2020
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import os, time, sys
import porting

now = None

def timespent(start=None):
    """ Returns time spent between the specified start time and now, in a printable string. """
    global now
    if start!=None:
        now=start
    elif now==None:
        now=time.time()
    elapsed = time.gmtime(time.time()-now)
    # Add the number of hours in a day for every day since the start time
    hours = elapsed.tm_hour + (elapsed.tm_yday-1) * 24
    return "%02d:%02d:%02d" % (hours, elapsed.tm_min, elapsed.tm_sec)

def display_update(number, name, reset=False):
    """ displays a running count of things when a lot of time has gone by with nothing else printed """
    global now
    if reset or now == None:
        now = time.time()
    else:
        test = time.time()
        if (test - now) > 5:  # Seconds between updates
            print("{:,} {}s".format(number, name), end='\r')
            now = test

class logging:
    """ Provides a simple class to log messages to a file. """
    logfile = None
    style = None    # [ length, prefix, postfix ]

    def __init__(self, pn=None, clean=True, style=[32, 38]):
        """ pn can be a fully qualifed pathname or relative pathname.
            clean defaults to True, meaning that the logfile will be removed.
        """
        global now
        if now==None:
            now=time.time()
        if pn==None:
            rootp, fn = os.path.split(sys.argv[0])
            fn, ext = os.path.splitext(fn)
            pn = fn + '.txt'

        rootp, fn = os.path.split(pn)
        if rootp == '':
            rootp = os.environ.get('TEMP')
            if rootp is None:
                rootp = porting.addpath('', 'tmp')  # Linux default

        self.logfile = os.path.abspath(porting.addpath(rootp, fn))
        self.style = [style[0]+style[1]+5] + style
        if clean:
            self.remove()

    def msg(self, message, silent=False):
        """ Log a simple message """
        global now
        log = open(self.logfile, 'a')
        log.write(message + '\n')
        log.close()
        if not silent:
            print(message)
            now = time.time()

    def nickname(self, pn):
        """ Shorten really long names when all I really need is the basics. """
        if len(pn) > self.style[0]:
            return pn[0:self.style[1]] + "[...]" + pn[-self.style[2]:]
        return pn

    def command(self, prefix1, pn1, prefix2=None, pn2=None, silent=False):
        """ Log a command with one or two pathnames included """
        global now
        cmd = '{} "{}" '.format(prefix1, pn1)
        if prefix2 != None:
            cmd += prefix2
        if pn2 != None:
            cmd += ' "{}"'.format(pn2)

        try:
            log = open(self.logfile, 'a')
            log.write(cmd + '\n')
            log.close()
            if not silent:
                print(cmd)
                now = time.time()
        except:
            pass

    def count(self, counters, name, pathname=None, silent=False):
        """ Log message that includes a counter and possible a pathname """
        fullmsg = name + '\n'
        shortmsg = name
        if pathname != None:
            fullmsg = '"' + pathname + '": ' + fullmsg
            shortmsg = self.nickname(pathname) + ": " + shortmsg
        try:
            log = open(self.logfile, 'a')
            log.write(fullmsg)
            log.close()
            if not silent:
                print(shortmsg)
                now = time.time()
        except:
            pass
        self.increment(counters, name)
        return counters

    def error(self, counters, err, pathname=None, silent=False):
        """ Log an error that may include a pathname """
        global now
        fullmsg = err + '\n'
        shortmsg = err + ' (error)'
        if pathname != None:
            fullmsg = '"' + pathname + '": ' + fullmsg
            shortmsg = self.nickname(pathname) + ": " + shortmsg
        try:
            log = open(self.logfile, 'a')
            log.write(fullmsg)
            log.close()
            if not silent:
                print(shortmsg)
                now = time.time()
        except:
            pass
        self.increment(counters, err)
        return counters

    def increment(self, counters, name):
        """ Increment a counter in a dictionary."""
        if name in counters:
            counters[name] += 1
        else:
            counters[name] = 1

    def counter(self, count, msg):
        """ Display a counter in a consistent way. """
        if count == 1:
            self.msg("1 {}.".format(msg))
        elif count > 1:
            self.msg("{:,} {}s.".format(count, msg))

    def counters(self, counters):
        """ Display a dictionary of counters """
        for err in counters:
            self.counter(counters[err], err)

    def sum(self, counters):
        """ Return the sum of a dictionary of counters """
        sum = 0
        for err in counters:
            sum += counters[err]
        return sum

    def remove(self):
        if os.path.exists(self.logfile):
            os.remove(self.logfile)

if __name__ == '__main__':
    """ Test this class """
    counters = {}
    timespent()
    testfile = "Logging.txt"
    log = logging(testfile, style=[10,12])
    log.msg("This is a simple message")
    log.error(counters, "simple counter")
    time.sleep(1)
    log.increment(counters, "delay")
    time.sleep(1)
    log.increment(counters, "delay")
    log.error(counters, "simple counter", log.logfile)
    log = logging(clean=False)
    log.error(counters, "additional error", log.logfile)
    time.sleep(1)
    log.increment(counters, "delay")
    log.counter(123, "stick")
    log.counter(1, "pizza")
    log.counter(0, "unknown")
    log.counter(log.sum(counters), "counter")
    for l in range(17):
        time.sleep(1)
        log.increment(counters, "delay")
        display_update(l, "loop")
    log.counters(counters)
    log.msg("Completed in {}".format(timespent()))
