#!/usr/bin/python3

from scapy.all import *

"""
This snip is an example of using the tls layer in scapy to extract the name of
websites when visited using https.  This example is useful for wired, monitor or
managed mode as we are avoiding the higher layers and only concentrating only on
whether or not the TLS_Ext_ServerName object exists.

Uses whatever is populated in conf.iface when scapy.all is imported.  There is
no interface is specificed in sniff().  If you have multiple NICs modify sniff()
accordingly and add in the desired iface.
"""

def lFilter(ourFilter):
    """
    Only allow packets with a TLS_Ext_ServerName layer to proceed
    """
    def snarf(packet):
        if packet.haslayer(ourFilter):

            ## Ignore server hellos
            if packet[TLS].msg[0].name != 'TLS Handshake - Server Hello':
                return True
    return snarf


def pFilter():
    """
    Prints the <ip> <tls message name> <website> in a given packet.
    """
    def snarf(packet):
        sList = [i.servername.decode() for i in packet[TLS_Ext_ServerName].servernames]
        print(f"{packet[IP].src:10} ~~> {packet[TLS].msg[0].name:28} ~~> {','.join(sList):20}")
    return snarf

## Load the layer before sniffing begins otherwise none of this matters
load_layer('tls')
if __name__ == '__main__':
    LFILTER = lFilter(TLS_Ext_ServerName)
    PRN = pFilter()
    p = sniff(prn = PRN, lfilter = LFILTER)
