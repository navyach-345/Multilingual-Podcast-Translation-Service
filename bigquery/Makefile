# Define variables
VERSION=latest
PROJECT_ID=speech-translation-443516
SERVICE_NAME=bigquery-service
IMAGE_PATH=gcr.io/$(PROJECT_ID)/$(SERVICE_NAME)
DOCKERFILE=Dockerfile

# Build the Docker image
build:
	docker build -f $(DOCKERFILE) -t $(SERVICE_NAME)-image .

# Tag and push the Docker image to GCR
push:
	docker tag $(SERVICE_NAME)-image $(IMAGE_PATH):$(VERSION)
	docker push $(IMAGE_PATH):$(VERSION)
	docker tag $(SERVICE_NAME)-image $(IMAGE_PATH):latest
	docker push $(IMAGE_PATH):latest
