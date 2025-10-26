import time
import random
from prometheus_client import start_http_server, Counter, Gauge

# --- Configuration ---
EXPORTER_PORT = 8000
SCRAPE_INTERVAL = 5  # Time in seconds for metric updates

# --- Metric Definitions ---

# 1. Counter: A metric that can only increase (e.g., total requests)
REQUEST_COUNT = Counter(
    'app_http_requests_total', 
    'Total number of simulated HTTP requests processed.', 
    ['method', 'endpoint']
)

# 2. Gauge: A metric that can go up and down (e.g., current active users)
ACTIVE_USERS = Gauge(
    'app_active_users', 
    'Current number of simulated active users.'
)

def simulate_data():
    """Simulates metric updates periodically."""
    while True:
        # 1. Increment the Counter: Simulate an API call
        method = random.choice(['GET', 'POST'])
        endpoint = random.choice(['/home', '/status'])
        
        # Increment the counter for the specific labels
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        
        # 2. Set the Gauge: Simulate fluctuating active users
        # Generates a random number between 10 and 50
        current_users = random.randint(10, 50)
        ACTIVE_USERS.set(current_users)
        
        print(f"Metrics updated: Requests={REQUEST_COUNT.collect()[0].samples[0].value}, Users={current_users}")
        time.sleep(SCRAPE_INTERVAL)

if __name__ == '__main__':
    # Start the HTTP server to expose metrics
    try:
        start_http_server(EXPORTER_PORT)
        print(f"✅ Prometheus metrics exposed on port {EXPORTER_PORT}")
        print(f"   Scrape URL: http://localhost:{EXPORTER_PORT}/metrics")
        
        # Start the loop to update the metric values
        simulate_data()
    except Exception as e:
        print(f"❌ Failed to run exporter: {e}")