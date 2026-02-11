# Production Deployment Guide: CI/CD, Local Development, and API Access

**Updated:** February 10, 2026
**Status:** Production-Ready Implementation Guide

This guide addresses three critical production concerns:
1. **CI/CD with GitHub Actions** - Automated deployments
2. **Local Development with Strands** - Test before deploying
3. **OpenAI-Compatible API** - Simple header auth instead of SigV4

---

## Table of Contents
1. [Local Development Workflow](#local-development-workflow)
2. [CI/CD with GitHub Actions](#cicd-with-github-actions)
3. [OpenAI-Compatible API Wrapper](#openai-compatible-api-wrapper)
4. [Complete Production Deployment Roadmap](#complete-production-deployment-roadmap)

---

## Local Development Workflow

### Why Local Development First?

**Your Question:** "I want to start locally using Strands framework and then transfer to AgentCore deployment to make sure the agent/tools work properly."

**Answer:** ✅ **This is the RECOMMENDED approach!**

### Development Philosophy

```
Local Testing (Strands) → agentcore dev (hot reload) → Deploy to AWS

Benefits:
- Fast iteration (no cloud deployment wait)
- Real AWS testing with your credentials
- Mocked testing for unit tests
- Identical code between local and deployed
```

### Setup: Pure Local Strands Development

**Step 1: Create Standalone Strands Agent**

```python
# agent.py - Works without AgentCore wrapper
from strands import Agent, tool
import boto3

@tool
def search_s3(bucket: str, prefix: str = "") -> str:
    """Search S3 bucket for objects."""
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=20)
    objects = [obj['Key'] for obj in response.get('Contents', [])]
    return f"Found {len(objects)} objects: {objects}"

# Create agent - runs directly locally
agent = Agent(
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    tools=[search_s3],
    system_prompt="You are an S3 search assistant."
)

if __name__ == "__main__":
    # Test locally
    result = agent("Search my bucket 'test-data' for files starting with 'reports/'")
    print(result.message)
```

**Step 2: Install Dependencies (using uv per your preference)**

```bash
# Create virtual environment
uv venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
uv pip install strands-agents strands-agents-tools boto3
```

**Step 3: Test Locally**

```bash
# Run directly - uses your AWS CLI credentials
python agent.py
```

**Output:**
```
Found 5 objects: ['reports/q1-2024.pdf', 'reports/q2-2024.pdf', ...]
```

### Three Testing Approaches

#### Approach 1: Real S3 (Recommended for Initial Development)

```python
# Uses your actual AWS credentials
@tool
def search_s3(bucket: str) -> str:
    s3 = boto3.client('s3')  # Automatically uses ~/.aws/credentials
    response = s3.list_objects_v2(Bucket=bucket, MaxKeys=10)
    return str(response.get('Contents', []))
```

**Pros:** Real behavior, no mocking
**Cons:** Costs money, requires AWS setup
**Best for:** Integration testing

#### Approach 2: Moto (S3 Mocking)

```python
# test_agent.py
from moto import mock_s3
import boto3
from agent import search_s3

@mock_s3
def test_agent():
    # Create mock S3 bucket
    s3 = boto3.client('s3', region_name='us-east-1')
    s3.create_bucket(Bucket='test-bucket')
    s3.put_object(Bucket='test-bucket', Key='data.txt', Body=b'test')

    # Test tool
    result = search_s3('test-bucket')
    assert 'data.txt' in result
    print("✓ Test passed!")

test_agent()
```

**Install:**
```bash
uv pip install moto[s3] pytest
python test_agent.py
```

**Pros:** Free, fast, repeatable
**Cons:** Mocked behavior may differ
**Best for:** Unit testing, CI/CD

#### Approach 3: LocalStack (Full AWS Mock)

```bash
# Start LocalStack
docker run -d -p 4566:4566 localstack/localstack

# Set environment variable
export BOTO3_ENDPOINT_URL=http://localhost:4566
```

```python
@tool
def search_s3(bucket: str) -> str:
    s3 = boto3.client('s3', endpoint_url='http://localhost:4566')
    response = s3.list_objects_v2(Bucket=bucket)
    return str(response)
```

**Pros:** Most realistic mock
**Cons:** Requires Docker
**Best for:** Integration tests without AWS costs

### Migrating to AgentCore

**Minimal Changes Required!**

**Before (Standalone Strands):**
```python
from strands import Agent, tool

@tool
def search_s3(bucket: str) -> str:
    # ... implementation

agent = Agent(tools=[search_s3])

if __name__ == "__main__":
    result = agent("Query")
    print(result.message)
```

**After (AgentCore-Wrapped):**
```python
from strands import Agent, tool
from bedrock_agentcore.runtime import BedrockAgentCoreApp  # ADD THIS

app = BedrockAgentCoreApp()  # ADD THIS

@tool
def search_s3(bucket: str) -> str:
    # ... same implementation (unchanged!)

@app.entrypoint  # ADD THIS
def invoke(payload, context):
    agent = Agent(tools=[search_s3])
    result = agent(payload.get("prompt", ""))
    return {"result": result.message}

if __name__ == "__main__":
    app.run()  # CHANGE THIS
```

**That's it!** Only 4 lines added.

### AgentCore Dev Server (Hot Reload)

```bash
# Start dev server with hot reload
agentcore dev

# Terminal 2: Test agent
agentcore invoke --dev '{"prompt": "Search bucket test-data"}'

# Edit agent.py, save, and it auto-reloads!
```

**Hot Reload Example:**
```
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Detected changes in 'agent.py'
INFO:     Reloading...
INFO:     Started reloader process
```

### Config-Based Multi-Environment Setup

Per your preference for config-driven approaches:

```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class AgentConfig:
    model_id: str
    aws_region: str
    s3_endpoint: str | None = None
    mock_aws: bool = False

    @classmethod
    def from_env(cls):
        env = os.getenv('ENV', 'local')

        configs = {
            'test': cls(
                model_id='mock-model',
                aws_region='us-east-1',
                s3_endpoint='http://localhost:4566',  # LocalStack
                mock_aws=True
            ),
            'local': cls(
                model_id='us.anthropic.claude-3-7-sonnet-20250219-v1:0',
                aws_region=os.getenv('AWS_REGION', 'us-east-1'),
                s3_endpoint=None,  # Real AWS
                mock_aws=False
            ),
            'production': cls(
                model_id='us.anthropic.claude-3-7-sonnet-20250219-v1:0',
                aws_region=os.getenv('AWS_REGION', 'us-east-1'),
                s3_endpoint=None,
                mock_aws=False
            )
        }

        return configs[env]

# agent.py
from config import AgentConfig
import boto3

config = AgentConfig.from_env()

def get_s3_client():
    kwargs = {'region_name': config.aws_region}
    if config.s3_endpoint:
        kwargs['endpoint_url'] = config.s3_endpoint
    return boto3.client('s3', **kwargs)

@tool
def search_s3(bucket: str) -> str:
    s3 = get_s3_client()  # Works in all environments!
    response = s3.list_objects_v2(Bucket=bucket)
    return str(response)
```

**Usage:**
```bash
# Test environment (LocalStack)
ENV=test python agent.py

# Local development (real AWS)
ENV=local python agent.py

# Production (deployed)
ENV=production agentcore deploy
```

---

## CI/CD with GitHub Actions

### Why GitHub Actions for AgentCore?

**Your Question:** "Wouldn't it be better if I can just update the image from a GitHub Action to automate updates?"

**Answer:** ✅ **YES! Fully supported and recommended.**

### CI/CD Support

AgentCore CLI is **designed for CI/CD** with:
- `--non-interactive` flag (skip all prompts)
- `--auto-update-on-conflict` flag (update existing agents)
- Environment variable configuration
- Headless operation
- AWS OIDC authentication (no secrets!)

### Complete GitHub Actions Workflow

**File: `.github/workflows/deploy.yml`**

```yaml
name: Deploy S3 Search Agent to AgentCore

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:  # Manual trigger

env:
  AWS_REGION: us-west-2
  AGENT_NAME: s3-search-agent
  PYTHON_VERSION: '3.11'

jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -r requirements.txt
          uv pip install pytest moto[s3]

      - name: Run unit tests (mocked S3)
        run: pytest tests/

  deploy:
    name: Deploy to AgentCore
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    permissions:
      id-token: write  # Required for AWS OIDC
      contents: read

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS Credentials (OIDC - No Secrets!)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install AgentCore CLI
        run: pip install bedrock-agentcore-starter-toolkit

      - name: Configure Agent (First-time setup)
        run: |
          agentcore configure \
            --entrypoint src/agent.py \
            --name ${{ env.AGENT_NAME }} \
            --deployment-type direct_code_deploy \
            --runtime PYTHON_3_11 \
            --region ${{ env.AWS_REGION }} \
            --disable-memory \
            --non-interactive
        if: github.event_name == 'workflow_dispatch'

      - name: Deploy Agent
        id: deploy
        run: |
          VERSION="${{ github.sha }}"

          agentcore deploy \
            --agent ${{ env.AGENT_NAME }} \
            --auto-update-on-conflict \
            --env "GIT_COMMIT=${VERSION}" \
            --env "DEPLOY_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

      - name: Validate Deployment
        run: |
          echo "Waiting for agent to be ready..."
          sleep 30

          agentcore status --agent ${{ env.AGENT_NAME }} --verbose

          echo "Testing agent invocation..."
          agentcore invoke \
            --agent ${{ env.AGENT_NAME }} \
            '{"prompt": "CI/CD health check test"}'

      - name: Notify on Success
        run: |
          echo "✅ Deployment successful!"
          echo "Agent: ${{ env.AGENT_NAME }}"
          echo "Commit: ${{ github.sha }}"

      - name: Notify on Failure
        if: failure()
        run: |
          echo "❌ Deployment failed!"
          echo "Check logs above for errors"
          # Add Slack/email notification here
```

### AWS OIDC Setup (No Secrets Needed!)

**Step 1: Create GitHub OIDC Provider in AWS**

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

**Step 2: Create IAM Role for GitHub Actions**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/YOUR_REPO:*"
        }
      }
    }
  ]
}
```

**Step 3: Attach Permissions**

```bash
aws iam attach-role-policy \
  --role-name GitHubActionsAgentCoreRole \
  --policy-arn arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess
```

**Step 4: Add Role ARN to GitHub Secrets**

```
Settings → Secrets → Actions → New repository secret

Name: AWS_ROLE_ARN
Value: arn:aws:iam::YOUR_ACCOUNT:role/GitHubActionsAgentCoreRole
```

### Direct Code Deploy vs Container in CI/CD

| Aspect | Direct Code Deploy | Container |
|--------|-------------------|-----------|
| **CI/CD Speed** | ⚡ 3-5 min | 🐢 5-8 min |
| **Docker Required** | ❌ No | ⚠️ Only for local build |
| **GitHub Actions** | ✅ Simple | ✅ Works (slower) |
| **Versioning** | Code-based | Image tag-based |
| **Best For** | Most agents | Complex dependencies |

**Recommendation:** Use **Direct Code Deploy** for faster CI/CD pipelines.

### Container Deployment (If Needed)

```yaml
- name: Deploy Agent (Container Mode)
  run: |
    agentcore configure \
      --entrypoint src/agent.py \
      --deployment-type container \
      --ecr auto \
      --non-interactive

    agentcore deploy \
      --image-tag ${{ github.sha }} \
      --auto-update-on-conflict
```

**CodeBuild handles ARM64 build automatically in the cloud!**

### Deployment Versioning

```yaml
- name: Deploy with Git-based Versioning
  run: |
    VERSION=$(git describe --tags --always)

    agentcore deploy \
      --auto-update-on-conflict \
      --env "VERSION=${VERSION}" \
      --env "COMMIT_SHA=${{ github.sha }}" \
      --env "BRANCH=${{ github.ref_name }}"
```

### Rollback Strategy

```yaml
- name: Rollback to Previous Version
  if: failure()
  run: |
    PREVIOUS_SHA=$(git rev-parse HEAD~1)
    git checkout $PREVIOUS_SHA
    agentcore deploy --auto-update-on-conflict
```

---

## OpenAI-Compatible API Wrapper

### Why OpenAI Compatibility?

**Your Question:** "I want to serve the agent through an OpenAI compatible API with header auth instead of SigV4."

**Answer:** ✅ **Achievable with API Gateway + Lambda proxy pattern.**

### Current AgentCore Authentication

**Default:** AWS SigV4 (complex signature-based auth)
**Alternative:** OAuth 2.0 with Cognito (token-based)
**Not built-in:** Simple API key authentication

### Recommended Architecture

```
Client (OpenAI SDK)
  ↓ Header: X-API-Key: your-key
API Gateway (API Key Auth)
  ↓
Lambda Proxy Function
  ↓ OAuth Bearer Token
AgentCore Runtime
```

### Complete Implementation

**Step 1: Deploy Agent with OAuth**

```bash
agentcore configure -e src/agent.py --protocol HTTP
# During prompts, select OAuth authentication
agentcore deploy
```

**Step 2: Create Lambda Proxy Function**

**File: `lambda/openai_proxy.py`**

```python
import json
import boto3
import time
import os
import httpx

# Configuration
AGENTCORE_RUNTIME_ARN = os.environ['AGENTCORE_RUNTIME_ARN']
OAUTH_TOKEN_ENDPOINT = os.environ['OAUTH_TOKEN_ENDPOINT']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

# Token cache
_token_cache = {"token": None, "expires_at": 0}

def get_oauth_token():
    """Get cached or fresh OAuth token"""
    if _token_cache["token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["token"]

    response = httpx.post(
        OAUTH_TOKEN_ENDPOINT,
        data={
            'grant_type': 'client_credentials',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'scope': 'invoke'
        }
    )
    data = response.json()
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600) - 300
    return _token_cache["token"]

def transform_openai_to_agentcore(openai_request):
    """Transform OpenAI chat format to AgentCore format"""
    messages = openai_request.get("messages", [])
    latest_message = messages[-1]["content"] if messages else ""

    return {"prompt": latest_message}

def transform_agentcore_to_openai(agentcore_response, model, request_id):
    """Transform AgentCore response to OpenAI format"""
    return {
        "id": request_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": agentcore_response.get("result", "")
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }

def lambda_handler(event, context):
    """Lambda handler for OpenAI-compatible API"""
    try:
        # Parse OpenAI request
        body = json.loads(event['body'])

        # Generate request ID
        request_id = f"chatcmpl-{context.request_id}"

        # Transform to AgentCore format
        agentcore_payload = transform_openai_to_agentcore(body)

        # Get OAuth token
        token = get_oauth_token()

        # Invoke AgentCore
        runtime_url = f"https://bedrock-agentcore.{os.environ['AWS_REGION']}.amazonaws.com/runtimes/{AGENTCORE_RUNTIME_ARN}/invocations"

        response = httpx.post(
            runtime_url,
            headers={
                "Authorization": f"Bearer {token}",
                "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": f"session-{request_id}",
                "Content-Type": "application/json"
            },
            json=agentcore_payload,
            timeout=60.0
        )
        agentcore_result = response.json()

        # Transform to OpenAI format
        openai_response = transform_agentcore_to_openai(
            agentcore_result,
            body.get("model", "agentcore-agent"),
            request_id
        )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(openai_response)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "error": {
                    "message": str(e),
                    "type": "internal_server_error"
                }
            })
        }
```

**Step 3: Deploy Lambda**

```bash
# Create deployment package
cd lambda
pip install httpx -t .
zip -r function.zip .

# Deploy
aws lambda create-function \
  --function-name agentcore-openai-proxy \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT:role/LambdaExecutionRole \
  --handler openai_proxy.lambda_handler \
  --zip-file fileb://function.zip \
  --environment Variables="{
    AGENTCORE_RUNTIME_ARN=arn:aws:bedrock-agentcore:us-west-2:ACCOUNT:runtime/agent,
    OAUTH_TOKEN_ENDPOINT=https://your-cognito.auth.us-west-2.amazoncognito.com/oauth2/token,
    CLIENT_ID=your-client-id,
    CLIENT_SECRET=your-client-secret,
    AWS_REGION=us-west-2
  }" \
  --timeout 60
```

**Step 4: Create API Gateway**

```bash
# Create REST API
aws apigateway create-rest-api \
  --name "AgentCore OpenAI Proxy" \
  --description "OpenAI-compatible API for AgentCore agents"

# Create API key
aws apigateway create-api-key \
  --name "MyAPIKey" \
  --enabled

# Link Lambda to API Gateway
# Configure /v1/chat/completions endpoint
# Enable API key requirement
```

**Step 5: Test with OpenAI SDK**

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-api-id.execute-api.us-west-2.amazonaws.com/v1",
    api_key="your-api-key-from-gateway"
)

response = client.chat.completions.create(
    model="agentcore-agent",
    messages=[
        {"role": "user", "content": "Search bucket test-data for reports"}
    ]
)

print(response.choices[0].message.content)
```

### API Key Management

**Create usage plan:**
```bash
aws apigateway create-usage-plan \
  --name "Standard" \
  --throttle rate-limit=100,burst-limit=200 \
  --quota limit=10000,period=DAY
```

**Associate API key:**
```bash
aws apigateway create-usage-plan-key \
  --usage-plan-id abcd1234 \
  --key-id your-api-key-id \
  --key-type API_KEY
```

---

## Complete Production Deployment Roadmap

### Phase-by-Phase Implementation

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: LOCAL DEVELOPMENT (Days 1-3)                      │
├─────────────────────────────────────────────────────────────┤
│ ✓ Create standalone Strands agent                          │
│ ✓ Add S3 search tools with boto3                           │
│ ✓ Test with real S3 (use test bucket)                      │
│ ✓ Add unit tests with moto                                 │
│ ✓ Verify all tools work correctly                          │
│ ✓ Add skills (.md files) if using                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: AGENTCORE WRAPPER (Day 4)                         │
├─────────────────────────────────────────────────────────────┤
│ ✓ Add BedrockAgentCoreApp wrapper                          │
│ ✓ Add @app.entrypoint decorator                            │
│ ✓ Test with 'agentcore dev' (hot reload)                   │
│ ✓ Verify behavior matches local                            │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: MANUAL DEPLOYMENT (Day 5)                         │
├─────────────────────────────────────────────────────────────┤
│ ✓ Run 'agentcore configure'                                │
│ ✓ Deploy with 'agentcore deploy'                           │
│ ✓ Test deployed agent                                      │
│ ✓ Verify CloudWatch logs                                   │
│ ✓ Document deployment process                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: CI/CD SETUP (Week 2)                              │
├─────────────────────────────────────────────────────────────┤
│ ✓ Create GitHub Actions workflow                           │
│ ✓ Set up AWS OIDC provider                                 │
│ ✓ Configure IAM role for GitHub Actions                    │
│ ✓ Test automated deployment                                │
│ ✓ Add deployment validation                                │
│ ✓ Set up rollback strategy                                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: API GATEWAY (Week 3 - Optional)                   │
├─────────────────────────────────────────────────────────────┤
│ ✓ Deploy agent with OAuth                                  │
│ ✓ Create Lambda proxy function                             │
│ ✓ Set up API Gateway                                       │
│ ✓ Configure API key authentication                         │
│ ✓ Test with OpenAI SDK                                     │
│ ✓ Add monitoring and alerts                                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 6: PRODUCTION HARDENING (Week 4)                     │
├─────────────────────────────────────────────────────────────┤
│ ✓ Load testing                                             │
│ ✓ Security review                                          │
│ ✓ Documentation complete                                   │
│ ✓ Runbooks created                                         │
│ ✓ Monitoring dashboards                                    │
│ ✓ Cost optimization                                        │
└─────────────────────────────────────────────────────────────┘
```

### Recommended Timeline

- **Week 1:** Local development + first deployment
- **Week 2:** CI/CD automation
- **Week 3:** API Gateway (if needed)
- **Week 4:** Production hardening
- **Total:** 4 weeks to production-ready system

---

## Summary

### Key Answers to Your Questions

**1. Local Development First?**
✅ **YES - Highly recommended!**
- Develop with pure Strands locally
- Test with real or mocked S3
- Add AgentCore wrapper when ready
- Only 4 lines of code difference

**2. GitHub Actions for CI/CD?**
✅ **YES - Fully supported!**
- Use `--non-interactive` and `--auto-update-on-conflict`
- AWS OIDC (no secrets needed!)
- Direct Code Deploy = 3-5 min deployments
- Container mode also supported

**3. OpenAI-Compatible API?**
✅ **YES - Via API Gateway + Lambda proxy**
- AgentCore supports OAuth 2.0
- Lambda transforms OpenAI ↔ AgentCore formats
- API Gateway handles simple API key auth
- Works with OpenAI SDK

### Files Created
- `PRODUCTION_DEPLOYMENT_GUIDE.md` (this file)
- Updated `PDR_AGENTIC_S3_SEARCH.md` with production sections
- GitHub Actions workflow examples
- Lambda proxy code examples
- Config-driven multi-environment setup

**All research complete and documented!**
