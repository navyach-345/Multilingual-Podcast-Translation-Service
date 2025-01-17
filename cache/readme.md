# Redis Cache Service

## Introduction
The Redis Cache Service in the "Multilingual Podcast Translation Service" project functions as a high-speed data caching layer.
 By using Redis, this service significantly enhances the performance of data retrieval processes, crucial for delivering fast responses for
 recurring queries within the system, especially in multilingual content management and translation tasks.

## Setup Instructions

### Prerequisites
- Google Cloud Platform (GCP) account with billing enabled.
- Configured `kubectl` command-line tool with access to your Kubernetes cluster.
- Kubernetes cluster operational within your GCP environment.

### Configuration and Deployment
Please make the changes mentioned below as noted in the respective `.sh` file.

#### 1. Creating Redis Deployment and Service
Deploy Redis using the Kubernetes configuration that sets up both the deployment and the necessary service for Redis interaction.
*Note: Adjust the paths in the commands according to where your YAML files are stored.*

## Modifications
- **File Paths**: Adjust file paths in the script to match the directory structure on your machine where the necessary files
 are located, particularly for the deployment and service YAML files.

### Using the Script
To execute the setup for the Redis Cache Service, navigate to the directory containing `cache.sh` and run the script:
Ensure you have execution permissions set on the script:
```bash
chmod +x cache.sh
```

```bash
./cache.sh
```


### Testing the Service
Verify that the Redis Service is operational by performing simple connection tests using port-forwarding and a Redis client tool such as `redis-cli`:

1. **Port-forwarding for Redis Cache**:
   Use kubectl to forward a local port to the Redis cache service:
   ```bash
   kubectl port-forward deployment/cache-service 8080:8080
   ```

2. **Testing with Redis Client for Redis Cache**:
   Connect using the Redis client:
   ```bash
   redis-cli -h localhost -p 8080
   ```
   Try executing commands such as `SET` and `GET` to ensure the cache is functioning correctly.

3. **Port-forwarding for Redis Deployment**:
   Use kubectl to forward a local port to the Redis deployment:
   ```bash
   kubectl port-forward deployment/redis-deployment 6379:6379
   ```

4. **Testing with Redis Client for Redis Deployment**:
   Connect using the Redis client:
   ```bash
   redis-cli -h localhost -p 6379
   ```
   Execute a simple command like `PING` which should return `PONG` if the service is running properly.

These tests confirm the connectivity and readiness of the Redis Cache Service within your Kubernetes cluster, ensuring it
can handle caching operations effectively.

## Conclusion
Once setup and tested, the Redis Cache Service will significantly enhance the system's performance by caching frequently accessed data
related to translation tasks, thus reducing latency and improving the user experience. This service is essential for maintaining high
throughput and responsiveness in the "Multilingual Podcast Translation Service" project, especially when dealing with diverse languages and large datasets.
