import logging
from google.cloud import storage, pubsub_v1
import requests
import os
import json
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/healthz', methods=['GET'])
def healthz():
    return "OK", 200

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = storage.Client()

def upload_file_to_gcs(signed_url, bucket_name, folder_name, destination_blob_name):
    """
    Downloads a file from a signed URL and uploads it to Google Cloud Storage in a specified folder.
    """
    try:
        logging.info(f"Downloading file from signed URL: {signed_url}")
        response = requests.get(signed_url)
        response.raise_for_status()  

        local_file_path = f"/tmp/{os.path.basename(destination_blob_name)}"
        with open(local_file_path, "wb") as file:
            file.write(response.content)

        logging.info(f"File downloaded successfully: {local_file_path}")

        # Upload file to GCS
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"{folder_name}/{destination_blob_name}")
        blob.upload_from_filename(local_file_path)

        logging.info(f"Uploaded {local_file_path} to gs://{bucket_name}/{folder_name}/{destination_blob_name}")
        return f"gs://{bucket_name}/{folder_name}/{destination_blob_name}"
    except Exception as e:
        logging.error(f"Error uploading file to GCS: {e}")
        raise

def publish_to_queue6(project_id, topic_name, message):
    """
    Publishes the message to queue6.
    """
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)

        # Serialize the message to JSON format
        message_json = json.dumps(message, ensure_ascii=False)
        future = publisher.publish(topic_path, message_json.encode("utf-8"))
        logging.info(f"Published message to {topic_name}: {message_json}")
        return future.result()
    except Exception as e:
        logging.error(f"Error publishing message to {topic_name}: {e}")
        raise

def process_messages(project_id, subscription_name, bucket_name):
    """
    Processes messages from the subscription using streaming_pull.
    """
    def callback(message):
        try:
            logging.info(f"Received message ID: {message.message_id}")
            logging.info(f"Message data: {message.data.decode('utf-8')}")
            data = json.loads(message.data.decode("utf-8"))

            job_id = data.get("job_id")
            metadata = data.get("metadata")
            if not metadata:
                raise ValueError("Missing 'metadata' key in the message.")

            input_audio_file = metadata.get("input_audio_file")
            output_audio_file = metadata.get("output_audio_file")
            translated_text_url = data.get("translated_text_url")
            translated_audio_url = data.get("translated_audio_url")

            if not input_audio_file or not output_audio_file:
                raise ValueError("Missing required keys: 'input_audio_file' or 'output_audio_file' in metadata.")
            if not translated_text_url or not translated_audio_url:
                raise ValueError("Signed URLs missing in the message.")

            # Folder name based on input audio file
            folder_name = input_audio_file

            # Upload translated text
            text_blob_name = f"{output_audio_file}.txt"
            text_gcs_uri = upload_file_to_gcs(translated_text_url, bucket_name, folder_name, text_blob_name)

            # Upload translated audio
            audio_blob_name = f"{output_audio_file}.mp3"
            audio_gcs_uri = upload_file_to_gcs(translated_audio_url, bucket_name, folder_name, audio_blob_name)

            logging.info(f"Successfully processed and uploaded files:")
            logging.info(f"Text File URI: {text_gcs_uri}")
            logging.info(f"Audio File URI: {audio_gcs_uri}")

            # Publish the message to queue6
            publish_to_queue6(project_id, "queue6", data)

            # Acknowledge the message
            message.ack()
            logging.info(f"Message ID {message.message_id} acknowledged successfully.")
        except Exception as e:
            logging.error(f"Error processing message: {e}")

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_name)

    logging.info(f"Listening for messages on subscription: {subscription_path}...")
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

    try:
        streaming_pull_future.result()
    except Exception as e:
        logging.error(f"Error in streaming_pull: {e}")
        streaming_pull_future.cancel()
    finally:
        subscriber.close()

def run_flask():
    """
    Runs the Flask app for health checks.
    """
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    # GCS bucket name
    bucket_name = "output_storage_bucket_podcast_translation"

    # Pub/Sub details
    project_id = "speech-translation-443516"
    subscription_name = "queue5-sub"

    logging.info("Running stor.py")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Process messages from queue5-sub using streaming_pull
    process_messages(project_id, subscription_name, bucket_name)
