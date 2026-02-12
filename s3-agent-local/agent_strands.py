"""
S3 Agent - Pure Strands Implementation
For fast local development and iteration

Run: python agent_strands.py
"""
import os
from strands import Agent
from strands_tools.code_interpreter import AgentCoreCodeInterpreter
from config import S3AgentConfig

# Load configuration
config = S3AgentConfig.from_env()

# Load S3 interaction skill
SKILL_PATH = os.path.join(os.path.dirname(__file__), 'skills', 's3_interaction.md')
with open(SKILL_PATH, 'r') as f:
    S3_SKILL = f.read()

# Inject configuration into skill
S3_SKILL_WITH_CONFIG = f"""
{S3_SKILL}

---

## Your Current Configuration

- **S3 Bucket:** {config.bucket_name}
- **AWS Region:** {config.aws_region}
- **Environment:** {config.environment}

When executing boto3 code, use:
- bucket = '{config.bucket_name}'
- region = '{config.aws_region}'

---

## BEHAVIORAL ENFORCEMENT - MANDATORY RULES

You MUST follow these rules for ALL S3-related queries:

### Rule 1: Multi-Tool Sequential Use (CRITICAL!)
**NEVER stop after one tool call!** Always use multiple tools in sequence to build complete analysis.

### Rule 2: Always Apply Three-Phase Strategy
For ANY analysis or search query, execute ALL three phases:
- Phase 1: Scan/list files
- Phase 2: Preview relevant ones
- Phase 3: Analyze and provide comprehensive results

### Rule 3: Never Ask Permission - Act Autonomously
Instead of "Would you like me to examine it?", just DO IT.

- ❌ BAD: "Found 1 file. Would you like me to analyze it?"
- ✅ GOOD: "Found 1 file. Analyzing now..." [proceeds with preview → read → analysis]

### Rule 4: Build Complete Answers
Always provide comprehensive responses:
- List files → ALSO show metadata and previews
- Find files → ALSO analyze content
- Analyze document → ALSO provide summary and key findings

**YOU ARE AN AUTONOMOUS AGENT. USE ALL TOOLS NEEDED TO GIVE COMPLETE ANSWERS.**
"""

# Initialize Code Interpreter tool with persistent session
# This enables memory across queries in the same interactive session
code_interpreter_tool = AgentCoreCodeInterpreter(
    region=config.aws_region,
    identifier='s3_search_code_interpreter-JuyRObn76n',  # Your manually created Code Interpreter
    session_name='interactive-cli-session',  # Persistent session for memory
    auto_create=True,
    persist_sessions=True
)

# Create agent with code interpreter
agent = Agent(
    name="S3SearchAgent",
    model=config.model_id,
    system_prompt=S3_SKILL_WITH_CONFIG,
    tools=[code_interpreter_tool.code_interpreter]  # Official pattern from AWS docs
)

def main():
    """Main entry point for testing"""
    print("=" * 60)
    print("S3 Agent - Strands Implementation")
    print("=" * 60)
    print(f"Configuration: {config}")
    print("=" * 60)
    print()

    # Example queries to test
    test_queries = [
        f"List all files in the bucket {config.bucket_name}",
        f"Show me files in the test-documents/ folder",
        "Get metadata for the PDF file in test-documents/",
        "Preview the first 500 bytes of the PDF file"
    ]

    # Interactive mode
    print("Enter your query (or 'quit' to exit):")
    print("Example: 'List all files in my S3 bucket'")
    print()

    while True:
        user_input = input("> ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break

        if not user_input:
            continue

        try:
            print("\n[Agent thinking...]\n")
            result = agent(user_input)
            print(result.message)
            print()
        except Exception as e:
            print(f"Error: {e}")
            print()

if __name__ == "__main__":
    main()
