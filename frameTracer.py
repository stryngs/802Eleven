#!/usr/bin/env python
"""
Trace a framed based on a MAC or pair of MACs

Use macX as the quietest of the MACs
"""

import argparse
import binascii
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *
import packetEssentials as PE
import os
import sys

class Hub(object):
    """Hub and spoke concept for following frame interactions"""

    def __init__(self):
        self.mainDict = {}

def main(args):
    global pkts
    ## Verbosity
    if args.v is True:
        PE.hd.verbose = True
        verbosity = True
    else:
        verbosity = False

    """
    Perhaps retool mpTrafficCap and soloCap to be split functions for speed?
    """

    ## Trace a pair
    if args.y is not None:
        if args.c is not None:
            pHandler = PE.hd.mpTrafficCap(args.x.lower(), args.y.lower(), q = args.c, verbose = verbosity)
        else:
            pHandler = PE.hd.mpTrafficCap(args.x.lower(), args.y.lower(), verbose = verbosity)

    ## Trace a single
    else:
        if args.c is not None:
            pHandler = PE.hd.soloCap(args.x.lower(), q = args.c, verbose = verbosity)
        else:
            pHandler = PE.hd.soloCap(args.x.lower(), verbose = verbosity)

    ## pcap as an input
    if args.f is None:
        pkts = sniff(iface = args.i, prn = pHandler, store = 0)
    else:
        pkts = sniff(offline = args.f, prn = pHandler, store = 0)
        if args.c is None: ## Need to add mutual exclusion for pcap read -or- the option
            if len(PE.hd.soloList) > len(PE.hd.mpTrafficList):
                wrpcap('solo.pcap', PE.hd.soloList)
            else:
                wrpcap('mpTraffic.pcap', PE.hd.soloTraffic)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'frameTracer')
    parser.add_argument('--graph', action = 'store_true', help = 'Visualize the data via plotly')
    parser.add_argument('-c', metavar = 'frame count to capture', help = 'frame count to capture')
    parser.add_argument('-f', metavar = 'read from pcap', help = 'read from pcap') ## Not ideal for large pcaps, need PcapReader() instead
    parser.add_argument('-i', metavar = 'interface', help = 'interface', required = True)
    parser.add_argument('-x', metavar = 'mac X', help = 'mac X')
    parser.add_argument('-y', metavar = 'mac Y', help = 'mac Y')
    parser.add_argument('-v', help = 'verbose', action = 'store_true')
    args = parser.parse_args()
    main(args)
