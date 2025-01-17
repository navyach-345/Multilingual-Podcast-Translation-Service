# BigQuery Service

## Introduction
The BigQuery Service in the "Multilingual Podcast Translation Service" project is responsible for managing and analyzing metadata associated
with the translation and text-to-speech conversion processes. It utilizes Google Cloud BigQuery to store, update, and retrieve metadata efficiently,
enabling robust data analytics capabilities that support multilingual processing workflows.

## Setup Instructions

### Prerequisites
- Google Cloud Platform (GCP) account with billing enabled.
- BigQuery API enabled on your GCP account.
- Configured `kubectl` command-line tool with access to your Kubernetes cluster.
- Google Cloud SDK (`gcloud`) installed and configured on your machine.

### Configuration and Deployment
Follow the changes below as noted in the respective `.sh` file.

#### 1. Enabling BigQuery API
Enable the BigQuery API to interact with BigQuery services.
*Note: This step is crucial for creating datasets and tables necessary for the project.*

#### 2. Creating a BigQuery Dataset
Establish a dataset in BigQuery designed specifically to hold the project's metadata tables.
*Note: Modify the dataset description and location as necessary.*

#### 3. Creating a BigQuery Table
Set up a table within the dataset to store metadata using a predefined schema.
*Note: Ensure the schema file path matches the location of your schema definition.*

#### 4. Creating a Kubernetes Secret for Service Account
Create a Kubernetes secret to securely store the service account key, enabling secure interactions with BigQuery from within the Kubernetes cluster.
*Note: Replace the path with the path to your service account key.*

#### 5. Deploying BigQuery Service to Kubernetes Cluster
Build and deploy the BigQuery Service using the provided Makefile and Kubernetes configuration files.
*Note: Adjust the paths in the commands according to the location of your files.*

## Modifications
- **BigQuery API**: Ensure the BigQuery API is enabled in your Google Cloud project.
- **Dataset and Table Creation**: Verify that the dataset and table are correctly set up with the appropriate permissions.
- **Service Account and Key Path**: Check that the service account key path in your Kubernetes secret creation step is correct.
- **File Paths**: Modify any file paths in the script to match the directory structure on your machine where the necessary files are located.

### Using the Script
To execute the setup for the BigQuery Service, navigate to the directory containing `bigquery.sh` and run the script:
Ensure you have execution permissions set on the script:
```bash
chmod +x bigquery.sh
```


```bash
./bigquery.sh
```

### Testing the Service
To test the BigQuery Service, use port-forwarding verify the service's functionality:

**Port-forwarding**:
   Use kubectl to forward a local port to the service:
   ```bash
   kubectl port-forward deployment/bigquery-service 8080:8080
   ```


## Conclusion
With the BigQuery Service fully operational, it becomes a critical component in managing the metadata necessary for processing and translating multilingual content. This service ensures that data-driven insights are accessible, supporting the efficient execution of translation tasks across various languages in the "Multilingual Podcast Translation Service" project.
