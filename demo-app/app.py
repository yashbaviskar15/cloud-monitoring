import time
import random
import os
from flask import Flask, request, jsonify, send_from_directory
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Path to the dashboard directory (checks local ./dashboard or sibling ../dashboard)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DASHBOARD_DIR = os.path.join(BASE_DIR, 'dashboard')
SIBLING_DASHBOARD_DIR = os.path.join(os.path.dirname(BASE_DIR), 'dashboard')

if os.path.exists(LOCAL_DASHBOARD_DIR):
    DASHBOARD_DIR = LOCAL_DASHBOARD_DIR
else:
    DASHBOARD_DIR = SIBLING_DASHBOARD_DIR

# Custom application-level metrics
HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total number of HTTP requests received',
    ['method', 'endpoint', 'status']
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

@app.before_request
def handle_preflight_and_timer():
    if request.method == "OPTIONS":
        res = app.make_default_options_response()
        res.headers.add("Access-Control-Allow-Origin", "*")
        res.headers.add("Access-Control-Allow-Headers", "*")
        res.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        return res
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    # Retrieve endpoint name (default to path if endpoint is not matched)
    endpoint = request.endpoint or request.path
    
    # Exclude /metrics and /dashboard from our custom HTTP metrics to avoid scraping noise
    if endpoint not in ('metrics', 'dashboard', 'health') and not request.path.startswith('/dashboard'):
        latency = time.time() - getattr(request, 'start_time', time.time())
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
        
        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(latency)
        
    # Enable CORS headers for the frontend UI dashboard
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    return response

@app.route('/')
def home():
    # Introduce random artificial latency (10ms to 150ms) to make the histogram interesting
    time.sleep(random.uniform(0.01, 0.15))
    return jsonify({
        "status": "success",
        "message": "Welcome to the Instrument Demo Application!",
        "timestamp": time.time()
    })

@app.route('/slow')
def slow():
    # Introduce larger latency (200ms to 800ms)
    time.sleep(random.uniform(0.2, 0.8))
    return jsonify({
        "status": "success",
        "message": "This was a slow response",
        "latency": "slow"
    })

@app.route('/error')
def error():
    # Simulate application error response
    time.sleep(random.uniform(0.02, 0.1))
    return jsonify({
        "status": "error",
        "message": "Internal Server Error simulated!"
    }), 500

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "service": "devops-monitoring-stack",
        "timestamp": time.time()
    })

@app.route('/metrics')
def metrics():
    # Expose Prometheus formatted metrics
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/dashboard')
def dashboard():
    # Serve the monitoring control center UI
    return send_from_directory(DASHBOARD_DIR, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
