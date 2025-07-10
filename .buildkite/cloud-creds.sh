#!/bin/bash
set -euo pipefail

echo "INFO: Setting up environment for cloud: ${CLOUD:-unspecified}"

# Always required
export PULUMI_ACCESS_TOKEN="$(buildkite-agent secret get PULUMI_ACCESS_TOKEN)"

case "${CLOUD:-}" in
  aws)
    export AWS_ACCESS_KEY_ID="$(buildkite-agent secret get AWS_ACCESS_KEY_ID)"
    export AWS_SECRET_ACCESS_KEY="$(buildkite-agent secret get AWS_SECRET_ACCESS_KEY)"
    ;;

  gcp)
      : "${GOOGLE_PROJECT:=svmkit}"
      : "${GOOGLE_REGION:=us-central1}"
      : "${GOOGLE_ZONE:=${GOOGLE_REGION}-a}"
      
    ;;

  *)
    echo "ERROR: Unsupported or missing CLOUD environment variable: '${CLOUD:-}'"
    exit 1
    ;;
esac

