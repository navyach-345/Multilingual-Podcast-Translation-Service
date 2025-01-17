#!/bin/bash

####### Creating Storage Service in kubernetes Cluster ########
# 1. Creating a output storage bucket
gcloud storage buckets create gs://output_storage_bucket_podcast_translation \
	--location=us-central1 \
	--default-storage-class=STANDARD
	
# Step 2: Create a Kubernetes secret for the Storage service
echo "Creating Kubernetes secret for the Storage service..."
kubectl create secret generic gcp-stor-service-account-key \
    --from-file=service-account-key.json=./podcast-serviceAccount-key.json 

# Step 3: Build the Docker image
echo "Building the Docker image for the Storage service..."
make -C /home/nach9995/podcast-translation/storage build

# Step 4: Push the Docker image to the container registry
echo "Pushing the Docker image to the container registry..."
make -C /home/nach9995/podcast-translation/storage push

# Step 5: Apply the Kubernetes deployment YAML
echo "Applying Kubernetes deployment configuration..."
kubectl apply -f /home/nach9995/podcast-translation/storage/deployment.yaml


echo "Storage service deployment completed successfully."

#2. Add policy to that bucket :
gcloud storage buckets add-iam-policy-binding gs://wikipedia-summarizer-storage \
	--member="serviceAccount:wikipedia-service-account@dcsc2024-437804.iam.gserviceaccount.com" \
	--role="roles/storage.objectAdmin"
	
# 3. Creating a secret key for storage in kubernetes cluster:
kubectl create secret generic wikipedia-latest-account-key \
	--from-file=wikipedia-service-account-key.json=/home/jana3207/finalproject-final-project-team-61/Storage/wikipedia-service-account-key.json

#4. Creating pods in kubernetes cluster using the following commands
make -C /home/jana3207/finalproject-final-project-team-61/Storage build
make -C /home/jana3207/finalproject-final-project-team-61/Storage push
kubectl apply -f /home/jana3207/finalproject-final-project-team-61/Storage/storage-deployment.yaml

echo "Storage service deployed successfully."