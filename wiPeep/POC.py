#!/usr/bin/python3

from scapy.all import *

def wiPeep():
    bList = [b'\x00\x01\x00']
    bStr = bytes()
    for i in range(1):
        bList.append(b'\xff')
    for b in bList:
        bStr += b
    return RadioTap()\
           /Dot11FCS(type = 0,
                     subtype = 8,
                     addr1 = 'ff:ff:ff:ff:ff:ff',
                     addr2 = macGw,
                     addr3 = macGw)\
           /Dot11Beacon()\
           /Dot11Elt(ID = 0,
                     info = essid,
                     len = len(essid))\
           /Dot11EltRates(rates = rates)\
           /Dot11EltDSSSet(channel = channel)\
           /Dot11Elt(ID = 5,
                     info = bStr)

macGw = 'aa:bb:cc:dd:ee:ff'
essid = 'testing'
rates = [2, 4, 11, 22, 12, 18, 24, 36]
channel = 6
f = wiPeep()
sendp(f, iface = 'wlan1mon')
