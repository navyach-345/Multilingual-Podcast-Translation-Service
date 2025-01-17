import logging
import os
import json
from flask import Flask
from gtts import gTTS
from google.cloud import storage, pubsub_v1
from mutagen.mp3 import MP3
import threading
import time
import requests

# Flask app for health checks
app = Flask(__name__)

@app.route('/healthz', methods=['GET'])
def healthz():
    return "OK", 200

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set bucket name explicitly
bucket_name = "podcast_storage_bucket-input"

def upload_to_gcs_and_get_signed_url(project_id, bucket_name, blob_name, file_path, expiration=3600):
    """
    Uploads a file to GCS and generates a signed URL.
    """
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(file_path)
        signed_url = blob.generate_signed_url(expiration=expiration, version="v4")
        logging.info(f"Uploaded file {file_path} to GCS and generated signed URL: {signed_url}")
        return signed_url
    except Exception as e:
        logging.error(f"Error uploading file to GCS: {e}")
        raise

def get_audio_duration(file_path):
    """
    Returns the duration of the audio file in seconds.
    """
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        logging.error(f"Error calculating audio duration: {e}")
        raise

def tts_with_retry(text, lang, retries=5, backoff_factor=2):
    """
    Generate TTS audio with retries for handling rate limits or transient errors.
    """
    for attempt in range(retries):
        try:
            tts = gTTS(text, lang=lang)
            return tts
        except Exception as e:
            if "429" in str(e) or isinstance(e, requests.exceptions.HTTPError):
                logging.warning(f"Retry {attempt + 1}/{retries} due to rate limit: {e}")
                time.sleep(backoff_factor ** attempt)  
            else:
                logging.error(f"Error during TTS generation: {e}")
                raise
    raise Exception("Exceeded maximum retries for TTS generation.")

def publish_to_queue(project_id, topic_name, message):
    """
    Publishes the processed metadata to the next queue.
    """
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)
        message_json = json.dumps(message, ensure_ascii=False)
        future = publisher.publish(topic_path, message_json.encode("utf-8"))
        logging.info(f"Published message to {topic_name}: {message_json}")
        return future.result()
    except Exception as e:
        logging.error(f"Error publishing message: {e}")
        raise

def process_messages(project_id, subscription_name, bucket_name):
    """
    Processes messages from the subscription using streaming_pull.
    """
    def callback(message):
        try:
            logging.info(f"Received message ID: {message.message_id}")
            logging.info(f"Message data: {message.data.decode('utf-8')}")
            metadata = json.loads(message.data.decode("utf-8"))

            # Extract translated text and target language
            translated_text = metadata["translated_text"]
            target_language = metadata["target_language"]
            job_id = metadata["job_id"]  # Receive job ID from incoming message

            # Generate TTS audio with retry
            audio_output_path = "/tmp/translated_audio_output.mp3"
            tts = tts_with_retry(translated_text, target_language)
            tts.save(audio_output_path)
            logging.info("TTS audio generated successfully.")

            # Upload files to GCS and get signed URLs
            translated_audio_signed_url = upload_to_gcs_and_get_signed_url(
                project_id, bucket_name, "translated_audio_output.mp3", audio_output_path
            )
            translated_text_path = "/tmp/translated_text.txt"
            with open(translated_text_path, "w", encoding='utf-8') as text_file:
                text_file.write(translated_text)
            translated_text_signed_url = upload_to_gcs_and_get_signed_url(
                project_id, bucket_name, "translated_text.txt", translated_text_path
            )

            # Prepare metadata for Queue 4
            final_metadata = {
                "job_id": job_id,
                "metadata": {
                    "input_audio_file": metadata["audio_url"],
                    "output_audio_file": os.path.basename(audio_output_path),
                    "output_audio_length_seconds": get_audio_duration(audio_output_path),
                    "source_language": metadata["source_language"],
                    "target_language": metadata["target_language"],
                    "translated_text_length": len(translated_text),
                },
                "translated_text_url": translated_text_signed_url,
                "translated_audio_url": translated_audio_signed_url
            }

            # Publish updated metadata to the next queue (Queue 4)
            publish_to_queue(project_id, "queue4", final_metadata)

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
    project_id = "speech-translation-443516"
    subscription_name = "queue3-sub"

    logging.info("Running TTS.py")
    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Process messages from queue3-sub using streaming_pull
    process_messages(project_id, subscription_name, bucket_name)
