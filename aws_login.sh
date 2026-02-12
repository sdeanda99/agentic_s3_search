#!/bin/bash
# AWS SSO Login and Credential Export
# This script logs into AWS SSO and exports credentials to your terminal session
#
# USAGE:
#   source ./aws_login.sh    (recommended - exports credentials to current shell)
#   . ./aws_login.sh         (same as above)

# Note: We don't use 'set -e' because it can cause issues when sourcing

# Set the profile name as default for all AWS CLI commands
export AWS_PROFILE=saba

echo "==================================================================="
echo "AWS SSO Login"
echo "==================================================================="
aws sso login --profile saba

echo ""
echo "==================================================================="
echo "Exporting credentials to terminal session"
echo "==================================================================="
# Export credentials directly without requiring manual copy/paste
eval "$(aws configure export-credentials --profile saba --format env)"

# Verify credentials are set
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "ERROR: Failed to export AWS credentials"
    return 1 2>/dev/null || exit 1
fi

echo "✓ Credentials exported successfully"
echo ""
echo "AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID:0:20}..."
echo "AWS_SECRET_ACCESS_KEY: ${AWS_SECRET_ACCESS_KEY:0:20}..."
echo "AWS_SESSION_TOKEN: ${AWS_SESSION_TOKEN:0:20}..."
echo ""
echo "Credentials expire: $AWS_CREDENTIAL_EXPIRATION"
echo ""
echo "==================================================================="
echo "Verifying authentication with AWS STS"
echo "==================================================================="
aws sts get-caller-identity

echo ""
echo "==================================================================="
echo "✓ Authentication verified! You are now logged in."
echo "==================================================================="
echo ""
echo "AWS_PROFILE is set to: $AWS_PROFILE"
echo "IMPORTANT: Credentials are exported to THIS terminal session."
echo "If you opened a new terminal, run: source ./aws_login.sh"
echo "==================================================================="
