"""
S3 Agent - Pure Strands Implementation
For fast local development and iteration

Run: python agent_strands.py
"""
import os
from strands import Agent
from strands_tools.code_interpreter import create_code_interpreter
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
"""

# Create code interpreter tool
code_interpreter = create_code_interpreter()

# Create agent
agent = Agent(
    name="S3SearchAgent",
    model=config.model_id,
    system_prompt=S3_SKILL_WITH_CONFIG,
    tools=[code_interpreter]
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
