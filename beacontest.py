#!/usr/bin/env python3

#uuid="B9407F30-F5F8-466E-AFF9-25556B57FE6D"
#,device_filter=IBeaconFilter(uuid="8492e75f-4fd6-469d-b132-043fe94921d8")
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
    #print("MAC address:", bt_addr)
    #print("RSSI:", rssi)
    print("UUID:", additional_info['uuid'])
    #print("<%s, %d> %s %s" % (bt_addr, rssi, packet, additional_info))
    """This returns the following:
    <fb:91:ba:46:32:06, -54> IBeaconAdvertisement<tx_power: -58, uuid: b9407f30-f5f8-466e-aff9-25556b57fe6d, major: 43043, minor: 7457> 
    /{'major': 43043, 'uuid': 'b9407f30-f5f8-466e-aff9-25556b57fe6d', 'minor': 7457}
    """

# scan for all iBeacon advertisements from beacons with the specified uuid
scanner = BeaconScanner(callback)
scanner.start()
#time.sleep(5)
#scanner.stop()
