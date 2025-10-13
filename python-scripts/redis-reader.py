import redis
import json

# --- Configuration ---
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
TEST_KEY = 'kafka_data:my_test_topic_0_1' # Example key from the previous Kafka script
KEY_PATTERN = 'kafka_data:*'              # Pattern to find all keys stored by the Kafka script

def connect_to_redis(host, port):
    """
    Establishes and returns a connection to the Redis server.
    """
    try:
        # decode_responses=True means Redis returns strings instead of bytes
        r = redis.Redis(host=host, port=port, decode_responses=True)
        r.ping() # Check connection
        print(f"Successfully connected to Redis at {host}:{port}")
        return r
    except redis.exceptions.ConnectionError as e:
        print(f"ERROR: Could not connect to Redis. Please check Redis server status. {e}")
        return None

def get_single_key(redis_client, key):
    """
    Retrieves and prints the value for a single specific key.
    """
    print(f"\n--- Reading Single Key: {key} ---")
    
    value = redis_client.get(key)
    
    if value:
        print(f"Key: {key}")
        print(f"Raw Value: {value}")
        
        # If the value is stored as a JSON string (as in the Kafka example), parse it back to a Python object
        try:
            data = json.loads(value)
            print(f"Parsed Data (Python Dict): {data}")
            print(f"Example data field: {data.get('sensor', 'N/A')}")
        except json.JSONDecodeError:
            print("Value is not valid JSON, treating as plain string.")
    else:
        print(f"Key '{key}' not found in Redis.")

def get_multiple_keys(redis_client, pattern):
    """
    Uses the KEYS command (or SCAN for production) to find and display multiple keys.
    """
    print(f"\n--- Reading Multiple Keys matching Pattern: {pattern} ---")
    
    # NOTE: The KEYS command can block the Redis server for large databases.
    # For production environments, the SCAN command is preferred for iterating keys.
    # Here, we use KEYS for simplicity in a small script.
    keys_found = redis_client.keys(pattern)
    
    if keys_found:
        print(f"Found {len(keys_found)} keys matching '{pattern}'.")
        
        # Retrieve all values at once using the MGET command (more efficient than a loop of GETs)
        values = redis_client.mget(keys_found)

        for key, value in zip(keys_found, values):
            if value:
                # Value will be a string because of decode_responses=True
                try:
                    data = json.loads(value)
                    print(f"  - Key: {key}, Value: {data.get('value')}")
                except json.JSONDecodeError:
                    print(f"  - Key: {key}, Value: (Decoding Error)")
            
    else:
        print(f"No keys found matching the pattern '{pattern}'.")


if __name__ == "__main__":
    redis_conn = connect_to_redis(REDIS_HOST, REDIS_PORT)
    
    if redis_conn:
        # 1. Read a single key
        get_single_key(redis_conn, TEST_KEY)
        
        # 2. Read multiple keys using a pattern
        get_multiple_keys(redis_conn, KEY_PATTERN)
        
        print("\n--- Script Finished ---")