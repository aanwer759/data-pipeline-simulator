from kafka import KafkaConsumer
import redis
import json
import time

# --- Configuration ---
KAFKA_BROKER = 'localhost:9092'     # Kafka Broker address
KAFKA_TOPIC = 'device-1'       # Topic to read from
GROUP_ID = 'redis-pusher-group'     # Consumer group ID

REDIS_HOST = 'localhost'            # Redis server host
REDIS_PORT = 6379                   # Redis server port
REDIS_KEY_PREFIX = 'device1_data:'    # Prefix for keys stored in Redis

def json_deserializer(m_bytes):
    """
    Deserializes bytes back into a Python object (dictionary).
    """
    try:
        return json.loads(m_bytes.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error decoding message: {e}")
        return None

def connect_to_redis(host, port):
    """
    Establishes and returns a connection to the Redis server.
    """
    try:
        r = redis.Redis(host=host, port=port, decode_responses=False)
        r.ping() # Check connection
        print(f"Successfully connected to Redis at {host}:{port}")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"ERROR: Could not connect to Redis. Please check Redis server status. {e}")
        return None

def push_to_redis(redis_client, message, key_prefix):
    """
    Stores the Kafka message data in Redis.
    Uses the message key from Kafka, or generates one if it doesn't exist.
    """
    
    # 1. Determine the key for Redis
    if message.key:
        # Use the Kafka message key (must be decoded from bytes)
        key_suffix = message.key.decode('utf-8')
    else:
        # Generate a key based on topic and offset if no key is provided
        key_suffix = f"{message.topic}_{message.partition}_{message.offset}"
        
    redis_key = key_prefix + key_suffix
    
    # 2. Prepare the value
    # The message.value is already the deserialized Python object (dict)
    # Convert it back to a JSON string (bytes) for storage in Redis
    redis_value = json.dumps(message.value).encode('utf-8')
    
    try:
        # 3. Store the key-value pair in Redis
        # The 'set' command stores a simple string value
        redis_client.set(redis_key, redis_value)
        
        print(f"  -> Successfully stored in Redis. Key: {redis_key}")
        
        # Optional: Set an expiration time (e.g., 1 hour)
        # redis_client.expire(redis_key, 3600) 

    except Exception as e:
        print(f"  -> ERROR: Failed to push data to Redis for key {redis_key}. {e}")


def run_consumer_and_pusher(broker, topic, group_id, redis_host, redis_port, key_prefix):
    """
    Creates a Kafka Consumer, reads messages, and pushes them to Redis.
    """
    # 1. Connect to Redis
    redis_conn = connect_to_redis(redis_host, redis_port)
    if redis_conn is None:
        return # Exit if Redis connection fails

    try:
        # 2. Create Kafka Consumer instance
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[broker],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=group_id,
            value_deserializer=json_deserializer # Function to convert value bytes to Python dict
        )

        print(f"\n--- Listening for messages on topic: {topic} ---")
        
        # 3. Start consuming messages
        for message in consumer:
            print(f"\nReceived msg from Partition {message.partition}, Offset {message.offset}:")
            
            # message.value is the deserialized Python object (dict)
            if message.value is not None:
                push_to_redis(redis_conn, message, key_prefix)
            
            # Optional: Add a small delay
            # time.sleep(0.1)

    except Exception as e:
        print(f"An error occurred in the consumer loop: {e}")
    finally:
        if 'consumer' in locals():
            consumer.close()
            print("\nConsumer closed.")

if __name__ == "__main__":
    run_consumer_and_pusher(
        KAFKA_BROKER, KAFKA_TOPIC, GROUP_ID, 
        REDIS_HOST, REDIS_PORT, REDIS_KEY_PREFIX
    )