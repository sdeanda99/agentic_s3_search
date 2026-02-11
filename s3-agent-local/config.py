"""
Configuration for S3 Agent
Supports multiple environments: local, test, production
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env.local if it exists
load_dotenv('.env.local')

@dataclass
class S3AgentConfig:
    """Configuration for S3 agent across environments"""
    bucket_name: str
    aws_region: str
    model_id: str
    environment: str = 'local'

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        env = os.getenv('ENV', 'local')

        return cls(
            bucket_name=os.getenv('S3_BUCKET', 'agentic-search-test-bucket'),
            aws_region=os.getenv('AWS_REGION', 'us-west-2'),
            model_id=os.getenv('MODEL_ID', 'us.anthropic.claude-3-7-sonnet-20250219-v1:0'),
            environment=env
        )

    def __str__(self):
        return f"S3AgentConfig(bucket={self.bucket_name}, region={self.aws_region}, env={self.environment})"
