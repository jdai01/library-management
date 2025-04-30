-- User table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    tel_no VARCHAR(20),
    books_borrowed INT NOT NULL DEFAULT 0
);

-- Book table
CREATE TABLE books (
    book_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    edition INT,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    publication_year INT,
    shelf_location VARCHAR(10)
);

-- Author table
CREATE TABLE authors (
    author_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Genre table
CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Publisher table
CREATE TABLE publishers (
    publisher_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

-- Borrow table (link between User and Book)
CREATE TABLE borrows (
    borrow_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    borrow_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);

-- Return table (extension of borrows)
CREATE TABLE returns (
    return_id SERIAL PRIMARY KEY,
    borrow_id INT NOT NULL UNIQUE,
    return_date DATE NOT NULL DEFAULT CURRENT_DATE,
    fine DECIMAL(10,2) DEFAULT 0,
    overdue_status BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (borrow_id) REFERENCES borrows(borrow_id) ON DELETE CASCADE
);

-- Book-Author relation (many-to-many)
CREATE TABLE book_authors (
    book_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE CASCADE
);

-- Book-Genre relation (many-to-many)
CREATE TABLE book_genres (
    book_id INT NOT NULL,
    genre_id INT NOT NULL,
    PRIMARY KEY (book_id, genre_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id) ON DELETE CASCADE
);

-- Book-Publisher relation (many-to-many)
CREATE TABLE book_publishers (
    book_id INT NOT NULL,
    publisher_id INT NOT NULL,
    PRIMARY KEY (book_id, publisher_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (publisher_id) REFERENCES publishers(publisher_id) ON DELETE CASCADE
);