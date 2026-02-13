"""
S3 Agent - AgentCore Implementation
For production-like local testing with hot reload

Run: agentcore dev
Test: agentcore invoke --dev '{"prompt": "List S3 files"}'
"""
import os
import logging
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from strands_tools.code_interpreter import AgentCoreCodeInterpreter
from config import S3AgentConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize AgentCore app
app = BedrockAgentCoreApp()

# Load configuration
config = S3AgentConfig.from_env()

@app.entrypoint
def invoke(payload: dict, context) -> dict:
    """
    AgentCore entrypoint for S3 agent invocations

    Payload format:
    {
        "prompt": "Your S3 query here",
        "bucket": "optional-override-bucket"
    }
    """
    # Extract prompt
    user_prompt = payload.get("prompt", "")
    bucket_override = payload.get("bucket")

    if not user_prompt:
        return {"error": "No prompt provided"}

    # Use override bucket if provided
    bucket = bucket_override if bucket_override else config.bucket_name

    logger.info(f"Processing query: {user_prompt[:100]}...")
    logger.info(f"Using bucket: {bucket}")

    # Load BOTH skills: S3 interaction + Legal contract review
    skills_dir = os.path.join(os.path.dirname(__file__), 'skills')

    with open(os.path.join(skills_dir, 's3_interaction.md'), 'r') as f:
        S3_SKILL = f.read()

    with open(os.path.join(skills_dir, 'legal_contract_review.md'), 'r') as f:
        LEGAL_SKILL = f.read()

    # Combine both skills with configuration
    COMBINED_SKILLS = f"""
# SKILL 1: S3 Interaction

{S3_SKILL}

---

# SKILL 2: Legal Contract Review

{LEGAL_SKILL}

---

## Your Current Configuration

- **S3 Bucket:** {bucket}
- **AWS Region:** {config.aws_region}
- **Environment:** {config.environment}

When executing boto3 code, use:
- bucket = '{bucket}'
- region = '{config.aws_region}'

---

## BEHAVIORAL ENFORCEMENT - MANDATORY RULES

You MUST follow these rules for ALL S3-related queries:

### Rule 1: Multi-Tool Sequential Use (CRITICAL!)
**NEVER stop after one tool call!** Always use multiple tools in sequence to build complete analysis.

- ❌ BAD: User asks "List files" → You use scan_folder → STOP
- ✅ GOOD: User asks "List files" → scan_folder → head_object (metadata) → preview_file (sample) → Comprehensive response

### Rule 2: Always Apply Three-Phase Strategy
For ANY analysis or search query, execute ALL three phases:

**Phase 1 - Parallel Scan (Discovery):**
- Use scan_folder or glob to list files
- Filter by metadata (size, date, name)
- Identify candidates

**Phase 2 - Deep Dive (Selective Analysis):**
- Use preview_file on top candidates
- Confirm relevance
- Use parse_file or read_file as needed

**Phase 3 - Backtrack (Cross-References):**
- Analyze content for relationships
- Use grep if patterns needed
- Provide complete picture

### Rule 3: Build Context Progressively
Each tool call should build on the previous:
- First call: Discover what exists
- Second call: Confirm relevance
- Third call: Deep analysis
- Final response: Synthesize findings

### Rule 4: Examples of Mandatory Multi-Tool Workflows

**Query: "List files in my bucket"**
- Tool 1: list_objects_v2() → Get all files
- Tool 2: head_object() → Get metadata for each
- Tool 3: preview_file() → Sample top files
- Response: "Found X files, here's summary with metadata and previews"

**Query: "Analyze the PDF"**
- Tool 1: head_object() → Get size, type, modified date
- Tool 2: preview_file(Range=bytes=0-1000) → See first 1KB
- Tool 3: get_object() → Full content if needed
- Response: "PDF analysis: [size], [type], [content summary]"

**Query: "Find documents about X"**
- Phase 1: list_objects_v2() → Scan all files
- Phase 2: preview_file() → Check top candidates for keyword
- Phase 3: get_object() → Full read of matches + analysis
- Response: "Found N relevant documents: [detailed findings]"

### Rule 5: Never Say "Would you like me to..."
Instead of asking permission to do more analysis, JUST DO IT.

- ❌ BAD: "Found 1 file. Would you like me to examine it?"
- ✅ GOOD: "Found 1 file. Let me analyze it..." [proceeds to preview + read + analyze]

**YOU ARE AN AUTONOMOUS AGENT. ACT AUTONOMOUSLY. USE ALL AVAILABLE TOOLS TO PROVIDE COMPLETE ANSWERS.**

---

## YOUR COMBINED CAPABILITIES

You are a **Paralegal AI Assistant** with dual expertise:

1. **S3 Document Search** - Find and access documents in S3 buckets
2. **Legal Contract Analysis** - Review contracts using legal frameworks

### Integrated Workflow

When user asks to analyze legal documents:

**Step 1:** Use S3 tools to find contracts
- scan_folder, glob, grep to locate files

**Step 2:** Read contract content
- preview_file to sample, read_file for full content

**Step 3:** Apply legal analysis
- Identify clause types
- Classify risk (GREEN/YELLOW/RED)
- Generate redlines with priority tiers

**Step 4:** Provide comprehensive report
- Executive summary
- Clause-by-clause analysis
- Actionable recommendations

**Example:** "Review vendor contracts in S3" → Find files → Read each → Legal analysis → Consolidated report with risk assessment
"""

    # Initialize Code Interpreter tool with session persistence for memory
    # Use context.session_id to maintain state/variables across invocations
    session_id = getattr(context, 'session_id', 'default-session')
    logger.info(f"Using session ID: {session_id}")

    code_interpreter_tool = AgentCoreCodeInterpreter(
        region=config.aws_region,
        identifier='s3_search_code_interpreter-JuyRObn76n',  # Your manually created Code Interpreter
        session_name=session_id,  # KEY: Enables memory across queries in same session
        auto_create=True,
        persist_sessions=True
    )

    # Create agent with combined S3 + Legal skills
    agent = Agent(
        name="ParalegalS3Agent",
        model=config.model_id,
        system_prompt=COMBINED_SKILLS,
        tools=[code_interpreter_tool.code_interpreter]
    )

    try:
        # Invoke agent
        result = agent(user_prompt)

        # Extract result message
        response_text = result.message
        if isinstance(response_text, dict):
            response_text = response_text.get('content', [{}])[0].get('text', str(response_text))

        logger.info("Agent invocation successful")

        return {
            "result": response_text,
            "bucket": bucket,
            "status": "success"
        }

    except Exception as e:
        logger.error(f"Agent error: {e}", exc_info=True)
        return {
            "error": str(e),
            "status": "failed"
        }

if __name__ == "__main__":
    # Run local development server
    print("=" * 60)
    print("S3 Agent - AgentCore Dev Mode")
    print("=" * 60)
    print(f"Configuration: {config}")
    print("=" * 60)
    print()
    print("Starting development server with hot reload...")
    print("Server will be available at: http://localhost:8080")
    print()
    print("Test with:")
    print("  agentcore invoke --dev '{\"prompt\": \"List my S3 files\"}'")
    print()

    app.run(host="0.0.0.0", port=8080)
