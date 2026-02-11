# Complete Legal Contract Review Agent - Example Implementation

This document provides a **complete, ready-to-deploy** implementation of a legal contract review agent that combines Claude skills with S3 file search capabilities.

---

## Use Case

**Build an AI legal assistant that:**
1. Searches S3 bucket for contract documents
2. Applies legal contract review methodology
3. Classifies risk levels (RED/YELLOW/GREEN)
4. Generates comprehensive risk assessment reports
5. Provides actionable recommendations

**Business Value:**
- Accelerate contract review from days to minutes
- Consistent application of legal standards
- Reduce risk of missing critical clauses
- Scale legal expertise across organization

---

## Complete Project Structure

```
legal_contract_agent/
├── agent.py                          # Main entrypoint
├── requirements.txt                  # Dependencies
├── skills/
│   └── legal-contract-review.md     # Legal skill instructions
├── tools/
│   └── s3_search.py                 # S3 file search tools
└── README.md                         # Documentation
```

---

## File 1: agent.py

```python
"""
Legal Contract Review Agent
Combines Claude legal skill with S3 file search tools
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from tools.s3_search import S3FileTools
import os
import json

app = BedrockAgentCoreApp()

# Load legal skill instructions
SKILL_PATH = os.path.join(os.path.dirname(__file__), 'skills', 'legal-contract-review.md')
with open(SKILL_PATH, 'r') as f:
    LEGAL_SKILL = f.read()

# Configuration (can be overridden via environment variables)
S3_BUCKET = os.environ.get('CONTRACTS_BUCKET', 'legal-contracts-bucket')
S3_PREFIX = os.environ.get('CONTRACTS_PREFIX', 'contracts/')

# Initialize S3 search tools
s3_tools = S3FileTools(bucket=S3_BUCKET)

# Create agent with legal skill + S3 tools
agent = Agent(
    name="LegalContractReviewer",
    system_prompt=LEGAL_SKILL,
    tools=[
        s3_tools.scan_folder,
        s3_tools.preview_file,
        s3_tools.parse_file,
        s3_tools.read_file,
        s3_tools.grep,
        s3_tools.glob
    ],
    model="anthropic.claude-3-5-sonnet-20240620-v1:0"
)

@app.entrypoint
def invoke(payload):
    """
    Main entrypoint for contract review requests

    Payload format:
    {
        "query": "Review all NDAs in the contracts/2024/ folder",
        "prefix": "contracts/2024/",  # Optional: override default prefix
        "report_format": "detailed"    # Optional: "summary" or "detailed"
    }
    """
    query = payload.get('query', '')
    prefix = payload.get('prefix', S3_PREFIX)
    report_format = payload.get('report_format', 'detailed')

    if not query:
        return {"error": "No query provided"}

    # Add context to query
    enhanced_query = f"""
    S3 Bucket: {S3_BUCKET}
    Default Prefix: {prefix}

    User Request: {query}

    Instructions:
    1. Use the S3 search tools to find relevant contract documents
    2. Apply the legal contract review methodology to analyze each document
    3. Classify findings using RED/YELLOW/GREEN framework
    4. Generate a {report_format} report with:
       - Executive summary
       - Document-by-document analysis
       - High-priority recommendations
       - Risk summary
    """

    # Invoke agent
    result = agent(enhanced_query)

    return {
        "query": query,
        "bucket": S3_BUCKET,
        "prefix": prefix,
        "report": result.message,
        "status": "completed"
    }

@app.health_check
def health():
    """Health check endpoint"""
    return {"status": "healthy", "agent": "legal-contract-review"}

if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=8080)
```

---

## File 2: requirements.txt

```txt
bedrock-agentcore>=1.0.0
strands-agents>=1.0.0
boto3>=1.34.0
pyyaml>=6.0
```

---

## File 3: skills/legal-contract-review.md

```markdown
---
name: legal-contract-review
description: Review contracts using legal frameworks and company playbook
---

# Legal Contract Review Skill

You are an expert legal contract reviewer. Your role is to analyze contracts systematically, identify risks, and provide actionable recommendations.

## Core Methodology

Follow this **5-step process** for every contract:

### 1. Document Classification
First, identify the contract type:
- **NDA** (Non-Disclosure Agreement)
- **MSA** (Master Services Agreement)
- **SaaS Agreement**
- **Vendor Agreement**
- **Employment Agreement**
- **Other** (specify)

### 2. Clause-by-Clause Analysis

Analyze these **critical clause types**:

#### A. Liability and Indemnification
- **Liability Cap**: Is there a cap? What amount? Acceptable: <1x annual contract value
- **Unlimited Liability**: Any scenarios with unlimited liability? (data breach, IP infringement)
- **Mutual vs One-Sided**: Is indemnification mutual or one-sided?

**Classification:**
- 🟢 GREEN: Liability capped at reasonable amount, mutual indemnification
- 🟡 YELLOW: Higher cap, but still reasonable
- 🔴 RED: Unlimited liability, one-sided indemnification favoring counterparty

#### B. Intellectual Property Rights
- **IP Ownership**: Who owns work product? Pre-existing IP?
- **Licensing**: What rights are granted? Exclusive vs non-exclusive?
- **Restrictions**: Any restrictions on use?

**Classification:**
- 🟢 GREEN: Clear IP ownership, appropriate licensing, protects pre-existing IP
- 🟡 YELLOW: Some ambiguity, but manageable
- 🔴 RED: Counterparty claims broad IP rights, unclear ownership

#### C. Data Protection and Privacy
- **Data Processing**: Who is data controller vs processor?
- **GDPR/CCPA Compliance**: Are there data protection clauses?
- **Data Security**: What security standards required?
- **Data Breach Notification**: Notification requirements?

**Classification:**
- 🟢 GREEN: Clear data protection terms, compliant with regulations
- 🟡 YELLOW: Basic protections, may need addendum
- 🔴 RED: Insufficient data protection, non-compliant

#### D. Termination and Renewal
- **Term Length**: Initial term? Auto-renewal?
- **Termination Rights**: Can we terminate for convenience? Notice period?
- **Termination Fees**: Any penalties for early termination?

**Classification:**
- 🟢 GREEN: Reasonable term, can terminate with 30-60 day notice, no penalties
- 🟡 YELLOW: Longer term or notice period, but acceptable
- 🔴 RED: Long lock-in, significant termination penalties

#### E. Payment Terms
- **Pricing**: Fixed vs variable? Annual increases?
- **Payment Schedule**: Net 30? Net 60?
- **Late Fees**: What are late payment penalties?

**Classification:**
- 🟢 GREEN: Competitive pricing, Net 30-60, reasonable fees
- 🟡 YELLOW: Higher than market, but acceptable
- 🔴 RED: Excessive pricing, unfavorable terms

#### F. Warranties and Representations
- **Service Levels**: Any SLA? Uptime guarantees?
- **Warranties**: What is warranted?
- **Disclaimer**: Are warranties disclaimed?

**Classification:**
- 🟢 GREEN: Strong SLA, meaningful warranties
- 🟡 YELLOW: Basic warranties
- 🔴 RED: No SLA, disclaimers of all warranties

#### G. Governing Law and Dispute Resolution
- **Jurisdiction**: Which state/country law applies?
- **Venue**: Where are disputes resolved?
- **Arbitration**: Mandatory arbitration? Binding?

**Classification:**
- 🟢 GREEN: Favorable jurisdiction, acceptable dispute resolution
- 🟡 YELLOW: Neutral jurisdiction
- 🔴 RED: Unfavorable jurisdiction, one-sided dispute terms

#### H. Confidentiality
- **Definition**: What is considered confidential?
- **Term**: How long are obligations?
- **Exceptions**: Standard exceptions? (publicly available, independently developed, etc.)

**Classification:**
- 🟢 GREEN: Standard confidentiality terms, reasonable exceptions
- 🟡 YELLOW: Broader than typical
- 🔴 RED: Overly broad confidentiality, unreasonable obligations

### 3. Risk Classification

For each clause, assign a **risk level**:

- 🟢 **GREEN (Low Risk)**: Acceptable as-is, aligns with company standards
- 🟡 **YELLOW (Medium Risk)**: Minor deviation, requires business stakeholder review
- 🔴 **RED (High Risk)**: Unacceptable, must be renegotiated before signing

### 4. Generate Redline Recommendations

For YELLOW and RED findings, provide **specific redline language**:

**Format:**
```
[CLAUSE REFERENCE] - [RISK LEVEL]

Current Language:
"[exact text from contract]"

Proposed Redline:
"[your recommended replacement text]"

Rationale:
[why this change is needed]

Priority: [Tier 1 / Tier 2 / Tier 3]
```

**Priority Tiers:**
- **Tier 1 (Must-Have)**: Deal-breaker issues, required changes
- **Tier 2 (Should-Have)**: Important but negotiable
- **Tier 3 (Nice-to-Have)**: Minor improvements, concession candidates

### 5. Generate Summary Report

Produce a **structured report** with:

#### Executive Summary
- Contract type and counterparty
- Overall risk assessment (High/Medium/Low)
- Number of RED/YELLOW/GREEN findings
- Recommendation: Sign / Negotiate / Reject

#### Detailed Findings
- Clause-by-clause analysis with risk levels
- Specific redline recommendations
- Priority categorization

#### Next Steps
- Required actions before signing
- Stakeholders to involve (legal, procurement, security, etc.)
- Estimated negotiation effort

## Report Template

Use this template for all contract reviews:

```markdown
# Contract Review Report

## Executive Summary

**Document:** [Filename]
**Counterparty:** [Company Name]
**Contract Type:** [NDA/MSA/SaaS/etc.]
**Reviewed Date:** [Date]
**Overall Risk:** [🔴 HIGH / 🟡 MEDIUM / 🟢 LOW]

**Recommendation:** [✅ SIGN / ⚠️ NEGOTIATE / ❌ REJECT]

### Risk Summary
- 🔴 RED (High Risk): [count] findings
- 🟡 YELLOW (Medium Risk): [count] findings
- 🟢 GREEN (Low Risk): [count] findings

---

## Detailed Findings

### 🔴 HIGH RISK ISSUES

#### 1. [Clause Type] - Section [X.X]

**Current Language:**
> "[exact text]"

**Issue:**
[Explanation of the risk]

**Proposed Redline:**
> "[recommended replacement]"

**Rationale:**
[Why this change is needed]

**Priority:** Tier 1 (Must-Have)

---

### 🟡 MEDIUM RISK ISSUES

[Same format as above]

---

### 🟢 ACCEPTABLE TERMS

[Brief list of acceptable clauses]

---

## Recommended Redlines

### Tier 1 (Must-Have) - Deal Breakers
1. [Change 1]
2. [Change 2]

### Tier 2 (Should-Have) - Important
1. [Change 1]
2. [Change 2]

### Tier 3 (Nice-to-Have) - Negotiating Points
1. [Change 1]
2. [Change 2]

---

## Next Steps

1. **Legal Review:** [Actions needed]
2. **Business Approval:** [Stakeholders to consult]
3. **Negotiation Strategy:** [Approach recommendations]
4. **Timeline:** [Estimated time to resolve issues]

---

## Appendix

### Contract Metadata
- File path: [S3 path]
- File size: [size]
- Date uploaded: [date]
- Contract effective date: [date]
- Contract end date: [date]
```

## Special Considerations

### NDA-Specific Review
For NDAs, also check:
- **Mutual vs Unilateral**: Is it one-way or two-way?
- **Definition of Confidential Information**: Is it overly broad?
- **Term**: How long do obligations last? (Typical: 2-5 years)
- **Return/Destruction**: Required upon termination?
- **Residuals Clause**: Can we use residual knowledge?

### SaaS Agreement-Specific Review
For SaaS agreements, also check:
- **Data Ownership**: Do we retain ownership of our data?
- **Data Portability**: Can we export data easily?
- **Uptime SLA**: What is guaranteed uptime? (Expect: 99.9%+)
- **Support Terms**: What support is included?
- **Integration Rights**: Can we integrate with other tools?

### MSA-Specific Review
For Master Services Agreements, also check:
- **SOW Process**: How are Statements of Work created?
- **Resource Allocation**: Dedicated vs shared resources?
- **Change Order Process**: How are changes handled?
- **Acceptance Criteria**: How is work accepted?

## Edge Cases

- **Contracts in non-English**: Note language and recommend translation review
- **International contracts**: Flag jurisdictional issues, export controls, GDPR
- **Amendments**: If reviewing an amendment, reference original contract
- **Missing clauses**: Flag if critical clauses are absent (e.g., no liability cap)

## Output Format

Always output in **Markdown format** for readability.

Use emojis for visual clarity:
- 🔴 High Risk
- 🟡 Medium Risk
- 🟢 Low Risk
- ✅ Acceptable
- ❌ Unacceptable
- ⚠️ Needs Review
```

---

## File 4: tools/s3_search.py

```python
"""
S3 File Search Tools
Implements 6 core agentic file search capabilities for S3
"""

import boto3
import json
import csv
import re
from fnmatch import fnmatch
from io import StringIO
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor

class S3FileTools:
    """Agentic file search tools for S3"""

    def __init__(self, bucket: str):
        self.bucket = bucket
        self.s3 = boto3.client('s3')

    def scan_folder(self, prefix: str = '', recursive: bool = False,
                    max_results: int = 10000) -> List[Dict[str, Any]]:
        """
        Scan S3 prefix and return file metadata

        Args:
            prefix: S3 prefix to scan (folder path)
            recursive: If True, scan all nested folders
            max_results: Maximum number of results to return

        Returns:
            List of file metadata dicts
        """
        params = {'Bucket': self.bucket, 'Prefix': prefix, 'MaxKeys': 1000}
        if not recursive:
            params['Delimiter'] = '/'

        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(**params)

        files = []
        for page in pages:
            for obj in page.get('Contents', []):
                if len(files) >= max_results:
                    break
                files.append({
                    'name': obj['Key'].split('/')[-1],
                    'path': obj['Key'],
                    'size': obj['Size'],
                    'modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag'].strip('"')
                })
            if len(files) >= max_results:
                break

        return files

    def preview_file(self, key: str, max_bytes: int = 1000) -> Dict[str, Any]:
        """Preview first N bytes of S3 object"""
        try:
            response = self.s3.get_object(
                Bucket=self.bucket,
                Key=key,
                Range=f'bytes=0-{max_bytes-1}'
            )
            content = response['Body'].read().decode('utf-8', errors='ignore')

            return {
                'path': key,
                'preview': content,
                'size': response.get('ContentLength', 0),
                'content_type': response.get('ContentType', 'unknown')
            }
        except Exception as e:
            return {'error': str(e), 'path': key}

    def parse_file(self, key: str, format: Optional[str] = None) -> Dict[str, Any]:
        """Parse structured data file (JSON, CSV, YAML)"""
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            content = response['Body'].read().decode('utf-8')

            # Auto-detect format
            if not format:
                if key.endswith('.json'):
                    format = 'json'
                elif key.endswith('.csv'):
                    format = 'csv'
                elif key.endswith(('.yaml', '.yml')):
                    format = 'yaml'

            if format == 'json':
                return {'data': json.loads(content), 'format': 'json'}
            elif format == 'csv':
                reader = csv.DictReader(StringIO(content))
                return {'data': list(reader), 'format': 'csv'}
            elif format == 'yaml':
                import yaml
                return {'data': yaml.safe_load(content), 'format': 'yaml'}
            else:
                return {'data': content, 'format': 'text'}

        except Exception as e:
            return {'error': str(e), 'path': key}

    def read_file(self, key: str, start: Optional[int] = None,
                  end: Optional[int] = None) -> str:
        """Read complete or partial S3 object content"""
        params = {'Bucket': self.bucket, 'Key': key}
        if start is not None and end is not None:
            params['Range'] = f'bytes={start}-{end}'

        try:
            response = self.s3.get_object(**params)
            return response['Body'].read().decode('utf-8', errors='ignore')
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def grep(self, pattern: str, prefix: str = '', case_sensitive: bool = True,
             max_matches: int = 100) -> List[Dict[str, Any]]:
        """Search for regex pattern in S3 objects"""
        files = self.scan_folder(prefix, recursive=True)

        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)

        matches = []
        for file in files:
            if len(matches) >= max_matches:
                break

            # Skip binary files
            if file['name'].endswith(('.jpg', '.png', '.pdf', '.zip')):
                continue

            try:
                content = self.read_file(file['path'])
                lines = content.split('\n')

                for i, line in enumerate(lines):
                    if regex.search(line):
                        matches.append({
                            'file': file['path'],
                            'line_number': i + 1,
                            'line': line.strip()
                        })

                        if len(matches) >= max_matches:
                            break
            except:
                continue

        return matches

    def glob(self, pattern: str, prefix: str = '') -> List[Dict[str, Any]]:
        """Filter files by glob pattern"""
        files = self.scan_folder(prefix, recursive=True)
        return [f for f in files if fnmatch(f['name'], pattern)]
```

---

## Deployment Instructions

### Prerequisites
```bash
# Install AWS CLI
aws --version

# Configure AWS credentials
source ./aws_login.sh  # Your auth script

# Install uv for dependency management
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Local Testing

```bash
# Create project
mkdir legal_contract_agent && cd legal_contract_agent

# Create virtual environment with uv
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install bedrock-agentcore strands-agents boto3 pyyaml

# Create all files (agent.py, requirements.txt, skills/, tools/)
# [Copy files from above]

# Test locally
python agent.py

# In another terminal, test the agent
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Review all contracts in the contracts/2024/ folder",
    "prefix": "contracts/2024/"
  }'
```

### Deploy to AgentCore

```bash
# Configure agent
agentcore configure \
  --entrypoint agent.py \
  --non-interactive

# Set environment variables
export CONTRACTS_BUCKET=your-bucket-name
export CONTRACTS_PREFIX=contracts/

# Deploy
agentcore deploy

# Test deployed agent
agentcore invoke '{
  "query": "Find and review all NDAs",
  "report_format": "summary"
}'
```

---

## Example Usage

### Query 1: Review All NDAs
```json
{
  "query": "Find and review all NDA contracts in S3, provide a summary of high-risk terms"
}
```

**Agent Workflow:**
1. Uses `glob('*NDA*.pdf')` to find NDA files
2. Uses `read_file()` to extract contract text
3. Applies legal methodology to each NDA
4. Classifies risk using RED/YELLOW/GREEN framework
5. Generates summary report

### Query 2: Specific Contract Review
```json
{
  "query": "Review the contract at contracts/2024/vendor_agreement_acme.pdf and provide detailed analysis",
  "report_format": "detailed"
}
```

### Query 3: Find Unlimited Liability Clauses
```json
{
  "query": "Search all contracts for unlimited liability clauses and assess risk",
  "prefix": "contracts/"
}
```

**Agent Workflow:**
1. Uses `grep('unlimited.*liability', prefix='contracts/')` to find matches
2. Reads full context around matches
3. Applies legal analysis to each finding
4. Categorizes by risk level

---

## Cost Estimate

**Per Contract Review (typical):**
- Agent invocation: $0.001
- S3 operations (5 files): $0.001
- Data transfer (1MB): $0.0001
- **Total: ~$0.002 per contract**

**Monthly (100 contracts):**
- Total: ~$0.20/month
- **Annual: ~$2.40/year**

Compared to manual legal review at $300-500/hour, this represents 99.9%+ cost savings.

---

## Security Considerations

### IAM Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::legal-contracts-bucket",
        "arn:aws:s3:::legal-contracts-bucket/*"
      ]
    }
  ]
}
```

### Data Protection
- All S3 buckets should use SSE-S3 or SSE-KMS encryption
- Enable CloudTrail logging for audit trail
- Use VPC endpoints for S3 access if contracts are sensitive
- Consider S3 Object Lock for tamper-proof contract storage

---

## Monitoring

### CloudWatch Metrics to Track
- Agent invocation count
- Average execution time
- S3 GetObject count
- Error rate

### CloudWatch Logs Insights Query
```
fields @timestamp, @message
| filter @message like /RED/
| stats count() by bin(5m)
```

This shows high-risk findings over time.

---

## Limitations & Future Enhancements

### Current Limitations
- PDF parsing requires additional tooling (PyPDF2, pdfplumber)
- OCR not included (scanned contracts need pre-processing)
- No comparison across multiple contract versions
- English-language contracts only

### Planned Enhancements
1. **PDF Text Extraction:** Add PyPDF2 for native PDF parsing
2. **Contract Comparison:** Compare multiple versions side-by-side
3. **Playbook Customization:** Load company-specific contract playbooks from S3
4. **Multi-language Support:** Detect language, translate if needed
5. **Risk Scoring:** Quantitative risk score (1-100) per contract

---

## Support & Troubleshooting

### Common Issues

**Issue: "No such file or directory: skills/legal-contract-review.md"**
- **Solution:** Ensure skills/ directory is created and file exists before deployment

**Issue: "AccessDenied" on S3 operations**
- **Solution:** Check IAM execution role has S3 GetObject permissions

**Issue: "Module not found: tools.s3_search"**
- **Solution:** Ensure tools/ is a Python package (add `__init__.py`)

### Debug Mode
```python
# Add to agent.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Conclusion

This legal contract review agent demonstrates the power of combining:
1. **Claude skills** - Domain expertise encoded as instructions
2. **S3 file search** - Efficient document discovery and access
3. **AgentCore Runtime** - Managed, scalable deployment

The result is a production-ready AI legal assistant that provides expert-level contract review at a fraction of the cost and time of manual review.

**Next Steps:**
1. Customize the legal skill for your organization's standards
2. Add your company's contract playbook to skills/
3. Deploy to AgentCore and test with real contracts
4. Monitor usage and refine based on feedback
