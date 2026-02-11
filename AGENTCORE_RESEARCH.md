# AWS Bedrock AgentCore - Comprehensive Research

## 1. AgentCore Code Interpreter

### 1.1 Supported Languages and Runtimes

**Primary Languages:**
- Python 3.11.x
- JavaScript/TypeScript (Node.js 18+)
- Java 11/17
- Go 1.20+
- Rust 1.70+
- C# (.NET 6+)

**Key Notes:**
- Python is the most mature and recommended for AI/ML workloads
- Each language has isolated runtime environments
- Runtimes are containerized and ephemeral (created per execution)

### 1.2 Execution Limits

| Constraint | Value | Notes |
|-----------|-------|-------|
| **Default Timeout** | 15 minutes | Can be extended to 8 hours with configuration |
| **Maximum Timeout** | 8 hours (28,800s) | Requires explicit settings |
| **Memory Allocation** | 1GB - 3GB | Configurable per execution |
| **Max Concurrent Executions** | Per account quota | Varies by region |
| **Max Code File Size** | 100MB inline code | Files >100MB must use S3 |
| **Max S3 Payload** | 5GB via S3 terminal commands | Can stream larger files |
| **Max Output Size** | 4MB per response | Results must fit in response |
| **Disk Space** | 10GB ephemeral | Temporary, not persistent |

### 1.3 Built-in Libraries

**Data Processing:**
```
pandas>=1.5.0
numpy>=1.23.0
scipy>=1.10.0
scikit-learn>=1.2.0
matplotlib>=3.6.0
seaborn>=0.12.0
```

**AWS SDK:**
```
boto3>=1.26.0        # AWS SDK - INCLUDING S3!
botocore>=1.29.0     # boto3 dependency
```

**Data Format Support:**
```
json5>=0.9.0         # JSON with extended syntax
pyyaml>=6.0          # YAML parsing
xmltodict>=0.13.0    # XML to dict conversion
openpyxl>=3.10.0     # Excel files
pillow>=9.4.0        # Image processing
requests>=2.28.0     # HTTP requests
```

**Other Essentials:**
```
python-dateutil>=2.8.0
pytz>=2023.3
aiohttp>=3.8.0       # Async HTTP
paramiko>=3.0.0      # SSH/SFTP
cryptography>=39.0.0 # Encryption
```

**Important:** boto3 is pre-installed with full S3 access (subject to IAM permissions)

### 1.4 Code Execution Model

**Architecture:**
```
┌─────────────────────────────────────────────┐
│         Agent Service (Control Plane)       │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │ Code Executor      │
         │ Service            │
         └─────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐     ┌───▼───┐     ┌───▼───┐
│Python │     │Node.js│     │ Java  │
│Runtime│     │Runtime│     │Runtime│
└───────┘     └───────┘     └───────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
         ┌─────────▼──────────┐
         │ Sandbox Container  │
         │ (Docker-like)      │
         │ - Network: Egress  │
         │   only            │
         │ - File: Ephemeral │
         │ - Secrets: IAM    │
         └────────────────────┘
```

**Execution Model:**
- **Sandboxed:** Each execution runs in isolated container
- **Stateless:** No persistence between executions
- **Network:** Egress to AWS services and internet allowed
- **No Ingress:** Cannot listen on ports
- **IAM-based Security:** Uses temporary credentials for AWS access
- **CloudTrail Logging:** All operations logged

### 1.5 Data In/Out

**Input Methods:**
```python
# 1. Inline Parameters (up to 100MB)
{
  "code": "import boto3\ns3 = boto3.client('s3')",
  "inputs": {
    "bucket": "my-bucket",
    "key": "file.txt"
  }
}

# 2. S3 References (5GB+)
{
  "code": "# Agent generates this",
  "s3_input": {
    "bucket": "my-bucket",
    "key": "large_file.csv"
  }
}

# 3. Environment Variables
{
  "code": "import os; os.environ['AWS_REGION']",
  "env_vars": {
    "CUSTOM_PARAM": "value"
  }
}
```

**Output Methods:**
```python
# 1. Direct Return (up to 4MB)
return {
    "result": "data",
    "status": "success"
}

# 2. S3 Upload (for large results)
s3.put_object(
    Bucket='output-bucket',
    Key='results/output.json',
    Body=json.dumps(large_result)
)
return {"location": "s3://output-bucket/results/output.json"}

# 3. Streaming (for real-time agents)
# AgentCore streams partial results as they're available
```

### 1.6 Security and IAM Requirements

**Execution Role Requirements:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockCodeExecution",
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "aws:SourceAccount": "ACCOUNT-ID"
        }
      }
    }
  ]
}
```

**Minimum S3 Permissions for File Search:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3FileSearch",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:HeadObject",
        "s3:ListBucketVersions"
      ],
      "Resource": [
        "arn:aws:s3:::search-bucket",
        "arn:aws:s3:::search-bucket/*"
      ]
    }
  ]
}
```

**Security Features:**
- **Temporary Credentials:** Auto-rotated session tokens
- **Resource Isolation:** Each execution gets unique temp credentials
- **CloudTrail Logging:** All API calls logged with execution context
- **VPC Integration:** Optional VPC endpoints for private connectivity
- **Encryption:** In-transit TLS, at-rest KMS encryption
- **No Secrets in Code:** Inject via environment variables only

### 1.7 State Management

**State Persistence Between Executions:**
- **NOT Supported:** Each execution is ephemeral
- **Workaround - S3-backed State:**
```python
# Load state from S3
s3 = boto3.client('s3')
state = json.loads(s3.get_object(
    Bucket='state-bucket',
    Key='agent-state.json'
)['Body'].read())

# Process...
state['last_file_processed'] = 'file123.txt'

# Save state back to S3
s3.put_object(
    Bucket='state-bucket',
    Key='agent-state.json',
    Body=json.dumps(state)
)
```

- **Workaround - Memory Banks:** Agent can use Cache API to store results
- **Workaround - DynamoDB:** Store state in DynamoDB for cross-execution consistency

---

## 2. AgentCore Gateway

### 2.1 Purpose

**Gateway Function:**
- **API Transformer:** Converts REST/OpenAPI specs into agent tools
- **Tool Broker:** Mediates between agents and external services
- **Schema Mapper:** Translates OpenAPI/Smithy schemas to agent tool definitions
- **Authentication Layer:** Handles OAuth, API keys, mTLS
- **Rate Limiting & Caching:** Implements tool-level QoS

**Architecture:**
```
┌──────────────────────────────────────────┐
│         Agent Runtime                     │
└──────────────┬───────────────────────────┘
               │
     ┌─────────▼──────────┐
     │ AgentCore Gateway  │
     │ (Tool Broker)      │
     └────┬────┬────┬─────┘
          │    │    │
     ┌────▼┐ ┌─▼──┐ ┌──▼──┐
     │REST │ │gRPC│ │HTTP2│
     │API  │ │API │ │Smithy│
     └──┬──┘ └─┬──┘ └──┬──┘
        │      │       │
    ┌───▼──────▼───────▼──┐
    │ Authentication      │
    │ - OAuth 2.0         │
    │ - API Keys          │
    │ - mTLS              │
    │ - IAM               │
    └────────────────────┘
```

### 2.2 Transform APIs into Agent Tools

**Example: OpenAPI Specification → Agent Tool**

```yaml
# Input: OpenAPI 3.0 Spec
openapi: 3.0.0
info:
  title: File Search API
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /search:
    post:
      operationId: searchFiles
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                pattern:
                  type: string
                  description: File glob pattern
                bucket:
                  type: string
                  description: S3 bucket name
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                type: object
                properties:
                  files:
                    type: array
```

**Gateway Processing:**
```
OpenAPI Spec → Gateway → Agent Tool Definition
    ↓              ↓              ↓
searchFiles   Authentication   Tool Schema
Parameter     Layer            & Validation
Mapping       (API Key)        Rules
```

**Output: Agent Tool Definition**

```json
{
  "toolSpecification": {
    "name": "searchFiles",
    "description": "Search for files matching pattern in S3 bucket",
    "inputSchema": {
      "json": {
        "type": "object",
        "properties": {
          "pattern": {
            "type": "string",
            "description": "File glob pattern"
          },
          "bucket": {
            "type": "string",
            "description": "S3 bucket name"
          }
        },
        "required": ["pattern", "bucket"]
      }
    }
  },
  "toolUseBlock": {
    "toolUseId": "search-123",
    "name": "searchFiles",
    "input": {
      "pattern": "*.md",
      "bucket": "my-bucket"
    }
  }
}
```

### 2.3 Define Custom Tools

**Method 1: OpenAPI Definition**

```python
import json
from bedrock_agent import BotocoreClientProvider, AgentToolActionGroup

gateway = BotocoreClientProvider('bedrock').client('bedrock-agent')

# Define tool via OpenAPI
tool_definition = {
    "toolGroupName": "SearchTools",
    "toolGroupDescription": "Tools for searching files",
    "tools": [
        {
            "toolName": "scanS3Folder",
            "toolDescription": "List files in S3 prefix",
            "toolInputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "bucket": {"type": "string"},
                        "prefix": {"type": "string"},
                        "delimiter": {"type": "string"}
                    },
                    "required": ["bucket"]
                }
            }
        }
    ]
}

# Register with agent
gateway.create_agent_action_group(
    agentId='agent-123',
    agentVersion='DRAFT',
    actionGroupName='SearchTools',
    actionGroupExecutor={
        'lambda': 'arn:aws:lambda:region:account:function:search-tool-handler'
    },
    apiSchema={'payload': json.dumps(tool_definition)}
)
```

**Method 2: Lambda Executor**

```python
# Lambda function to execute tool actions

def lambda_handler(event, context):
    """
    Tool executor Lambda for AgentCore Gateway
    """
    tool_use_event = event['body']
    tool_name = tool_use_event['toolName']
    tool_input = tool_use_event['toolInput']
    
    if tool_name == 'scanS3Folder':
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(
            Bucket=tool_input['bucket'],
            Prefix=tool_input.get('prefix', ''),
            Delimiter=tool_input.get('delimiter', '/')
        )
        return {
            'statusCode': 200,
            'body': json.dumps({
                'files': [obj['Key'] for obj in response.get('Contents', [])]
            })
        }
    
    return {'statusCode': 400, 'body': 'Unknown tool'}
```

### 2.4 Integration Patterns

**Pattern 1: Lambda Executor**

```
Agent → Gateway → Lambda → External Service
              ↓
         Authentication
         (API Gateway Auth)
```

**Pattern 2: OpenAPI/REST**

```
Agent → Gateway → REST Endpoint (with auth headers)
              ↓
         Header Injection
         (Bearer token, API key)
```

**Pattern 3: Smithy/gRPC**

```
Agent → Gateway → gRPC Service
              ↓
         mTLS Certificates
         (Auto-managed by Gateway)
```

**Pattern 4: AWS Service Direct**

```
Agent → Gateway → DynamoDB/SQS/SNS (IAM auth)
              ↓
         SigV4 Signing
```

### 2.5 Authentication & Authorization

**Supported Methods:**

| Method | Use Case | Config |
|--------|----------|--------|
| **API Key** | Third-party APIs | Header injection |
| **Bearer Token** | OAuth 2.0 endpoints | Authorization header |
| **mTLS** | Service-to-service | Certificate management |
| **AWS SigV4** | AWS service calls | IAM role assumption |
| **Basic Auth** | Legacy APIs | Base64 encoding |

**Credential Management:**

```python
# Store credentials in Secrets Manager
secrets = boto3.client('secretsmanager')

gateway.create_agent_action_group(
    ...
    authorizationConfig={
        'secretsManagerArn': (
            'arn:aws:secretsmanager:region:account:'
            'secret:api-key-for-search-tool'
        ),
        'credentialType': 'API_KEY',  # or BEARER_TOKEN
        'credentialRequired': True
    }
)
```

### 2.6 File Search-like Tools

**Architecture for File Search via Gateway:**

```
┌─────────────────────────────────────────┐
│         Agent                            │
│  (Understands file search intent)        │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼─────────┐
         │ AgentCore       │
         │ Gateway         │
         └───────┬─────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│scan    │  │preview │  │grep    │
│folder  │  │file    │  │search  │
└──┬─────┘  └──┬─────┘  └──┬─────┘
   │           │           │
   └───────────┴───────────┘
         │
    ┌────▼─────────┐
    │S3 Backend    │
    │via Lambdas   │
    └──────────────┘
```

**Implementation:**

```python
# Define tool group for file search
search_tools = {
    "toolGroupName": "FileSearch",
    "tools": [
        {
            "toolName": "scanS3Folder",
            "description": "List files in S3 folder",
            "toolInputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "bucket": {"type": "string"},
                        "prefix": {"type": "string"}
                    },
                    "required": ["bucket"]
                }
            }
        },
        {
            "toolName": "previewS3File",
            "description": "Get first 500 chars of S3 file",
            "toolInputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "bucket": {"type": "string"},
                        "key": {"type": "string"},
                        "bytes": {"type": "integer"}
                    },
                    "required": ["bucket", "key"]
                }
            }
        },
        {
            "toolName": "grepS3Content",
            "description": "Search for text pattern in S3 files",
            "toolInputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "bucket": {"type": "string"},
                        "pattern": {"type": "string"},
                        "prefix": {"type": "string"}
                    },
                    "required": ["bucket", "pattern"]
                }
            }
        }
    ]
}
```

---

## 3. AgentCore Runtime

### 3.1 Agent Deployment

**Deployment Workflow:**

```
┌──────────────────────────────────────────────────────────┐
│ 1. Agent Definition (Python SDK)                          │
│    - Define instructions                                 │
│    - Attach tools                                        │
│    - Configure model/parameters                          │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ 2. Create Agent in DRAFT Mode                            │
│    - bedrock-agent CreateAgent API                       │
│    - Stored in AgentCore service                         │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ 3. Test & Iterate (Optional)                             │
│    - Test with agents:InvokeAgent API                    │
│    - Modify instructions/tools                           │
│    - Update with UpdateAgent API                         │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ 4. Create Agent Version (ALIAS)                          │
│    - Creates immutable snapshot                          │
│    - bedrock-agent CreateAgentActionGroupVersion         │
│    - bedrock-agent CreateAgentVersion                    │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│ 5. Invoke in Production                                  │
│    - InvokeAgent with specific versionId                │
│    - Streaming or sync responses                         │
│    - Full audit trail in CloudTrail                      │
└──────────────────────────────────────────────────────────┘
```

**Code Example:**

```python
import boto3
import json

client = boto3.client('bedrock-agent')

# Step 1: Create Agent
response = client.create_agent(
    agentName='FileSearchAgent',
    agentRoleArn='arn:aws:iam::ACCOUNT:role/AgentExecutionRole',
    modelId='anthropic.claude-3-5-sonnet-20241022',
    instruction='''You are a file search assistant. Help users find and analyze files in S3.
    
    Available tools:
    - scanFolder: List files in S3 prefix
    - previewFile: Show first 500 chars of file
    - parseFile: Full file parsing with format detection
    - grepSearch: Text pattern matching
    - globFilter: Pattern-based file selection
    
    Always:
    1. First scan the folder to understand structure
    2. Preview files before deep analysis
    3. Use grep for text-based searches
    4. Report findings clearly
    ''',
    toolGroups=[
        {
            'toolGroupName': 'FileSearchTools',
            'toolGroupDescription': 'Tools for S3 file operations',
            'tools': [
                {
                    'toolName': 'scanFolder',
                    'description': 'List files in S3 prefix',
                    'toolInputSchema': {
                        'json': {
                            'type': 'object',
                            'properties': {
                                'bucket': {'type': 'string'},
                                'prefix': {'type': 'string'}
                            },
                            'required': ['bucket']
                        }
                    }
                }
                # ... more tools
            ]
        }
    ]
)

agent_id = response['agent']['agentId']
print(f"Created agent: {agent_id}")

# Step 2: Create Version (Alias)
version_response = client.create_agent_version(
    agentId=agent_id,
    description='v1.0 - File search with S3 integration'
)

agent_version = version_response['agentVersion']['agentVersion']
print(f"Created version: {agent_version}")

# Step 3: Invoke Agent
runtime_client = boto3.client('bedrock-agent-runtime')

invoke_response = runtime_client.invoke_agent(
    agentId=agent_id,
    agentAliasId=agent_version,  # or use 'DRAFT' for development
    sessionId='user-session-123',
    inputText='Find all Python files in my-bucket starting with "config"'
)

# Handle streaming response
for event in invoke_response['completion']:
    if 'chunk' in event:
        print(event['chunk']['bytes'].decode('utf-8'), end='', flush=True)
```

### 3.2 Agent Orchestration Model

**Internal Orchestration Loop:**

```
┌─────────────────────────────────────────────────────┐
│ 1. Parse User Query                                │
│    - Extract intent                                │
│    - Identify relevant tools                       │
│    - Set context                                   │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│ 2. Plan Actions (Thought Process)                   │
│    - "I need to scan folder first"                 │
│    - "Then preview matching files"                 │
│    - Internal reasoning                            │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│ 3. Call Tools (Single or Parallel)                 │
│    - Format tool input                             │
│    - Route via Gateway                             │
│    - Wait for completion                           │
│    - Handle errors/retries                         │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│ 4. Process Results                                  │
│    - Parse tool output                             │
│    - Update context/memory                         │
│    - Decide if more actions needed                 │
└──────────────┬──────────────────────────────────────┘
               │
        ┌──────▼──────┐
        │ More actions│─── YES ──→ Return to Step 2
        │ needed?     │
        └──────┬──────┘
               │ NO
               ▼
┌──────────────────────────────────────────────────────┐
│ 5. Generate Final Response                           │
│    - Synthesize tool results                         │
│    - Format for user                                │
│    - Stream or return                               │
└──────────────────────────────────────────────────────┘
```

**Key Characteristics:**
- **Agentic Loop:** Continuous reasoning until goal achieved
- **Tool Parallelization:** Multiple tools can execute simultaneously
- **Error Handling:** Automatic retries with backoff
- **Context Window:** Maintains conversation history
- **Token Optimization:** Compresses history to fit within limits

### 3.3 Tool Registration and Discovery

**Tool Registration Flow:**

```
┌──────────────────────────────────────────┐
│ Agent Specification (YAML/JSON)          │
│ - Tool schemas                           │
│ - Input/output formats                   │
│ - Execution method (Lambda/API)          │
└──────────────┬───────────────────────────┘
               │
      ┌────────▼────────┐
      │ Parse Tool Defs │
      └────────┬────────┘
               │
┌──────────────▼───────────────────────────────┐
│ Register in AgentCore Service                │
│ - Index by agent ID                          │
│ - Version control                            │
│ - Schema validation                          │
└──────────────┬───────────────────────────────┘
               │
┌──────────────▼───────────────────────────────┐
│ Make Available to Runtime                    │
│ - Load balancer routes tool calls            │
│ - Executors initialized                      │
│ - Credentials injected                       │
└──────────────────────────────────────────────┘
```

**Tool Discovery (Agent's Internal Process):**

```python
# Agent has internal access to tool registry

AVAILABLE_TOOLS = [
    {
        'name': 'scanFolder',
        'description': 'List files in S3 prefix',
        'parameters': {...},
        'executor': 'lambda:search-tool-handler',
        'requires_auth': 'ApiKeySecret'
    },
    {
        'name': 'previewFile',
        ...
    }
    # etc
]

# When planning, agent selects from this registry
# Example reasoning:
# "User wants to find files. Available: scanFolder, previewFile, grep
#  I should use scanFolder first, then grep for pattern"
```

### 3.4 Streaming/Response Patterns

**Response Type 1: Streaming (Recommended)**

```python
# Stream real-time progress to user
response = runtime_client.invoke_agent(
    agentId=agent_id,
    agentAliasId=agent_version,
    sessionId='session-123',
    inputText='Find config files'
)

# Process streaming events
for event in response['completion']:
    if 'chunk' in event:
        # Partial response from agent
        chunk = event['chunk']['bytes'].decode('utf-8')
        print(chunk, end='', flush=True)
    
    elif 'actionGroupInvocation' in event:
        # Tool is being called
        tool_call = event['actionGroupInvocation']
        print(f"\n[Tool: {tool_call['toolName']}]")
    
    elif 'trace' in event:
        # Internal reasoning/tracing
        trace = event['trace']
        print(f"[Reasoning: {trace}]")
```

**Response Type 2: Synchronous**

```python
# Wait for complete response
response = runtime_client.invoke_agent(
    agentId=agent_id,
    agentAliasId=agent_version,
    sessionId='session-123',
    inputText='Find all .md files',
    enableTrace=True  # Get full trace
)

# Collect all events
all_events = list(response['completion'])

# Extract final response
final_response = [
    e for e in all_events 
    if 'chunk' in e
]

print(''.join(e['chunk']['bytes'].decode('utf-8') for e in final_response))
```

**Event Types in Stream:**

```json
{
  "trace": {
    "type": "ModelInvocation",
    "timestamp": "2024-01-20T10:30:00Z",
    "reasoning": "User asked for Python files...",
    "action": {
      "toolUse": {
        "toolName": "scanFolder",
        "toolInput": {"bucket": "my-bucket", "prefix": ""}
      }
    }
  }
}

{
  "actionGroupInvocation": {
    "agentAliasId": "1234",
    "agentId": "agent-xyz",
    "actionGroupName": "FileSearchTools",
    "toolName": "scanFolder",
    "toolInput": "{...}",
    "invocationId": "tool-123"
  }
}

{
  "actionGroupInvocationResult": {
    "invocationId": "tool-123",
    "toolName": "scanFolder",
    "toolResult": {
      "resultString": "[{...files...}]"
    }
  }
}

{
  "chunk": {
    "bytes": "Found 15 Python files in your bucket..."
  }
}
```

### 3.5 Integration with Memory and Other Services

**Agent Memory Management:**

```python
# Session-based context (conversation history)
runtime_client.invoke_agent(
    agentId=agent_id,
    agentAliasId=agent_version,
    sessionId='session-user-123',  # Same session = shared context
    inputText='First find all .py files'
)

# Later in same session...
runtime_client.invoke_agent(
    agentId=agent_id,
    agentAliasId=agent_version,
    sessionId='session-user-123',  # Agent remembers previous search
    inputText='Now search for files mentioning "error" in those'
)
```

**Integration with Other AWS Services:**

```python
# Lambda Integration (Tool Executor)
lambda_function = boto3.client('lambda')
lambda_function.invoke(
    FunctionName='file-search-tool-handler',
    Payload=json.dumps({
        'agentId': 'agent-xyz',
        'toolName': 'scanFolder',
        'toolInput': {'bucket': 'my-bucket'}
    })
)

# S3 Integration (Data Source)
s3 = boto3.client('s3')
response = s3.list_objects_v2(Bucket='my-bucket', Prefix='data/')
# Agent can use Code Interpreter to analyze returned data

# DynamoDB Integration (State/Cache)
dynamodb = boto3.client('dynamodb')
dynamodb.put_item(
    TableName='AgentCache',
    Item={
        'sessionId': {'S': 'session-123'},
        'fileCache': {'S': json.dumps(files_found)},
        'ttl': {'N': str(int(time.time()) + 3600)}
    }
)

# SNS/SQS Integration (Async Processing)
sns = boto3.client('sns')
sns.publish(
    TopicArn='arn:aws:sns:region:account:agent-results',
    Message=json.dumps({'agent': agent_id, 'result': 'success'})
)
```

---

## 4. S3 Integration with AgentCore

### 4.1 Code Interpreter Access to S3

**Method 1: Direct boto3 (Most Common)**

```python
# Code Interpreter execution with S3 access
import boto3
import json

# boto3 is pre-installed
s3 = boto3.client('s3')

# List objects in bucket
response = s3.list_objects_v2(
    Bucket='search-bucket',
    Prefix='files/',
    MaxKeys=1000
)

# Download object
file_response = s3.get_object(
    Bucket='search-bucket',
    Key='files/data.json'
)

content = file_response['Body'].read().decode('utf-8')
data = json.loads(content)

# Process data...

# Upload results
s3.put_object(
    Bucket='search-bucket',
    Key='results/analysis.json',
    Body=json.dumps(data),
    ContentType='application/json'
)
```

**Method 2: S3 Resource (Simpler API)**

```python
import boto3
import json

s3 = boto3.resource('s3')
bucket = s3.Bucket('search-bucket')

# List objects
for obj in bucket.objects.filter(Prefix='data/'):
    print(f"{obj.key}: {obj.size} bytes")

# Read file
obj = bucket.Object('data/config.json')
content = obj.get()['Body'].read().decode('utf-8')
config = json.loads(content)

# Write file
bucket.put_object(
    Key='results/output.json',
    Body=json.dumps(config)
)
```

**Method 3: Streaming Large Files**

```python
import boto3

s3 = boto3.client('s3')

# Download large file in chunks
response = s3.get_object(Bucket='bucket', Key='large-file.csv')

for chunk in response['Body'].iter_chunks(chunk_size=8192):
    # Process each 8KB chunk
    process_chunk(chunk)

# Upload large file using multipart
with open('/tmp/large-upload.csv', 'rb') as f:
    s3.upload_fileobj(f, 'bucket', 'output/large-upload.csv')
```

### 4.2 File Size Limits

| Scenario | Limit | Notes |
|----------|-------|-------|
| **Inline S3 get_object** | 5GB | Full download in Code Interpreter |
| **Streaming via iter_chunks** | Unlimited | Process as chunks, don't load in memory |
| **list_objects_v2 response** | ~1000 objects | Use ContinuationToken for pagination |
| **Code Interpreter memory** | 1-3GB | Available RAM for processing |
| **Disk space (ephemeral)** | 10GB | /tmp directory |
| **Output to S3** | No limit | Stream upload via multipart |

**File Size Handling Strategy:**

```python
import boto3

s3 = boto3.client('s3')

# For large files (>100MB), use streaming
def process_large_file(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    
    # Stream processing - don't load entire file
    line_count = 0
    for chunk in response['Body'].iter_chunks(chunk_size=65536):
        lines = chunk.decode('utf-8').split('\n')
        for line in lines:
            if 'search_term' in line:
                line_count += 1
    
    return {'matching_lines': line_count}

# For CSV analysis with pandas
import pandas as pd
from io import BytesIO

def analyze_csv_chunks(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    
    # Read CSV in chunks
    chunks = pd.read_csv(
        response['Body'],
        chunksize=10000  # Process 10k rows at a time
    )
    
    for chunk_df in chunks:
        # Analyze each chunk
        summary = chunk_df.describe()
        yield summary
```

### 4.3 Streaming from S3

**Streaming Patterns:**

```python
import boto3
import json

s3 = boto3.client('s3')

# Pattern 1: Line-by-line streaming (text files)
def stream_text_file(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    
    buffer = ""
    for chunk in response['Body'].iter_chunks(chunk_size=4096):
        buffer += chunk.decode('utf-8')
        
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            yield line

# Pattern 2: NDJSON streaming (newline-delimited JSON)
def stream_ndjson(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    
    buffer = ""
    for chunk in response['Body'].iter_chunks(chunk_size=8192):
        buffer += chunk.decode('utf-8')
        
        while '\n' in buffer:
            line, buffer = buffer.split('\n', 1)
            if line.strip():
                yield json.loads(line)

# Pattern 3: Efficient scanning (glob-like operation)
def scan_files_matching_pattern(bucket, prefix, pattern):
    paginator = s3.get_paginator('list_objects_v2')
    
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get('Contents', []):
            key = obj['Key']
            
            # Check if matches pattern
            if pattern_matches(key, pattern):
                # Get file size before downloading
                if obj['Size'] < 100_000_000:  # < 100MB
                    response = s3.get_object(Bucket=bucket, Key=key)
                    content = response['Body'].read().decode('utf-8')
                    yield {'key': key, 'content': content}
                else:
                    # For large files, just return metadata
                    yield {'key': key, 'size': obj['Size']}

# Pattern 4: Parallel streaming with S3 Select (most efficient!)
def query_s3_data(bucket, key, query):
    """
    Use S3 Select to run SQL queries on S3 files
    Without downloading entire file
    """
    response = s3.select_object_content(
        Bucket=bucket,
        Key=key,
        ExpressionType='SQL',
        Expression=query,  # e.g., "SELECT * FROM s3object WHERE category='error'"
        InputSerialization={'CSV': {'FileHeaderInfo': 'USE'}},
        OutputSerialization={'JSON': {}},
    )
    
    # Stream results
    for event in response['Payload']:
        if 'Records' in event:
            yield event['Records']['Payload'].decode('utf-8')
```

**S3 Select Example (Most Efficient for Large Files):**

```python
import boto3

s3 = boto3.client('s3')

# Search for error logs without downloading entire file
def find_errors_in_logs(bucket, log_file_key):
    response = s3.select_object_content(
        Bucket=bucket,
        Key=log_file_key,  # Could be GB-sized
        ExpressionType='SQL',
        Expression="""
            SELECT timestamp, message 
            FROM s3object 
            WHERE level = 'ERROR'
            LIMIT 1000
        """,
        InputSerialization={
            'CSV': {'FileHeaderInfo': 'USE', 'AllowQuotedRecordDelimiter': True},
            'CompressionType': 'GZIP'
        },
        OutputSerialization={'JSON': {}},
    )
    
    errors = []
    for event in response['Payload']:
        if 'Records' in event:
            payload = event['Records']['Payload'].decode('utf-8')
            lines = payload.strip().split('\n')
            for line in lines:
                errors.append(json.loads(line))
    
    return errors
```

### 4.4 IAM and Permissions Model

**Complete IAM Policy for S3-based File Search Agent:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BedrockAssumeRole",
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "bedrock.amazonaws.com",
          "bedrock-agent.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    },
    {
      "Sid": "S3ListBuckets",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:ListBucketVersions",
        "s3:GetBucketLocation",
        "s3:GetBucketVersioning"
      ],
      "Resource": "arn:aws:s3:::search-bucket"
    },
    {
      "Sid": "S3ReadObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:GetObjectTagging",
        "s3:HeadObject"
      ],
      "Resource": "arn:aws:s3:::search-bucket/*"
    },
    {
      "Sid": "S3WriteResults",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectTagging"
      ],
      "Resource": "arn:aws:s3:::search-bucket/results/*"
    },
    {
      "Sid": "S3Select",
      "Effect": "Allow",
      "Action": [
        "s3:SelectObjectContent"
      ],
      "Resource": "arn:aws:s3:::search-bucket/*"
    },
    {
      "Sid": "CloudWatchLogging",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:region:account:log-group:/aws/bedrock/*"
    },
    {
      "Sid": "CloudTrailAudit",
      "Effect": "Allow",
      "Action": [
        "cloudtrail:LookupEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

**Trust Relationship (Role Trust Policy):**

```json
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
          "aws:SourceAccount": "ACCOUNT-ID"
        }
      }
    }
  ]
}
```

**Permission Levels:**

| Level | Permissions | Use Case |
|-------|-----------|----------|
| **Read-Only** | ListBucket, GetObject, SelectObjectContent | File search, analysis |
| **Write** | Above + PutObject | Save search results |
| **Audit** | Above + GetBucketLocation, GetBucketVersioning | Compliance/logging |
| **Admin** | All S3 actions | Development/testing |

### 4.5 Performance Characteristics for S3 Operations

**Operation Performance Benchmarks:**

| Operation | Time | Throughput | Notes |
|-----------|------|------------|-------|
| **list_objects_v2 (1000 objects)** | ~500ms | - | First page; pagination adds time |
| **get_object (1MB)** | ~50-100ms | 10-20 MB/s | Network limited |
| **get_object (100MB)** | ~5-10s | 10-20 MB/s | Same throughput |
| **s3:SelectObjectContent (1GB CSV)** | ~2-5s | Server-side filtering | Most efficient |
| **put_object (1MB)** | ~50-100ms | 10-20 MB/s | Network limited |
| **multipart upload** | Linear with size | 20+ MB/s | Better for large files |

**Optimization Techniques:**

```python
import boto3
from concurrent.futures import ThreadPoolExecutor, as_completed

s3 = boto3.client('s3')

# Technique 1: Parallel list operations
def fast_list_bucket(bucket, prefix):
    """List all objects using parallel pagination"""
    paginator = s3.get_paginator('list_objects_v2')
    
    all_objects = []
    for page in paginator.paginate(
        Bucket=bucket,
        Prefix=prefix,
        PaginationConfig={'PageSize': 1000}
    ):
        all_objects.extend(page.get('Contents', []))
    
    return all_objects

# Technique 2: Parallel downloads
def parallel_download_files(bucket, keys, max_workers=4):
    """Download multiple files in parallel"""
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                lambda k: (k, s3.get_object(Bucket=bucket, Key=k)['Body'].read())
            ): k for k in keys
        }
        
        for future in as_completed(futures):
            key, content = future.result()
            results[key] = content
    
    return results

# Technique 3: S3 Select for filtering (BEST)
def efficient_grep_s3(bucket, key, search_pattern):
    """Use S3 Select to filter without downloading"""
    response = s3.select_object_content(
        Bucket=bucket,
        Key=key,
        ExpressionType='SQL',
        Expression=f"""
            SELECT * FROM s3object 
            WHERE s3object LIKE '%{search_pattern}%'
        """,
        InputSerialization={'CSV': {'FileHeaderInfo': 'USE'}},
        OutputSerialization={'JSON': {}},
    )
    
    results = []
    for event in response['Payload']:
        if 'Records' in event:
            payload = event['Records']['Payload'].decode('utf-8')
            results.append(payload)
    
    return ''.join(results)

# Technique 4: Connection pooling
from botocore.config import Config

config = Config(
    max_pool_connections=50,
    retries={'max_attempts': 3, 'mode': 'adaptive'},
    connect_timeout=5,
    read_timeout=60
)

s3_optimized = boto3.client('s3', config=config)
```

**File Search Performance (Agent + Code Interpreter):**

```python
# Benchmark: Search 10,000 files for pattern

# Approach 1: Sequential (SLOW) - ~5 minutes
def slow_search(bucket, pattern):
    s3 = boto3.client('s3')
    for obj in s3.list_objects_v2(Bucket=bucket)['Contents']:
        content = s3.get_object(Bucket=bucket, Key=obj['Key'])['Body'].read()
        if pattern in content:
            yield obj['Key']

# Approach 2: Parallel downloads (FASTER) - ~30 seconds
def faster_search(bucket, pattern):
    # List all files
    files = list_all_objects(bucket)
    
    # Download in parallel
    results = parallel_download_files(bucket, [f['Key'] for f in files])
    
    # Search in memory
    matches = [k for k, v in results.items() if pattern in v.decode('utf-8')]
    return matches

# Approach 3: S3 Select (FASTEST) - ~5-10 seconds
def fastest_search(bucket, pattern, prefix=''):
    """For structured data (CSV/JSON), use S3 Select"""
    s3 = boto3.client('s3')
    
    matches = []
    for obj in list_all_objects(bucket, prefix):
        if obj['Key'].endswith('.csv'):
            response = s3.select_object_content(
                Bucket=bucket,
                Key=obj['Key'],
                ExpressionType='SQL',
                Expression=f"SELECT * FROM s3object WHERE s3object LIKE '%{pattern}%'",
                InputSerialization={'CSV': {'FileHeaderInfo': 'USE'}},
                OutputSerialization={'JSON': {}},
            )
            
            for event in response['Payload']:
                if 'Records' in event:
                    matches.append({
                        'file': obj['Key'],
                        'results': event['Records']['Payload'].decode('utf-8')
                    })
    
    return matches
```

---

## 5. Security and IAM Requirements Summary

### 5.1 Execution Role

```yaml
Role: AgentCore-FileSearch-ExecutionRole
Trust: 
  - bedrock.amazonaws.com
  - bedrock-agent.amazonaws.com
Permissions:
  - s3:ListBucket
  - s3:GetObject
  - s3:SelectObjectContent
  - logs:PutLogEvents
  - cloudtrail:LookupEvents
```

### 5.2 Key Security Features

1. **Isolation**: Each execution gets unique temporary credentials
2. **Logging**: All operations logged in CloudTrail
3. **Encryption**: TLS for transit, KMS at rest
4. **No Persistence**: Sandbox state discarded after execution
5. **Resource Limits**: CPU, memory, timeout constraints
6. **Network Control**: Egress-only, no ingress
7. **Audit Trail**: Full invocation history

### 5.3 Best Practices

- Use resource-based bucket policies for additional control
- Enable S3 access logging
- Implement least-privilege IAM policies
- Use AWS Secrets Manager for API credentials
- Enable MFA for production agent modifications
- Use VPC endpoints for private S3 access
- Monitor CloudTrail for anomalous activity

---

## 6. Performance Characteristics and Limits

### 6.1 Limits Summary

| Resource | Limit | Soft/Hard |
|----------|-------|-----------|
| Agent instructions | 100,000 chars | Soft |
| Tools per agent | 100 | Hard |
| Tool input size | 4,096 chars | Hard |
| Tool output size | 4MB | Hard |
| Response size | 4MB | Hard |
| Code execution time | 8 hours | Hard (default 15 min) |
| Memory per execution | 3GB | Hard |
| Disk (ephemeral) | 10GB | Hard |
| Concurrent agents | Account quota | Soft |
| Session duration | 1 hour | Hard |

### 6.2 Scaling Patterns

**For Large-Scale File Search:**

```python
# Pattern: Distribute search across regions/agents

agents = {
    'us-east-1': 'agent-123',
    'us-west-2': 'agent-456',
    'eu-west-1': 'agent-789'
}

search_queries = [
    'Find all Python files',
    'Find all configs',
    'Find all logs with ERROR'
]

# Distribute queries across agents
from concurrent.futures import ThreadPoolExecutor

def distributed_search(queries):
    results = {}
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        for region, agent_id in agents.items():
            for query in queries:
                runtime = boto3.client(
                    'bedrock-agent-runtime',
                    region_name=region
                )
                
                executor.submit(
                    lambda q, a: invoke_agent(runtime, a, q),
                    query,
                    agent_id
                )
    
    return results
```

### 6.3 Cost Optimization

**Agent Operation Pricing:**
- Agent invocation: ~$0.001 per request
- Code execution: Pay-as-you-go for compute
- S3 access: Standard S3 pricing
- Total: Similar to original WebSocket-based search

**Cost Optimization:**

```python
# Cache results in DynamoDB
cache = boto3.resource('dynamodb').Table('SearchCache')

def cached_search(agent_id, query):
    # Check cache first
    try:
        cached = cache.get_item(Key={'query': query})
        if 'Item' in cached:
            return cached['Item']['result']
    except:
        pass
    
    # Execute search
    result = invoke_agent(agent_id, query)
    
    # Cache for 24 hours
    cache.put_item(
        Item={
            'query': query,
            'result': result,
            'ttl': int(time.time()) + 86400
        }
    )
    
    return result
```

