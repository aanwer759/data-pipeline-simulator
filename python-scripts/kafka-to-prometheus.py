import time
import json
import logging
from kafka import KafkaConsumer
from prometheus_client import start_http_server, Counter, Histogram

# --- Configuration ---
KAFKA_BROKERS = ['localhost:9092']  # Replace with your Kafka broker list
KAFKA_TOPIC = 'your_topic_name'      # Replace with your topic name
PROMETHEUS_PORT = 8000
CONSUMER_GROUP_ID = 'prometheus-exporter-group'

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Prometheus Metric Definitions ---
# 1. Counter: Tracks the total number of messages processed
MESSAGES_PROCESSED_TOTAL = Counter(
    'kafka_consumer_messages_processed_total',
    'Total number of messages successfully processed from Kafka.',
    ['topic', 'partition']  # Labels for powerful filtering/aggregation in Prometheus
)

# 2. Histogram: Tracks the distribution of message processing times
MESSAGE_PROCESSING_TIME = Histogram(
    'kafka_consumer_message_process_seconds',
    'Time spent processing a Kafka message payload.'
)

# 3. Custom Counter Example: Tracks a metric *derived* from the message payload
# Assuming your message payload is JSON with a 'value' field.
TOTAL_VALUE_SUM = Counter(
    'kafka_message_payload_value_sum',
    'Cumulative sum of the "value" field from all messages.'
)

def process_message(message):
    """
    Core function to deserialize the message and extract/calculate metrics.
    """
    try:
        # Use a context manager to automatically track processing time
        with MESSAGE_PROCESSING_TIME.time():
            # 1. Decode the message value (assuming UTF-8 encoded JSON)
            raw_data = message.value.decode('utf-8')
            data = json.loads(raw_data)
            
            # --- Business Logic & Custom Metric Calculation ---
            
            # Example: Increment the custom counter by a value from the message
            if 'value' in data and isinstance(data['value'], (int, float)):
                TOTAL_VALUE_SUM.inc(data['value'])
            
            # Example: Log the processed message (optional)
            logging.debug(f"Processed message from {message.topic}-{message.partition}: Offset {message.offset}")
            
            # 2. Increment the standard message counter with labels
            MESSAGES_PROCESSED_TOTAL.labels(
                topic=message.topic,
                partition=message.partition
            ).inc()

    except json.JSONDecodeError:
        logging.error(f"Failed to decode message as JSON: {message.value}")
    except Exception as e:
        logging.error(f"An error occurred during message processing: {e}")

def run_kafka_consumer():
    """
    Initializes the Kafka consumer and starts the main consumption loop.
    """
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKERS,
            group_id=CONSUMER_GROUP_ID,
            auto_offset_reset='latest',  # Start reading from the latest offset
            enable_auto_commit=True,
            value_deserializer=None  # We'll decode manually in process_message
        )
        
        logging.info(f"Consumer started for topic: {KAFKA_TOPIC}")

        # Main loop to read messages
        for message in consumer:
            process_message(message)
            
    except Exception as e:
        logging.critical(f"Kafka consumer failed: {e}")
    finally:
        if 'consumer' in locals():
            consumer.close()
            logging.info("Kafka consumer closed.")

# --- Main Execution Block ---
if __name__ == '__main__':
    # 1. Start the Prometheus HTTP server on a separate thread
    try:
        start_http_server(PROMETHEUS_PORT)
        logging.info(f"Prometheus metrics exposed on http://localhost:{PROMETHEUS_PORT}/metrics")
    except Exception as e:
        logging.critical(f"Failed to start Prometheus server: {e}")
        exit(1)
        
    # 2. Start the Kafka consumer loop (this will block the main thread)
    run_kafka_consumer()