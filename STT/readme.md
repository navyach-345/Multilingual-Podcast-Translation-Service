# STT (Speech-to-Text) Service

## Introduction
The STT (Speech-to-Text) Service in the "Multilingual Podcast Translation Service" project is responsible for converting spoken language into written text.
This service is crucial for the initial stage of the podcast translation process, as it transcribes audio content into text that can then be translated into
multiple languages.

## Setup Instructions

### Prerequisites
- Google Cloud Platform (GCP) account with billing enabled.
- Enable `Google Speech-to-Text` Api in API library.
- Configured `kubectl` command-line tool with access to your Kubernetes cluster.
- Google Cloud SDK (`gcloud`) installed and configured on your machine.

### Configuration and Deployment
Please make the changes mentioned below as noted in the respective `.sh` file.

#### 1. Building and Pushing the Docker Image
Construct the Docker image for the STT service and push it to your Google Container Registry.
*Note: Adjust the `Makefile` paths according to your project directory.*

#### 2. Deploying STT Service to Kubernetes
Deploy the service using Kubernetes deployment configurations to manage the service at scale.
*Note: Modify the file paths in the deployment command to align with your local environment.*

#### 3. Creating a Kubernetes Secret for Service Account
Create a Kubernetes secret to securely store the service account key that will be used by your application running on Kubernetes.
*Note: Replace the path with the path to your service account key.*

## Modifications
- **Project and Container Paths**: Ensure that paths and identifiers in the Docker commands and Kubernetes configurations reflect your actual
-  GCP setup and directory structure.

### Using the Script
To deploy the STT Service, navigate to the directory containing `stt.sh` and execute the script:
Make sure the script has execution permissions:
```bash
chmod +x stt.sh
```

```bash
./stt.sh
```


### Testing the Service
To confirm that the STT Service is operating correctly, perform a test using port-forwarding and curl to interact with the service's health check endpoint.

1. **Port-forwarding**:
   Use kubectl to forward a local port to the service:
   ```bash
   kubectl port-forward deployment/stt-service 8080:8080
   ```

## Conclusion
The STT Service is a pivotal component of the "Multilingual Podcast Translation Service" project, enabling the accurate transcription of spoken 
content into text. This foundational step is essential for facilitating the subsequent translation and text-to-speech processes, ensuring the project
efficiently handles multiple languages and dialects, enhancing accessibility and global reach.
