from builtins import map
from builtins import str
from builtins import object
import string
import json
import os.path
import re
import subprocess
import socket
import sys
from .common import *
from .execute import *


# --------------------------------------------------------------------------------------------------------------------------
# Network Utilities
# --------------------------------------------------------------------------------------------------------------------------

def reachable(host, timeout=2):
    """ Return True if the given host is reachable"""
    opts = {
        'verbosityThreshold':5,
        'captureStdOutStdErr': True,
        'permitShowingStdOut': False,
        'permitShowingStdErr': False,
        'ignoreErrors': True}
    ping_response = execute("ping -c1 -W{timeout} {host}", **opts)[1]
    return ('1 packets transmitted, 1 received' in ping_response) or ('1 packets transmitted, 1 packets received' in ping_response)



# --------------------------------------------------------------------------------------------------------------------------
# IP utilities
# --------------------------------------------------------------------------------------------------------------------------

def octetFromIP(ip,n):
    '''Returns the nth octet (0-indexed) of the given ip string'''
    return ip.split('.')[n]

def ip2Long(ip):
    '''Returns IP in Int format from Octet form'''
    octs = list(map(int, ip.split('.')))
    return octs[0]*2**24 + octs[1]*2**16 + octs[2]*2**8 + octs[3]

def long2ip(ipnum):
    '''Returns IP in Octet form from int form'''
    def octet(ipnum,n):
        return str((ipnum & (255*256**(3-n))) >> 8*(3-n))
    return octet(ipnum,0) +'.'+ octet(ipnum,1) +'.'+ octet(ipnum,2) +'.'+ octet(ipnum,3)

def maskByIP(ip, mask):
    '''Return the given ip masked out by the given ip mask'''
    return long2ip(ip2Long(ip) & ip2Long(mask))

def validIP(ipstr):
    '''Check that the given string represents a quad dotted IP address'''
    octets = ipstr.split('.')
    if len(octets) != 4:
        return False
    return not (False in [quiet(lambda s: 0<=int(s) and int(s)<=255, o) for o in octets])

def subnetOfIp(ipstr, octetsToDrop = 1):
    return ".".join(ipstr.split(".")[:-octetsToDrop])

def getLocalHostIP():
    return [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

