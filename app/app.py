from flask import Flask, render_template, jsonify, request
import configparser
import requests
import logging
from flask_cors import CORS
import psycopg2
from psycopg2 import OperationalError, DatabaseError
from collections import defaultdict

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
    # Initialising DB
    drop_all_tables()
    initialize_database()
    load_initial_data()

    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/main.html')
def main():
    try:
        conn = get_db_connection()
        if conn is None:
            print("Unable to connect to the database")
            return []
        
        cursor = conn.cursor()
        query = """
            SELECT 
                b.book_id,
                b.title,
                CASE WHEN NOT b.is_available THEN u.name END AS borrower, 
                CASE WHEN NOT b.is_available THEN bo.borrow_date END AS borrow_date,
                CASE WHEN NOT b.is_available THEN bo.due_date END AS due_date,
                b.is_available
            FROM books b
            -- LEFT JOIN book_authors ba ON ba.book_id = b.book_id
            -- LEFT JOIN authors a ON a.author_id = ba.author_id
            -- LEFT JOIN book_publishers bp ON bp.book_id = b.book_id
            -- LEFT JOIN publishers p ON p.publisher_id = bp.publisher_id
            -- LEFT JOIN book_genres bg ON bg.book_id = b.book_id
            -- LEFT JOIN genres g ON g.genre_id = bg.genre_id
            LEFT JOIN borrows bo ON bo.book_id = b.book_id
            LEFT JOIN users u ON u.user_id = bo.user_id
            GROUP BY b.book_id, b.title, u.name, bo.borrow_date, bo.due_date, b.is_available
            ORDER BY b.book_id;
        """

        author_query = """
            SELECT 
                b.book_id,
                a.author_id,
                a.name
            FROM books b
            LEFT JOIN book_authors ba ON ba.book_id = b.book_id
            LEFT JOIN authors a ON a.author_id = ba.author_id
            ORDER BY book_id
        """

        genre_query = """
            SELECT 
                b.book_id,
                g.genre_id,
                g.name
            FROM books b
            LEFT JOIN book_genres bg ON bg.book_id = b.book_id
            LEFT JOIN genres g ON g.genre_id = bg.genre_id
            ORDER BY book_id
        """

        publisher_query = """
            SELECT 
                b.book_id,
                p.publisher_id,
                p.name
            FROM books b
            LEFT JOIN book_publishers bp ON bp.book_id = b.book_id
            LEFT JOIN publishers p ON p.publisher_id = bp.publisher_id
            ORDER BY book_id
        """

        user_query = """
            SELECT
                u.user_id,
                u.name
            FROM users u
            ORDER BY u.name
        """

        unavailable_books_query = """
            SELECT 
                b.book_id,
                b.title
            FROM books b
            WHERE b.is_available = FALSE
        """

        cursor.execute(query)  # Query to fetch all books
        info = cursor.fetchall()  # Fetch all rows
        
        cursor.execute(author_query)
        authors = cursor.fetchall()

        cursor.execute(genre_query)
        genres = cursor.fetchall()

        cursor.execute(publisher_query)
        publishers = cursor.fetchall()

        # Group related data by book_id
        author_map = defaultdict(dict)
        for book_id, author_id, author_name in authors:
            author_map[book_id][author_id] = author_name

        publisher_map = defaultdict(dict)
        for book_id, publisher_id, publisher_name in publishers:
            publisher_map[book_id][publisher_id] = publisher_name

        genre_map = defaultdict(dict)
        for book_id, genre_id, genre_name in genres:
            genre_map[book_id][genre_id] = genre_name

        # Insert into info
        for i in range(len(info)):
            book_id = info[i][0]
            info[i] = list(info[i])
            info[i].insert(2, author_map.get(book_id, {}))
            info[i].insert(3, publisher_map.get(book_id, {}))
            info[i].insert(4, genre_map.get(book_id, {}))

        
        cursor.execute(user_query)
        users = cursor.fetchall()

        cursor.execute(unavailable_books_query)
        unavailable_books = cursor.fetchall()


        cursor.close()
        conn.close()
        
        return render_template('main.html', info=info, users=users, unavailable_books=unavailable_books)
    except DatabaseError as e:
        logging.error(f"Database error occurred: {e}")
        return []

# Route to serve viewer.html
@app.route('/viewer.html')
def viewer():
    type = request.args.get('type')
    id = request.args.get('id')

    heading = type.capitalize()

    try: 
        conn = get_db_connection()
        if conn is None:
            print("Unable to connect to the database")
            return []
        
        cursor = conn.cursor()

        if type == 'book':
            columns = ['Title', 'Edition', 'ISBN', 'Publication Year', 'Shelf Location', 'Status']
            query = f"""
                SELECT b.title, b.edition, b.isbn, b.publication_year, b.shelf_location, b.is_available
                FROM books b
                WHERE book_id = {id}
            """

            book_author_query = f"""
                SELECT 
                    a.author_id,
                    a.name
                FROM books b
                LEFT JOIN book_authors ba ON ba.book_id = b.book_id
                LEFT JOIN authors a ON a.author_id = ba.author_id
                WHERE b.book_id = {id}
                ORDER BY a.name
            """

            book_publisher_query = f"""
                SELECT 
                    p.publisher_id,
                    p.name
                FROM books b
                LEFT JOIN book_publishers bp ON bp.book_id = b.book_id
                LEFT JOIN publishers p ON p.publisher_id = bp.publisher_id
                WHERE b.book_id = {id}
                ORDER BY p.name
            """

            book_genre_query = f"""
                SELECT 
                    g.genre_id,
                    g.name
                FROM books b
                LEFT JOIN book_genres bg ON bg.book_id = b.book_id
                LEFT JOIN genres g ON g.genre_id = bg.genre_id
                WHERE b.book_id = {id}
                ORDER BY g.name
            """

        elif type == 'author':
            columns = ['Name']
            query = f"""
                SELECT name
                FROM authors
                WHERE author_id = {id}
            """
        elif type == 'publisher':
            columns = ['Name']
            query = f"""
                SELECT name
                FROM publishers
                WHERE publisher_id = {id}
            """
        elif type == 'genre':
            columns = ['Name']
            query = f"""
                SELECT name
                FROM genres
                WHERE genre_id = {id}
            """
        

        cursor.execute(query)
        result = cursor.fetchall()
        info = dict(zip(columns, result[0])) if result else {}


        if type == 'book':
            i = 0
            col_list = ['Author', 'Publisher', 'Genre']
            for q in [book_author_query, book_publisher_query, book_genre_query]:
                cursor.execute(q)
                r = cursor.fetchall()
                temp_dict = dict(r)
                # logging.info(temp_dict)

                info[col_list[i]] = temp_dict
                i += 1

        cursor.close()
        conn.close()
    except DatabaseError as e:
        logging.error(f"Database error occurred: {e}")
        return []
    

    return render_template('viewer.html', heading=heading, info=info)

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
        logging.info("All tables dropped successfully.")
    except DatabaseError as e:
        logging.error(f"Error dropping tables: {e}")

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


# @app.before_first_request
# def init_app():
#     drop_all_tables()

if __name__ == '__main__':
    

    app.run(debug=True)
