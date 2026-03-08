#!/usr/bin/env bash
# deploy.sh — Deploy the Telegram AI Agent to a GCP VM
#
# Prerequisites:
#   1. gcloud CLI installed and authenticated
#   2. A GCP project selected (gcloud config set project YOUR_PROJECT)
#   3. A .env file with your secrets
#
# Usage:
#   ./deploy.sh              # Deploy to default VM
#   ./deploy.sh --create     # Create VM first, then deploy
#   ./deploy.sh --logs       # Tail container logs on the VM
#   ./deploy.sh --ssh        # SSH into the VM
#
set -euo pipefail

# ── Config ──
VM_NAME="${VM_NAME:-telegram-ai-agent}"
ZONE="${ZONE:-us-central1-a}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-micro}"
REMOTE_DIR="/opt/telegram-ai-agent"

# ── Helpers ──
info()  { echo -e "\033[1;34m→\033[0m $*"; }
error() { echo -e "\033[1;31m✗\033[0m $*" >&2; exit 1; }

# ── Commands ──

create_vm() {
    info "Creating GCP VM: $VM_NAME ($MACHINE_TYPE in $ZONE)"
    gcloud compute instances create "$VM_NAME" \
        --zone="$ZONE" \
        --machine-type="$MACHINE_TYPE" \
        --image-family=cos-stable \
        --image-project=cos-cloud \
        --boot-disk-size=20GB \
        --tags=telegram-bot \
        --metadata=startup-script='#!/bin/bash
# Container-Optimized OS ships with Docker pre-installed
sudo mkdir -p '"$REMOTE_DIR"'/{memory,skills}'
    info "VM created. Waiting for SSH to be ready..."
    sleep 15
}

deploy() {
    if [ ! -f .env ]; then
        error ".env file not found. Copy .env.example to .env and fill in your secrets."
    fi

    info "Uploading files to $VM_NAME..."
    # Upload project files (excluding .git, memory data, venvs)
    gcloud compute scp --zone="$ZONE" --recurse \
        --compress \
        Dockerfile docker-compose.yml requirements.txt \
        bot.py ai_brain.py config.py memory_store.py scheduler.py \
        "$VM_NAME:$REMOTE_DIR/"

    # Upload directories
    gcloud compute scp --zone="$ZONE" --recurse \
        tools/ skills/ \
        "$VM_NAME:$REMOTE_DIR/"

    # Upload .env separately (never in version control)
    gcloud compute scp --zone="$ZONE" \
        .env \
        "$VM_NAME:$REMOTE_DIR/.env"

    info "Building and starting container on $VM_NAME..."
    gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="
        cd $REMOTE_DIR && \
        docker compose down 2>/dev/null || true && \
        docker compose build --no-cache && \
        docker compose up -d && \
        echo '' && \
        docker compose ps
    "

    info "Deployed! Use './deploy.sh --logs' to check output."
}

show_logs() {
    gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="
        cd $REMOTE_DIR && docker compose logs -f --tail=50
    "
}

ssh_vm() {
    gcloud compute ssh "$VM_NAME" --zone="$ZONE"
}

# ── Main ──

case "${1:-}" in
    --create)
        create_vm
        deploy
        ;;
    --logs)
        show_logs
        ;;
    --ssh)
        ssh_vm
        ;;
    --help|-h)
        echo "Usage: $0 [--create|--logs|--ssh|--help]"
        echo ""
        echo "  (no args)   Deploy to existing VM"
        echo "  --create    Create a new GCP VM and deploy"
        echo "  --logs      Tail container logs"
        echo "  --ssh       SSH into the VM"
        echo ""
        echo "Environment variables:"
        echo "  VM_NAME=$VM_NAME  ZONE=$ZONE  MACHINE_TYPE=$MACHINE_TYPE"
        ;;
    *)
        deploy
        ;;
esac
