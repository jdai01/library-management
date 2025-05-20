import configparser
from pymongo import MongoClient
from pymongo.errors import CollectionInvalid
from datetime import datetime

def initialize():
    # Load config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')

    uri = config.get('DATABASE', 'MONGO_URI')
    db_name = config.get('DATABASE', 'MONGO_DB')

    if not uri or not db_name:
        print("Missing MONGO_URI or MONGO_DB in config.ini")
        exit(1)

    client = MongoClient(uri)
    db = client[db_name]

    # List of collections to drop
    collections = ['users', 'books', 'authors', 'genres', 'publishers', 'borrows', 'returns']

    for coll in collections:
        if coll in db.list_collection_names():
            db.drop_collection(coll)

    # Insert documents
    
    # Users
    db.users.insert_many([
        { "name": "Lothar Gorman", "email": "lothar_gorman@example.com", "tel_no": "(230) 865-2886", "books_borrowed": 0 },
        { "name": "Jakob Hofmann", "email": "jakob_hofmann@example.com", "tel_no": "", "books_borrowed": 0 },
        { "name": "Tadday Müller", "email": "tadday_mueller@example.com", "tel_no": "(307) 601-0688", "books_borrowed": 0 },
        { "name": "Susanne Messer", "email": "susanne_messer@example.com", "tel_no": "", "books_borrowed": 0 },
        { "name": "Jan Waltz", "email": "jan_waltz@example.com", "tel_no": "(645) 989-5053", "books_borrowed": 0 }
    ])

    # Authors
    authors_result = db.authors.insert_many([
        { "name": "J.K. Rowling" },
        { "name": "Kevin Kwan" }
    ])

    # Genres
    genres_result = db.genres.insert_many([
        { "name": "Fantasy" },
        { "name": "Adventure" },
        { "name": "Young Adult" },
        { "name": "Contemporary Fiction" },
        { "name": "Romance" },
        { "name": "Comedy" }
    ])

    # Publishers
    publishers_result = db.publishers.insert_many([
        { "name": "Bloomsbury" },
        { "name": "Scholastic" },
        { "name": "Doubleday" }
    ])

    # Books (using inserted IDs)
    db.books.insert_many([
        {
            "title": "Harry Potter and the Philosopher's Stone",
            "is_available": True,
            "edition": 1,
            "isbn": "9780747532743",
            "publication_year": 1997,
            "shelf_location": "A1",
            "authors": [authors_result.inserted_ids[0]],
            "genres": [genres_result.inserted_ids[0], genres_result.inserted_ids[1], genres_result.inserted_ids[2]],
            "publishers": [publishers_result.inserted_ids[0], publishers_result.inserted_ids[1]],
            "movie_release": datetime.strptime("2001-11-22", "%Y-%m-%d")
        },
        {
            "title": "Harry Potter and the Chamber of Secrets",
            "is_available": True,
            "edition": 1,
            "isbn": "9780747538486",
            "publication_year": 1998,
            "shelf_location": "A1",
            "authors": [authors_result.inserted_ids[0]],
            "genres": [genres_result.inserted_ids[0], genres_result.inserted_ids[1], genres_result.inserted_ids[2]],
            "publishers": [publishers_result.inserted_ids[0], publishers_result.inserted_ids[1]],
            "movie_release": datetime.strptime("2002-11-14", "%Y-%m-%d")
        },
        {
            "title": "Harry Potter and the Prisoner of Azkaban",
            "is_available": True,
            "edition": 1,
            "isbn": "9780747542155",
            "publication_year": 1999,
            "shelf_location": "A1",
            "authors": [authors_result.inserted_ids[0]],
            "genres": [genres_result.inserted_ids[0], genres_result.inserted_ids[1], genres_result.inserted_ids[2]],
            "publishers": [publishers_result.inserted_ids[0], publishers_result.inserted_ids[1]],
            "movie_release": datetime.strptime("2004-06-03", "%Y-%m-%d")
        },
        {
            "title": "Harry Potter and the Goblet of Fire",
            "is_available": True,
            "edition": 1,
            "isbn": "9780747546245",
            "publication_year": 2000,
            "shelf_location": "A1",
            "authors": [authors_result.inserted_ids[0]],
            "genres": [genres_result.inserted_ids[0], genres_result.inserted_ids[1], genres_result.inserted_ids[2]],
            "publishers": [publishers_result.inserted_ids[0], publishers_result.inserted_ids[1]],
            "movie_release": datetime.strptime("2005-11-16", "%Y-%m-%d")
        },
        {
            "title": "Harry Potter and the Order of the Phoenix",
            "is_available": True,
            "edition": 1,
            "isbn": "9780747551003",
            "publication_year": 2003,
            "shelf_location": "A1",
            "authors": [authors_result.inserted_ids[0]],
            "genres": [genres_result.inserted_ids[0], genres_result.inserted_ids[1], genres_result.inserted_ids[2]],
            "publishers": [publishers_result.inserted_ids[0], publishers_result.inserted_ids[1]],
            "movie_release": datetime.strptime("2007-07-12", "%Y-%m-%d")
        },
        {
            "title": "Harry Potter and the Half-Blood Prince",
            "is_available": True,
            "edition": 1,
            "isbn": "9780747581086",
            "publication_year": 2005,
            "shelf_location": "A1",
            "authors": [authors_result.inserted_ids[0]],
            "genres": [genres_result.inserted_ids[0], genres_result.inserted_ids[1], genres_result.inserted_ids[2]],
            "publishers": [publishers_result.inserted_ids[0], publishers_result.inserted_ids[1]],
            "movie_release": datetime.strptime("2009-07-16", "%Y-%m-%d")
        },
        {
            "title": "Harry Potter and the Deathly Hallows",
            "is_available": True,
            "edition": 1,
            "isbn": "9780747591054",
            "publication_year": 2007,
            "shelf_location": "A1",
            "authors": [authors_result.inserted_ids[0]],
            "genres": [genres_result.inserted_ids[0], genres_result.inserted_ids[1], genres_result.inserted_ids[2]],
            "publishers": [publishers_result.inserted_ids[0], publishers_result.inserted_ids[1]],
            "movie_release": datetime.strptime("2018-08-23", "%Y-%m-%d")
        },
        {
            "title": "Crazy Rich Asians",
            "is_available": True,
            "edition": 1,
            "isbn": "9780385537447",
            "publication_year": 2013,
            "shelf_location": "B2",
            "authors": [authors_result.inserted_ids[1]],
            "genres": [genres_result.inserted_ids[3], genres_result.inserted_ids[4], genres_result.inserted_ids[5]],
            "publishers": [publishers_result.inserted_ids[2]],
            "movie_release": datetime.strptime("2010-11-17", "%Y-%m-%d")
        },
        {
            "title": "China Rich Girlfriend",
            "is_available": True,
            "edition": 1,
            "isbn": "9780385537478",
            "publication_year": 2015,
            "shelf_location": "B2",
            "authors": [authors_result.inserted_ids[1]],
            "genres": [genres_result.inserted_ids[3], genres_result.inserted_ids[4], genres_result.inserted_ids[5]],
            "publishers": [publishers_result.inserted_ids[2]]
        },
        {
            "title": "Rich People Problems",
            "is_available": True,
            "edition": 1,
            "isbn": "9780385537485",
            "publication_year": 2017,
            "shelf_location": "B2",
            "authors": [authors_result.inserted_ids[1]],
            "genres": [genres_result.inserted_ids[3], genres_result.inserted_ids[4], genres_result.inserted_ids[5]],
            "publishers": [publishers_result.inserted_ids[2]]
        }
    ])

    print("Database initialized.")

if __name__ == "__main__":
    initialize()
