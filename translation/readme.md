# Translation Service

## Introduction
The Translation Service in the "Multilingual Podcast Translation Service" project is responsible for converting transcribed text from
one language to another. This service utilizes the Google Cloud Translation API to provide fast and accurate translations,
enabling podcasts to be accessible in multiple languages.

## Setup Instructions

### Prerequisites
- Google Cloud Platform (GCP) account with billing enabled.
- Configured `kubectl` command-line tool with access to your Kubernetes cluster.
- Google Cloud SDK (`gcloud`) installed and configured on your machine.
- `Google Cloud Translation` API enabled on your GCP account.

### Configuration and Deployment
Please make the changes mentioned below as noted in the respective `.sh` file.

#### 1. Enabling Google Translation API
Ensure that the Google Translation API is enabled in your Google Cloud project through the Google Cloud Console.

#### 2. Building and Pushing the Docker Image
Construct the Docker image for the Translation service and push it to your Google Container Registry.
*Note: Adjust the `Makefile` paths according to your project directory.*

#### 3. Deploying Translation Service to Kubernetes
Deploy the service using Kubernetes deployment configurations to manage the service efficiently at scale.
*Note: Modify the file paths in the deployment command to align with your local environment.*

#### 4. Creating a Kubernetes Secret for Service Account
Create a Kubernetes secret to securely store the service account key that will be used by your application running on Kubernetes.
*Note: Replace the path with the path to your service account key.*

## Modifications
- **Project and Container Paths**: Ensure that paths and identifiers in the Docker commands and Kubernetes configurations
-  reflect your actual GCP setup and directory structure.

### Using the Script
To deploy the Translation Service, navigate to the directory containing `translation.sh` and execute the script:
Make sure the script has execution permissions:
```bash
chmod +x translation.sh
```

```bash
./translation.sh
```


### Testing the Service
To confirm that the Translation Service is operating correctly, perform a test using port-forwarding and curl to interact
with the service's health check endpoint.

1. **Port-forwarding**:
   Use kubectl to forward a local port to the service:
   ```bash
   kubectl port-forward deployment/translation-service 8080:8080
   ```

## Conclusion
The Translation Service is essential for the "Multilingual Podcast Translation Service" project, providing a crucial layer that transforms 
content into various languages. By enabling podcasts to reach a broader audience, this service enhances the global accessibility
and appeal of the content, making it inclusive and available to non-native speakers.
