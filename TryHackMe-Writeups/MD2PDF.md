<h2>Target: 10.10.202.61 MD2PDF</h2>
<b>Initial Access:</b><br>
Step 1: nmap -Pn --min-rate=5000 10.10.202.61 -p-|grep open|awk -F '/' "{print $1}"|sed -z 's/\n/,/g' <br>
Nmap returns opon ports: 22,80,5000 <br><br>

Step 2: Run directory brute force on port 80 using dirsearch: dirsearch -r -u http://10.10.202.61/ -e txt,html -f -o dsearch-md2pdf

Dirsearch returns showing their is a directory of /admin.

Step 3: Visiting http://10.10.202.61/admin shows this /admin can only be accessed internally.  

Step 4: Navigating to port 80 shows the page has a place for a user to input text and the bottom right corner of the page has a ‘Convert to PDF’ function.  The top left corner of the site shows ‘MD2PDF’ which seems to indicate that this is a markdown to pdf converter.  

Step 5: Check if we can input markdown code which will run when converted to a pdf.  Write the following code in the user input: <script>document.write('hacked')</script>
 
Step 6: Clicking on ‘Convert to PDF’ creates a pdf page showing that it ran our code, and therefore only shows the word ‘hacked’ and not the words we entered.  The pdf created confirms that when converting from markdown to pdf our code runs.  This is called Server Side XSS.  

For further reading on Server Side XSS see: https://book.hacktricks.xyz/pentesting-web/xss-cross-site-scripting/server-side-xss-dynamic-pdf 

Step 7: Leverage the server side xss to get server side request forgery so that we can access the directory of /admin: <iframe src="http://localhost:5000/admin";style=position:fixed;width=1000px;height=500px</iframe>

Click on ‘Convert to PDF’ and we get the flag.  
