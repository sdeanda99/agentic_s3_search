# S3 Agent - Local Development

Skill-powered agentic S3 search agent for local development and testing.

## Features

- Code execution tool for running boto3 operations
- S3 interaction skill with 9 boto3 operations
- Hybrid skill approach (works with Claude and other AWS models)
- Two implementations: Pure Strands and AgentCore dev mode
- Config-based multi-environment setup
- Unit tests with moto (no AWS costs)

---

## Quick Start

### 1. AWS Setup (Run manually)

See `AWS_SETUP_COMMANDS.md` for commands to:
- Create S3 bucket
- Upload your test PDF
- Create IAM policy
- Configure AWS credentials

### 2. Install Dependencies (using uv)

```bash
cd s3-agent-local
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r requirements.txt
```

### 3. Configure Environment

Edit `.env.local`:
```bash
S3_BUCKET=agentic-search-test-bucket
AWS_REGION=us-west-2
MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0
ENV=local
```

### 4. Run Strands Agent (Fast Iteration)

```bash
python agent_strands.py
```

**Interactive mode:**
```
> List all files in my S3 bucket
> Show me files in test-documents/ folder
> Get metadata for the PDF file
> Preview the first 500 bytes
> quit
```

### 5. Run AgentCore Dev Mode (Hot Reload)

```bash
agentcore dev
```

**In another terminal:**
```bash
agentcore invoke --dev '{"prompt": "List all files in my S3 bucket"}'
agentcore invoke --dev '{"prompt": "Show metadata for the PDF in test-documents/"}'
agentcore invoke --dev '{"prompt": "Preview first 1KB of the PDF file"}'
```

**Edit files and they auto-reload!**

---

## Project Structure

```
s3-agent-local/
├── agent_strands.py              # Strands agent (fast iteration)
├── agent_agentcore.py            # AgentCore dev mode (hot reload)
├── config.py                     # Environment configuration
├── requirements.txt              # Dependencies
├── .env.local                    # Local settings (gitignored)
├── .gitignore                    # Git exclusions
├── AWS_SETUP_COMMANDS.md         # AWS CLI commands to run
├── README.md                     # This file
├── skills/
│   └── s3_interaction.md         # S3 skill with boto3 examples
└── tests/
    └── test_s3_ops.py            # Unit tests with moto
```

---

## Usage Examples

### Example 1: List Files

**Query:** "List all files in my S3 bucket"

**Agent will:**
1. Use code interpreter to execute `list_objects_v2()`
2. Parse results and format for display
3. Show file names, sizes, modified dates

### Example 2: Analyze PDF

**Query:** "What's the metadata for the PDF file in test-documents/?"

**Agent will:**
1. Use `head_object()` to get metadata
2. Show file size, type, last modified date
3. Provide summary

### Example 3: Preview File

**Query:** "Show me the first 500 bytes of the PDF file"

**Agent will:**
1. Use `get_object()` with Range header
2. Download only first 500 bytes
3. Display as hex or text

### Example 4: Search for Pattern

**Query:** "Find all files containing the word 'invoice'"

**Agent will:**
1. Use `list_objects_v2()` to get all files
2. Download each file with `get_object()`
3. Search with regex
4. Report matches

### Example 5: Upload File

**Query:** "Upload a file named 'summary.txt' with content 'Test summary'"

**Agent will:**
1. Use `put_object()` to upload
2. Confirm successful upload
3. Provide S3 URI

---

## Testing

### Run Unit Tests (Mocked S3)

```bash
pytest tests/test_s3_ops.py -v
```

**No AWS costs!** Tests use moto to mock S3.

### Test with Real S3

```bash
# Make sure AWS credentials are configured
source ./aws_login.sh  # Your auth script

# Run Strands agent
python agent_strands.py

# Try: "List files in agentic-search-test-bucket"
```

---

## Configuration

### Environment Variables

Set in `.env.local` or export:

| Variable | Description | Default |
|----------|-------------|---------|
| `S3_BUCKET` | S3 bucket name | agentic-search-test-bucket |
| `AWS_REGION` | AWS region | us-west-2 |
| `MODEL_ID` | Bedrock model ID | claude-3-7-sonnet |
| `ENV` | Environment (local/test/prod) | local |

### Multi-Environment Setup

**Test (with LocalStack):**
```bash
ENV=test python agent_strands.py
```

**Local (real AWS):**
```bash
ENV=local python agent_strands.py
```

---

## S3 Operations Supported

### Core Operations (6)

1. **scan_folder** - `list_objects_v2()` with pagination
2. **preview_file** - `get_object()` with Range header
3. **parse_file** - `get_object()` + JSON/CSV parsers
4. **read_file** - `get_object()` full download
5. **grep** - `get_object()` + regex search
6. **glob** - `list_objects_v2()` + fnmatch filter

### Advanced Operations (3)

7. **S3 Select** - `select_object_content()` for SQL queries on CSV/JSON
8. **Presigned URLs** - `generate_presigned_url()` for temporary sharing
9. **Multipart Upload** - `create_multipart_upload()` for large files

All operations have code examples in `skills/s3_interaction.md`

---

## How It Works

### Architecture

```
User Query
    ↓
Agent (Strands)
    ↓ Loaded from skills/s3_interaction.md
S3 Interaction Skill (teaches WHEN and HOW)
    ↓
Code Interpreter Tool (executes boto3)
    ↓
boto3 → AWS S3
```

### Skill-Powered Approach

The S3 skill (`skills/s3_interaction.md`) teaches the agent:
- **Strategic guidance:** When to use each S3 operation
- **Code templates:** Boto3 examples for all 9 operations
- **Error handling:** Common errors and solutions
- **Performance tips:** S3 Select, Range requests, pagination

The agent reads the skill, decides which operation to use, generates boto3 code, and executes it with the code interpreter.

### Hybrid System Prompt

```python
# The skill file is loaded and injected into system prompt
with open('skills/s3_interaction.md', 'r') as f:
    skill = f.read()

# Configuration is added
full_prompt = f"{skill}\n\nYour bucket: {config.bucket_name}"

# Agent uses this as system prompt
agent = Agent(system_prompt=full_prompt, tools=[code_interpreter])
```

**Benefits:**
- Works with any model (Claude, Titan, etc.)
- Easy to update skill without code changes
- Reusable across local and deployed agents

---

## Comparison: Strands vs AgentCore Dev

| Feature | agent_strands.py | agent_agentcore.py |
|---------|------------------|-------------------|
| **Execution** | `python agent_strands.py` | `agentcore dev` |
| **Hot Reload** | ❌ No (restart required) | ✅ Yes (auto-reload on save) |
| **Production-Like** | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Identical to prod |
| **Setup** | ✅ Simple | ⭐⭐⭐ Requires AgentCore CLI |
| **Speed** | ⚡ Instant start | 🐢 2-3 sec startup |
| **Debugging** | ✅ Print statements | ✅ CloudWatch-style logs |
| **Best For** | Quick iteration | Final validation before deploy |

**Recommendation:**
- Start with `agent_strands.py` for development
- Use `agentcore dev` before deploying to AWS

---

## Troubleshooting

### Issue: "NoCredentialsError"

**Solution:**
```bash
# Configure AWS credentials
source ./aws_login.sh

# Or
aws configure
```

### Issue: "AccessDenied" on S3 operations

**Solution:**
Check IAM permissions. Run:
```bash
aws s3 ls s3://agentic-search-test-bucket/
```

If this fails, IAM policy is not attached correctly.

### Issue: "No such file: skills/s3_interaction.md"

**Solution:**
Ensure you're running from the `s3-agent-local/` directory:
```bash
cd s3-agent-local
python agent_strands.py
```

### Issue: "Module not found: strands"

**Solution:**
Install dependencies:
```bash
uv pip install -r requirements.txt
```

---

## Next Steps

### After Local Testing

1. **Refine the skill** based on agent behavior
2. **Add organization-specific guidance** to skill file
3. **Test with real documents** in your S3 bucket
4. **Deploy to AgentCore** for production:
   ```bash
   agentcore configure --entrypoint agent_agentcore.py
   agentcore deploy
   ```

### Production Deployment

See `../PRODUCTION_DEPLOYMENT_GUIDE.md` for:
- GitHub Actions CI/CD setup
- OpenAI-compatible API wrapper
- Production hardening checklist

---

## Testing Your PDF File

**Your test file:** `00010, Nice detailing, 7.5k, 4_1_19, advance.pdf`

**Test queries:**

```bash
python agent_strands.py
```

```
> List files in the test-documents/ folder
> Get metadata for the PDF file in test-documents/
> Show me the first 1000 bytes of the PDF as a preview
> What is the file size of the PDF?
```

The agent will use boto3 to interact with your actual S3 bucket and PDF file!

---

## Cost

### Local Development
- **Free** if using moto for tests
- **Minimal** if using real S3 ($0.0004 per 1000 requests)
- **Bedrock API calls** depend on usage (~$0.003 per 1000 input tokens)

### Total
Less than $0.01 for typical development session

---

## Support

**Issues?**
- Check AWS credentials: `aws sts get-caller-identity`
- Verify S3 access: `aws s3 ls s3://agentic-search-test-bucket/`
- Check Python version: `python --version` (need 3.11+)
- Review logs for errors

**Documentation:**
- S3 Skill: `skills/s3_interaction.md`
- AWS Setup: `AWS_SETUP_COMMANDS.md`
- Production Guide: `../PRODUCTION_DEPLOYMENT_GUIDE.md`
- Main PDR: `../PDR_AGENTIC_S3_SEARCH.md`
