#!/bin/bash

# Setup Code Interpreter Execution Role with S3 Permissions
# Run this script to give AgentCore Code Interpreter access to your S3 bucket

set -e  # Exit on error

echo "==========================================================="
echo "Setting up Code Interpreter Execution Role"
echo "==========================================================="
echo ""

# Configuration
BUCKET_NAME="agentic-search-test-sdeanda-001"
ROLE_NAME="CodeInterpreterS3AccessRole"
ACCOUNT_ID="694676321662"

echo "Configuration:"
echo "  S3 Bucket: $BUCKET_NAME"
echo "  IAM Role: $ROLE_NAME"
echo "  Account ID: $ACCOUNT_ID"
echo ""

# 1. Create S3 policy
echo "Step 1: Creating S3 policy..."
cat > s3-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "s3:ListBucket",
      "s3:GetObject",
      "s3:PutObject",
      "s3:HeadObject",
      "s3:SelectObjectContent",
      "s3:GetObjectVersion",
      "s3:DeleteObject"
    ],
    "Resource": [
      "arn:aws:s3:::$BUCKET_NAME",
      "arn:aws:s3:::$BUCKET_NAME/*"
    ]
  }]
}
EOF
echo "✓ S3 policy created: s3-policy.json"
echo ""

# 2. Create trust policy
echo "Step 2: Creating trust policy for Bedrock AgentCore service..."
cat > code-interpreter-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock-agentcore.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
echo "✓ Trust policy created: code-interpreter-trust-policy.json"
echo ""

# 3. Create IAM role
echo "Step 3: Creating IAM role..."
if aws iam get-role --role-name $ROLE_NAME &>/dev/null; then
    echo "⚠ Role $ROLE_NAME already exists, updating trust policy..."
    # Update the trust policy for existing role
    aws iam update-assume-role-policy \
      --role-name $ROLE_NAME \
      --policy-document file://code-interpreter-trust-policy.json
    echo "✓ Trust policy updated"
else
    aws iam create-role \
      --role-name $ROLE_NAME \
      --assume-role-policy-document file://code-interpreter-trust-policy.json \
      --description "Execution role for AgentCore Code Interpreter to access S3"
    echo "✓ IAM role created: $ROLE_NAME"
fi
echo ""

# 4. Attach S3 policy to role
echo "Step 4: Attaching S3 policy to role..."
aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name S3AccessPolicy \
  --policy-document file://s3-policy.json
echo "✓ S3 policy attached to role"
echo ""

# 5. Get and display role ARN
echo "Step 5: Getting role ARN..."
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)
echo "✓ Role ARN: $ROLE_ARN"
echo ""

# 6. Note about Code Interpreter resource
echo "Step 6: Code Interpreter setup..."
echo "⚠ Note: The Code Interpreter resource will be auto-created on first use"
echo "  by the AgentCoreCodeInterpreter tool with the execution role."
echo ""
echo "The AgentCoreCodeInterpreter uses identifier='aws.codeinterpreter.v1' by default"
echo "and will use the role: $ROLE_ARN"
echo ""

echo "==========================================================="
echo "Setup Complete!"
echo "==========================================================="
echo ""
echo "Role ARN: $ROLE_ARN"
echo ""
echo "Permissions granted:"
echo "  ✓ s3:ListBucket"
echo "  ✓ s3:GetObject"
echo "  ✓ s3:PutObject"
echo "  ✓ s3:HeadObject"
echo "  ✓ s3:SelectObjectContent"
echo "  ✓ s3:GetObjectVersion"
echo "  ✓ s3:DeleteObject"
echo ""
echo "Bucket: $BUCKET_NAME"
echo ""
echo "Code Interpreter Name: $CODE_INTERPRETER_NAME"
echo "Code Interpreter ARN: $CODE_INTERPRETER_ARN"
echo ""
echo "Next steps:"
echo "  1. Run: python agent_strands.py"
echo "  2. Test query: 'List all files in my S3 bucket'"
echo ""
