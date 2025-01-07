<h2>Target: Micro-CMS v1</h2>

<b>Flag 1:</b><br>
Upon starting the lab we are taken to this site:

![image](https://user-images.githubusercontent.com/93153300/205707449-6d88c19a-8651-4222-9bac-266a1a5458a2.png)
 
Clicking on ‘Testing’ shows a url of: https://69ae4549d3c741bc3d6f3e2ee9ffa7bf.ctf.hacker101.com/page/1

Clicking on ‘Markdown Test’ shows a url of: https://69ae4549d3c741bc3d6f3e2ee9ffa7bf.ctf.hacker101.com/page/2

Clicking on ‘Create a new page’ and creating a new page shows a url of: https://69ae4549d3c741bc3d6f3e2ee9ffa7bf.ctf.hacker101.com/page/13

Based on the page numbers given in each url (1,2, and 13), fuzz to see if any other numbers exist:

![image](https://user-images.githubusercontent.com/93153300/205707511-4d73f428-9a60-46b6-84b1-e0f986af362d.png)
 
Wfuzz found number 6.  Go to the directory of /page/6: 

![image](https://user-images.githubusercontent.com/93153300/205707556-5fdba78a-a45c-4f33-abde-69b815ad960b.png)
 
Not much we can get in this directory.  Go back to the main page and click on ‘Testing’.  This take us to a page that shows an option for editing the page:

![image](https://user-images.githubusercontent.com/93153300/205707592-c9ff9c77-b282-4720-8d90-33a7e3ccfbb4.png)
 
Click on ‘Edit this page’.  The url changes to a directory of /page/edit/1:

![image](https://user-images.githubusercontent.com/93153300/205707615-1f3d2733-b5bb-465e-83df-eacb5b434c96.png)

Change the 1 to a 6 and we get the first flag:
 
![image](https://user-images.githubusercontent.com/93153300/205707635-f2ba8d1c-cff6-42f3-941b-689e8024db36.png)
 
____________________________________________________________________________
<b>Flag 2:</b><br>
Looking back at the directory of /page/edit/1, test for xss using the payload <script>alert(1)</script>:
 
![image](https://user-images.githubusercontent.com/93153300/205707674-93e14f53-e759-4108-a968-14b84a6f378b.png)
  
Save it and go back to the home directory, and we get the second flag: 

![image](https://user-images.githubusercontent.com/93153300/205707701-9654000c-69a4-44b5-899e-15a402d0a66e.png)
 
____________________________________________________________________________
<b>Flag 3: </b><br>
Go back to the directory of /page/edit/1.  Instead of testing xss on the ‘Title’ section, test for xss in the ‘body’ section.  The bottom of the page says “Markdown is supported, but scripts are not” so use a different payload than our previous one: \<img src=0 onerror=alert(1)>
 
![image](https://user-images.githubusercontent.com/93153300/205707730-4f307b46-3699-4fbe-9311-ad73eed62599.png)
 
Save it and we immediately get an alert pop up message of the number 1.  Look at the source code and we find the third flag:
 
![image](https://user-images.githubusercontent.com/93153300/205707754-93c0b664-9a18-41d0-b8d1-6174fa819b5a.png)
___________________________________________________________________________
<b>Flag 4:</b><br>
On the directory of /page/edit/1 test for sql injection by replacing the number 1 with the payload of: ' or 1=1-- - <br>

![image](https://user-images.githubusercontent.com/93153300/205707779-905b1eb0-6b7c-47e5-b0ca-48c518c5b879.png)

