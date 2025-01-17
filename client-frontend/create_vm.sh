#!/bin/bash

echo "Starting frontend VM and firewall setup..."

# 1. Create a VM for the frontend
echo "Creating the frontend VM..."
gcloud compute instances create frontend-vm \
    --machine-type=e2-medium \
    --image-family=debian-11 \
    --image-project=debian-cloud \
    --zone=us-central1-a \
    --tags=frontend-http \
    --scopes=https://www.googleapis.com/auth/cloud-platform

if [ $? -eq 0 ]; then
    echo "Frontend VM created successfully."
else
    echo "Failed to create frontend VM. Exiting."
    exit 1
fi

# 2. Create a firewall rule for HTTP traffic
echo "Creating a firewall rule to allow HTTP traffic..."
gcloud compute firewall-rules create allow-http-frontend \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:80 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=frontend-http

if [ $? -eq 0 ]; then
    echo "Firewall rule created successfully."
else
    echo "Failed to create firewall rule. Exiting."
    exit 1
fi

echo "Frontend VM and firewall setup completed successfully."
