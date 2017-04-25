#!/usr/bin/python3

#start of the speaker output 
import cgi
import os
import cgitb
import sys

cgitb.enable()
sys.path.insert(0, "/usr/bin/espeak")

def say(something):
    os.system('sudo espeak "{0}"'.format(something))

print("I am speaking to you")

res1 = say("Hello again")

print("end")