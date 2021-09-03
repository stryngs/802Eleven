#!/usr/bin/python3

"""
Traces the source of a given 802.11 transmission based on the specs from IEEE in
 reference to ADDRs 1-4 for the source of a given frame that has been
 transmitted.
"""

import packetEssentials as PE
import sys
from scapy.all import *

def pHandler(tgtMac):
    def tailChaser(packet):

        ## Null the flags
        fromDS = False
        toDS = False
        fcField = None

        ## Notate bits
        if PE.pt.nthBitSet(packet[Dot11].FCfield, 0) is True:
            toDS = True
        if PE.pt.nthBitSet(packet[Dot11].FCfield, 1) is True:
            fromDS = True

        ## Who sent it
        if fromDS & toDS:
            direc = '11'
            theMac = packet[Dot11].addr4
        elif toDS:
            direc = '01'
            theMac = packet[Dot11].addr2
        elif fromDS:
            direc = '10'
            theMac = packet[Dot11].addr3
        else:
            direc = '00'
            theMac = packet[Dot11].addr2

        ## Was it ours
        if theMac == tgtMac:
            return True

        ### Need some kind of flicker to let the human know just how active
    return tailChaser

if __name__ == '__main__':
    try:
        LFILTER = pHandler(sys.argv[2])
    except Exception as E:
        print('python3 ./foxHunter.py <NIC> <tgt mac address>')
        sys.exit(1)
    try:
        mNic = sys.argv[1]
    except Exception as E:
        print('python3 ./foxHunter.py <NIC> <tgt mac address>')
        sys.exit(1)

    p = sniff(iface = mNic, prn = lambda x: x[RadioTap].dBm_AntSignal, lfilter = LFILTER)
