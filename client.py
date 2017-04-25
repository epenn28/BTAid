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
from twilio.rest import Client

MY_BUSSTOP = "1101"

# Test passanger UUIDs
uuid_list = ["B9407F30-F5F8-466E-AFF9-25556B57FE6D","D0B32A8C-B407-AD88-D6DB-5E88C25E3438"]

cgitb.enable()

# Command Line Parsing to start Monitor RPi
parser = argparse.ArgumentParser()
parser.add_argument("-b", metavar="message broker", required=True, dest="ip")
args = parser.parse_args()
ip = args.ip
print(" IP address: {}\n Virtual host: {}\n Credentials username: {}\n Credentials password: {}\n"
      .format(ip, "my_host12", "team12", "21maet"))

def say(something):
    os.system('sudo flite -voice rms -t "{0}" 2>/dev/null'.format(something))

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

    ACCOUNT_SID = "AC391fcbead1e4edb0e10194f9be44096e"
    AUTH_TOKEN = "c7945b061ae8f67654d0b6e61d2b77eb"
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    for passenger_uuid in uuid_list:
        print(" [x] Requesting route information on UUID {}".format(passenger_uuid))
        request_payload = (MY_BUSSTOP, passenger_uuid)
        response = client_rpc.call(request_payload)
        response = str(response)[1:]
        print(" [.] Got %r" % response)
        say(response)
        """
        client.messages.create(
                to = "+12404995406",
                from_ = "+12402058160",
                body = response,
            )
        """

        print(" [.] Information was sent")



if __name__ == '__main__':
    try:
        client_rpc = RpcClient()
        main()
    # Capture Ctrl+C and cleanly exit
    except KeyboardInterrupt:
        # Close exchange connection
        client_rpc.close_connection
        print('Program was interrupted. Host RPi closed (close connection)')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
