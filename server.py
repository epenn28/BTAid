#!/usr/bin/python3

import requests
import xml.etree.ElementTree as ET

TORG = "1114"
BURRUSS = "1101"
SQUIRESWEST = "1113"
SQUIRESEAST = "1110"
NEWMAN = "1100"


def getNextBus(routeName, stopCode):
    userData = {'routeShortName': routeName, 'stopCode': stopCode}
    r = requests.post("http://216.252.195.248/webservices/bt4u_webservice.asmx/GetNextDepartures", data=userData)
    root = ET.fromstring(r.text)
    try:
        nextBus = root[0].find('AdjustedDepartureTime').text
        (nextDate, nextTime, ampm) = nextBus.split(" ")
        (hours, minutes, seconds) = nextTime.split(":")
        print("The next bus for {} stop {} will show up at {}:{} {}.".format(routeName, stopCode, hours, minutes, ampm))
        return (routeName, stopCode, nextTime)
    except IndexError:
        print("You did something wrong, dummy")
    
    
def main():
    (routeName, stopCode, nextTime) = getNextBus("HWDB", TORG)
    print("Function returned", routeName, stopCode, nextTime)
    
    
if __name__ == '__main__':
    main()