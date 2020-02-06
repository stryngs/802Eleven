#!/usr/bin/python

import os
import subprocess
import sys
import threading
import time
import packetEssentials as PE
from shlex import split

"""
2 Classes, one for channel hopping and the other for control/display of the NIC

__main__ is setup as a rudimentary channel hopper for an example of how to use
this library.
"""

class Hopper(object):
    """Threading class for channel hopping"""

    def __init__(self, controlObj):
        self.controlObj = controlObj
        thread = threading.Thread(target = self.controlObj.chanHop,
                                  args = (self.controlObj.chanList, self.controlObj.interval))
        thread.daemon = True
        thread.start()


class Control(object):
    """Control the underlying OS"""
    def __init__(self, nic, chanList = False, interval = 10):
        self.nic = nic
        self.interval = interval
        self.curChan = None
        self.curFreq = None

        if chanList is not False:
            self.chanList = [i for i in chanList.split()]

        ## Deal with channel hopping
        if chanList is not False:
            Hopper(self)

        ## Deal with no channel hopping
        else:
            self.curChan = int(self.iwGet().split('(Channel')[1].strip().split(')')[0])
            self.curFreq = PE.chanFreq.twoFourRev(int(self.curChan))


    def chanHop(self, chanList, interval):
        """Hop to channel based on chanList"""
        while True:
            for chan in chanList:
                self.iwSet(chan)
                self.curChan = chan
                self.curFreq = PE.chanFreq.twoFourRev(int(self.curChan))
                time.sleep(int(interval))


    def iwSet(self, channel):
        """Set the wifi channel"""
        os.system('iwconfig {0} channel {1}'.format(self.nic, channel))


    def iwGet(self):
        """Show the current wifi channel in str() format"""
        p1 = subprocess.Popen(split('iwlist %s channel' % self.nic),
                              stdout = subprocess.PIPE)
        p2 = subprocess.Popen(split('tail -n 2'),
                              stdin = p1.stdout,
                              stdout = subprocess.PIPE)
        p3 = subprocess.Popen(split('head -n 1'),
                              stdin = p2.stdout,
                              stdout = subprocess.PIPE)
        return p3.communicate()[0].strip()


    def iwDriver(self):
        """Determine driver in use"""
        p1 = subprocess.Popen(split("grep 'DRIVER=' '/sys/class/net/%s/device/uevent'" % self.nic),
                              stdout = subprocess.PIPE)
        p2 = subprocess.Popen(split('cut -d= -f2'),
                              stdin = p1.stdout,
                              stdout = subprocess.PIPE)
        return p2.communicate()[0].strip()


if __name__ == '__main__':

    ### Toss up an argparse later on
    if len(sys.argv) == 2:
        ctl = Control(sys.argv[1])
    elif len(sys.argv) == 3:
        ctl = Control(sys.argv[1], chanList = sys.argv[2])
        print('Hopping on {0}'.format(ctl.chanList))
    elif len(sys.argv) == 4:
        ctl = Control(sys.argv[1], chanList = sys.argv[2], interval = sys.argv[3])
        print('Hopping on {0} @ {1} second intervals'.format(ctl.chanList, ctl.interval))
    else:
        print('os_control.py <Monitor Mode NIC> <Channels>\n')
        print('i.e.')
        print("  ./os_control.py wlan0mon '1 6 11'\n")

    ## Keep running
    while True:
        time.sleep(1)
