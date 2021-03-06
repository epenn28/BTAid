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
from ast import literal_eval as make_tuple

TORG = "1114"
BURRUSS = "1101"
SQUIRESWEST = "1113"
SQUIRESEAST = "1110"
NEWMAN = "1100"

output = ""

# Set up Mongo database
client = MongoClient()

db = client.my_database
db.my_collection.drop()
db.my_collection.create_index([("beaconid", 1)], unique=True)
collection = db.my_collection

# Function to return the next bus for a specific stop on a given route using BT4U web services 
def getNextBus(routeName, stopCode):
    userData = {'routeShortName': routeName, 'stopCode': stopCode}
    r = requests.post("http://216.252.195.248/webservices/bt4u_webservice.asmx/GetNextDepartures", data=userData)
    root = ET.fromstring(r.text)
    try:
        nextBus = root[0].find('AdjustedDepartureTime').text
        longRouteName = root[0].find('PatternName').text
        # nextBus example format: 4/25/2017 5:15 PM
        timeStruct = datetime.strptime(nextBus, "%m/%d/%Y %I:%M:%S %p").time()
        currentTime = datetime.now().time()
        difference = datetime.combine(date.min, timeStruct) - datetime.combine(date.min, currentTime)
        numMins = round(difference.seconds / 60)
        if numMins == 1:
            output = "The next " + longRouteName + " bus will arrive in " + str(numMins) + " minute."
        else:
            output = "The next " + longRouteName + " bus will arrive in " + str(numMins) + " minutes."
        return(output)
    # Exception handler for the web service returning invalid data (bus is not running)
    except IndexError:
        print("BT4U API: there is no bus running on that route at this time.")
    
def main():
    global collection
    
    # Set up pika connection with broker
    credentials = pika.PlainCredentials("team12", "21maet")
    parameters =  pika.ConnectionParameters("localhost", 5672, "my_host12", credentials)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='rpc_queue')

    # Database values
    messages = [{"beaconid": "D0B32A8C-B407-AD88-D6DB-5E88C25E3438", 
    	"pid": "caml323", "route": "UCB", 
    	"phone": "+12404860906", "name": "Cory Latham"}, 
    	{"beaconid": "B9407F30-F5F8-466E-AFF9-25556B57FE6D", 
    	"pid": "epenn28", "route": "HWDA", 
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
    # Get information from client Pi, check beacon UUID against database
    (busStop, beaconUUID) = make_tuple(request_msg.decode())
    temp = collection.find_one({"beaconid": beaconUUID})
    print(" [.] BLE beacon UUID received:%s" % beaconUUID)
    # Create response tuple to send to client and handle unrecognized beacons
    if temp == None:
        output = "Incorrect beacon UUID"
        phoneNumber = "-1"
    else:
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
