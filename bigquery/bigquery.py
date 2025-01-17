import logging
import os
import json
from flask import Flask

from google.cloud import bigquery
from google.cloud import pubsub_v1
import threading

# Initialize Flask app
app = Flask(__name__)

@app.route('/healthz', methods=['GET'])
def healthz():
    return "OK", 200

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize BigQuery client
def connect_to_bigquery():
    try:
        client = bigquery.Client()
        logging.info("Connected to BigQuery.")
        return client
    except Exception as e:
        logging.error(f"Error connecting to BigQuery: {e}")
        raise

def create_table_if_not_exists(client, dataset_name, table_name, schema):
    try:
        # Check if the dataset exists
        dataset_ref = client.dataset(dataset_name)
        try:
            client.get_dataset(dataset_ref)
            logging.info(f"Dataset '{dataset_name}' exists.")
        except Exception:
            # Create the dataset if it doesn't exist
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"  # Specify location if necessary
            client.create_dataset(dataset, timeout=30)
            logging.info(f"Created dataset '{dataset_name}'.")

        # Check if the table exists
        table_ref = dataset_ref.table(table_name)
        try:
            table = client.get_table(table_ref)  
            logging.info(f"Table '{table_name}' already exists.")
            
            # Check if the schema matches the required schema
            existing_schema = {field.name: field.field_type for field in table.schema}
            required_schema = {field.name: field.field_type for field in schema}
            if existing_schema != required_schema:
                logging.warning(f"Schema mismatch detected for table '{table_name}'. Updating schema.")
                table.schema = schema
                client.update_table(table, ["schema"])
                logging.info(f"Schema updated successfully for table '{table_name}'.")
        except Exception:
            # Create the table if it doesn't exist
            table = bigquery.Table(table_ref, schema=schema)
            client.create_table(table)
            logging.info(f"Created table '{table_name}' in dataset '{dataset_name}'.")
    except Exception as e:
        logging.error(f"Error creating or updating table: {e}")
        raise

def insert_data_into_table(client, dataset_name, table_name, rows):
    try:
        table_ref = client.dataset(dataset_name).table(table_name)
        errors = client.insert_rows_json(table_ref, rows)  # Insert rows
        if errors:
            logging.error(f"Errors occurred while inserting data: {errors}")
        else:
            logging.info(f"Inserted data into '{table_name}': {rows}")
    except Exception as e:
        logging.error(f"Error inserting data into table: {e}")
        raise

def publish_to_queue(project_id, topic_name, message):
    try:
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)
        message_json = json.dumps(message, ensure_ascii=False)
        future = publisher.publish(topic_path, message_json.encode("utf-8"))
        logging.info(f"Published message to {topic_name}: {message_json}")
        return future.result()
    except Exception as e:
        logging.error(f"Error publishing message to {topic_name}: {e}")
        raise

def process_messages(project_id, subscription_name, client, dataset_name, table_name):
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
                logging.error("No 'metadata' key found in the message.")
                return

            # Process file names
            input_audio_basename = os.path.splitext(os.path.basename(metadata["input_audio_file"]))[0]
            formatted_output_audio_file = f"{input_audio_basename}-{metadata['target_language']}"

            metadata["input_audio_file"] = input_audio_basename
            metadata["output_audio_file"] = formatted_output_audio_file
            metadata["job_id"] = job_id  

            # Define schema for the table
            schema = [
                bigquery.SchemaField("input_audio_file", "STRING"),
                bigquery.SchemaField("output_audio_file", "STRING"),
                bigquery.SchemaField("output_audio_length_seconds", "FLOAT"),
                bigquery.SchemaField("source_language", "STRING"),
                bigquery.SchemaField("target_language", "STRING"),
                bigquery.SchemaField("translated_text_length", "INTEGER"),
                bigquery.SchemaField("job_id", "STRING"),  
            ]

            # Ensure the table exists
            create_table_if_not_exists(client, dataset_name, table_name, schema)

            # Insert the metadata into the table
            rows_to_insert = [metadata]
            insert_data_into_table(client, dataset_name, table_name, rows_to_insert)

            # Publish the message to the next queue
            publish_to_queue(project_id, "queue5", data)

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
    # Project and BigQuery details
    project_id = "speech-translation-443516"
    subscription_name = "queue4-sub"
    dataset_name = "podcast_data"
    table_name = "podcast_metadata"

    logging.info("Running BigQuery.py")
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    client = connect_to_bigquery()
    process_messages(project_id, subscription_name, client, dataset_name, table_name)
