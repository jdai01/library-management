-- Populate initial data

-- User table
INSERT INTO users (name, email, tel_no) 
VALUES
    ('Lothar Gorman', 'lothar_gorman@example.com', '(230) 865-2886'),
    ('Jakob Hofmann', 'jakob_hofmann@example.com', ''),
    ('Tadday Müller', 'tadday_mueller@example.com', '(307) 601-0688'),
    ('Susanne Messer', 'susanne_messer@example.com', ''),
    ('Jan Waltz', 'jan_waltz@example.com', '(645) 989-5053')
;

-- Book table
INSERT INTO books (title, is_available, edition, isbn, publication_year, shelf_location)
VALUES 
    ('Harry Potter and the Philosopher''s Stone', TRUE, 1, '9780747532743', 1997, 'A1'),
    ('Harry Potter and the Chamber of Secrets', TRUE, 1, '9780747538486', 1998, 'A1'),
    ('Harry Potter and the Prisoner of Azkaban', TRUE, 1, '9780747542155', 1999, 'A1'),
    ('Harry Potter and the Goblet of Fire', TRUE, 1, '9780747546245', 2000, 'A1'),
    ('Harry Potter and the Order of the Phoenix', TRUE, 1, '9780747551003', 2003, 'A1'),
    ('Harry Potter and the Half-Blood Prince', TRUE, 1, '9780747581086', 2005, 'A1'),
    ('Harry Potter and the Deathly Hallows', FALSE, 1, '9780747591054', 2007, 'A1'),
    ('Crazy Rich Asians', TRUE, 1, '9780385537447', 2013, 'B2'),
    ('China Rich Girlfriend', TRUE, 1, '9780385537478', 2015, 'B2'),
    ('Rich People Problems', FALSE, 1, '9780385537485', 2017, 'B2');
;

-- Author table
INSERT INTO authors (name)
VALUES 
    ('J.K. Rowling'),
    ('Kevin Kwan')
;

-- Genre table
INSERT INTO genres (name)
VALUES 
    ('Fantasy'),
    ('Adventure'),
    ('Young Adult'),
    ('Contemporary Fiction'),
    ('Romance'),
    ('Comedy')
;

-- Publisher table
INSERT INTO publishers (name)
VALUES 
    ('Bloomsbury'),
    ('Scholastic'), 
    ('Doubleday')
;

-- Book-Author
INSERT INTO book_authors (book_id, author_id)
VALUES 
    (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), -- Harry Potter series
    (8, 2),  (9, 2),  (10, 2) -- Crazy Rich Asians trilogy 
;

-- Book-Genre
INSERT INTO book_genres (book_id, genre_id)
VALUES 
    (1, 1), (1, 2), (1, 3),
    (2, 1), (2, 2), (2, 3),
    (3, 1), (3, 2), (3, 3),
    (4, 1), (4, 2), (4, 3),
    (5, 1), (5, 2), (5, 3),
    (6, 1), (6, 2), (6, 3),
    (7, 1), (7, 2), (7, 3),
    (8, 4), (8, 5), (8, 6),
    (9, 4), (9, 5), (9, 6),
    (10, 4), (10, 5), (10, 6)
;

-- Book-Publisher
INSERT INTO book_publishers (book_id, publisher_id)
VALUES 
    (1, 1), (1, 2),
    (2, 1), (2, 2),
    (3, 1), (3, 2),
    (4, 1), (4, 2),
    (5, 1), (5, 2),
    (6, 1), (6, 2),
    (7, 1), (7, 2),
    (8, 3),
    (9, 3),
    (10, 3)
;

-- -- Borrow table
-- INSERT INTO borrows (user_id, book_id, due_date)
-- VALUES 
--     (1, 1, '2025-03-15'),
--     (2, 2, '2025-03-15'),
--     (1, 3, '2025-04-20'),
--     (2, 4, '2025-04-20'),
--     (3, 8, '2025-03-15'),
--     (4, 9, '2025-04-20'),
--     (3, 10, '2025-03-15')
-- ;

-- -- Return table 
-- INSERT INTO returns (borrow_id, return_date, fine, overdue_status)
-- VALUES 
--     (1, '2025-04-30', 10.00, TRUE),
--     (2, '2025-04-15', 0.00, FALSE),
--     (3, '2025-04-30', 0.00, FALSE),
--     (4, '2025-05-30', 5.00, TRUE),
--     (5, '2025-04-20', 5.00, TRUE), 
--     (6, '2025-04-30', 0.00, FALSE), 
--     (7, '2025-04-30', 10.00, TRUE)
-- ;




