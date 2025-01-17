import logging
import json
import base64
import requests
from flask import Flask
from google.cloud import pubsub_v1
import redis
import threading

app = Flask(__name__)

@app.route('/healthz', methods=['GET'])
def healthz():
    return "OK", 200

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CacheService:
    def __init__(self, host="redis-service", port=6379, db=0):
        """
        Initialize the Redis cache client.
        """
        try:
            self.redis_client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)
            logging.info("Connected to Redis.")
        except Exception as e:
            logging.error(f"Error connecting to Redis: {e}")
            raise

    def add_to_cache(self, key, encoded_data, ttl=3600):
        """
        Add encoded data to Redis with a key and TTL.
        """
        try:
            self.redis_client.setex(key, ttl, encoded_data)
            logging.info(f"Data stored in cache with key: {key}")
        except Exception as e:
            logging.error(f"Error adding data to cache: {e}")
            raise

    def get_from_cache(self, key):
        """
        Retrieve data from Redis using a key.
        """
        try:
            cached_data = self.redis_client.get(key)
            return cached_data if cached_data else None
        except Exception as e:
            logging.error(f"Error retrieving data from cache: {e}")
            raise

def download_file(signed_url):
    """
    Download a file from a signed URL.
    """
    try:
        response = requests.get(signed_url)
        response.raise_for_status()
        logging.info(f"Downloaded file from {signed_url}")
        return response.content
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        raise

def encode_file_content(content):
    """
    Encode file content into Base64.
    """
    try:
        return base64.b64encode(content).decode("utf-8")
    except Exception as e:
        logging.error(f"Error encoding file content: {e}")
        raise

def process_messages(project_id, subscription_name, cache_service):
    """
    Processes messages from the subscription using streaming_pull.
    """
    def callback(message):
        try:
            logging.info(f"Received message ID: {message.message_id}")
            logging.info(f"Message data: {message.data.decode('utf-8')}")
            data = json.loads(message.data.decode("utf-8"))

            # Extract metadata and signed URLs
            job_id = data["job_id"]
            input_file_name = data["metadata"]["input_audio_file"].split("/")[-1]
            target_language = data["metadata"]["target_language"]
            text_url = data["translated_text_url"]
            audio_url = data["translated_audio_url"]

            # Download and encode files
            text_content = download_file(text_url)
            encoded_text = encode_file_content(text_content)
            logging.info(f"Encoded text stored in cache: {encoded_text}...")
            audio_content = download_file(audio_url)
            encoded_audio = encode_file_content(audio_content)

            # Store encoded data in Redis using job_id
            cache_service.add_to_cache(f"{job_id}_text", encoded_text)
            cache_service.add_to_cache(f"{job_id}_audio", encoded_audio)

            # Acknowledge the message
            message.ack()
            logging.info(f"Message ID {message.message_id} acknowledged successfully.")
            logging.info(f"Data stored in cache with keys: {job_id}_text and {job_id}_audio")
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
    # Redis configuration
    redis_host = "redis-service"
    redis_port = 6379
    redis_db = 0 

    # Pub/Sub configuration
    project_id = "speech-translation-443516"
    subscription_name = "queue6-sub"

    logging.info("Running cache.py")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Initialize Redis and process messages from queue6-sub
    cache_service = CacheService(host=redis_host, port=redis_port, db=redis_db)
    process_messages(project_id, subscription_name, cache_service)
