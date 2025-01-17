# REST API Service

## Introduction
The REST API Service in the "Multilingual Podcast Translation Service" project functions as the interface between the
frontend and various backend services. It orchestrates processes such as input retrieval, Speech-to-text, Translation,
 text-to-speech conversion, cache checking, ensuring seamless interaction across services using Google pub/sub.

## Setup Instructions

### Prerequisites
- Google Cloud Platform (GCP) account with billing enabled.
- Configured kubectl command-line tool with access to your Kubernetes cluster.
- Google Cloud SDK (gcloud) installed and configured on your machine.
- Enable `Google Pub/sub` api and add the `pubsub.admin` role to your service account
- An operational Virtual Machine instance on Google Cloud Compute Engine with a static external IP address.

### Configuration and Deployment
Please make the changes mentioned below as noted in the respective .sh file.

#### 1. Virtual Machine Setup
Before deploying the REST API service, create a Virtual Machine (VM) instance in Google Cloud Compute Engine using the
 shell script in the frontend directory `frontend1.sh`. Obtain the external IP address of this VM and update the CORS
 configuration and response headers in the rest.py file to match this IP.

#### 2. Building and Pushing the Docker Image
Compile the Docker image for the REST API service and push it to your Google Container Registry.
*Note: Adjust the Makefile paths to reflect your project directory.*

#### 3. Deploying REST API Service to Kubernetes
Deploy the service using Kubernetes deployment configurations to manage the service efficiently at scale.
Note: Ensure file paths in the deployment commands correspond with your local environment setup.

#### 4. Creating a Kubernetes Secret for Service Account
Create a Kubernetes secret to securely store the service account key that will be used by your application running on Kubernetes.
*Note: Replace the path with the path to your service account key.*

## Modifications
- *File Paths and Project Settings*: Check and modify any project-specific paths and settings in the Docker commands,
 Kubernetes configurations, and .sh script to reflect your actual GCP and local directory structure.
- *IP Address Replacement*: Replace the placeholder <VM_IP_Address> in the rest.py & ingress.yaml file's CORS settings
 with the external IP address of your VM to ensure proper functioning of cross-origin requests.

### Using the Script
1. *Creating a VM and Setting Up Firewall Rules*:
   Navigate to the frontend directory containing `create_vm.sh` and execute the script to create a VM and configure firewall rules:
   Ensure the script has execution permissions:
   ```bash
   chmod +x create_vm.sh
   ```

   ```bash
   ./create_vm.sh
   ```
   

   
3. *Later deploy the REST API Service*, navigate to the directory containing `rest.sh` and execute the script:
   Ensure the script has execution permissions:
   ```bash
   chmod +x rest.sh
   ```
 
   ```bash
   ./rest.sh
   ```
   

   
### Testing the Service
To verify that the REST API Service is fully operational, perform a test using port-forwarding and curl to interact with
the service's health check endpoint.

1. *Port-forwarding*:
   Use kubectl to forward a local port to the service:
   ```bash
   kubectl port-forward deployment/rest-server 5000:5000
   ```

2. *Testing with Curl*:
   Send a request to the service’s health endpoint to check its status:
   ```bash
   curl http://localhost:5000/health
   ```

If the service is correctly set up and running, you will receive a status indicating "healthy".

## Conclusion
The REST API Service is a critical component of the "Multilingual Podcast Translation Service" project, ensuring that
user requests are processed through the various backend services seamlessly. Proper setup and operation of this service
are paramount for the smooth execution of real-time and batch processing workflows, enhancing the overall user experience and system reliability.
