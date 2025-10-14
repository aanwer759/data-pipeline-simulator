from kafka import KafkaProducer
import json
import time
import random
import socket 

# --- Configuration ---
# Replace 'localhost:9092' with your Kafka broker's address if needed
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'device-1' # Replace with your desired topic name

def json_serializer(data):
    """
    Serializes Python dictionary/object to a JSON string bytes.
    """
    return json.dumps(data).encode('utf-8')

def push_data_to_kafka(broker, topic):
    """
    Creates a KafkaProducer and sends sample messages to a topic.
    """
    try:
        # Create a Kafka Producer instance
        producer = KafkaProducer(
            bootstrap_servers=[broker],
            value_serializer=json_serializer,
            # Acknowledges all replicas before considering the message sent
            acks='all'
        )
        
        print(f"Successfully connected to Kafka broker at {broker}")
        
        # Sample data to send
        data_points = [
            {"id": 1, "sensor": "temp", "value": random.randint(10,50), "timestamp": time.time()},
            {"id": 2, "sensor": "humidity", "value": random.randint(10,80), "timestamp": time.time()},
            {"id": 3, "sensor": "pressure", "value": random.randint(50,1500), "timestamp": time.time()}
        ]

        # Send messages
        for i, data in enumerate(data_points):
            # The .send() method is asynchronous
            future = producer.send(topic, value=data)
            
            # Optional: Block until the message is sent (useful for debugging/small scripts)
            record_metadata = future.get(timeout=10) 
            
            print(f"Sent message {i+1} to topic '{record_metadata.topic}', "
                  f"partition {record_metadata.partition}, "
                  f"offset {record_metadata.offset}")

            # Wait a little before sending the next message
            time.sleep(0.5) 

        # Block until all outstanding messages are delivered
        producer.flush()
        print("\nAll messages successfully flushed and sent.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'producer' in locals():
            producer.close()
            print("Producer closed.")

if __name__ == "__main__":
    HOST_NAME = socket.gethostname()
    print(f"HOSTNAME : {HOST_NAME}")
    print(f"--- Starting Kafka Producer for topic: {KAFKA_TOPIC} ---")
    push_data_to_kafka(KAFKA_BROKER, KAFKA_TOPIC)
    print("--- Script Finished ---")