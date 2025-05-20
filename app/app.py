from flask import Flask, render_template, jsonify, request, redirect
import configparser
import requests
import logging
from flask_cors import CORS
from neo4j import GraphDatabase
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

from neo4j import GraphDatabase

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


# Read Neo4j config from config.ini
try:
    NEO4J_URI = config['neo4j']['uri']
    NEO4J_USER = config['neo4j']['user']
    NEO4J_PASSWORD = config['neo4j']['password']
    logging.info(f"Neo4j URI from config: {NEO4J_URI}")
except KeyError as e:
    logging.error(f"Missing Neo4j configuration in config.ini: {e}")
    raise

NEO4J_INI = "init_neo4j.cypher"

logging.info(f"Connecting to Neo4j at {NEO4J_URI} with user {NEO4J_USER}")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def close_driver():
    driver.close()


def test_connection():
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            record = result.single()
            if record and record["test"] == 1:
                logging.info("Neo4j connection test succeeded.")
                return True
            else:
                logging.error("Neo4j connection test failed: unexpected result.")
                return False
    except Exception as e:
        logging.error(f"Neo4j connection test failed: {e}")
        return False


@app.route('/test')
def test_neo4j():
    if test_connection():
        return jsonify({"status": "success", "message": "Connected to Neo4j successfully."})
    else:
        return jsonify({"status": "error", "message": "Failed to connect to Neo4j."}), 500



# Initialize the Neo4j database
def initialize_database():
    logging.info("="*100)
    with driver.session() as session:
        with open(NEO4J_INI, 'r') as file:
            cypher_script = file.read()
        for statement in cypher_script.strip().split(';'):
            if statement.strip():
                session.run(statement)
        logging.info("Database initialised.")

# Route to serve the home page
@app.route('/init')
def initialise():
    initialize_database()

    return redirect('/')
    # return jsonify({"status": "success", "message": "Database initialised."})


# Book Cateloge
@app.route('/')
def index():
    
    with driver.session() as session:
        # Cypher query to get all books with latest borrow info (if any) and availability
        result = session.run("""
        MATCH (b:Book)
        OPTIONAL MATCH (b)<-[br:BORROWED]-(u:User)
        WITH b, u, br
        ORDER BY br.borrow_date DESC
        WITH b, head(collect({user: u, borrow_date: br.borrow_date, due_date: br.due_date})) AS latestBorrow
        RETURN b.book_id AS book_id,
               b.title AS title,
               b.is_available AS is_available,
               CASE WHEN latestBorrow IS NULL THEN null ELSE latestBorrow.user.user_id END AS borrower_id,
               CASE WHEN latestBorrow IS NULL THEN null ELSE latestBorrow.user.name END AS borrower_name,
               CASE WHEN latestBorrow IS NULL THEN null ELSE latestBorrow.borrow_date END AS borrow_date,
               CASE WHEN latestBorrow IS NULL THEN null ELSE latestBorrow.due_date END AS due_date
        ORDER BY book_id
        """)

        books = []
        for record in result:
            books.append({
                "book_id": record["book_id"],
                "title": record["title"],
                "is_available": record["is_available"],
                "borrower": {record["borrower_id"]: record["borrower_name"]} if record["borrower_id"] else None,
                "borrow_date": record["borrow_date"],
                "due_date": record["due_date"],
                "authors": {},
                "publishers": {},
                "genres": {},
            })

        # Fetch authors, publishers, genres for all books
        # This can be done in separate queries or merged, here separated for clarity:

        def fetch_related(label, rel_type):
            rel_result = session.run(f"""
                MATCH (b:Book)-[:{rel_type}]->(e:{label})
                RETURN b.book_id AS book_id, e.{label.lower()}_id AS entity_id, e.name AS name
                ORDER BY b.book_id
            """)
            mapping = {}
            for rec in rel_result:
                mapping.setdefault(rec["book_id"], {})[rec["entity_id"]] = rec["name"]
            return mapping

        author_map = fetch_related("Author", "WRITTEN_BY")
        publisher_map = fetch_related("Publisher", "PUBLISHED_BY")
        genre_map = fetch_related("Genre", "HAS_GENRE")

        for book in books:
            book_id = book["book_id"]
            book["authors"] = author_map.get(book_id, {})
            book["publishers"] = publisher_map.get(book_id, {})
            book["genres"] = genre_map.get(book_id, {})

        # Get all users
        users_result = session.run("MATCH (u:User) RETURN u.user_id AS user_id, u.name AS name ORDER BY u.name")
        users = [{"user_id": r["user_id"], "name": r["name"]} for r in users_result]

        # Unavailable books
        unavailable_books_result = session.run("MATCH (b:Book) WHERE b.is_available = false RETURN b.book_id AS book_id, b.title AS title ORDER BY title")
        unavailable_books = [{"book_id": r["book_id"], "title": r["title"]} for r in unavailable_books_result]

    return render_template('index.html', info=books, users=users, unavailable_books=unavailable_books)



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

#         cursor.execute(query, id)
#         result = cursor.fetchall()
#         info = dict(zip(column, result[0])) if result else {}


#         if type == 'book':
#             # Get related information for books: Author, Publisher, Genre
#             for label, query in book_specific_queries.items():
#                 cursor.execute(query, id)
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

#                 cursor.execute(borrower_query, id)
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


@app.route('/reset', methods=['POST'])
def reset_database():
    # Redirect to initialise
    return redirect('/init')


if __name__ == '__main__':
    app.run(debug=True)
