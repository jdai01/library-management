from flask import Flask, render_template, jsonify, request
import configparser
import requests
import logging
from flask_cors import CORS
import psycopg2
from psycopg2 import OperationalError, DatabaseError

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Configure logging to DEBUG level for detailed logs
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Load the configuration from the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# # Get the API key and URL from the configuration
# try:
#     GEMINI_API_KEY = config.get('API', 'GEMINI_API_KEY')
#     GEMINI_API_URL = config.get('API', 'GEMINI_API_URL')
#     logging.info("Gemini API configuration loaded successfully.")
# except Exception as e:
#     logging.error("Error reading config.ini: %s", e)
#     GEMINI_API_KEY = None
#     GEMINI_API_URL = None

# Database configuration
DB_USER = config.get('DATABASE', 'DB_USER')
DB_PASSWORD = config.get('DATABASE', 'DB_PASSWORD')
DB_HOST = config.get('DATABASE', 'DB_HOST')
DB_PORT = config.get('DATABASE', 'DB_PORT')
DB_NAME = config.get('DATABASE', 'DB_NAME')

def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        logging.info("Database connection successful.")
        return conn
    except psycopg2.Error as e:
        logging.error(f"Database connection failed: {e}")
        return None

# Route to serve the home page
@app.route('/')
def home():
    drop_all_tables()
    initialize_database()
    load_initial_data()
    return render_template('index.html')

# Route to serve viewer.html
@app.route('/viewer.html')
def viewer():
    return render_template('viewer.html')

# # API route to fetch description from Gemini API
# @app.route('/api/description', methods=['GET'])
# def get_description():
#     entity_name = request.args.get('name')
#     logging.debug(f"Received request for entity name: {entity_name}")  # Changed to DEBUG

#     if not entity_name:
#         logging.warning("Missing entity name in request.")
#         return jsonify({'error': 'Missing entity name'}), 400

#     if not GEMINI_API_URL or not GEMINI_API_KEY:
#         logging.error("Gemini API configuration missing.")
#         return jsonify({'error': 'Server configuration error'}), 500

#     # Prepare the JSON payload with explicit instructions
#     payload = {
#         "contents": [
#             {
#                 "parts": [
#                     {
#                         "text": (
#                             f"Provide a detailed description of '{entity_name}'"
#                             "If it is a book include information about the setting, characters, themes, key concepts, and its influence. "
#                             "Do not include any concluding remarks or questions."
#                             "Do not mention any Note at the end about not including concluding remarks or questions."
#                         )
#                     }
#                 ]
#             }
#         ]
#     }

#     # Construct the API URL with the API key as a query parameter
#     api_url_with_key = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

#     headers = {
#         "Content-Type": "application/json"
#     }

#     # Log the API URL and payload for debugging
#     logging.debug(f"API URL: {api_url_with_key}")
#     logging.debug(f"Payload: {payload}")

#     try:
#         # Make the POST request to the Gemini API
#         response = requests.post(
#             api_url_with_key,  # Include the API key in the URL
#             headers=headers,
#             json=payload,
#             timeout=10  # seconds
#         )
#         logging.debug(f"Gemini API response status: {response.status_code}")  # Changed to DEBUG

#         if response.status_code != 200:
#             logging.error(f"Failed to fetch description from Gemini API. Status code: {response.status_code}")
#             logging.error(f"Response content: {response.text}")
#             return jsonify({
#                 'error': 'Failed to fetch description from Gemini API',
#                 'status_code': response.status_code,
#                 'response': response.text
#             }), 500

#         response_data = response.json()
#         # Extract the description from the response
#         description = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No description available.')
#         logging.debug(f"Fetched description: {description}")  # Changed to DEBUG

#         return jsonify({'description': description})

#     except requests.exceptions.RequestException as e:
#         logging.error(f"Exception during Gemini API request: {e}")
#         return jsonify({'error': 'Failed to connect to Gemini API', 'message': str(e)}), 500
#     except ValueError as e:
#         logging.error(f"JSON decoding failed: {e}")
#         return jsonify({'error': 'Invalid JSON response from Gemini API', 'message': str(e)}), 500
#     except Exception as e:
#         logging.exception(f"Unexpected error: {e}")
#         return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500

# Initialize the database schema
def initialize_database():
    try:
        conn = get_db_connection()
        if conn is None:
            logging.error("Database connection could not be established.")
            return
        with open('schema/schema.sql', 'r') as f:
            schema_sql = f.read()
        with conn.cursor() as cursor:
            cursor.execute(schema_sql)
            conn.commit()
            logging.info("Database schema initialized.")
        conn.close()
    except Exception as e:
        logging.error(f"Error initializing the database: {e}")

# Load initial data into the database
def load_initial_data():
    try:
        conn = get_db_connection()
        if conn is None:
            logging.error("Database connection could not be established.")
            return
        with open('schema/data.sql', 'r') as f:
            data_sql = f.read()
        with conn.cursor() as cursor:
            cursor.execute(data_sql)
            conn.commit()
            logging.info("Initial data loaded into the database.")
        conn.close()
    except Exception as e:
        logging.error(f"Error loading initial data into the database: {e}")

# Function to fetch all books
def fetch_all_books():
    try:
        conn = get_db_connection()
        if conn is None:
            print("Unable to connect to the database")
            return []
        
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")  # Query to fetch all books
        books = cursor.fetchall()  # Fetch all rows
        
        cursor.close()
        conn.close()
        
        return books
    except DatabaseError as e:
        print(f"Database error occurred: {e}")
        return []

# Route to display books on the page
@app.route('/books')
def show_books():
    books = fetch_all_books()  # Get all books from the database
    return render_template('books.html', books=books)  # Pass books to template

def drop_all_tables():
    try:
        conn = get_db_connection()
        if conn is None:
            print("Skipping drop: No DB connection.")
            return
        cursor = conn.cursor()
        with open('schema/drop.sql', "r") as f:
            cursor.execute(f.read())
        conn.commit()
        cursor.close()
        conn.close()
        print("All tables dropped successfully.")
    except DatabaseError as e:
        print(f"Error dropping tables: {e}")

# @app.before_first_request
# def init_app():
#     drop_all_tables()

if __name__ == '__main__':
    app.run(debug=True)
