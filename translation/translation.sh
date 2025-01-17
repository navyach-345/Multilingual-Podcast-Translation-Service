#!/bin/bash

echo "Starting Translation service deployment..."

# Step 1: Copy the JSON service account key to the Translation directory
echo "Copying the service account key to the Translation directory..."
cp /home/nach9995/podcast-serviceAccount-key.json .

if [ $? -eq 0 ]; then
    echo "Service account key copied successfully."
else
    echo "Failed to copy the service account key. Exiting."
    exit 1
fi

# Step 2: Create a Kubernetes secret for the Translation service
echo "Creating Kubernetes secret for the Translation service..."
kubectl create secret generic gcp-translation-service-account-key \
    --from-file=service-account-key.json=./podcast-serviceAccount-key.json 

# Step 3: Build the Docker image
echo "Building the Docker image for the Translation service..."
make -C /home/nach9995/podcast-translation/translation build

# Step 4: Push the Docker image to the container registry
echo "Pushing the Docker image to the container registry..."
make -C /home/nach9995/podcast-translation/translation push

# Step 5: Apply the Kubernetes deployment YAML
echo "Applying Kubernetes deployment configuration..."
kubectl apply -f /home/nach9995/podcast-translation/translation/deployment.yaml


echo "Translation service deployment completed successfully."
