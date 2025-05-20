from flask import Flask, render_template, jsonify, request, redirect
import configparser
import logging
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from collections import defaultdict
from datetime import datetime
from dateutil.relativedelta import relativedelta
import subprocess
from bson.objectid import ObjectId

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# Configure logging to DEBUG level for detailed logs
logging.basicConfig(
    level=logging.INFO,  # Changed from INFO to DEBUG
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
INIT_MONGO = "init_mongo.py"

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
            ["python3", INIT_MONGO],  # changed from "node" to "python3"
            capture_output=True,
            text=True,
            check=True
        )
        logging.info("MongoDB initialization output:\n%s", result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error("MongoDB initialization failed with exit code %s:\n%s", e.returncode, e.stderr)
    except Exception as e:
        logging.error("Unexpected error during MongoDB initialization:\n%s", str(e))


# Route to serve the home page
@app.route('/init')
def initialise():
    initialize_database()

    return redirect('/')


# Book Cateloge
@app.route('/')
def index():
    db = get_db_connection()
    if db is None:
        logging.error("Unable to connect to MongoDB")
        return []

    try:
        # Fetch all books
        books_cursor = db.books.find()
        books = list(books_cursor)

        # Build mappings from authors, publishers, and genres
        authors = {str(a['_id']): a['name'] for a in db.authors.find()}
        genres = {str(g['_id']): g['name'] for g in db.genres.find()}
        publishers = {str(p['_id']): p['name'] for p in db.publishers.find()}

        # Fetch borrows to find latest borrow per book
        borrows = list(db.borrows.aggregate([
            { "$sort": { "borrow_date": -1 } },
            { "$group": {
                "_id": "$book_id",
                "latest": { "$first": "$$ROOT" }
            }}
        ]))
        latest_borrows = {str(b["_id"]): b["latest"] for b in borrows}

        # Get user information for borrows
        users = {str(u["_id"]): u for u in db.users.find()}

        # Compose book info
        book_info = []
        for index, book in enumerate(books):
            book_id_str = str(book["_id"])

            borrow = None
            if not book["is_available"]:
                borrow = latest_borrows.get(book_id_str)

            borrower = None
            borrow_date = None
            due_date = None
            if borrow:
                user = users.get(str(borrow["user_id"]))
                if user:
                    borrower = {str(user["_id"]): user["name"]}
                    borrow_date = borrow.get("borrow_date")
                    due_date = borrow.get("due_date")

            book_info.append({
                "book_id": book_id_str,
                "title": book["title"],
                "is_available": book["is_available"],
                "authors": {str(a_id): authors.get(str(a_id), "") for a_id in book.get("authors", [])},
                "publishers": {str(p_id): publishers.get(str(p_id), "") for p_id in book.get("publishers", [])},
                "genres": {str(g_id): genres.get(str(g_id), "") for g_id in book.get("genres", [])},
                "borrower": borrower,
                "borrow_date": borrow_date,
                "due_date": due_date,
            })

        # All users for dropdown
        users_list = [
            { "user_id": str(user["_id"]), "name": user["name"] }
            for user in users.values()
        ]

        # Unavailable books for dropdown
        unavailable_books_cursor = db.books.find({ "is_available": False }).sort("title", 1)
        unavailable_books = [
            { "book_id": str(book["_id"]), "title": book["title"] }
            for book in unavailable_books_cursor
        ]

        return render_template("index.html", info=book_info, users=users_list, unavailable_books=unavailable_books)

    except Exception as e:
        logging.error(f"MongoDB error occurred: {e}")
        return jsonify({
            'status': 'error',
            'message': f"MongoDB error occurred: {e}"
        }), 500


# Route to serve viewer.html: Query for Book, Author, Publisher, Genre, 
@app.route('/viewer.html')
def viewer():
    type = request.args.get('type')
    id = request.args.get('id')

    borrower = None
    heading = type.capitalize()
    info = {}

    try:
        db = get_db_connection()
        if db is None:
            print("Unable to connect to the database")
            return []

        # Map types to fields
        columns = {
            "book": ['Title', 'Edition', 'ISBN', 'Publication Year', 'Shelf Location', 'Status'],
            "author": ['Name'],
            "publisher": ["Name"],
            "genre": ["Name"],
            "user": ["Name", "Email", "Tel-No"]
        }

        # Fetch entity details based on type
        if type == "book":
            book = db.books.find_one({"_id": ObjectId(id)})
            if not book:
                return render_template('viewer.html', heading=heading, info={}, borrower={})

            info = {
                "Title": book.get("title", ""),
                "Edition": book.get("edition", ""),
                "ISBN": book.get("isbn", ""),
                "Publication Year": book.get("publication_year", ""),
                "Shelf Location": book.get("shelf_location", ""),
                "Status": book.get("is_available", True)
            }

            # Get related Author(s)
            if "author_ids" in book:
                authors = db.authors.find({"_id": {"$in": book["author_ids"]}})
                info["Author"] = {str(a["_id"]): a["name"] for a in authors}

            # Get related Publisher(s)
            if "publisher_ids" in book:
                publishers = db.publishers.find({"_id": {"$in": book["publisher_ids"]}})
                info["Publisher"] = {str(p["_id"]): p["name"] for p in publishers}

            # Get related Genre(s)
            if "genre_ids" in book:
                genres = db.genres.find({"_id": {"$in": book["genre_ids"]}})
                info["Genre"] = {str(g["_id"]): g["name"] for g in genres}

            # Get borrower if not available
            if not book.get("is_available", True):
                borrow = db.borrows.find_one(
                    {"book_id": book["_id"]},
                    sort=[("borrow_date", -1)]
                )
                if borrow:
                    user = db.users.find_one({"_id": borrow["user_id"]})
                    if user:
                        borrower = {
                            "Name": user.get("name", ""),
                            "Email": user.get("email", ""),
                            "Tel-No": user.get("tel_no", "")
                        }

        elif type in {"author", "publisher", "genre", "user"}:
            collection = db[type + "s"]
            document = collection.find_one({"_id": ObjectId(id)})
            if document:
                keys = columns[type]
                info = {keys[i]: document.get(k.lower(), "") for i, k in enumerate(keys)}

    except PyMongoError as e:
        logging.error(f"MongoDB error occurred: {e}")
        return []

    return render_template('viewer.html', heading=heading, info=info, borrower=borrower)

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


@app.route('/borrow', methods=['POST'])
def borrow_book():
    db = get_db_connection()
    if db is None:
        logging.error("Unable to connect to MongoDB")
        return redirect('/')

    try:
        # Get form data
        book_id = request.form.get('borrowBookId')
        user_id = request.form.get('borrowerName')
        borrow_date_str = request.form.get('borrowDate')

        # Convert to ObjectId
        book_oid = ObjectId(book_id)
        user_oid = ObjectId(user_id)

        # Parse borrow date
        borrow_date = datetime.strptime(borrow_date_str, '%Y-%m-%d')
        due_date = borrow_date + relativedelta(months=1)

        # Insert borrow document
        db.borrows.insert_one({
            "user_id": user_oid,
            "book_id": book_oid,
            "borrow_date": borrow_date,
            "due_date": due_date
        })

        # Update book availability
        db.books.update_one(
            {"_id": book_oid},
            {"$set": {"is_available": False}}
        )

        # Update user's borrowed book count
        db.users.update_one(
            {"_id": user_oid},
            {"$inc": {"books_borrowed": 1}}
        )

    except Exception as e:
        logging.error(f"Error processing borrow request: {e}")
    
    return redirect('/')


@app.route('/return', methods=['POST'])
def return_book():
    db = get_db_connection()
    if db is None:
        logging.error("Unable to connect to MongoDB")
        return redirect('/')

    try:
        # Get form data
        book_id = request.form.get('returnBookId')
        return_date_str = request.form.get('returnDate')
        return_date = datetime.strptime(return_date_str, '%Y-%m-%d')

        book_oid = ObjectId(book_id)

        # Find the latest borrow record for this book
        borrow_record = db.borrows.find_one(
            {"book_id": book_oid},
            sort=[("_id", -1)]  # latest borrow
        )

        if not borrow_record:
            return jsonify({'error': 'No active borrow record found for this book'}), 404

        borrow_id = borrow_record["_id"]
        user_id = borrow_record["user_id"]
        due_date = borrow_record["due_date"]

        # Check for overdue
        overdue_status = return_date > due_date
        fine = 0.0
        if overdue_status:
            days_late = (return_date - due_date).days
            fine = round(days_late * 1.0, 2)  # €1 per day

        # Insert return document
        db.returns.insert_one({
            "borrow_id": borrow_id,
            "return_date": return_date,
            "fine": fine,
            "overdue_status": overdue_status
        })

        # Update book availability
        db.books.update_one(
            {"_id": book_oid},
            {"$set": {"is_available": True}}
        )

        # Decrement books_borrowed for user
        db.users.update_one(
            {"_id": user_id},
            {"$inc": {"books_borrowed": -1}}
        )

    except Exception as e:
        logging.error(f"Error during book return: {e}")
        return jsonify({'error': 'An error occurred'}), 500

    return redirect('/')


@app.route('/reset', methods=['POST'])
def reset_database():
    # Redirect to initialise
    return redirect('/init')


if __name__ == '__main__':
    app.run(debug=True)
