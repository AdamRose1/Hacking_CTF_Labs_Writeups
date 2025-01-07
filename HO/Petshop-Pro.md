<h2>Target: Petshop Pro</h2>

<b>Flag 1:</b><br>
Visiting the site shows:
 
![image](https://user-images.githubusercontent.com/93153300/205710765-d6c23683-d473-4e49-b182-00605b4394bd.png)
 
Click on ‘Add to Cart’.  That adds an item to the cart and takes us to a directory called /cart.  Click on ‘Check Out’ and capture this request in burp suite:
 
![image](https://user-images.githubusercontent.com/93153300/205710796-d3be3cdf-1716-411c-8660-46c2f58473d8.png)

Url decode (Ctrl+shift+U) the item at the bottom after ‘cart=’ shows:

![image](https://user-images.githubusercontent.com/93153300/205710813-6ee0138a-5e63-48c3-8089-bd59f436e17b.png)
 
Change the price to 0.00 and forward the request:

![image](https://user-images.githubusercontent.com/93153300/205710841-04f319cb-7f02-4695-9e94-0b516fea10bc.png)
  
This gives us the first flag: 

![image](https://user-images.githubusercontent.com/93153300/205710862-1bd0f902-bfcf-4de4-88e5-f18b6e69f8f1.png)
__________________________________________________________________________
<b>Flag 2:</b><br>
Run directory brute force: dirsearch -r -u https://40fb3ad6e4ca76b169e455af0c4c8cd4.ctf.hacker101.com/ -o dsearch -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt 

Dirsearch found a directory called /login. Visiting the page shows a login page but we don’t have credentials.  Trying to login with some default credentials doesn’t work but it does show that it validates if the username is correct by saying ‘Invalid Username’: 

![image](https://user-images.githubusercontent.com/93153300/205710886-1a6f3e84-893d-4464-bd55-80d94b0f1c83.png)
 
Use hydra to find the correct username: hydra -L /usr/share/wordlists/rockyou.txt -p idk 40fb3ad6e4ca76b169e455af0c4c8cd4.ctf.hacker101.com http-post-form -s 443 -S "/login:username=^USER^&password=^PASS^:F=Invalid username"

Hydra found the username benni.  Now that we have the username, go back to the /login page.  If we enter the correct username and incorrect password the page returns saying ‘Invalid password’.  

Use hydra to find the correct password: hydra -l benni -P /usr/share/wordlists/rockyou.txt  40fb3ad6e4ca76b169e455af0c4c8cd4.ctf.hacker101.com http-post-form -s 443 -S "/login:username=^USER^&password=^PASS^:F=Invalid password"

Hydra found the password.  Login with the credentials to get the second flag.  
_____________________________________________________________
<b>Flag 3:</b><br>
After logging in, the page shows:
 
![image](https://user-images.githubusercontent.com/93153300/205944134-dcc4ea4e-7958-475d-b6b0-b60db234ca5e.png)
 
Click on ‘Edit’, and then enter an xss payload in the ‘Name’ field: \<img src=0 onerror=alert(1)>
 
![image](https://user-images.githubusercontent.com/93153300/205944186-45464a5c-f30f-4eb0-8941-f64509e83352.png)
 
Click on ‘Save’.  Go back to the main page we had after logging in.  Click on ‘Add to cart’  on the item we just added the xss payload to.  That will take us to the directory of /cart where the xss payload will run and we will get the third flag:
 
![image](https://user-images.githubusercontent.com/93153300/205944235-08d0001d-026c-4ff9-9ca2-0256ba402b8f.png)
  
