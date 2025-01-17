#!/bin/bash

echo "Starting file transfer and frontend deployment setup..."

# Step 1: Transfer files to the frontend VM
echo "Transferring files to frontend VM..."
gcloud compute scp /home/nach9995/podcast-translation/client-frontend/index.html \
    /home/nach9995/podcast-translation/client-frontend/app.js \
    /home/nach9995/podcast-translation/client-frontend/style.css \
    frontend-vm:~/ --zone=us-central1-a

if [ $? -eq 0 ]; then
    echo "Files transferred successfully."
else
    echo "Failed to transfer files. Exiting."
    exit 1
fi

# Step 2: SSH into the VM and configure it
echo "SSH into the frontend VM to configure it..."
gcloud compute ssh frontend-vm --zone=us-central1-a --command="
    echo 'Updating and installing nginx...'
    sudo apt update && sudo apt install -y nginx

    echo 'Checking nginx status...'
    sudo systemctl status nginx

    echo 'Moving files to nginx web root...'
    sudo mv ~/index.html /var/www/html/index.html
    sudo mv ~/app.js /var/www/html/app.js
    sudo mv ~/style.css /var/www/html/style.css

    echo 'Setting permissions for web root...'
    sudo chmod -R 755 /var/www/html/

    echo 'Restarting nginx to apply changes...'
    sudo systemctl restart nginx

    echo 'Frontend deployment setup complete.'
"

if [ $? -eq 0 ]; then
    echo "Frontend deployment completed successfully."
else
    echo "Failed to configure frontend VM. Exiting."
    exit 1
fi

echo "Exiting frontend VM setup."
