#!/bin/bash

# Enable debugging mode and stop the script on the first error
set -euo pipefail

# Function to parse command-line arguments
parse_arguments() {
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            --namespace) NAMESPACE="$2"; shift ;;
            --profile) PROFILE="$2"; shift ;;
            --cluster_name) CLUSTER_NAME="$2"; shift ;;
            --policy_name) POLICY_NAME="$2"; shift ;;
            --policy_file) POLICY_FILE="$2"; shift ;;
            --service_account_name) SERVICE_ACCOUNT_NAME="$2"; shift ;;
            --aws_region) AWS_REGION="$2"; shift ;;
            --help) show_help; exit 0 ;;
            *) echo "Unknown parameter passed: $1"; show_help; exit 1 ;;
        esac
        shift
    done
}

# Function to display help
show_help() {
    echo "Usage: $0 [options]"
    echo
    echo "Options:"
    echo "  --namespace                Kubernetes namespace (default: $NAMESPACE)"
    echo "  --profile                  AWS CLI profile to use (default: $PROFILE)"
    echo "  --cluster_name             EKS Cluster name (default: $CLUSTER_NAME)"
    echo "  --policy_name              IAM policy name (default: $POLICY_NAME)"
    echo "  --policy_file              IAM policy file (default: $POLICY_FILE)"
    echo "  --service_account_name     Kubernetes service account name (default: $SERVICE_ACCOUNT_NAME)"
    echo "  --aws_region               AWS region (default: $AWS_REGION)"
    echo "  --help                     Show this help message and exit"
}


# Default values for variables
NAMESPACE="kafka-chaos-experiments"
PROFILE="iac-playground"
CLUSTER_NAME="iac-playground"
POLICY_NAME="msk-policy"
POLICY_FILE="msk-policy.json"
SERVICE_ACCOUNT_NAME="kafka-chaos-experiments"
AWS_REGION="us-west-2"

# Parse command-line arguments
parse_arguments "$@"

# Function to update kubeconfig
update_kubeconfig() {
    echo "Updating kubeconfig for cluster $CLUSTER_NAME using profile $PROFILE"
    aws eks update-kubeconfig --name "$CLUSTER_NAME" --profile "$PROFILE" --region "$AWS_REGION"
}

# Function to create namespace
create_namespace() {
    echo "Checking if namespace $NAMESPACE exists"
    if ! kubectl get ns "$NAMESPACE" >/dev/null 2>&1; then
        echo "Creating namespace $NAMESPACE"
        kubectl create ns "$NAMESPACE"
    else
        echo "Namespace $NAMESPACE already exists"
    fi
}

# Function to create IAM policy
create_iam_policy() {
    echo "Creating IAM policy $POLICY_NAME"
    ACCOUNT_ID=$(aws --profile "$PROFILE" sts get-caller-identity --query "Account" --output text)
    if aws --profile "$PROFILE" iam get-policy --policy-arn "arn:aws:iam::$ACCOUNT_ID:policy/$POLICY_NAME" >/dev/null 2>&1; then
        echo "IAM policy $POLICY_NAME already exists"
    else
        aws --profile "$PROFILE" iam create-policy --policy-name "$POLICY_NAME" --policy-document "file://$POLICY_FILE" --no-cli-pager
    fi
}

# Function to create IAM service account
create_iam_service_account() {
    echo "Creating IAM service account $SERVICE_ACCOUNT_NAME in namespace $NAMESPACE"
    ACCOUNT_ID=$(aws --profile "$PROFILE" sts get-caller-identity --query "Account" --output text)
    eksctl --profile "$PROFILE" create iamserviceaccount \
        --cluster="$CLUSTER_NAME" \
        --namespace="$NAMESPACE" \
        --name="$SERVICE_ACCOUNT_NAME" \
        --attach-policy-arn="arn:aws:iam::$ACCOUNT_ID:policy/$POLICY_NAME" \
        --override-existing-serviceaccounts \
        --role-name="$SERVICE_ACCOUNT_NAME" \
        --approve
}

# Main script execution
main() {
    update_kubeconfig
    create_namespace
    create_iam_policy
    create_iam_service_account

    echo "Script completed successfully!"
}

# Run the main function
main "$@"