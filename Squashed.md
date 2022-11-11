<h2> Target: 10.10.11.191 Squashed </h2>
<html> 
<body> 
<b>Initial Access:</b><br>
nmap -Pn -p- 10.10.11.191 --min-rate=5000|grep open|awk -F '/' '{print $1}'|tr '\n' ',' 	<br>
Output shows open ports: 22,80,111,2049,36873,45053,45653,46087 <br><br>
Enumerating these open ports further with nmap: <br>
nmap -Pn 10.10.11.191 --min-rate=5000 -p 22,80,111,2049,36873,45053,45653,46087 -sC -sV -oN nmap.squashed
  
<br> ![image](https://user-images.githubusercontent.com/93153300/201415120-8ecfb9f5-c174-487f-b0c4-751f762293c3.png)
 
Check if anything is mounted and accessible on port 2049/nfs using command: showmount -e 10.10.11.191:
 
![image](https://user-images.githubusercontent.com/93153300/201415208-a4c7cf1f-6a56-4604-98a6-e044f82cb366.png)
 
We find 2 file-shares that we can look into.  The ‘*’ at the end of the file-shares indicates that it is globally accessible, meaning we can access those file-shares.  Start by checking on /var/www/html.  Create a mounting directory, we will call it mmnt, using command: mkdir mmnt <br>
Mount the ‘/var/www/html’ share using command: mount -o soft -o bg -t nfs 10.10.11.191:/var/www/html/ mmnt
 
Go into mmnt to check the target file-share ‘/var/www/html’ we just mounted using command: cd mmnt.  <br>
We get a 'permission denied' response: 
 
![image](https://user-images.githubusercontent.com/93153300/201415223-8edce889-39c4-4945-b730-f06b52e3f25a.png)
 
Check file permissions using command: ls-al mmnt 
 
![image](https://user-images.githubusercontent.com/93153300/201415249-97a66f19-039e-416d-83c5-7270bf7f8d2f.png)

Not much clues here to help us.  Instead of looking at permissions inside of directory mmnt, look at permissions of the directory mmnt using command: ls -al 

![image](https://user-images.githubusercontent.com/93153300/201415267-811e1fdc-72f0-4f3a-9b11-f0384eee0d81.png)

This shows the mounted directory is owned by www-data.  In order to be able to read the files in the mounted directory mmnt, create a user called ‘www-data’.  These are the steps to create a new user: <br>
Step 1: open /etc/passwd with a text editor. <br>
Step 2: copy a user you currently have on the system in /etc/passwd, we will call him ‘testuser’, and change the name to www-data. 

![image](https://user-images.githubusercontent.com/93153300/201415283-bd8be1f9-7ac5-492a-afc6-32a426fd9853.png)
 
Step 3: change the ‘x’ found after the name of the user into a ‘*’.
 
![image](https://user-images.githubusercontent.com/93153300/201415311-d3faf871-76e6-473d-ad4f-1a41a278621b.png)
 
To change to user www-data use command: su www-data.  <br>
Now we have access to the mounted share.  

![image](https://user-images.githubusercontent.com/93153300/201415344-017d1402-3676-44a9-8b3c-4f735066df96.png)

Use this to get a reverse shell.  First, put a pentestmonkey php reverse shell in this ‘/var/www/html’ mounted file share, we will call it ‘shell.php’.  Next, open a netcat listener using command: nc -lvnp 443 (I will use pwncat-cs -lp 443 because pwncat gives a better shell than netcat).  Finally, visit port 80 at http://10.10.11.191/shell.php to run the ‘shell.php’ file. <br>
It worked, we have shell as alex.  We can go to /home/alex/user.txt to get the flag.
 
![image](https://user-images.githubusercontent.com/93153300/201415416-4b04cbf0-1ce3-4bd6-932e-a4e7be57547f.png)
_______________________________________________________________________________
<b>Privilege Escalation:</b><br>
Directory /home/ross shows a ‘.Xauthority’ file.  ‘.Xauthority’ file is used to store credentials in the form of cookies.  If we can get the ‘.Xauthority’ file then we should be able to use that to dump an image of an X window.  The image of an X window will show us a screenshot of the display in its current state.  The display may reveal interesting information.  

Steps to read the ‘.Xauthority’ file: <br>
Step 1: we don’t have permissions to read the file ‘.Xauthority’, however we saw earlier that /home/ross is a mounted file-share that we can access.  We can get access to that file-share the same way we did for user www-data.  Repeat the steps we did before to create a user www-data, but this time call the user ‘ross’.  
Step 2: unmount the ‘/var/www/html’ share using command: umount mmnt.  <br>
Step 3: mount file-share /home/ross using command: mount -o soft -o bg -t nfs 10.10.11.191:/home/ross mmnt.  
Step 4: on our local system, switch to user ross using command: su ross.   We now have permissions to read ‘.Xauthority’ in /home/ross.   

To make use of the ‘.Xauthority’ we need the ‘.Xauthority’ file to be on the target shell, not on our local system.  Here are the steps to get the ‘.Xauthority’ on the target shell:

(Usually, the standard copy/upload commands would suffice to do this.  However, we run into some issues if we do that because this is a mounted share and not a local file on our system. So we will output the file content and then copy and paste the file content.  The challenge is that ‘.Xauthority’ is in raw format.  Raw format doesn’t copy well so we cannot do a simple copy paste.)

Step 1:  on the mounted file-share, base64 encode the content of ‘.Xauthority’ by using the command: cat .Xauthority | base64 -w 0 <br>
Step 2: copy the base64 string to the target, and decode the base64 string back to its original raw format.  To do this, go back to the target alex user shell and run the command: echo -n '<put here the base64 encoded string>' | base64 -d > /tmp/.Xauthority 
 
![image](https://user-images.githubusercontent.com/93153300/201415434-3ce491fe-d5ef-4209-be4d-0872e9eee185.png)

We now have the ‘.Xauthority’ file on the target shell.  To get the screenshot of the display in its current state we will use a command called ‘xwd’.  We need to do two things before we can run ‘xwd’ successfully.  
Step 1: Set the environment variable of XAUTHORITY to the file we made in /tmp/.Xauthority.  Use command: export XAUTHORITY=/tmp/.Xauthority <br>
Step 2: To run ‘xwd’ we need to know the ‘display’.  Run command ‘w’  to see the display:
 
![image](https://user-images.githubusercontent.com/93153300/201415457-53513776-95f7-4d9a-a33a-23f3bdf5089b.png)
  
The output from the ‘w’ command shows in the ‘FROM’ column that the display used is ‘:0’ .

We are ready to run ‘xwd’. Use command: xwd -root -screen -silent -dsiplay :0 > /tmp/screen.xwd 
Download /tmp/screen.xwd to our local system.  To do this we will open a python server on the target shell using command: python3 -m http.server 8000.  <br>
On our local system, use command: wget http://10.10.11.191/screen.xwd

The ‘screen.xwd’ file is now on our local system.  To see the display on ‘screen.xwd’ convert it to a ‘.png’ file using command: convert screen.xwd screen.png <br>
Opening the ‘screen.png’  file shows:

![image](https://user-images.githubusercontent.com/93153300/201415474-6e93858c-05d9-4696-bef6-582d5e16560f.png)

This shows root’s password. Use command ‘tesseract’ to convert the password image into clear text  instead of copying it down letter by letter: tesseract screen.png screen.txt <br>
The password is ‘cah$mei7rai9A’.  Back on the target shell as user alex run command: su → when prompted for password enter the password.  <br>
We have shell as root.  We can get the flag at /root/root.txt
</body>
</html>
