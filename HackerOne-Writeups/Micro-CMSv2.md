<h2>Target: Micro-CMS v2</h2>

<b>Flag 1:</b><br> 
Visiting the site and clicking on ‘Micro-CMS Changelog’ shows:

![image](https://user-images.githubusercontent.com/93153300/205704141-9b93d770-a87d-4c49-90b9-8bde4f239b21.png)
 
If we click on ‘Edit this page’ we get redirected to a login page.  As it says on the page, we cannot edit pages without logging in.  However, we can bypass this authentication by simply using curl:<br>
curl https://2ef52960f05e97401f3ac5ef8787b49f.ctf.hacker101.com/page/edit/1 -X POST

We can also do this bypass with burp suite.  Capture the ‘Edit this page’ request in burp suite.  Send it to ‘repeater’.  Change the request method to ‘POST’, and send the request:

![image](https://user-images.githubusercontent.com/93153300/205704168-254d427d-8f96-443b-9abb-6b090538f998.png)
__________________________________________________________________________
<b>Flag 2:</b><br>
Go to the login page and enter in the username a simple sqli payload: ‘ or 1=1-- <br>
Submit the payload.  The page returns an error page:
 
![image](https://user-images.githubusercontent.com/93153300/205704189-74325a48-1928-4b95-a600-ef4eb0aa9706.png)
 
The page is vulnerable to sql injection.  Back to the login page, enter a regular string for the username and capture the request in burp suite. Save the captured burp suite request to a file.  Next, run sqlmap:  sqlmap -r burp --batch --force-ssl --dbs -D level2 --tables -T admins --columns -C id,username,password –dump

Sqlmap gets the username ‘rossana’ and the password ‘ignacia’.  Login to get the second flag.
_______________________________________________________________________
<b>Flag 3:</b><br>
We can find the third flag in a different column in the database: sqlmap -r burp --batch --force-ssl --dbs -D level2 --tables -T pages --columns -C body –dump
