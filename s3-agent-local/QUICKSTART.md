# Quick Start Guide - S3 Agent Local Development

**Goal:** Get the S3 agent running locally in 15 minutes.

---

## Step 1: AWS Setup (5 minutes)

### Run these commands:

```bash
# 1. Create S3 bucket
aws s3 mb s3://agentic-search-test-bucket --region us-west-2

# 2. Upload your PDF test file
aws s3 cp "../00010, Nice detailing, 7.5k, 4_1_19, advance.pdf" \
  s3://agentic-search-test-bucket/test-documents/

# 3. Verify upload
aws s3 ls s3://agentic-search-test-bucket/test-documents/

# 4. Create IAM policy file
cat > s3-policy.json << 'EOF'
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
EOF

# 5. Attach policy (get your username first)
aws sts get-caller-identity
aws iam put-user-policy \
  --user-name YOUR_USERNAME \
  --policy-name LocalS3AgentPolicy \
  --policy-document file://s3-policy.json

# 6. Configure AWS (if not already done)
source ./aws_login.sh  # or aws configure
```

**Checklist:**
- [ ] S3 bucket created
- [ ] PDF uploaded
- [ ] IAM policy attached
- [ ] AWS credentials configured

---

## Step 2: Python Environment Setup (5 minutes)

```bash
# Navigate to project
cd s3-agent-local

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt
```

---

## Step 3: Test the Agent (5 minutes)

### Option A: Strands Agent (Fastest)

```bash
python agent_strands.py
```

**Try these queries:**
```
> List all files in my S3 bucket
> Show me files in the test-documents/ folder
> Get metadata for the PDF file in test-documents/
> Preview the first 500 bytes of the PDF
```

### Option B: AgentCore Dev (Hot Reload)

**Terminal 1:**
```bash
agentcore dev
```

**Terminal 2:**
```bash
# Test queries
agentcore invoke --dev '{"prompt": "List all files in my S3 bucket"}'
agentcore invoke --dev '{"prompt": "Show files in test-documents/"}'
agentcore invoke --dev '{"prompt": "Get PDF metadata"}'
```

---

## Step 4: Run Tests (Optional)

```bash
# Run unit tests with moto (no AWS costs)
pytest tests/test_s3_ops.py -v
```

**Expected output:**
```
test_list_objects PASSED
test_list_with_prefix PASSED
test_get_object PASSED
test_get_object_with_range PASSED
test_head_object PASSED
test_put_object PASSED
test_pagination PASSED
test_delete_object PASSED
test_file_not_found_error PASSED

9 passed in 2.5s
```

---

## Example Session

```bash
$ python agent_strands.py

============================================================
S3 Agent - Strands Implementation
============================================================
Configuration: S3AgentConfig(bucket=agentic-search-test-bucket, region=us-west-2, env=local)
============================================================

Enter your query (or 'quit' to exit):
Example: 'List all files in my S3 bucket'

> List all files in test-documents/ folder

[Agent thinking...]

I'll list the files in the test-documents/ folder for you.

[Code executed]
import boto3

s3 = boto3.client('s3')
response = s3.list_objects_v2(
    Bucket='agentic-search-test-bucket',
    Prefix='test-documents/'
)

for obj in response.get('Contents', []):
    print(f"- {obj['Key']} ({obj['Size']} bytes)")

[Output]
- test-documents/00010, Nice detailing, 7.5k, 4_1_19, advance.pdf (737000 bytes)

Found 1 file in the test-documents/ folder:
- 00010, Nice detailing, 7.5k, 4_1_19, advance.pdf (737 KB)

> Get metadata for this PDF

[Agent thinking...]

[Code executed]
import boto3

s3 = boto3.client('s3')
response = s3.head_object(
    Bucket='agentic-search-test-bucket',
    Key='test-documents/00010, Nice detailing, 7.5k, 4_1_19, advance.pdf'
)

print(f"Size: {response['ContentLength']} bytes")
print(f"Type: {response['ContentType']}")
print(f"Modified: {response['LastModified']}")
print(f"ETag: {response['ETag']}")

[Output]
Size: 737000 bytes
Type: application/pdf
Modified: 2026-02-10 18:30:00+00:00
ETag: "abc123def456..."

Here's the metadata for your PDF:
- File size: 737 KB
- Content type: PDF document
- Last modified: February 10, 2026 at 6:30 PM
- This is a valid PDF file ready for processing

> quit
Goodbye!
```

---

## Next Steps

### Immediate (Today)
1. ✅ Run AWS setup commands
2. ✅ Install dependencies
3. ✅ Test with your PDF file
4. ✅ Verify all S3 operations work

### This Week
1. Customize skill for your use case
2. Add more test files to S3
3. Test all 9 S3 operations
4. Refine error handling

### Next Week
1. Deploy to AgentCore: `agentcore deploy`
2. Set up CI/CD with GitHub Actions
3. Add API Gateway (if needed)

---

## Specs Summary

### Strands Code Interpreter
- **Runtime:** Python 3.11
- **Pre-installed:** boto3, standard library
- **Timeout:** 60 seconds (default)
- **Isolation:** Sandboxed execution
- **Output:** stdout, stderr, result

### AgentCore Dev Mode
- **Runtime:** Production-identical environment
- **Hot Reload:** Auto-reload on file save
- **Port:** 8080 (default)
- **Logging:** CloudWatch-style structured logs
- **Testing:** `agentcore invoke --dev`

---

## Success Criteria

After quick start, you should be able to:
- ✅ List files in your S3 bucket
- ✅ Get metadata for your PDF
- ✅ Preview file contents
- ✅ Upload new files
- ✅ Search for patterns

**Time to first successful S3 operation: ~15 minutes**

---

**Questions?** See `README.md` for full documentation.
