#!/bin/bash

###### Initial Setup #############
# 1. Setting up Project ID -- Change your respective project id.
gcloud config set project speech-translation-443516

# 2. Enabling apis for project
gcloud services enable \
        compute.googleapis.com \
        pubsub.googleapis.com \
        storage.googleapis.com \
        bigquery.googleapis.com \
        redis.googleapis.com \
        cloudbuild.googleapis.com \
        artifactregistry.googleapis.com
    
# # 3. Creating a service account 
# gcloud iam service-accounts create multi-purpose-service-account \
#     --description="Service account for Podcast Translation project" \
#     --display-name="Podcast Translation Service Account"
    
# # 4. Assigning Roles/Permissions for Service Account - please do check the project id before executing the commands

# gcloud projects add-iam-policy-binding speech-translation-443516 \
#     --member="serviceAccount:multi-purpose-service-account@speech-translation-443516.iam.gserviceaccount.com" \
#     --role="roles/storage.admin"

# gcloud projects add-iam-policy-binding speech-translation-443516 \
#     --member="serviceAccount:multi-purpose-service-account@speech-translation-443516.iam.gserviceaccount.com" \
#     --role="roles/pubsub.editor"

# gcloud projects add-iam-policy-binding speech-translation-443516 \
#     --member="serviceAccount:multi-purpose-service-account@speech-translation-443516.iam.gserviceaccount.com" \
#     --role="roles/container.admin"

# gcloud projects add-iam-policy-binding speech-translation-443516 \
#     --member="serviceAccount:multi-purpose-service-account@speech-translation-443516.iam.gserviceaccount.com" \
#     --role="roles/cloudsql.admin"

# gcloud projects add-iam-policy-binding speech-translation-443516 \
#     --member="serviceAccount:multi-purpose-service-account@speech-translation-443516.iam.gserviceaccount.com" \
#     --role="roles/redis.admin"

# gcloud projects add-iam-policy-binding speech-translation-443516 \
#     --member="serviceAccount:multi-purpose-service-account@speech-translation-443516.iam.gserviceaccount.com" \
#     --role="roles/bigquery.dataEditor"
    
# gcloud projects add-iam-policy-binding speech-translation-443516 \
#     --member="serviceAccount:multi-purpose-service-account@speech-translation-443516.iam.gserviceaccount.com" \
#     --role="roles/bigquery.user"
    
# # 5. Generating a Key for Service Account:
# gcloud iam service-accounts keys create ~/multi-purpose-service-account-key.json \
#     --iam-account=multi-purpose-service-account@speech-translation-443516.iam.gserviceaccount.com
    
# # 6. Exporting :
# export GOOGLE_APPLICATION_CREDENTIALS=~/podcast-serviceAccount-key.json

#7. Creating Kubernetes Cluster for the project :

gcloud container clusters create podcast-cluster \
    --num-nodes=1 \
    --machine-type=e2-standard-4 \
    --zone=us-central1-a \
    --service-account=multi-purpose-service-account@speech-translation-443516.iam.gserviceaccount.com 

    
#8. Storing Cluster Credentials :
gcloud container clusters get-credentials podcast-cluster --zone us-central1-a

# 9. Checking for the nodes in created cluster:
kubectl get nodes

# 10. Authenicate docker with GCR:
gcloud auth configure-docker

echo "Environment setup complete....till step 10 "