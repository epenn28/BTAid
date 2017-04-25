#!/usr/bin/python3

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, date

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
        # nextBus format: 4/25/2017 5:15 PM
        timeStruct = datetime.strptime(nextBus, "%m/%d/%Y %I:%M:%S %p").time()
        currentTime = datetime.now().time()
        difference = datetime.combine(date.min, timeStruct) - datetime.combine(date.min, currentTime)
        output = "The next bus will arrive in " + str(round(difference.seconds / 60)) + " minutes."
        print(output)
    except IndexError:
        print("You did something wrong, dummy!")
    # get stop code, uuid
    # return output string, phone number
    
def main():
    getNextBus("HWDB", TORG)
    #print("Function returned", routeName, stopCode, hours, minutes, ampm)
    
    
if __name__ == '__main__':
    main()