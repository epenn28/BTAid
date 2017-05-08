#!/usr/bin/env python3 

import pika
import uuid
import argparse
import sys
import os
import json
import time
import cgi
import cgitb
import subprocess
from threading import Timer
from ast import literal_eval as make_tuple
from twilio.rest import Client
from beacontools import BeaconScanner, IBeaconFilter

MY_BUSSTOP = "1101"
SET_VAL = 3
STATE_INIT = 4
STATE_FOUND = 3
STATE_WAIT = 2
STATE_CHECK = 1
STATE_REQUEST = 0
STATE_DONE = -1
THRESH_VAL = -75
WAIT_PERIOD = 10
REFRESH_PERIOD = 180

cgitb.enable()

# Command Line Parsing to start Monitor RPi
parser = argparse.ArgumentParser()
parser.add_argument("-b", metavar="message broker", required=True, dest="ip")
args = parser.parse_args()
ip = args.ip
print(" IP address: {}\n Virtual host: {}\n Credentials username: {}\n Credentials password: {}\n"
      .format(ip, "my_host12", "team12", "21maet"))

count = 0
total = 0
rider = {'uuid': '0', 'flag_p1': STATE_INIT}


def callback(bt_addr, rssi, packet, additional_info):
    global count
    global total
    global rider

    if count < SET_VAL:
        total = total + rssi
        count = count + 1
    else:
        avg = total / SET_VAL
        total = 0
        count = 0
        print("Average:", avg)
        if (avg > THRESH_VAL):
            if (rider['flag_p1'] == STATE_INIT):
                rider['flag_p1'] = STATE_FOUND
                rider['uuid'] = additional_info['uuid']
            elif (rider['flag_p1'] == STATE_CHECK):
                rider['flag_p1'] = STATE_REQUEST
        elif (avg <= THRESH_VAL):
            if (rider['flag_p1'] == STATE_CHECK):
                rider['flag_p1'] = STATE_INIT


scanner = BeaconScanner(callback)
scanner.start()

def say(something):
    os.system('sudo flite -voice rms -t "{0}" 2>/dev/null'.format(something))

def presence_check():
    global rider
    rider['flag_p1'] = STATE_CHECK
    print(" [x] State changed to CHECK")

def presence_refresh():
    global rider
    rider['flag_p1'] = STATE_INIT
    print(" [x] State refreshed to INIT")

class RpcClient(object):
    def __init__(self):

        credentials = pika.PlainCredentials("team12", "21maet")
        parameters =  pika.ConnectionParameters(ip, 5672, "my_host12", credentials)

        self.connection = pika.BlockingConnection(parameters)

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def close_connection(self):
        self.connection.close()

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return str(self.response)


def main():

    global rider

    ACCOUNT_SID = "AC391fcbead1e4edb0e10194f9be44096e"
    AUTH_TOKEN = "c7945b061ae8f67654d0b6e61d2b77eb"
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    while True:
        if (rider['flag_p1'] == STATE_FOUND):
            rider['flag_p1'] = STATE_WAIT
            print(" [x] State refreshed to WAIT")
            t1 = Timer(WAIT_PERIOD, presence_check)
            t1.start()
        elif (rider['flag_p1'] == STATE_REQUEST):
            rider['flag_p1'] = STATE_DONE
            passenger_uuid = rider['uuid'].upper()
            print(" [x] Requesting route information on UUID {}".format(passenger_uuid))
            
            request_payload = (MY_BUSSTOP, passenger_uuid)
            response = client_rpc.call(request_payload)
            response = str(response)[1:]
            response = response.strip('"')
            print(response)
            (bus_info, user_phone) = make_tuple(response)
            print(" [.] Got %r" % response)

            if (user_phone == "-1"):
                print (" [!] ", bus_info)
            else:
                say(bus_info)
                client.messages.create(
                        to = user_phone,
                        from_ = "+12402058160",
                        body = bus_info,
                    )
                print(" [.] Information was sent")
            t2 = Timer(REFRESH_PERIOD, presence_refresh)
            t2.start()


if __name__ == '__main__':
    try:
        client_rpc = RpcClient()

        main()
    # Capture Ctrl+C and cleanly exit
    except KeyboardInterrupt:
        # Close exchange connection
        client_rpc.close_connection
        scanner.stop()
        print('Program was interrupted. Host RPi closed (close connection)')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
