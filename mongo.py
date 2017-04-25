#!/usr/bin/env python3

import pymongo

from pymongo import MongoClient
client = MongoClient()

db = client.my_database
db.my_collection.drop()
db.my_collection.create_index([("beaconid", 1)], unique=True)
collection = db.my_collection

messages = [{"beaconid": "B9407F30-F5F8-466E-AFF9-25556B57FE6D", 
	"pid": "caml323", "route": "UCB", 
	"phone": 2404860906, "name": "Cory Latham"}, 
	{"beaconid": "D0B32A8C-B407-AD88-D6DB-5E88C25E3438", 
	"pid": "epenn28", "route": "HWDB", 
	"phone": 2404995406, "name": "Elliot Penn"},
	{"beaconid": "EA8FCA33-C569-5E09-3260-E0D038256D3B", 
	"pid": "kosovo", "route": "HWDA", 
	"phone": 5409981120, "name": "Daulet Talapkaliyev"},
	{"beaconid": "394CD435-D71C-DCD9-1C8D-1218CE4DFE62", 
	"pid": "anajahd4", "route": "UMS", 
	"phone": 7577086232, "name": "Anajah Delestre"}]

collection.insert_many(messages)

beaconString = "394CD435-D71C-DCD9-1C8D-1218CE4DFE62"
temp = collection.find_one({"beaconid": beaconString})

print("Database Ready")
print(temp['name'])

#print(db.profiles.index_information())
