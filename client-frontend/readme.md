# Frontend Service

## Introduction
The Frontend Service for the "Multilingual Podcast Translation Service" project provides a user interface that allows users to interact with the translation system.
This service is crucial for submitting audio files for translation, selecting Source & Target languages, and receiving both translated text and audio playback directly in the web browser.

## Setup Instructions

### Prerequisites
- A Google Cloud Platform (GCP) account with billing enabled.
- Access to Google Compute Engine with permissions to create VM instances and set firewall rules.

### Configuration and Deployment
Before deploying the frontend, ensure the external IP addresses for service endpoints in the script files are correctly updated to match your environment.

#### 1. Virtual Machine Setup
Create a Virtual Machine (VM) instance in Google Cloud Compute Engine to host the frontend service. After creation, note the external IP address of this VM.

#### 2. Update JavaScript File
Modify the `script.js` to update endpoints with the external IP address of the ingress. This step ensures the frontend can correctly communicate with the backend services.

#### 3. Deploying the Frontend
Transfer the frontend files (HTML, CSS, JavaScript) to the VM and configure the web server (Nginx) to serve these files.

## Modifications
- **File Paths and IP Addresses**: Review and adjust the paths in the commands and scripts to align with your GCP settings and local directory structure.
- **IP Address Update**: Replace the placeholders <Ingress_IP_Addresse> in the `script.js` file with the actual external IP address of your ingress to ensure correct service interaction.

### Using the Scripts
To deploy the Frontend Service, execute the following scripts step-by-step:

1. **Creating a VM and Setting Up Firewall Rules**:
   Navigate to the directory containing `create_vm.sh` and execute the script to create a VM and configure firewall rules:
   Ensure the script has execution permissions:
   ```bash
   chmod +x create_vm.sh
   ```

   ```bash
   ./create_vm.sh
   ```


3. **Transferring Files and Configuring the Web Server**:
   After updating the JavaScript file, use `transfer.sh` to transfer all frontend files to the VM and configure the Nginx web server:
   
   Ensure the script has execution permissions:
   ```bash
   chmod +x transfer.sh
   ```
   
   ```bash
   ./transfer.sh
   ```


### Testing the Service
To ensure that the Frontend Service is functioning correctly, access the external IP address of the VM using a web browser.
The interface should load, allowing you to upload audio files, select languages, and receive translations both in text and audio forms.

## Conclusion
The Frontend Service is a critical component of the "Multilingual Podcast Translation Service" project, facilitating user interaction
with the system's translation capabilities. Proper setup and configuration are essential to ensure a seamless and responsive user experience,
enabling users to easily translate and listen to multilingual content.
