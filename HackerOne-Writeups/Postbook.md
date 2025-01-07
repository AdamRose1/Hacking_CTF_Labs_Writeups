<h2>Target: Postbook</h2>

<b>Flag 1:</b><br>
Visiting the site shows:
 
![image](https://user-images.githubusercontent.com/93153300/206239416-5dfac6d0-79dc-4b13-9ea7-2422ad849709.png)

Click on ‘Sign up’ and create a new user.  After logging in the page shows:
 
![image](https://user-images.githubusercontent.com/93153300/206239499-c3f656ba-e9ff-4e7a-a9e8-dfb374a1590f.png)

Click on ‘Create post’ and capture the request in burp suite.  Change the user id from 3 to 1 and forward the request:
 
![image](https://user-images.githubusercontent.com/93153300/206239535-4493bd34-db3f-4e70-994d-46a9bb6175d4.png)

This causes the posted request to be under the Author name admin instead of our username, and gets us the 1st flag:

![image](https://user-images.githubusercontent.com/93153300/206239579-610bb474-f6c0-49b1-80b9-3207de7d097b.png)

__________________________________________________________________________
<b>Flag 2:</b><br>
After logging in, on the home page click on the ‘Hello everyone!’ post:
 
![image](https://user-images.githubusercontent.com/93153300/206239614-b48643c8-b728-4493-80f5-1aaba20c3910.png)

The url shows: https://20100fe400049ef7d5f3c9950b5d87e4.ctf.hacker101.com/index.php?page=view.php&id=3 <br>
Change the id from ‘3’ to ‘2’ to find a hidden post and get the 2nd flag.
 
![image](https://user-images.githubusercontent.com/93153300/206239655-7862d286-1e72-4b77-a3db-ac95c1173d43.png)

___________________________________________________________________________
<b>Flag 3:</b><br>
After logging in, on the home page click on the ‘Hello everyone!’ post.  The url shows: https://20100fe400049ef7d5f3c9950b5d87e4.ctf.hacker101.com/index.php?page=view.php&id=3. Use wfuzz to check if there are any other hidden posts: <br>
wfuzz -c -w /usr/share/seclists/Fuzzing/3-digits-000-999.txt -u "https://20100fe400049ef7d5f3c9950b5d87e4.ctf.hacker101.com/index.php?page=view.php&id=FUZZ" --hh 1311 -b "id=eccbc87e4b5ce2fe28308fd9f2a7baf3"

Wfuzz found a hidden post at ‘id=945’. Go to https://20100fe400049ef7d5f3c9950b5d87e4.ctf.hacker101.com/index.php?page=view.php&id=945 to get the 3rd flag. 
__________________________________________________________________________
<b>Flag 4</b><br>
After logging in, on the home page we find a username named ‘user’:
 
![image](https://user-images.githubusercontent.com/93153300/206239688-49ead7af-de8c-46e3-8991-d8953a71e74c.png)
 
Use hydra to brute force his password: <br>
hydra -l user -P /usr/share/wordlists/rockyou.txt e01fdf1b4477cd512179b5745dc5b2e6.ctf.hacker101.com http-post-form -s 443 -S "/index.php?page=sign_in.php:username=^USER^&password=^PASS^:F=You've entered a wrong username"

Hydra finds the password in a few seconds.  Use the credentials to login to get the 4th flag.
____________________________________________________________
<b>Flag 5:</b><br>
After logging in, on the home page we see 2 posts by other users:

![image](https://user-images.githubusercontent.com/93153300/206239715-c454bddf-6fad-4d5a-a052-c56fc121c2a4.png)
 
There is no option for editing the post of another user.  Create a post with our user.  After creating the post we see an option of ‘edit’ on our post:
 
![image](https://user-images.githubusercontent.com/93153300/206239748-9b13407a-c30b-4c41-918a-95c15d0afd23.png)
 
Click on ‘edit’ and capture the request in burp suite. Change the parameter of ‘id=4’ to ‘id=1’: 
 
![image](https://user-images.githubusercontent.com/93153300/206239789-378b5add-ee77-4fab-b64b-e98bd9961843.png)
 
Forward the request.  This takes us to edit the admin post instead of our own post.  Change the post, save it, and then we get the 5th flag. 
___________________________________________________________________________
<b>Flag 6:</b><br>
After logging in, look at the cookie we have: eccbc87e4b5ce2fe28308fd9f2a7baf3 <br>
It looks like an md5 hash.  Save the cookie to a file (we will call the file ‘hash’).   To confirm the hash type run the command: nth -f hash    (‘hash’ being the filename containing our hash).  The command confirms that it is a md5 hash:
 
![image](https://user-images.githubusercontent.com/93153300/206239830-e2b46c4a-a1fc-4531-9eb2-93c62741adbb.png)
 
Crack the hash with john: john hash --wordlist=/usr/share/wordlists/rockyou.txt --format=raw-md5
 
![image](https://user-images.githubusercontent.com/93153300/206239868-db40108f-2121-4f42-93c8-6b1e35065f3f.png)
 
The hash is a md5 hash of the number 3.  Create a hash for the admin which is likely a md5 hash of the number one.  To create the hash run the command: echo -n '1'|md5sum <br>
The md5 hash for the number one is c4ca4238a0b923820dcc509a6f75849b

Open the developer tools (F12), go to ‘storage’, and replace the cookie value with the hash we created.  Refresh the pash and we get the 6th flag.  
_______________________________________________________________________________
<b>Flag 7:</b><br>
After logging in, on the home page it shows our posts with an option to delete the post:
 
![image](https://user-images.githubusercontent.com/93153300/206239897-dd91eabc-36fb-4762-a4ca-a92bb9ac5844.png)
 
Click on ‘delete’ and capture the request in burp suite: 
 
![image](https://user-images.githubusercontent.com/93153300/206239945-95938103-c61f-406d-8e9a-45ffb68fe305.png)
 
The page being deleted is reference as a hash.  It seems like an md5 hash.  Save the md5 hash in a file (we will call the file ‘hash’).  To confirm the hash type run the command: nth -f hash.  The command output confirms that it is a md5 hash.  Crack the hash with john: john hash --wordlist=/usr/share/wordlists/rockyou.txt –-format=raw-md5
 
![image](https://user-images.githubusercontent.com/93153300/206239972-7dea1ba9-5807-401a-afaf-b9f1b0e805c2.png)
   
The hash is a md5 hash of the number 7.   Create a md5 hash of a different number that refers to a post by a different user (we will try number 2).  To create the hash use the command: echo -n '2'|md5sum

The md5 hash for the number 2 is c81e728d9d4c2f636f067f89cc14862c.  Back in the burp suite capture we have, change the id=hash to the hash we just created.  Forward the request, and we get the 7th flag.
