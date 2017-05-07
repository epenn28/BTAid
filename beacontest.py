#!/usr/bin/env python3

#uuid="B9407F30-F5F8-466E-AFF9-25556B57FE6D"
import time
from beacontools import BeaconScanner, IBeaconFilter

count = 0
total = 0

def callback(bt_addr, rssi, packet, additional_info):
    global count
    global total
    
    if count < 15:
        total = total + rssi
        count = count + 1
    else:
        count = 0
        avg = total / 15
        total = 0
        print("Average:", avg)
    print("MAC address:", bt_addr)
    print("RSSI:", rssi)
    #print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))

# scan for all iBeacon advertisements from beacons with the specified uuid
scanner = BeaconScanner(callback)
scanner.start()
#time.sleep(5)
#scanner.stop()