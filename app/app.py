from flask import Flask, render_template, jsonify, request, redirect
import configparser
import requests
import logging
from flask_cors import CORS
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
import subprocess
import os

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
MONGO_URI = config.get('DATABASE', 'MONGO_URI')
DB_NAME = config.get('DATABASE', 'MONGO_DB')
INIT_MONGO = os.path.join('schema', 'init_mongo.js')

def get_db_connection():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        logging.info("MongoDB connection successful.")
        return db
    except Exception as e:
        logging.error(f"MongoDB connection failed: {e}")
        return None

@app.route('/test')
def test_connection():
    try:
        db = get_db_connection()

        collections = db.list_collection_names()
        logging.info(f"Connected to MongoDB database successfully.")
        logging.info(f"Available collections: {collections if collections else 'No collections found yet.'}")
        
        return jsonify({
            'status': 'success',
            'message': f'Connected to MongoDB database.',
            'collections': collections
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'MongoDB connection failed: {str(e)}'
        }), 500



# Initialize the database schema
def initialize_database():
    try:
        result = subprocess.run(
            ["node", INIT_MONGO],
            capture_output=True,
            text=True,
            check=True
        )
        logging.info("MongoDB initialization output:\n%s", result.stdout)
    except Exception as e:
        logging.error("MongoDB initialization failed with exit code %s:\n%s", e.returncode, e.stderr)


# Route to serve the home page
@app.route('/init')
def initialise():
    initialize_database()

    # return redirect('/')
    return jsonify({
        'status': 'success',
        'message': f'Database initialised.',
    }), 200


# # Book Cateloge
# @app.route('/')
# def index():
#     conn = None
#     cursor = None
#     try:
#         conn = get_db_connection()
#         if conn is None:
#             logging.error("Unable to connect to the database")
#             return []

#         cursor = conn.cursor()

#         # Fetch book info with borrower data if unavailable
#         book_query = """
#             WITH LatestBorrows AS (
#                 SELECT 
#                     bo.book_id,
#                     bo.user_id,
#                     bo.borrow_date,
#                     bo.due_date,
#                     ROW_NUMBER() OVER (PARTITION BY bo.book_id ORDER BY bo.borrow_id DESC) AS rn
#                 FROM borrows bo
#                 LEFT JOIN books b ON bo.book_id = b.book_id
#                 WHERE b.is_available=FALSE
#             )
#             SELECT 
#                 b.book_id,
#                 b.title,
#                 b.is_available,
#                 u.name AS borrower,
#                 lb.borrow_date,
#                 lb.due_date,
#                 u.user_id
#             FROM books b
#             LEFT JOIN LatestBorrows lb ON lb.book_id = b.book_id AND lb.rn = 1
#             LEFT JOIN users u ON u.user_id = lb.user_id
#             ORDER BY b.book_id;
#         """
#         cursor.execute(book_query)
#         books = cursor.fetchall()

#         # Fetch authors, publishers, genres
#         def fetch_and_map(query):
#             cursor.execute(query)
#             results = cursor.fetchall()
#             mapping = defaultdict(dict)
#             for book_id, entity_id, entity_name in results:
#                 mapping[book_id][entity_id] = entity_name
#             return mapping

#         author_query = """
#             SELECT b.book_id, a.author_id, a.name
#             FROM books b
#             JOIN book_authors ba ON ba.book_id = b.book_id
#             JOIN authors a ON a.author_id = ba.author_id
#             ORDER BY b.book_id
#         """

#         publisher_query = """
#             SELECT b.book_id, p.publisher_id, p.name
#             FROM books b
#             JOIN book_publishers bp ON bp.book_id = b.book_id
#             JOIN publishers p ON p.publisher_id = bp.publisher_id
#             ORDER BY b.book_id
#         """

#         genre_query = """
#             SELECT b.book_id, g.genre_id, g.name
#             FROM books b
#             JOIN book_genres bg ON bg.book_id = b.book_id
#             JOIN genres g ON g.genre_id = bg.genre_id
#             ORDER BY b.book_id
#         """

#         author_map = fetch_and_map(author_query)
#         publisher_map = fetch_and_map(publisher_query)
#         genre_map = fetch_and_map(genre_query)

#         # Combine all info into structured list of dicts
#         book_info = []
#         for row in books:
#             book_id, title, is_available, borrower_name, borrow_date, due_date, borrower_id = row
#             book_info.append({
#                 "book_id": book_id,
#                 "title": title,
#                 "is_available": is_available,
#                 "authors": author_map.get(book_id, {}),
#                 "publishers": publisher_map.get(book_id, {}),
#                 "genres": genre_map.get(book_id, {}),
#                 "borrower": {borrower_id: borrower_name} if borrower_id else None,
#                 "borrow_date": borrow_date,
#                 "due_date": due_date,
#             })

#         # Get user list
#         user_query = """
#             SELECT 
#                 user_id, 
#                 name 
#             FROM users 
#             ORDER BY name
#         """
#         cursor.execute(user_query)
#         users_tuples = cursor.fetchall()
#         users = [
#             { 'user_id': u_id, 'name': name }
#             for u_id, name in users_tuples
#         ]

#         # Get unavailable books
#         unavailable_books_query = """
#             SELECT 
#                 book_id, 
#                 title 
#             FROM books 
#             WHERE is_available = FALSE 
#             ORDER BY title
#         """
#         cursor.execute(unavailable_books_query)
#         unavailable_books_tuples = cursor.fetchall()
#         unavailable_books = [
#             { 'book_id': b_id, 'title': title }
#             for b_id, title in unavailable_books_tuples
#         ]

#         return render_template('/index.html', info=book_info, users=users, unavailable_books=unavailable_books)

#     except DatabaseError as e:
#         logging.error(f"Database error occurred: {e}")
#         return []

#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()


# # Route to serve viewer.html: Query for Book, Author, Publisher, Genre, 
# @app.route('/viewer.html')
# def viewer():
#     type = request.args.get('type')
#     id = request.args.get('id')
    
#     borrower = None
#     heading = type.capitalize()

#     try: 
#         conn = get_db_connection()
#         if conn is None:
#             print("Unable to connect to the database")
#             return []
        
#         cursor = conn.cursor()

#         columns = {
#             "book": ['Title', 'Edition', 'ISBN', 'Publication Year', 'Shelf Location', 'Status'],
#             "author": ['Name'],
#             "publisher": ["Name"],
#             "genre": ["Name"], 
#             "user": ["Name", "Email", "Tel-No"]
#         }

#         queries = {
#             "book": f"""
#                 SELECT b.title, b.edition, b.isbn, b.publication_year, b.shelf_location, b.is_available
#                 FROM books b
#                 WHERE book_id = %s
#             """,
#             "author": f"""
#                 SELECT name
#                 FROM authors
#                 WHERE author_id = %s
#             """,
#             "publisher": f"""
#                 SELECT name
#                 FROM publishers
#                 WHERE publisher_id = %s
#             """,
#             "genre": f"""
#                 SELECT name
#                 FROM genres
#                 WHERE genre_id = %s
#             """, 
#             "user": f"""
#                 SELECT name, email, tel_no
#                 FROM users
#                 WHERE user_id = %s
#             """
#         }

#         book_specific_queries = {
#             "author": f"""
#                 SELECT 
#                     a.author_id,
#                     a.name
#                 FROM books b
#                 LEFT JOIN book_authors ba ON ba.book_id = b.book_id
#                 LEFT JOIN authors a ON a.author_id = ba.author_id
#                 WHERE b.book_id = %s
#                 ORDER BY a.name
#             """,
#             "publisher": f"""
#                 SELECT 
#                     p.publisher_id,
#                     p.name
#                 FROM books b
#                 LEFT JOIN book_publishers bp ON bp.book_id = b.book_id
#                 LEFT JOIN publishers p ON p.publisher_id = bp.publisher_id
#                 WHERE b.book_id = %s
#                 ORDER BY p.name
#             """, 
#             "genre": f"""
#                 SELECT 
#                     g.genre_id,
#                     g.name
#                 FROM books b
#                 LEFT JOIN book_genres bg ON bg.book_id = b.book_id
#                 LEFT JOIN genres g ON g.genre_id = bg.genre_id
#                 WHERE b.book_id = %s
#                 ORDER BY g.name
#             """
#         }

#         # Get information based on type
#         query = queries[type]
#         column = columns[type]

#         cursor.execute(query, (id,))
#         result = cursor.fetchall()
#         info = dict(zip(column, result[0])) if result else {}


#         if type == 'book':
#             # Get related information for books: Author, Publisher, Genre
#             for label, query in book_specific_queries.items():
#                 cursor.execute(query, (id,))
#                 results = cursor.fetchall()
#                 info[label.capitalize()] = dict(results) if results else {}

#             # If book is not available, get borrower details
#             if not info["Status"]:
#                 borrower_query = f"""
#                     SELECT u.name, u.email, u.tel_no
#                     FROM books b
#                     JOIN borrows br ON br.book_id = b.book_id
#                     JOIN users u ON br.user_id = u.user_id
#                     WHERE 
#                         b.is_available = FALSE
#                         AND b.book_id = %s
#                     ORDER BY br.borrow_id DESC
#                     LIMIT 1
#                 """

#                 cursor.execute(borrower_query, (id,))
#                 borrower_result = cursor.fetchone()

#                 borrower = dict(zip(columns['user'], borrower_result)) if borrower_result else {}

#         cursor.close()
#         conn.close()
#     except DatabaseError as e:
#         logging.error(f"Database error occurred: {e}")
#         return []
    
#     return render_template('viewer.html', heading=heading, info=info, borrower=borrower)

# # # API route to fetch description from Gemini API
# # @app.route('/api/description', methods=['GET'])
# # def get_description():
# #     entity_name = request.args.get('name')
# #     logging.debug(f"Received request for entity name: {entity_name}")  # Changed to DEBUG

# #     if not entity_name:
# #         logging.warning("Missing entity name in request.")
# #         return jsonify({'error': 'Missing entity name'}), 400

# #     if not GEMINI_API_URL or not GEMINI_API_KEY:
# #         logging.error("Gemini API configuration missing.")
# #         return jsonify({'error': 'Server configuration error'}), 500

# #     # Prepare the JSON payload with explicit instructions
# #     payload = {
# #         "contents": [
# #             {
# #                 "parts": [
# #                     {
# #                         "text": (
# #                             f"Provide a detailed description of '{entity_name}'"
# #                             "If it is a book include information about the setting, characters, themes, key concepts, and its influence. "
# #                             "Do not include any concluding remarks or questions."
# #                             "Do not mention any Note at the end about not including concluding remarks or questions."
# #                         )
# #                     }
# #                 ]
# #             }
# #         ]
# #     }

# #     # Construct the API URL with the API key as a query parameter
# #     api_url_with_key = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

# #     headers = {
# #         "Content-Type": "application/json"
# #     }

# #     # Log the API URL and payload for debugging
# #     logging.debug(f"API URL: {api_url_with_key}")
# #     logging.debug(f"Payload: {payload}")

# #     try:
# #         # Make the POST request to the Gemini API
# #         response = requests.post(
# #             api_url_with_key,  # Include the API key in the URL
# #             headers=headers,
# #             json=payload,
# #             timeout=10  # seconds
# #         )
# #         logging.debug(f"Gemini API response status: {response.status_code}")  # Changed to DEBUG

# #         if response.status_code != 200:
# #             logging.error(f"Failed to fetch description from Gemini API. Status code: {response.status_code}")
# #             logging.error(f"Response content: {response.text}")
# #             return jsonify({
# #                 'error': 'Failed to fetch description from Gemini API',
# #                 'status_code': response.status_code,
# #                 'response': response.text
# #             }), 500

# #         response_data = response.json()
# #         # Extract the description from the response
# #         description = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No description available.')
# #         logging.debug(f"Fetched description: {description}")  # Changed to DEBUG

# #         return jsonify({'description': description})

# #     except requests.exceptions.RequestException as e:
# #         logging.error(f"Exception during Gemini API request: {e}")
# #         return jsonify({'error': 'Failed to connect to Gemini API', 'message': str(e)}), 500
# #     except ValueError as e:
# #         logging.error(f"JSON decoding failed: {e}")
# #         return jsonify({'error': 'Invalid JSON response from Gemini API', 'message': str(e)}), 500
# #     except Exception as e:
# #         logging.exception(f"Unexpected error: {e}")
# #         return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500


# @app.route('/borrow', methods=['POST'])
# def borrow_book():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     book_id = request.form.get('borrowBookId')
#     user_id = request.form.get('borrowerName')
#     borrow_date_str = request.form.get('borrowDate')

#     # Parse string to date
#     borrow_date = datetime.strptime(borrow_date_str, '%Y-%m-%d').date()
#     due_date = borrow_date + relativedelta(months=1)


#     borrow_insert_query = """
#         INSERT INTO borrows (user_id, book_id, borrow_date, due_date)
#         VALUES (%s, %s, %s, %s)
#     """
#     cursor.execute(borrow_insert_query, (user_id, book_id, borrow_date.strftime('%Y-%m-%d'), due_date.strftime('%Y-%m-%d')))

#     book_update_query = """
#         UPDATE books
#         SET is_available = FALSE
#         WHERE book_id = %s
#     """
#     cursor.execute(book_update_query, (book_id,))

#     user_update_query = """
#         UPDATE users
#         SET books_borrowed = books_borrowed + 1
#         WHERE user_id = %s
#     """
#     cursor.execute(user_update_query, (user_id,))

#     conn.commit()
#     conn.close()

#     return redirect('/')


# @app.route('/return', methods=['POST'])
# def return_book():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     book_id = request.form.get('returnBookId')
#     return_date_str = request.form.get('returnDate')
#     return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()

#     # Get borrow_id, due_date, user_id using parameterized query
#     borrow_record_query = """
#         SELECT borrow_id, user_id, due_date
#         FROM borrows
#         WHERE book_id = %s
#         ORDER BY borrow_id DESC
#         LIMIT 1
#     """
#     cursor.execute(borrow_record_query, (book_id,))
#     borrow_record = cursor.fetchone()

#     if not borrow_record:
#         cursor.close()
#         conn.close()
#         return jsonify({'error': 'No active borrow record found for this book'}), 404

#     borrow_id, user_id, due_date_obj = borrow_record
#     due_date = due_date_obj if isinstance(due_date_obj, datetime) else datetime.strptime(str(due_date_obj), '%Y-%m-%d').date()


#     # Check for overdue
#     overdue_status = return_date > due_date
#     fine_amount_per_day = 1
#     fine = 0.0
#     if overdue_status:
#         days_late = (return_date - due_date).days
#         fine = round(days_late * fine_amount_per_day, 2)


#     # Insert into returns using parameterized query
#     returns_query = """
#         INSERT INTO returns (borrow_id, return_date, fine, overdue_status)
#         VALUES (%s, %s, %s, %s)
#     """
#     cursor.execute(returns_query, (borrow_id, return_date, fine, overdue_status))

#     # Update book availability
#     update_book_query = """
#         UPDATE books
#         SET is_available = TRUE
#         WHERE book_id = %s
#     """
#     cursor.execute(update_book_query, (book_id,))

#     # Update user's borrowed book count
#     update_user_query = """
#         UPDATE users
#         SET books_borrowed = books_borrowed - 1
#         WHERE user_id = %s
#     """
#     cursor.execute(update_user_query, (user_id,))


#     conn.commit()
#     conn.close()

#     return redirect('/')


# @app.route('/reset', methods=['POST'])
# def reset_database():
#     # Redirect to initialise
#     return redirect('/init')


# if __name__ == '__main__':
#     app.run(debug=True)
