import os
import time
import psycopg2
from flask import Flask, jsonify, request, abort

# Initialize Flask application
app = Flask(__name__)

# --- Database Connection Logic ---

def get_db_connection():
    """
    Attempts to establish a connection to the PostgreSQL database using environment variables.
    Implements a retry mechanism (5 attempts, 5 seconds delay) to wait for the database
    container to become available.
    """
    db_host = os.environ.get('DB_HOST')
    db_name = os.environ.get('DB_NAME')
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASS')

    retries = 5
    while retries > 0:
        try:
            # Attempt to connect
            conn = psycopg2.connect(
                host=db_host,
                database=db_name,
                user=db_user,
                password=db_pass
            )
            return conn
        except psycopg2.OperationalError as e:
            retries -= 1
            app.logger.warning(f"Database not ready. Retries left: {retries}. Error: {e}")
            time.sleep(5)
        
    app.logger.error("Could not connect to database after multiple retries.")
    return None

# --- API Endpoints ---

@app.route("/db-health", methods=["GET"])
def db_health_check():
    """
    Checks the status of the database connection.
    Returns 200 (OK) if connection is successful, 500 otherwise.
    """
    conn = get_db_connection()

    if conn is None:
        return jsonify({
            "status": "error", 
            "message": "Database connection failed after retries."
        }), 500

    # If connection was successful, close it immediately and return success
    conn.close()
    return jsonify({"status": "ok", "message": "Database connection successful"})

# Note: The previous in-memory news code would go here.

# --- Application Startup ---

if __name__ == "__main__":
    # Ensure all database environment variables are set for clear operation
    if not all(os.environ.get(v) for v in ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASS']):
        print("WARNING: Database environment variables (DB_HOST, DB_NAME, etc.) are missing.")
    
    # Run the Flask application
    app.run(threaded=True, host='0.0.0.0', port=3000)
