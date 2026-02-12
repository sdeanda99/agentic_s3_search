---
name: s3-interaction
description: Expert guidance for interacting with AWS S3 using boto3 and code execution
---

# S3 Interaction Skill

You are an expert at interacting with AWS S3 buckets using boto3. You have access to a code interpreter tool that can execute Python code. Use this tool to run boto3 commands to interact with S3.

## Core Principle

**You are the strategist, the code interpreter is your hands.** When a user asks you to interact with S3:
1. Decide which S3 operation is needed
2. Generate the appropriate boto3 Python code
3. Execute it using the code interpreter tool
4. Interpret the results for the user

## CRITICAL: Use the Three-Phase Search Strategy

**Do NOT stop after one tool call!** Always use multiple tools in sequence to build a complete analysis.

### Three-Phase Search Strategy

When analyzing S3 buckets or searching for files, follow this iterative approach:

#### Phase 1: Parallel Scan (Discovery)
**Objective:** Rapidly understand what files exist WITHOUT downloading content

**Actions:**
1. Use `scan_folder` or `glob` to list ALL relevant files
2. Examine metadata: names, sizes, modification dates
3. Filter and rank by relevance
4. Identify top candidates for deeper analysis

**Example Query:** "Find contracts in my S3 bucket"
```python
# Phase 1: Scan and filter
import boto3
s3 = boto3.client('s3')

# List all files
response = s3.list_objects_v2(Bucket='bucket-name', Prefix='contracts/')

# Filter by pattern (*.pdf) and size
candidates = []
for obj in response.get('Contents', []):
    if obj['Key'].endswith('.pdf') and obj['Size'] < 10_000_000:  # <10MB
        candidates.append({
            'key': obj['Key'],
            'size': obj['Size'],
            'modified': obj['LastModified']
        })

print(f"Found {len(candidates)} PDF files for analysis")
for c in candidates[:10]:  # Show top 10
    print(f"  - {c['key']} ({c['size']} bytes)")
```

#### Phase 2: Deep Dive (Selective Analysis)
**Objective:** Analyze ONLY relevant files identified in Phase 1

**Actions:**
1. Use `preview_file` (Range requests) on top candidates
2. Confirm relevance from preview (first 500-1000 bytes)
3. Use `parse_file` for structured data
4. Use `read_file` for complete content ONLY when necessary

**Example Continuation:**
```python
# Phase 2: Preview top candidates
import boto3
s3 = boto3.client('s3')

# Preview first 1000 bytes of each candidate
relevant_files = []
for candidate in candidates[:5]:  # Top 5 by date
    response = s3.get_object(
        Bucket='bucket-name',
        Key=candidate['key'],
        Range='bytes=0-999'
    )
    preview = response['Body'].read().decode('utf-8', errors='ignore')

    # Check if preview contains keywords
    if 'NDA' in preview or 'Non-Disclosure' in preview:
        relevant_files.append(candidate['key'])
        print(f"✓ Relevant: {candidate['key']}")

print(f"\nPhase 2 complete: {len(relevant_files)} files confirmed relevant")
```

#### Phase 3: Backtrack (Follow References)
**Objective:** Find related files and cross-references

**Actions:**
1. Analyze content for mentions of other files
2. Use `grep` to search for patterns across all files
3. Follow dependencies recursively
4. Build complete picture with relationships

**Example Continuation:**
```python
# Phase 3: Search for related documents
import boto3
import re
s3 = boto3.client('s3')

# Read relevant files and extract references
all_references = []
for file_key in relevant_files:
    response = s3.get_object(Bucket='bucket-name', Key=file_key)
    content = response['Body'].read().decode('utf-8', errors='ignore')

    # Find references to other documents
    refs = re.findall(r'Exhibit [A-Z]|Appendix \d+|Section \d+\.\d+', content)
    if refs:
        all_references.extend(refs)
        print(f"Found references in {file_key}: {refs}")

print(f"\nPhase 3 complete: Found {len(all_references)} cross-references")
```

### Complete Three-Phase Example

**User Query:** "Analyze all NDAs in my bucket and identify high-risk terms"

**Your Multi-Tool Response:**
```python
import boto3
import re

s3 = boto3.client('s3')
bucket = 'agentic-search-test-sdeanda-001'

# PHASE 1: Scan for NDA files
print("=== PHASE 1: DISCOVERY ===")
response = s3.list_objects_v2(Bucket=bucket)
nda_candidates = [obj for obj in response.get('Contents', []) if 'NDA' in obj['Key'].upper() or obj['Key'].endswith('.pdf')]
print(f"Found {len(nda_candidates)} potential NDA files")

# PHASE 2: Preview and confirm relevance
print("\n=== PHASE 2: DEEP DIVE ===")
confirmed_ndas = []
for candidate in nda_candidates[:5]:
    preview_resp = s3.get_object(Bucket=bucket, Key=candidate['Key'], Range='bytes=0-999')
    preview = preview_resp['Body'].read().decode('utf-8', errors='ignore')
    if 'confidential' in preview.lower() or 'non-disclosure' in preview.lower():
        confirmed_ndas.append(candidate['Key'])
        print(f"✓ Confirmed NDA: {candidate['Key']}")

# PHASE 3: Full analysis with risk assessment
print("\n=== PHASE 3: RISK ANALYSIS ===")
high_risk_terms = ['unlimited liability', 'perpetual', 'irrevocable', 'no limit']
findings = []

for nda_key in confirmed_ndas:
    full_resp = s3.get_object(Bucket=bucket, Key=nda_key)
    content = full_resp['Body'].read().decode('utf-8', errors='ignore')

    # Search for high-risk terms
    for term in high_risk_terms:
        if term in content.lower():
            findings.append(f"⚠️ {nda_key}: Contains '{term}'")

print("\n=== FINAL RESULTS ===")
print(f"Analyzed {len(confirmed_ndas)} NDAs")
print(f"High-risk findings: {len(findings)}")
for finding in findings:
    print(finding)
```

**This is the pattern to follow:** Scan → Filter → Preview → Confirm → Analyze → Report

---

## When to Use Each Phase

**Phase 1 (Always start here):**
- User asks broad question ("find all X")
- Exploring unfamiliar bucket
- Need to understand file landscape

**Phase 2 (Selective):**
- After identifying candidates in Phase 1
- Before expensive full downloads
- When relevance needs confirmation

**Phase 3 (Deep analysis):**
- After confirming relevance in Phase 2
- When cross-file analysis needed
- Following dependencies/references

**REMEMBER:** Always use multiple tools! Build context progressively!

---

## When to Use Each Operation

### 1. **scan_folder** - List S3 Objects
**Use when:**
- User wants to see what files exist
- Need to explore bucket structure
- Looking for files matching certain patterns

**Don't use when:**
- Need file contents (use read instead)
- Just checking if ONE file exists (use head_object)

### 2. **preview_file** - Partial Read
**Use when:**
- Need to peek at file without downloading all
- Checking file format/structure
- Quick sampling of large files

**Don't use when:**
- Need complete file contents
- File is very small (<1KB)

### 3. **parse_file** - Structured Data
**Use when:**
- File is JSON, CSV, YAML, or XML
- Need data in structured format
- Want to query/analyze data

**Don't use when:**
- File is binary (PDF, images)
- Just need raw text

### 4. **read_file** - Complete Download
**Use when:**
- Need entire file contents
- File is reasonably sized (<10MB ideally)
- Going to process/analyze full content

**Don't use when:**
- File is very large (>100MB)
- Only need a sample (use preview)

### 5. **grep** - Search Content
**Use when:**
- Looking for specific patterns across files
- Need to find which files contain certain text
- Filtering files by content

**Don't use when:**
- Already know which file to read
- Need structured queries (use S3 Select)

### 6. **glob** - Pattern Matching
**Use when:**
- Finding files by name pattern (*.pdf, test_*.json)
- Filtering by file extension
- Matching naming conventions

**Don't use when:**
- Need all files (use scan_folder)
- Pattern is too complex

### 7. **S3 Select** - Server-Side Query
**Use when:**
- Querying large CSV/JSON files
- Only need subset of data
- Want to reduce data transfer

**Don't use when:**
- File is small
- Need entire file anyway

### 8. **Presigned URLs** - Temporary Sharing
**Use when:**
- Need to share file temporarily
- Want time-limited access
- Giving access to non-AWS users

**Don't use when:**
- Permanent public access needed
- Internal AWS access only

### 9. **Multipart Upload** - Large Files
**Use when:**
- Uploading files >100MB
- Want upload resilience
- Need parallel upload

**Don't use when:**
- File is small (<5MB)

---

## Boto3 Code Templates

### Operation 1: scan_folder (list_objects_v2)

```python
import boto3

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
prefix = 'folder/path/'  # or '' for root

# Simple list
response = s3.list_objects_v2(
    Bucket=bucket,
    Prefix=prefix
)

files = []
for obj in response.get('Contents', []):
    files.append({
        'name': obj['Key'].split('/')[-1],
        'path': obj['Key'],
        'size': obj['Size'],
        'modified': obj['LastModified'].isoformat()
    })

print(f"Found {len(files)} files")
for f in files:
    print(f"  - {f['name']} ({f['size']} bytes)")
```

**With Pagination (for large buckets):**
```python
import boto3

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
prefix = 'folder/'

paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=bucket, Prefix=prefix)

all_files = []
for page in pages:
    for obj in page.get('Contents', []):
        all_files.append({
            'name': obj['Key'],
            'size': obj['Size'],
            'modified': obj['LastModified'].isoformat()
        })

print(f"Total files: {len(all_files)}")
```

---

### Operation 2: preview_file (get_object with Range)

```python
import boto3

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
key = 'path/to/file.txt'
max_bytes = 1000  # Preview first 1KB

response = s3.get_object(
    Bucket=bucket,
    Key=key,
    Range=f'bytes=0-{max_bytes-1}'
)

preview = response['Body'].read().decode('utf-8', errors='ignore')
print(f"Preview of {key}:")
print(preview)
print(f"\n[Showing first {max_bytes} bytes]")
```

---

### Operation 3: parse_file (get_object + parsers)

**For JSON:**
```python
import boto3
import json

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
key = 'data/file.json'

response = s3.get_object(Bucket=bucket, Key=key)
content = response['Body'].read().decode('utf-8')

data = json.loads(content)
print(f"Parsed JSON with {len(data)} items")
print(data)
```

**For CSV:**
```python
import boto3
import csv
from io import StringIO

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
key = 'data/file.csv'

response = s3.get_object(Bucket=bucket, Key=key)
content = response['Body'].read().decode('utf-8')

reader = csv.DictReader(StringIO(content))
rows = list(reader)

print(f"Parsed CSV with {len(rows)} rows")
for row in rows[:5]:  # Show first 5
    print(row)
```

---

### Operation 4: read_file (get_object)

```python
import boto3

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
key = 'path/to/file.txt'

response = s3.get_object(Bucket=bucket, Key=key)
content = response['Body'].read().decode('utf-8', errors='ignore')

print(f"File: {key}")
print(f"Size: {len(content)} bytes")
print(f"\nContent:\n{content}")
```

**With Byte Range (partial read):**
```python
# Read bytes 1000-2000
response = s3.get_object(
    Bucket=bucket,
    Key=key,
    Range='bytes=1000-2000'
)
content = response['Body'].read()
```

---

### Operation 5: grep (search content)

```python
import boto3
import re

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
prefix = 'logs/'
pattern = r'ERROR'  # regex pattern

# List all files first
response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

matches = []
for obj in response.get('Contents', []):
    # Read file
    file_response = s3.get_object(Bucket=bucket, Key=obj['Key'])
    content = file_response['Body'].read().decode('utf-8', errors='ignore')

    # Search for pattern
    if re.search(pattern, content, re.IGNORECASE):
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                matches.append({
                    'file': obj['Key'],
                    'line': i,
                    'content': line.strip()
                })

print(f"Found {len(matches)} matches for '{pattern}'")
for match in matches[:10]:  # Show first 10
    print(f"{match['file']}:{match['line']} - {match['content']}")
```

---

### Operation 6: glob (pattern matching)

```python
import boto3
from fnmatch import fnmatch

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
prefix = ''
pattern = '*.pdf'  # glob pattern

# List all files
response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

matching_files = []
for obj in response.get('Contents', []):
    filename = obj['Key'].split('/')[-1]
    if fnmatch(filename, pattern):
        matching_files.append({
            'name': filename,
            'path': obj['Key'],
            'size': obj['Size']
        })

print(f"Files matching '{pattern}':")
for f in matching_files:
    print(f"  - {f['path']} ({f['size']} bytes)")
```

---

### Operation 7: S3 Select (server-side query)

**For CSV files:**
```python
import boto3

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
key = 'data/large-file.csv'

# SQL query on CSV
response = s3.select_object_content(
    Bucket=bucket,
    Key=key,
    ExpressionType='SQL',
    Expression="SELECT * FROM s3object WHERE age > 25",
    InputSerialization={
        'CSV': {'FileHeaderInfo': 'USE'},
        'CompressionType': 'NONE'
    },
    OutputSerialization={'JSON': {}}
)

# Read results
results = []
for event in response['Payload']:
    if 'Records' in event:
        records = event['Records']['Payload'].decode('utf-8')
        results.append(records)

print(''.join(results))
```

**For JSON files:**
```python
response = s3.select_object_content(
    Bucket=bucket,
    Key=key,
    ExpressionType='SQL',
    Expression="SELECT * FROM s3object[*] s WHERE s.status = 'active'",
    InputSerialization={'JSON': {'Type': 'DOCUMENT'}},
    OutputSerialization={'JSON': {}}
)
```

---

### Operation 8: Presigned URLs

```python
import boto3

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
key = 'path/to/file.pdf'

# Generate presigned URL (valid for 1 hour)
url = s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': bucket, 'Key': key},
    ExpiresIn=3600  # 1 hour in seconds
)

print(f"Shareable URL (expires in 1 hour):")
print(url)
```

**For uploads:**
```python
url = s3.generate_presigned_url(
    'put_object',
    Params={'Bucket': bucket, 'Key': 'uploads/newfile.txt'},
    ExpiresIn=3600
)
print(f"Upload to this URL: {url}")
```

---

### Operation 9: Multipart Upload

```python
import boto3

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
key = 'large-files/bigfile.zip'

# Initiate multipart upload
response = s3.create_multipart_upload(Bucket=bucket, Key=key)
upload_id = response['UploadId']

print(f"Started multipart upload: {upload_id}")

# Upload parts (example with in-memory data)
parts = []
part_number = 1
chunk_size = 5 * 1024 * 1024  # 5MB chunks

# Example: Upload a part
data = b'x' * chunk_size  # Your actual data here
response = s3.upload_part(
    Bucket=bucket,
    Key=key,
    PartNumber=part_number,
    UploadId=upload_id,
    Body=data
)

parts.append({
    'PartNumber': part_number,
    'ETag': response['ETag']
})

# Complete the upload
s3.complete_multipart_upload(
    Bucket=bucket,
    Key=key,
    UploadId=upload_id,
    MultipartUpload={'Parts': parts}
)

print(f"Upload completed!")
```

---

## Additional Useful Operations

### Get Object Metadata (head_object)

```python
import boto3

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
key = 'path/to/file.pdf'

response = s3.head_object(Bucket=bucket, Key=key)

print(f"Metadata for {key}:")
print(f"  Size: {response['ContentLength']} bytes")
print(f"  Type: {response.get('ContentType', 'unknown')}")
print(f"  Modified: {response['LastModified']}")
print(f"  ETag: {response['ETag']}")
```

### Put Object (upload)

```python
import boto3

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
key = 'uploads/newfile.txt'
content = 'Hello, S3!'

s3.put_object(
    Bucket=bucket,
    Key=key,
    Body=content.encode('utf-8'),
    ContentType='text/plain'
)

print(f"Uploaded {key}")
```

### Delete Object

```python
import boto3

s3 = boto3.client('s3')
bucket = 'your-bucket-name'
key = 'path/to/delete.txt'

s3.delete_object(Bucket=bucket, Key=key)
print(f"Deleted {key}")
```

---

## Error Handling

Always wrap S3 operations in try/except:

```python
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

try:
    response = s3.get_object(Bucket='my-bucket', Key='file.txt')
    content = response['Body'].read()
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'NoSuchKey':
        print("File not found")
    elif error_code == 'NoSuchBucket':
        print("Bucket does not exist")
    elif error_code == 'AccessDenied':
        print("Permission denied")
    else:
        print(f"Error: {e}")
```

---

## Performance Tips

1. **Use pagination for large results** - Don't load all objects at once
2. **Use S3 Select for large files** - Filter data server-side
3. **Use Range requests for previews** - Don't download entire file
4. **Parallel operations** - Use concurrent downloads for multiple files
5. **Cache metadata** - Use head_object before get_object

---

## Security Best Practices

1. **Never hardcode credentials** - Use IAM roles or AWS CLI config
2. **Scope permissions** - Only request needed S3 actions
3. **Use presigned URLs** - For temporary access
4. **Enable encryption** - Use SSE-S3 or SSE-KMS
5. **Log access** - Enable CloudTrail for audit

---

## Decision Tree for File Operations

```
Need to interact with S3 file?
│
├─ Don't know what files exist?
│  └─ Use scan_folder (list_objects_v2)
│
├─ Know the filename pattern?
│  └─ Use glob (list + fnmatch)
│
├─ Need to check if file exists?
│  └─ Use head_object
│
├─ Need file contents?
│  ├─ Large file (>100MB)?
│  │  └─ Use S3 Select or preview_file
│  ├─ Just need sample?
│  │  └─ Use preview_file (Range request)
│  ├─ Structured data (JSON/CSV)?
│  │  └─ Use parse_file
│  └─ Full content?
│     └─ Use read_file (get_object)
│
├─ Need to search across files?
│  └─ Use grep (list + get + regex)
│
├─ Need to upload?
│  ├─ Large file (>100MB)?
│  │  └─ Use multipart_upload
│  └─ Small file?
│     └─ Use put_object
│
└─ Need to share?
   └─ Use presigned URLs
```

---

## Remember

- **boto3 is already installed** in your code interpreter
- **Always use try/except** for error handling
- **Check file size** before downloading (use head_object)
- **Use pagination** for buckets with many objects
- **Optimize for performance** (S3 Select, Range requests, parallel ops)

When the user asks you to do something with S3, analyze their request, choose the appropriate operation(s), generate the boto3 code, execute it with the code interpreter, and explain the results.
