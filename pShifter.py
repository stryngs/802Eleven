#!/usr/bin/python3

import argparse
import random
from scapy.all import *

"""
The first iteration of this code will focus on frames gathered in monitor mode
and operate at layer 2 for pcap anonymization.  This code uses a random mac
generator and tracks what changed.  The original pcap is left untouched and a
new one using the same name with a prefix of shifted_ is created.  theShift.log
is a list that shows all mac addresses found and their subsequent change.

Subsequent versions will work at the TCP/UDP level for further anonymization
options as well as offering hardcoded mac options on the shifting.
"""

class Shifter():
    """Parent class for tracking the identifiers"""
    def __init__(self):
        self.parser = argparse.ArgumentParser(description = 'pShifter - Anonymize a given pcap')
        self.parser.add_argument('-p', help = 'pcap file', metavar = '<pcap>', required = True)
        self.args = self.parser.parse_args()
        self.trackerDict = {}


    def l2Shifter(self):
        """Shifts at layer 2"""
        oList = rdpcap(pS.args.p)
        fList = []
        for n in oList:
            try:
                a1 = pS.trackerDict.get(n.addr1.lower())
            except:
                a1 = None
            try:
                a2 = pS.trackerDict.get(n.addr2.lower())
            except:
                a2 = None
            try:
                a3 = pS.trackerDict.get(n.addr3.lower())
            except:
                a3 = None
            try:
                a4 = pS.trackerDict.get(n.addr4.lower())
            except:
                a4 = None

            ## Deal with not seen and track the seen
            if a1 is None:
                new1 = pS.randMac(n.addr1)
                pS.trackerDict.update({n.addr1: new1})
                n.addr1 = new1
            else:
                n.addr1 = a1
            if a2 is None:
                new2 = pS.randMac(n.addr2)
                pS.trackerDict.update({n.addr2: new2})
                n.addr2 = new2
            else:
                n.addr2 = a2
            if a3 is None:
                new3 = pS.randMac(n.addr3)
                pS.trackerDict.update({n.addr3: new3})
                n.addr3 = new3
            else:
                n.addr3 = a3
            if a4 is None:
                if n.addr4 is None:
                    new4 = None
                else:
                    new4 = pS.randMac(a4)
                if new4 is not None:
                    pS.trackerDict.update({n.addr4: new4})
                    n.addr4 = new4
            fList.append(RadioTap(n.build()))
        with open('theShift.log', 'w') as oFile:
            for k, v in pS.trackerDict.items():
                oFile.write(f'{k} - {v}\n')
        wrpcap(f'shifted_{pS.args.p}', fList)


    def randMac(self, orig):
        """Generate a random mac != the original mac"""
        found = False
        while found is False:
            new = ':'.join([hex(random.randint(0, 255))[2:].zfill(2) for r in range(6)])
            if new != orig.lower():
                found = True
                return new

if __name__ == '__main__':
    pS = Shifter()
    pS.l2Shifter()
