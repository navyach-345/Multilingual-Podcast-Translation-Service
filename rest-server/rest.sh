#!/bin/bash

echo "Starting REST service deployment..."

# Step 1. Creating a input storage bucket
gcloud storage buckets create gs://podcast_storage_bucket_input \
	--location=us-central1 \
	--default-storage-class=STANDARD

# Step 2: Copy the JSON service account key to the rest-server directory
echo "Copying the service account key to the rest-server directory..."
cp /home/nach9995/podcast-serviceAccount-key.json .

if [ $? -eq 0 ]; then
    echo "Service account key copied successfully."
else
    echo "Failed to copy the service account key. Exiting."
    exit 1
fi

# Step 3: Create a Kubernetes secret for the REST service
echo "Creating Kubernetes secret for the REST service..."
kubectl create secret generic gcp-rest-service-account-key \
    --from-file=service-account-key.json=./podcast-serviceAccount-key.json

# Step 4: Build the Docker image
echo "Building the Docker image for the REST service..."
make -C /home/nach9995/podcast-translation/rest-server build

# Step 5: Push the Docker image to the container registry
echo "Pushing the Docker image to the container registry..."
make -C /home/nach9995/podcast-translation/rest-server push

# Step 6: Apply the Kubernetes deployment YAML
echo "Applying Kubernetes deployment configuration..."
kubectl apply -f /home/nach9995/podcast-translation/rest-server/deployment.yaml

# Step 7: Apply the Kubernetes ingress YAML
echo "Applying Kubernetes ingress configuration..."
kubectl apply -f /home/nach9995/podcast-translation/rest-server/ingress.yaml


echo "REST service deployment completed successfully."
