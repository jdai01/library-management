// Delete existing data
MATCH (n) DETACH DELETE n;

// === Create Users ===
CREATE (:User {user_id: 1, name: 'Lothar Gorman', email: 'lothar_gorman@example.com', tel_no: '(230) 865-2886', books_borrowed: 0});
CREATE (:User {user_id: 2, name: 'Jakob Hofmann', email: 'jakob_hofmann@example.com', tel_no: '', books_borrowed: 0});
CREATE (:User {user_id: 3, name: 'Tadday Müller', email: 'tadday_mueller@example.com', tel_no: '(307) 601-0688', books_borrowed: 0});
CREATE (:User {user_id: 4, name: 'Susanne Messer', email: 'susanne_messer@example.com', tel_no: '', books_borrowed: 0});
CREATE (:User {user_id: 5, name: 'Jan Waltz', email: 'jan_waltz@example.com', tel_no: '(645) 989-5053', books_borrowed: 0});

// === Create Authors ===
CREATE (:Author {author_id: 1, name: 'J.K. Rowling'});
CREATE (:Author {author_id: 2, name: 'Kevin Kwan'});

// === Create Genres ===
CREATE (:Genre {genre_id: 1, name: 'Fantasy'});
CREATE (:Genre {genre_id: 2, name: 'Adventure'});
CREATE (:Genre {genre_id: 3, name: 'Young Adult'});
CREATE (:Genre {genre_id: 4, name: 'Contemporary Fiction'});
CREATE (:Genre {genre_id: 5, name: 'Romance'});
CREATE (:Genre {genre_id: 6, name: 'Comedy'});

// === Create Publishers ===
CREATE (:Publisher {publisher_id: 1, name: 'Bloomsbury'});
CREATE (:Publisher {publisher_id: 2, name: 'Scholastic'});
CREATE (:Publisher {publisher_id: 3, name: 'Doubleday'});

// === Create Books ===
CREATE (:Book {book_id: 1, title: "Harry Potter and the Philosopher's Stone", edition: 1, isbn: '9780747532743', publication_year: 1997, shelf_location: 'A1', is_available: true});
CREATE (:Book {book_id: 2, title: "Harry Potter and the Chamber of Secrets", edition: 1, isbn: '9780747538486', publication_year: 1998, shelf_location: 'A1', is_available: true});
CREATE (:Book {book_id: 3, title: "Harry Potter and the Prisoner of Azkaban", edition: 1, isbn: '9780747542155', publication_year: 1999, shelf_location: 'A1', is_available: true});
CREATE (:Book {book_id: 4, title: "Harry Potter and the Goblet of Fire", edition: 1, isbn: '9780747546245', publication_year: 2000, shelf_location: 'A1', is_available: true});
CREATE (:Book {book_id: 5, title: "Harry Potter and the Order of the Phoenix", edition: 1, isbn: '9780747551003', publication_year: 2003, shelf_location: 'A1', is_available: true});
CREATE (:Book {book_id: 6, title: "Harry Potter and the Half-Blood Prince", edition: 1, isbn: '9780747581086', publication_year: 2005, shelf_location: 'A1', is_available: true});
CREATE (:Book {book_id: 7, title: "Harry Potter and the Deathly Hallows", edition: 1, isbn: '9780747591054', publication_year: 2007, shelf_location: 'A1', is_available: true});
CREATE (:Book {book_id: 8, title: "Crazy Rich Asians", edition: 1, isbn: '9780385537447', publication_year: 2013, shelf_location: 'B2', is_available: true});
CREATE (:Book {book_id: 9, title: "China Rich Girlfriend", edition: 1, isbn: '9780385537478', publication_year: 2015, shelf_location: 'B2', is_available: true});
CREATE (:Book {book_id: 10, title: "Rich People Problems", edition: 1, isbn: '9780385537485', publication_year: 2017, shelf_location: 'B2', is_available: true});

// === Relationships: Book WRITTEN_BY Author ===
MATCH (b:Book), (a:Author)
WHERE b.book_id IN [1,2,3,4,5,6,7] AND a.author_id = 1
CREATE (b)-[:WRITTEN_BY]->(a);
MATCH (b:Book), (a:Author)
WHERE b.book_id IN [8,9,10] AND a.author_id = 2
CREATE (b)-[:WRITTEN_BY]->(a);

// === Relationships: Book HAS_GENRE Genre ===
UNWIND [
    [1, [1,2,3]], [2, [1,2,3]], [3, [1,2,3]], [4, [1,2,3]],
    [5, [1,2,3]], [6, [1,2,3]], [7, [1,2,3]],
    [8, [4,5,6]], [9, [4,5,6]], [10, [4,5,6]]
] AS pair
WITH pair[0] AS bookId, pair[1] AS genreIds
MATCH (b:Book {book_id: bookId})
UNWIND genreIds AS gid
MATCH (g:Genre {genre_id: gid})
CREATE (b)-[:HAS_GENRE]->(g);

// === Relationships: Book PUBLISHED_BY Publisher ===
UNWIND [
    [1, [1,2]], [2, [1,2]], [3, [1,2]], [4, [1,2]], [5, [1,2]], [6, [1,2]], [7, [1,2]],
    [8, [3]], [9, [3]], [10, [3]]
] AS pair
WITH pair[0] AS bookId, pair[1] AS publisherIds
MATCH (b:Book {book_id: bookId})
UNWIND publisherIds AS pid
MATCH (p:Publisher {publisher_id: pid})
CREATE (b)-[:PUBLISHED_BY]->(p);
