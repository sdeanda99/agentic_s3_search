# AWS Bedrock AgentCore - Implementation Guide for S3 File Search

## Executive Summary

AgentCore is **fully viable** for building an agentic S3 file search system. The Code Interpreter provides:
- Pre-installed boto3 with S3 access
- 8-hour max execution (default 15 min)
- 5GB streaming capability per file
- Sandbox isolation with IAM-based security
- CloudTrail audit trail

**Recommendation: Use Code Interpreter for file operations. Gateway is optional for external APIs.**

---

## Quick Comparison: Code Interpreter vs Gateway

### Code Interpreter (Recommended for S3)
```
Agent → Code Interpreter → S3 (boto3)
         ↓
    - boto3 pre-installed ✓
    - Native IAM auth ✓
    - 8-hour timeout ✓
    - 5GB file streaming ✓
    - No Lambda overhead ✓
```

### Gateway (For External APIs)
```
Agent → Gateway → Lambda/API → External Service
         ↓
    - API transformation ✓
    - OAuth/API Key management ✓
    - Schema validation ✓
    - Would add complexity ✗
```

**Verdict:** Use Code Interpreter directly for S3 file search operations.

---

## Implementation Approach

### Phase 1: Core File Search Agent

```python
import boto3
from bedrock_agent import create_agent, invoke_agent

# Step 1: Create execution role with S3 permissions
# (See IAM policy section below)

# Step 2: Define agent with built-in tools
agent_config = {
    'agentName': 'S3FileSearchAgent',
    'agentRoleArn': 'arn:aws:iam::ACCOUNT:role/AgentS3ExecutionRole',
    'modelId': 'anthropic.claude-3-5-sonnet-20241022',
    'instruction': '''You are an S3 file search specialist. Your goal is to help users find and analyze files in S3 buckets.

Tools Available:
- Code Interpreter: Execute Python for file scanning, filtering, and analysis
- Memory: Store search results across session

Process:
1. Ask user which bucket and what they're searching for
2. Use Code Interpreter to scan the S3 prefix
3. Filter by name/extension using glob patterns
4. Preview files (first 500 chars) to validate relevance
5. For text searches, grep through content
6. Compile results with file paths, sizes, and previews

Execution Guardrails:
- List up to 1000 files per scan (use pagination for larger results)
- Preview only first 500 chars (use full read for analysis)
- For files >100MB, use streaming or S3 Select
- Always report execution time and data processed
''',
    'enableUserInput': True,
    'toolGroups': [
        {
            'toolGroupName': 'CodeInterpreter',
            'toolGroupDescription': 'Execute Python for file operations',
            'tools': [
                {
                    'toolName': 'execute_python',
                    'description': 'Run Python code against S3',
                    'toolInputSchema': {
                        'json': {
                            'type': 'object',
                            'properties': {
                                'code': {
                                    'type': 'string',
                                    'description': 'Python code to execute'
                                }
                            },
                            'required': ['code']
                        }
                    }
                }
            ]
        }
    ]
}

# Step 3: Deploy agent
client = boto3.client('bedrock-agent')
response = client.create_agent(**agent_config)
agent_id = response['agent']['agentId']

# Step 4: Create version for production
version_response = client.create_agent_version(
    agentId=agent_id,
    description='v1.0 - S3 File Search'
)

# Step 5: Invoke agent
runtime = boto3.client('bedrock-agent-runtime')

response = runtime.invoke_agent(
    agentId=agent_id,
    agentAliasId='DRAFT',  # or version number
    sessionId='session-123',
    inputText='Find all .py files in my-bucket that contain "def search"'
)

# Handle streaming
for event in response['completion']:
    if 'chunk' in event:
        print(event['chunk']['bytes'].decode('utf-8'), end='', flush=True)
```

### Phase 2: Code Interpreter Script Templates

**Template 1: Scan Folder**
```python
import boto3
import json

s3 = boto3.client('s3')

bucket = "my-bucket"
prefix = "files/"

response = s3.list_objects_v2(
    Bucket=bucket,
    Prefix=prefix,
    MaxKeys=1000
)

files = []
for obj in response.get('Contents', []):
    files.append({
        'key': obj['Key'],
        'size': obj['Size'],
        'modified': obj['LastModified'].isoformat()
    })

print(json.dumps(files, indent=2))
```

**Template 2: Preview File**
```python
import boto3

s3 = boto3.client('s3')

bucket = "my-bucket"
key = "files/example.txt"

response = s3.get_object(Bucket=bucket, Key=key)
content = response['Body'].read().decode('utf-8')

preview = content[:500]
print(f"Preview of {key}:")
print(preview)
print(f"\n... (truncated, total: {len(content)} chars)")
```

**Template 3: Grep Search**
```python
import boto3

s3 = boto3.client('s3')

bucket = "my-bucket"
pattern = "ERROR"
prefix = "logs/"

# Get paginator for large result sets
paginator = s3.get_paginator('list_objects_v2')

matches = []
for page in paginator.paginate(Bucket=bucket, Prefix=prefix, PaginationConfig={'PageSize': 1000}):
    for obj in page.get('Contents', []):
        if obj['Size'] < 100_000_000:  # Skip very large files
            try:
                response = s3.get_object(Bucket=bucket, Key=obj['Key'])
                content = response['Body'].read().decode('utf-8', errors='ignore')
                
                if pattern in content:
                    lines = content.split('\n')
                    matching_lines = [l for l in lines if pattern in l]
                    matches.append({
                        'file': obj['Key'],
                        'matches': len(matching_lines),
                        'sample': matching_lines[0] if matching_lines else None
                    })
            except Exception as e:
                print(f"Error processing {obj['Key']}: {e}")

print(f"Found {len(matches)} matching files")
for match in matches[:10]:  # Show first 10
    print(f"  {match['file']}: {match['matches']} matches")
```

**Template 4: S3 Select for Large Files**
```python
import boto3
import json

s3 = boto3.client('s3')

bucket = "my-bucket"
key = "data/large.csv"

# S3 Select for efficient querying without full download
response = s3.select_object_content(
    Bucket=bucket,
    Key=key,
    ExpressionType='SQL',
    Expression="SELECT * FROM s3object WHERE level = 'ERROR' LIMIT 100",
    InputSerialization={'CSV': {'FileHeaderInfo': 'USE'}},
    OutputSerialization={'JSON': {}},
)

results = []
for event in response['Payload']:
    if 'Records' in event:
        payload = event['Records']['Payload'].decode('utf-8')
        results.append(payload)

output = ''.join(results)
print(output)
```

---

## Deployment Instructions

### Step 1: Create IAM Execution Role

```bash
# Create trust policy
cat > trust-policy.json << 'TRUST'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "bedrock.amazonaws.com",
          "bedrock-agent.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "YOUR-ACCOUNT-ID"
        }
      }
    }
  ]
}
TRUST

# Create role
aws iam create-role \
  --role-name AgentS3ExecutionRole \
  --assume-role-policy-document file://trust-policy.json

# Create inline policy with S3 permissions
cat > s3-policy.json << 'POLICY'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ReadOperations",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:ListBucketVersions",
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:GetObjectTagging",
        "s3:HeadObject",
        "s3:SelectObjectContent"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    },
    {
      "Sid": "S3WriteResults",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectTagging"
      ],
      "Resource": "arn:aws:s3:::my-bucket/results/*"
    }
  ]
}
POLICY

aws iam put-role-policy \
  --role-name AgentS3ExecutionRole \
  --policy-name S3SearchPolicy \
  --policy-document file://s3-policy.json
```

### Step 2: Create Agent

```python
import boto3
import json

client = boto3.client('bedrock-agent', region_name='us-east-1')

# Create agent
response = client.create_agent(
    agentName='S3FileSearchAgent',
    agentRoleArn='arn:aws:iam::ACCOUNT-ID:role/AgentS3ExecutionRole',
    modelId='anthropic.claude-3-5-sonnet-20241022',
    instruction='''You are an S3 file search specialist.

When users ask to find files:
1. Clarify the bucket name and search criteria
2. Use Python code to scan and filter files
3. For text searches, read file content and search
4. Return file paths, sizes, and relevant excerpts

Available Python libraries:
- boto3: AWS SDK
- pandas: CSV/Excel processing
- json: JSON parsing
- re: regex patterns
- pathlib: Path operations

Best Practices:
- Use list_objects_v2 for scanning (paginate if needed)
- For large files (>100MB), use S3 Select or streaming
- Always handle UTF-8 decode errors gracefully
- Report operation statistics (files scanned, matches found, time taken)
''',
    description='Search and analyze files in S3 buckets'
)

agent_id = response['agent']['agentId']
print(f"Created agent: {agent_id}")

# Create version
version_resp = client.create_agent_version(
    agentId=agent_id,
    description='v1.0 - Initial S3 file search'
)

print(f"Created version: {version_resp['agentVersion']['agentVersion']}")
```

### Step 3: Test Agent

```python
import boto3

runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

response = runtime.invoke_agent(
    agentId='AGENT-ID',
    agentAliasId='DRAFT',
    sessionId='test-session-001',
    inputText='Find all Python files in my-bucket'
)

print("Agent response:")
for event in response['completion']:
    if 'chunk' in event:
        chunk_text = event['chunk']['bytes'].decode('utf-8')
        print(chunk_text, end='', flush=True)
    elif 'actionGroupInvocation' in event:
        print(f"\n[Executing: {event['actionGroupInvocation']['toolName']}]")

print("\n\nDone!")
```

---

## Performance Optimization

### For Large Buckets (10,000+ files)

**Problem:** Pagination overhead, long execution time

**Solution 1: Prefix-based Sharding**
```python
import boto3
from concurrent.futures import ThreadPoolExecutor

s3 = boto3.client('s3')

def scan_prefix(bucket, prefix):
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [obj['Key'] for obj in response.get('Contents', [])]

# Scan multiple prefixes in parallel
prefixes = ['2024/01/', '2024/02/', '2024/03/']
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(lambda p: scan_prefix('my-bucket', p), prefixes)

all_files = []
for result in results:
    all_files.extend(result)

print(f"Total files: {len(all_files)}")
```

**Solution 2: S3 Select for Filtering**
```python
# Instead of downloading CSV and filtering in Python:
s3.select_object_content(
    Bucket=bucket,
    Key='data.csv',
    Expression="SELECT * FROM s3object WHERE category = 'important'",
    ...
)
# This filters server-side, returning only matching rows
```

**Solution 3: CloudTrail Query (Post-Execution Analysis)**
```python
import boto3
from datetime import datetime, timedelta

ct = boto3.client('cloudtrail')

response = ct.lookup_events(
    LookupAttributes=[
        {'AttributeKey': 'ResourceType', 'AttributeValue': 'AWS::S3::Object'}
    ],
    StartTime=datetime.now() - timedelta(hours=1),
    MaxResults=50
)

for event in response['Events']:
    print(f"{event['EventName']}: {event['EventName']}")
```

---

## Cost Analysis

### Example: Search 100,000 files for pattern

**Setup:**
- Bucket: 100,000 files, 500GB total
- Search: Find files containing "ERROR"
- Execution time: ~2 minutes
- Code executed: ~50 list operations, 10,000 get_object calls

**Costs:**
- AgentCore invocation: 1 × $0.001 = **$0.001**
- S3 ListBucket: 50 × $0.005/1000 = **$0.00025**
- S3 GetObject: 10,000 × $0.0004/1000 = **$0.004**
- Total: **~$0.005** per search

**Optimization:** Same search with S3 Select
- S3 Select: 1 query × $0.0025 = **$0.0025**
- Total: **~$0.003** per search (40% cheaper)

---

## Monitoring and Logging

### CloudWatch Logs

```python
import boto3
import json
from datetime import datetime, timedelta

logs = boto3.client('logs')

# Query agent execution logs
response = logs.filter_log_events(
    logGroupName='/aws/bedrock/agents',
    startTime=int((datetime.now() - timedelta(hours=1)).timestamp() * 1000),
)

for event in response['events']:
    log = json.loads(event['message'])
    print(f"{log['agentId']}: {log['executionStatus']} ({log['duration']}ms)")
```

### CloudTrail Audit

```bash
# Find all S3 operations by agent
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=bedrock-agent \
  --max-results 50 \
  --query 'Events[*].[EventTime,EventName,Resources[0].ResourceName]' \
  --output table
```

---

## Security Hardening

### 1. Least Privilege S3 Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ListSpecificBucket",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::search-bucket",
      "Condition": {
        "StringLike": {
          "s3:prefix": ["data/*", "files/*"]
        }
      }
    },
    {
      "Sid": "S3ReadSpecificPaths",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:SelectObjectContent"],
      "Resource": "arn:aws:s3:::search-bucket/data/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-server-side-encryption": "aws:kms"
        }
      }
    }
  ]
}
```

### 2. Enable S3 Access Logging

```bash
aws s3api put-bucket-logging \
  --bucket search-bucket \
  --bucket-logging-status '{
    "LoggingEnabled": {
      "TargetBucket": "logs-bucket",
      "TargetPrefix": "s3-logs/"
    }
  }'
```

### 3. Monitor for Anomalies

```python
import boto3
from datetime import datetime, timedelta

ct = boto3.client('cloudtrail')

# Find unusual activity (many failed attempts)
response = ct.lookup_events(
    LookupAttributes=[
        {'AttributeKey': 'EventStatus', 'AttributeValue': 'failure'}
    ],
    StartTime=datetime.now() - timedelta(hours=1)
)

if len(response['Events']) > 10:
    print("ALERT: Unusual number of failed operations detected")
    for event in response['Events'][:5]:
        print(f"  - {event['EventName']}: {event['EventID']}")
```

---

## Troubleshooting

### Issue: Agent timeout (15 minutes)

**Solution:** Increase timeout or optimize query
```python
# In agent creation, set timeout explicitly
client.update_agent(
    agentId='agent-123',
    agentName='S3FileSearchAgent',
    maxRetries=3,
    timeout=3600  # 1 hour instead of default 15 min
)
```

### Issue: Memory exhaustion with large files

**Solution:** Use streaming
```python
# Instead of:
content = s3.get_object(Bucket=bucket, Key=key)['Body'].read()

# Use:
response = s3.get_object(Bucket=bucket, Key=key)
for chunk in response['Body'].iter_chunks(chunk_size=65536):
    process_chunk(chunk)
```

### Issue: Slow list operations

**Solution:** Use pagination efficiently
```python
# Instead of:
response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

# Use:
paginator = s3.get_paginator('list_objects_v2')
for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
    process_page(page)
```

---

## Next Steps

1. **Create IAM role** with S3 permissions
2. **Deploy agent** using provided code
3. **Test with sample queries** (find .py files, search for patterns)
4. **Monitor CloudWatch logs** for execution metrics
5. **Optimize based on actual usage** patterns
6. **Consider caching** frequently accessed results in DynamoDB

---

## References

- AWS Bedrock Agents: https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html
- Code Interpreter: https://docs.aws.amazon.com/bedrock/latest/userguide/code-interpreter.html
- S3 API Reference: https://docs.aws.amazon.com/AmazonS3/latest/API/
- S3 Select: https://docs.aws.amazon.com/AmazonS3/latest/userguide/selecting-content-from-objects.html
- boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/

