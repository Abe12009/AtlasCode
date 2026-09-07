#!/usr/bin/env bash
# Pulls AtlasCode's backend config from AWS Systems Manager Parameter Store
# and writes it as an EnvironmentFile for systemd (see atlascode-backend.service).
#
# Only needed if you chose the SSM Parameter Store option in deploy/aws/README.md
# (Step 6 / Step 3 env-var decision) instead of a plain .env file. Requires the
# EC2 instance to have an IAM role with ssm:GetParametersByPath on the prefix
# below (see README for the exact policy JSON).
#
# Run manually once, or from a boot-time systemd unit / cron @reboot, before
# atlascode-backend.service starts. Not run automatically by anything in this
# repo — wire it up yourself if you pick this option.
#
# Usage: fetch-env-from-ssm.sh [ssm-path-prefix]
#   default prefix: /atlascode/prod/

set -euo pipefail

PREFIX="${1:-/atlascode/prod/}"
OUT_FILE=/etc/atlascode/atlascode.env
OUT_DIR=$(dirname "$OUT_FILE")

mkdir -p "$OUT_DIR"
umask 077

aws ssm get-parameters-by-path \
  --path "$PREFIX" \
  --with-decryption \
  --query "Parameters[*].{Name:Name,Value:Value}" \
  --output text |
while IFS=$'\t' read -r name value; do
  key=$(basename "$name" | tr '[:lower:]' '[:upper:]')
  printf '%s=%s\n' "$key" "$value"
done > "$OUT_FILE"

chown atlascode:atlascode "$OUT_FILE"
chmod 600 "$OUT_FILE"
echo "Wrote $(wc -l < "$OUT_FILE") vars to $OUT_FILE"
