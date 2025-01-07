<h2>Target:  10.10.10.29    Bank</h2>

<b>Initial Access:</b><br>
nmap -Pn 10.10.10.29 --min-rate=5000 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Output shows open ports: 22,53,80

Enumerate these open ports further with nmap: <br>
nmap -Pn 10.10.10.29 --min-rate=5000 -p 22,53,80 -sC -sV -oN nmap.bank 

![image](https://user-images.githubusercontent.com/93153300/206328930-1516e182-1b4f-433a-a2e1-3430214dc28b.png)

Before querying port 53, add into the file /etc/hosts: 10.10.10.29  bank.htb <br>
Next run the command dig any bank.htb @10.10.10.29 <br>

![image](https://user-images.githubusercontent.com/93153300/206328940-c41e5500-ce5e-4fe3-aa36-a0d79e2dbccc.png)
 
The output from dig shows two subdomains: ns.bank.htb and chris.bank.htb.  We don’t end up needing these subdomains, so no need to add this into /etc/hosts. 

Visiting port 80 shows nothing of interest.  Run a directory brute force: dirsearch -r -u http://bank.htb -e php -f -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -o dsearch.txt

Dirsearch found a /login.php and a /balance-transfer/ directory.   The Directory /login.php is a login page.  We don’t have credentials and default credentials didn’t work.  Visiting /balance-transfer/ shows: 

![image](https://user-images.githubusercontent.com/93153300/206328965-06dc261f-4771-41cf-80fb-65126224369b.png)
 
The amount of files on this page is quite long.  The screenshot above shows some of the files.  Download all the files using the command: wget -r http://bank.htb/balance-transfer <br>
Opening a file shows: 
 
![image](https://user-images.githubusercontent.com/93153300/206328985-7154abdb-e801-4337-80f6-4aeb98da2397.png)
 
The files don’t seem to give any hints on how to decrypt these files.  All the files seem very similar to this one.  Check if we can find a hint in one of the files as to how to decrypt the information.  Going through every file manually would take an incredible amount of time, instead use the ‘grep’ command: grep -ri encrypt.  The output to this command is quite long.  The screenshot below shows part of the output: 
![image](https://user-images.githubusercontent.com/93153300/206329146-f430ab91-a559-40fc-8080-59a8ca83837e.png)

The output is too long, to minimize the output run: grep -ri encrypt | grep -vi success
 
![image](https://user-images.githubusercontent.com/93153300/206329172-8a97b0ff-3704-4a2e-9fd8-2a2906c08e86.png)

Open the file we found with grep.  The file shows credentials in plaintext.  Use these credentials to login on the directory of /login.php.

After logging in the page shows:

![image](https://user-images.githubusercontent.com/93153300/206329186-a90fef63-589d-43fb-9c79-d866d6b68206.png)

Click on ‘Support’.  The page shows:

![image](https://user-images.githubusercontent.com/93153300/206329208-e6f1193a-63ce-4fb8-b92a-0cde2d66bb63.png)
 
We see there is an upload file option.  The source code to this page (/support.php) shows an interesting comment:
 
![image](https://user-images.githubusercontent.com/93153300/206329222-9a5f8f7f-066c-4350-898b-ec56cdca747e.png)

Upload a pentestmonkey php reverse shell but first change the filename extension from .php to .htb.  Open a netcat listener (we will use pwncat since it gives a better shell): pwncat-cs -lp 443 <br>
After uploading the file the page shows our uploaded file:
 
![image](https://user-images.githubusercontent.com/93153300/206329243-986d1bb4-ffe1-45af-b9d5-fcfdb6f0d40a.png)
  
Click on the ‘Click Here’ under ‘Attachment’.  Our pwncat gets a shell as www-data.
_________________________________________________________________________
<b>Lateral Movement:</b><br>
Found credentials in directory /var/www/bank/inc/user.php: 
 
![image](https://user-images.githubusercontent.com/93153300/206329259-fbf52ea3-1749-4f94-92a8-eec569bf6b67.png)
 
Directory /var/htb/emergency shows a strange file: 
 
![image](https://user-images.githubusercontent.com/93153300/206329276-990b2fda-de63-4954-83e8-133aef7d98fd.png)
 
Run this file to get a shell as root:
 
![image](https://user-images.githubusercontent.com/93153300/206329296-66c97977-c18b-4164-a07a-d253ab07166a.png)

We can get the flags in /home/chris/user.txt and in /root/root.txt. 
