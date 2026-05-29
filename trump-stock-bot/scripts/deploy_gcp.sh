#!/usr/bin/env bash
#
# Provision a small GCP VM, install Docker, copy this bot to it, and start it
# under docker compose. Idempotent-ish: re-running re-syncs code and restarts.
#
# Prereqs on YOUR machine:
#   - gcloud CLI installed and authenticated:  gcloud auth login
#   - a project set:                           gcloud config set project <PROJECT_ID>
#   - a local .env file filled in (see .env.example)
#
# Usage:
#   ./scripts/deploy_gcp.sh                 # uses defaults below
#   VM_NAME=trump-bot ZONE=us-central1-a ./scripts/deploy_gcp.sh
#
set -euo pipefail

VM_NAME="${VM_NAME:-trump-stock-bot}"
ZONE="${ZONE:-us-central1-a}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-small}"      # e2-micro is free-tier eligible in some regions
IMAGE_FAMILY="${IMAGE_FAMILY:-ubuntu-2204-lts}"
IMAGE_PROJECT="${IMAGE_PROJECT:-ubuntu-os-cloud}"
REMOTE_DIR="/opt/trump-stock-bot"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -f "$HERE/.env" ]]; then
  echo "ERROR: $HERE/.env not found. Copy .env.example to .env and fill it in." >&2
  exit 1
fi

echo "==> Ensuring VM '$VM_NAME' exists in $ZONE ($MACHINE_TYPE)..."
if ! gcloud compute instances describe "$VM_NAME" --zone "$ZONE" >/dev/null 2>&1; then
  gcloud compute instances create "$VM_NAME" \
    --zone "$ZONE" \
    --machine-type "$MACHINE_TYPE" \
    --image-family "$IMAGE_FAMILY" \
    --image-project "$IMAGE_PROJECT" \
    --boot-disk-size 20GB \
    --metadata startup-script='#!/bin/bash
set -e
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
fi'
  echo "==> Waiting 45s for the VM + Docker install to settle..."
  sleep 45
else
  echo "==> VM already exists; reusing it."
fi

echo "==> Syncing code to the VM..."
gcloud compute ssh "$VM_NAME" --zone "$ZONE" --command "sudo mkdir -p $REMOTE_DIR && sudo chown \$(whoami) $REMOTE_DIR"

# Copy the project (excluding local cruft). --recurse keeps the layout.
gcloud compute scp --recurse --zone "$ZONE" \
  "$HERE/Dockerfile" "$HERE/docker-compose.yml" "$HERE/requirements.txt" \
  "$HERE/main.py" "$HERE/.env" "$HERE/src" "$HERE/config" \
  "$VM_NAME:$REMOTE_DIR/"

echo "==> Building & starting the container on the VM..."
gcloud compute ssh "$VM_NAME" --zone "$ZONE" --command "
  cd $REMOTE_DIR &&
  sudo docker compose up -d --build &&
  echo '--- container status ---' &&
  sudo docker compose ps
"

echo ""
echo "==> Done. Useful commands:"
echo "    Logs:    gcloud compute ssh $VM_NAME --zone $ZONE --command 'cd $REMOTE_DIR && sudo docker compose logs -f'"
echo "    Restart: gcloud compute ssh $VM_NAME --zone $ZONE --command 'cd $REMOTE_DIR && sudo docker compose restart'"
echo "    Stop:    gcloud compute ssh $VM_NAME --zone $ZONE --command 'cd $REMOTE_DIR && sudo docker compose down'"
