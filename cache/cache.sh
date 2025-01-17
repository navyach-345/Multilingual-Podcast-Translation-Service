#!/bin/bash

echo "Starting Redis Cache service deployment..."

# Step 1: Copy the JSON service account key to the Redis Cache directory
echo "Copying the service account key to the Redis Cache directory..."
cp /home/nach9995/podcast-serviceAccount-key.json .

if [ $? -eq 0 ]; then
    echo "Service account key copied successfully."
else
    echo "Failed to copy the service account key. Exiting."
    exit 1
fi
 

# Step 2: Build the Docker image
echo "Building the Docker image for the Redis Cache service..."
make -C /home/nach9995/podcast-translation/cache build

# Step 3: Push the Docker image to the container registry
echo "Pushing the Docker image to the container registry..."
make -C /home/nach9995/podcast-translation/cache push

# Step 4: Apply the Kubernetes deployment YAML
echo "Applying Kubernetes deployment configuration..."
kubectl apply -f /home/nach9995/podcast-translation/cache/deployment.yaml


# Step 5: Apply the Kubernetes redis-deployment YAML
echo "Applying Kubernetes redis-deployment configuration..."
kubectl apply -f /home/nach9995/podcast-translation/cache/redis-deployment.yaml


echo "Redis Cache service deployment completed successfully."
