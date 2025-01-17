import logging
import json
from flask import Flask
from google.cloud import speech
from google.cloud import pubsub_v1
import threading

# Flask app for health checks
app = Flask(__name__)

@app.route('/healthz', methods=['GET'])
def healthz():
    return "OK", 200

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def transcribe_speech(audio_url, language_code):
    """
    Transcribes speech from an audio file stored in GCS using Google Speech-to-Text API.
    """
    try:
        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(uri=audio_url)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True
        )
        operation = client.long_running_recognize(config=config, audio=audio)
        logging.info("Waiting for transcription operation to complete...")
        response = operation.result(timeout=1800)

        transcript = "".join(result.alternatives[0].transcript for result in response.results)
        logging.info("Transcription completed successfully.")
        return transcript
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        raise

def publish_to_queue(project_id, topic_name, message):
    """
    Publishes the message to the next queue.
    """
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)
        message_json = json.dumps(message, ensure_ascii=False)
        future = publisher.publish(topic_path, message_json.encode("utf-8"))
        logging.info(f"Published message to topic {topic_name}: {message_json}")
        return future.result()
    except Exception as e:
        logging.error(f"Error publishing message to {topic_name}: {e}")
        raise

def process_messages(project_id, subscription_name):
    """
    Processes messages from the subscription using streaming_pull.
    """
    def callback(message):
        try:
            logging.info(f"Received message ID: {message.message_id}")
            logging.info(f"Message data: {message.data.decode('utf-8')}")
            data = json.loads(message.data.decode("utf-8"))

            # Extract metadata and job ID
            audio_url = data["audio_url"]
            source_language = data["source_language"]
            job_id = data["job_id"]  # Receive job ID from incoming message

            # Transcribe the audio
            transcribed_text = transcribe_speech(audio_url, source_language)

            # Update metadata to include transcribed text and propagate job ID
            updated_data = {
                "job_id": job_id,
                "audio_url": audio_url,
                "source_language": source_language,
                "target_language": data["target_language"],
                "transcribed_text": transcribed_text
            }

            # Publish updated data to Queue 2
            publish_to_queue(project_id, "queue2", updated_data)

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
    # Pub/Sub configuration
    project_id = "speech-translation-443516"
    subscription_name = "queue1-sub"

    logging.info("Running STT.py")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Process messages from queue1 using streaming_pull
    process_messages(project_id, subscription_name)
    