# TTS (Text-to-Speech) Service

## Introduction
The TTS (Text-to-Speech) Service in the "Multilingual Podcast Translation Service" project is essential for converting translated text into speech.
This service enhances the accessibility of translated podcasts by producing audible outputs, allowing users to listen to podcasts in their preferred language.

## Setup Instructions

### Prerequisites
- Google Cloud Platform (GCP) account with billing enabled.
- Configured `kubectl` command-line tool with access to your Kubernetes cluster.
- Google Cloud SDK (`gcloud`) installed and configured on your machine.
- Ensure the Python `gTTS` (Google Text-to-Speech) library is installed on your system.

### Configuration and Deployment
Please make the changes mentioned below as noted in the respective `.sh` file.

#### 1. Building and Pushing the Docker Image
Construct the Docker image for the TTS service and push it to your Google Container Registry.
*Note: Adjust the `Makefile` paths to reflect your project directory.*

#### 2. Deploying TTS Service to Kubernetes
Deploy the service using Kubernetes deployment configurations to manage the service efficiently at scale.
*Note: Ensure that file paths in the deployment commands correspond with your local environment setup.*

#### 3. Creating a Kubernetes Secret for Service Account
Create a Kubernetes secret to securely store the service account key that will be used by your application running on Kubernetes.
*Note: Replace the path with the path to your service account key.*

## Modifications
- **Project and Container Paths**: Check and adjust the paths and identifiers in the Docker commands and Kubernetes configurations to
-  ensure they reflect your actual GCP setup and directory structure.

### Using the Script
To deploy the TTS Service, navigate to the directory containing `tts.sh` and execute the script:
Ensure you have execution permissions set on the script:
```bash
chmod +x tts.sh
```

```bash
./tts.sh
```


### Testing the Service
To ensure that the TTS Service is functioning correctly, perform a test using port-forwarding and curl to interact with the
service's health check endpoint.

1. **Port-forwarding**:
   Use kubectl to forward a local port to the service:
   ```bash
   kubectl port-forward deployment/tts-service 8080:8080
   ```

## Conclusion
The TTS Service is integral to the "Multilingual Podcast Translation Service" project, making translated content accessible through audio.
By providing high-quality audio outputs of translated texts, this service ensures that podcasts are enjoyable and accessible to a global audience, 
thereby enhancing user engagement and satisfaction.
