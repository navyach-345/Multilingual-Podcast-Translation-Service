from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import redis
import tempfile
from google.cloud import storage, pubsub_v1
import json
import logging
import hashlib

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://<VM_IP_Address>"}}, supports_credentials=True)  

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Health check endpoint
@app.route("/healthz", methods=["GET"])
def healthz():
    return "OK", 200

app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # Limit file size to 50 MB

# Redis configuration
redis_client = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "redis-service"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

# Google Cloud configuration
PROJECT_ID = "speech-translation-443516"
INPUT_BUCKET = "podcast_storage_bucket-input"

gcs_client = storage.Client()

def generate_job_id(audio_file, source_language, target_language):
    # Generate a unique ID based on file content and language parameters
    audio_file.seek(0)  # Reset file pointer
    file_content = audio_file.read()
    hasher = hashlib.sha256()
    hasher.update(file_content)
    hasher.update(source_language.encode('utf-8'))
    hasher.update(target_language.encode('utf-8'))
    return hasher.hexdigest()

def check_cache(job_id):
    text_key = f"{job_id}_text"
    audio_key = f"{job_id}_audio"
    encoded_text = redis_client.get(text_key)
    encoded_audio = redis_client.get(audio_key)
    logging.info(f"Cache check: text_key={text_key}, audio_key={audio_key}")
    return encoded_text, encoded_audio

def upload_file_to_gcs(file_path, bucket_name, destination_blob_name):
    try:
        bucket = gcs_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        logging.info(f"File uploaded to GCS: gs://{bucket_name}/{destination_blob_name}")
        return f"gs://{bucket_name}/{destination_blob_name}"
    except Exception as e:
        logging.error(f"Error uploading file to GCS: {e}")
        raise

def publish_message_to_queue(audio_url, source_language, target_language, job_id):
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(PROJECT_ID, "queue1")
        message = {
            "audio_url": audio_url,
            "source_language": source_language,
            "target_language": target_language,
            "job_id": job_id  
        }
        logging.info(f"Publishing message to queue1: {message}")
        future = publisher.publish(topic_path, json.dumps(message).encode("utf-8"))
        result = future.result()
        logging.info(f"Published message to queue1: {result}")
        return result
    except Exception as e:
        logging.error(f"Error publishing message to queue1: {e}")
        raise

@app.route("/translate", methods=["POST"])
def translate():
    try:
        logging.info("Starting the request...")
        audio_file = request.files.get("file")
        source_language = request.form.get("source_language")
        target_language = request.form.get("target_language")

        if not audio_file or not source_language or not target_language:
            logging.warning("Missing required input")
            return jsonify({"error": "Missing required input"}), 400

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        audio_file.save(temp_file.name)

        # Generate a job ID based on the file content and languages
        job_id = generate_job_id(audio_file, source_language, target_language)

        # Check Redis Cache
        encoded_text, encoded_audio = check_cache(job_id)
        if encoded_text and encoded_audio:
            logging.info("Cache hit: Returning cached results.")
            return jsonify({"text": encoded_text, "audio": encoded_audio}), 200

        # Upload to GCS and get GCS URL
        gcs_url = upload_file_to_gcs(temp_file.name, INPUT_BUCKET, audio_file.filename)

        # Publish to Queue1
        publish_message_to_queue(gcs_url, source_language, target_language, job_id)

        return jsonify({"message": "Your request is being processed", "job_id": job_id}), 202

    except Exception as e:
        logging.error(f"Error in translate endpoint: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if "temp_file" in locals():
            os.remove(temp_file.name)

@app.route("/results/<job_id>", methods=["GET"])
def get_results(job_id):
    logging.info(f"checking the cache with job id {job_id}..........")
    encoded_text, encoded_audio = check_cache(job_id)
    if encoded_text and encoded_audio:
        logging.info("Returning results from cache.")
        return jsonify({"text": encoded_text, "audio": encoded_audio}), 200
    else:
        logging.info("Results not ready yet.")
        return jsonify({"error": "Results not ready yet", "status": "processing"}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    
    