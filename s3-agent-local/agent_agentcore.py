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
from strands_tools.code_interpreter import create_code_interpreter
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

    # Load S3 skill
    skill_path = os.path.join(os.path.dirname(__file__), 'skills', 's3_interaction.md')
    with open(skill_path, 'r') as f:
        S3_SKILL = f.read()

    # Inject configuration
    S3_SKILL_WITH_CONFIG = f"""
{S3_SKILL}

---

## Your Current Configuration

- **S3 Bucket:** {bucket}
- **AWS Region:** {config.aws_region}
- **Environment:** {config.environment}

When executing boto3 code, use:
- bucket = '{bucket}'
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

@app.health_check
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": "s3-search-agent",
        "bucket": config.bucket_name
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
