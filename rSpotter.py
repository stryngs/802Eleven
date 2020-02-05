#!/usr/bin/env python
"""
Spot the RSSI

To Do:
    - Add in min and max seen RSSIs on crtl + C
    - Omni tgt hunting on lost comms
"""

import argparse
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
import packetEssentials as PE
import os
import sys

class Handler(object):
    """ Hunting class """
    def __init__(self):
        self.spC = 4
        self.spA = ['[ | ]',
                    '[ / ]',
                    '[ ~ ]',
                    '[ \\ ]',
                    '[ * ]']


    def pHandler(self, tgtMac):
        """ prn """
        def snarf(packet):
            if PE.pt.macFilter(tgtMac.lower(), packet) is True:

                ## Find the channel in decimal
                spitball = PE.chanFreq.twoFour(packet[RadioTap].ChannelFrequency)
                if spitball is not None:
                    print(self.spinner() + ' ' + str(tgtMac.lower()) + ' --> ' + str(PE.chanFreq.twoFour(packet[RadioTap].ChannelFrequency)) + ' @ ' + str(packet[RadioTap].dBm_AntSignal))
                else:
                    print(self.spinner() + ' ' + str(tgtMac.lower()) + ' --> ' + str(PE.chanFreq.fiveEight(packet[RadioTap].ChannelFrequency)) + ' @ ' + str(packet[RadioTap].dBm_AntSignal))
        return snarf


    def lHandler(self):
        """
        Only hunt To-DS
        """
        def snarf(packet):
            if packet[RadioTap].FCfield == 1 or packet[RadioTap].FCfield == 65:
                return True
            else:
                return False
        return snarf


    def spinner(self):
        """ Track and return the spins """
        ## Grab orig value
        sp = self.spA[self.spC]
        self.spC += 1

        ## Increase or set to 0 new value
        if self.spC >= len(self.spA):
            self.spC = 0
        return sp



def main(args):
    """ Live sniff RSSI hunting """
    hdlr = Handler()
    pHandler = hdlr.pHandler(args.t)
    lHandler = hdlr.lHandler()
    p = sniff(iface = args.i, prn = pHandler, lfilter = lHandler, store = 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'rSpotter - Spot the RSSI')
    parser.add_argument('-t', metavar = 'mac X', help = 'mac to hunt', required = True)
    parser.add_argument('-i', metavar = 'interface', help = 'interface', required = True)
    args = parser.parse_args()
    main(args)
