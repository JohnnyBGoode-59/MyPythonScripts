#-------------------------------------------------------------------------------
# Name:        PyPing
# Purpose:     Provide an easy way to ping a range of IP addresses to identify
#              what devices are on my local network.
#
# Author:      John Eichenberger
#
# Created:     25/07/2023
# Copyright:   (c) John Eichenberger 2023
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

# pip install pythonping
from pythonping import ping

import glob, os, socket, sys
pingTimeout = 1 # seconds to wait for a ping response

def pingonce(ip):
    """ Send one ping and report the response time, if any """
    global pingTimeout
    rsp = ping(ip, count=1, timeout=pingTimeout)
    if rsp.stats_packets_returned:
        try:
            host = socket.gethostbyaddr(ip)
            print("%s(%s): %.1fms" %(ip, host[0], rsp.rtt_avg_ms))
        except:
            print("%s: %.1fms" %(ip, rsp.rtt_avg_ms))

def pingrange(IPs):
    """ Ping a range of IP addresses """
    IPstart = IPs[0].split('.')
    net = IPstart[0] + '.' + IPstart[1] + '.' + IPstart[2] + '.'
    for a in range(int(IPstart[3]), int(IPs[1])):
        pingonce(net + str(a))

def main():
    """ Ping IP addresses and/or simple address ranges """
    global pingTimeout
    range = None
    for arg in sys.argv[1:]:
        if arg[0] == '-' or arg[0] == '/':
            match(arg[1]):
                case 'r' | 'R':
                    range = []
                case 't':
                    pingTimeout = int(arg[2:])
                case '?':
                    print("Ping {IP} [-r IP node]")
        elif range == None:
            pingonce(arg)
        elif len(range) < 2:
            range += [arg]

        # if a complette range is now available, ping that range
        if range != None and len(range) == 2:
            pingrange(range)
            range = None

if __name__ == '__main__':
    main()

