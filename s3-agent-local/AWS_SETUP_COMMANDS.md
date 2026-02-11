# AWS Setup Commands - Run These Manually

**Run these commands yourself to set up AWS resources.**

---

## 1. Create S3 Bucket

```bash
aws s3 mb s3://agentic-search-test-bucket --region us-west-2
```

**Verify:**
```bash
aws s3 ls
```

---

## 2. Upload Your Test PDF

```bash
# From the project root directory
aws s3 cp "00010, Nice detailing, 7.5k, 4_1_19, advance.pdf" \
  s3://agentic-search-test-bucket/test-documents/

# Upload with proper naming (spaces in filenames can cause issues)
# OR rename first:
mv "00010, Nice detailing, 7.5k, 4_1_19, advance.pdf" test-document.pdf
aws s3 cp test-document.pdf s3://agentic-search-test-bucket/test-documents/
```

**Verify upload:**
```bash
aws s3 ls s3://agentic-search-test-bucket/test-documents/
```

---

## 3. Create IAM Policy

**Save this to `s3-policy.json`:**

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject",
      "s3:HeadObject",
      "s3:SelectObjectContent",
      "s3:GetObjectVersion",
      "s3:DeleteObject"
    ],
    "Resource": [
      "arn:aws:s3:::agentic-search-test-bucket",
      "arn:aws:s3:::agentic-search-test-bucket/*"
    ]
  }]
}
```

**Attach to your AWS user:**

```bash
# Get your username
aws sts get-caller-identity

# Attach policy (replace YOUR_USERNAME)
aws iam put-user-policy \
  --user-name YOUR_USERNAME \
  --policy-name LocalS3AgentPolicy \
  --policy-document file://s3-policy.json
```

---

## 4. Verify Permissions

```bash
# Test you can list the bucket
aws s3 ls s3://agentic-search-test-bucket/

# Test you can get object
aws s3 cp s3://agentic-search-test-bucket/test-documents/test-document.pdf ./test-download.pdf
```

---

## 5. Configure AWS Credentials (if needed)

```bash
# Use your existing login script
source ./aws_login.sh

# OR configure manually
aws configure
```

---

## Checklist

- [ ] S3 bucket created: `agentic-search-test-bucket`
- [ ] PDF uploaded to `s3://agentic-search-test-bucket/test-documents/`
- [ ] IAM policy created and attached
- [ ] AWS credentials configured
- [ ] Verified: can list bucket
- [ ] Verified: can download file

Once all checked, you're ready to test the agent!
