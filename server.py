#!/usr/bin/env python3

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, date
import pymongo
from pymongo import MongoClient
import os
import pika
import sys
import argparse

TORG = "1114"
BURRUSS = "1101"
SQUIRESWEST = "1113"
SQUIRESEAST = "1110"
NEWMAN = "1100"

output = ""


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
        return(output)
    except IndexError:
        print("You did something wrong, dummy!")
    # get stop code, uuid
    # return output string, phone number
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", metavar="message broker", required=True, dest="ip")
    args = parser.parse_args()
    ip = args.ip
    print("IP address: {}\nVirtual host: {}\nCredentials username: {}\nCredentials password: {}\n"
          .format(ip, "my_host12", "team12", "21maet"))
    
    credentials = pika.PlainCredentials("team12", "21maet")
    parameters =  pika.ConnectionParameters(ip, 5672, "my_host12", credentials)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='rpc_queue')
    
    client = MongoClient()

    db = client.my_database
    db.my_collection.drop()
    db.my_collection.create_index([("beaconid", 1)], unique=True)
    collection = db.my_collection

    messages = [{"beaconid": "B9407F30-F5F8-466E-AFF9-25556B57FE6D", 
    	"pid": "caml323", "route": "UCB", 
    	"phone": "+12404860906", "name": "Cory Latham"}, 
    	{"beaconid": "D0B32A8C-B407-AD88-D6DB-5E88C25E3438", 
    	"pid": "epenn28", "route": "HWDB", 
    	"phone": "+12404995406", "name": "Elliot Penn"},
    	{"beaconid": "EA8FCA33-C569-5E09-3260-E0D038256D3B", 
    	"pid": "kosovo", "route": "HWDA", 
    	"phone": "+15409981120", "name": "Daulet Talapkaliyev"},
    	{"beaconid": "394CD435-D71C-DCD9-1C8D-1218CE4DFE62", 
    	"pid": "anajahd4", "route": "UMS", 
    	"phone": "+17577086232", "name": "Anajah Delestre"}]

    collection.insert_many(messages)
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_request, queue='rpc_queue')
    print(" [x] Awaiting RPC requests")
    channel.start_consuming()
    
def on_request(ch, method, props, body):
    global output
    request_msg = body

    print(" [.] BLE beacon UUID received:%s" % request_msg)

    (beaconUUID, busStop) = request_msg
    temp = collection.find_one({"beaconid": beaconUUID})
    
    phoneNumber = temp['phone']
    busRoute = temp['route']
    
    output = getNextBus(busRoute, busStop)
    response = (output, phoneNumber)

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag = method.delivery_tag)
    
    
if __name__ == '__main__':
    try:
        main()
    # Capture Ctrl+C and cleanly exit
    except KeyboardInterrupt:
        print('Program was interrupted. Monitor RPi closed')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)