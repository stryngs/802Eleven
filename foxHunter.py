#!/usr/bin/python3

import argparse
import packetEssentials as PE
import sys
from scapy.all import *

class Fox(object):
    """ Traces the source of a given 802.11 transmission based on the specs from
    IEEE in reference to ADDRs 1-4 for the source of a given frame that has been
    transmitted.
    """

    __slots__ = ['i', 't', 'spC', 'spA']

    def __init__(self, i, t):
        self.i = i
        self.t = t
        self.spC = 4
        self.spA = ['[ | ]',
                    '[ / ]',
                    '[ ~ ]',
                    '[ \\ ]',
                    '[ * ]']


    def lFilter(self, tgtMac):
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
        return tailChaser


    def pHandler(self, tgtMac):
        """ prn """
        def snarf(packet):

            ## Find the channel in decimal
            spitball = PE.chanFreq.twoFour(packet[RadioTap].ChannelFrequency)
            if spitball is not None:
                print(self.spinner() + ' ' + str(tgtMac.lower()) + ' --> ' + str(PE.chanFreq.twoFour(packet[RadioTap].ChannelFrequency)) + ' @ ' + str(packet[RadioTap].dBm_AntSignal))
            else:
                print(self.spinner() + ' ' + str(tgtMac.lower()) + ' --> ' + str(PE.chanFreq.fiveEight(packet[RadioTap].ChannelFrequency)) + ' @ ' + str(packet[RadioTap].dBm_AntSignal))
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
    """Grab a fox by the tail"""
    fx = Fox(args.i, args.t)
    lFilter = fx.lFilter(args.t)
    pHandler = fx.pHandler(args.t)
    mNic = args.i
    sniff(iface = mNic, prn = pHandler, lfilter = lFilter, store = 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Fox hunting for 802.11')
    parser.add_argument('-t',
                        metavar = 'MAC to listen for',
                        help = 'MAC to listen for', required = True)
    parser.add_argument('-i',
                        metavar = 'NIC to sniff with',
                        help = 'NIC to sniff with', required = True)
    args = parser.parse_args()
    main(args)
