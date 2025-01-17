import logging
import json
from flask import Flask
from google.cloud import translate_v2 as translate
from google.cloud import pubsub_v1
import threading

# Flask app for health checks
app = Flask(__name__)

@app.route('/healthz', methods=['GET'])
def healthz():
    return "OK", 200

# Configure logging to handle Unicode characters
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])

def translate_text(text, target_language):
    """
    Translates text to the specified target language using Google Translate API.
    """
    try:
        client = translate.Client()
        result = client.translate(text, target_language=target_language, format_='text')
        translated_text = result["translatedText"]
        logging.info(f"Text successfully translated to {target_language}.")
        logging.info(f"Translated text - {translated_text}")
        return translated_text
    except Exception as e:
        logging.error(f"Error during text translation: {e}")
        raise

def publish_to_queue(project_id, topic_name, message):
    """
    Publishes the processed metadata to the next queue, ensuring UTF-8 encoding.
    """
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)
        message_json = json.dumps(message, ensure_ascii=False)
        future = publisher.publish(topic_path, data=message_json.encode("utf-8"))
        logging.info(f"Published message to {topic_name}: {message_json}")
        return future.result()
    except Exception as e:
        logging.error(f"Error publishing message: {e}")
        raise

def process_messages(project_id, subscription_name):
    """
    Processes messages from the subscription using streaming_pull, ensuring proper Unicode handling.
    """
    def callback(message):
        try:
            logging.info(f"Received message ID: {message.message_id}")
            logging.info(f"Message data: {message.data.decode('utf-8')}")
            metadata = json.loads(message.data.decode("utf-8"))

            # Extract transcribed text and target language
            transcribed_text = metadata["transcribed_text"]
            target_language = metadata["target_language"]
            job_id = metadata["job_id"]  # Receive job ID from incoming message

            # Perform translation
            translated_text = translate_text(transcribed_text, target_language)

			# Update metadata with new fields without losing existing data
            metadata['translated_text'] = translated_text

            # Publish updated metadata to the next queue (Queue 3)
            publish_to_queue(project_id, "queue3", metadata)

            # Acknowledge the message
            message.ack()
            logging.info(f"Message ID {message.message_id} acknowledged successfully.")
        except Exception as e:
            logging.error(f"Error processing message: {e}")

    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription_name)
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
    subscription_name = "queue2-sub"
    
    logging.info("Running Translation.py")

    # Run Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Process messages from queue2-sub using streaming_pull
    process_messages(project_id, subscription_name)
