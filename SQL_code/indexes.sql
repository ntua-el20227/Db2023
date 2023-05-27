CREATE INDEX idx_date_of_borrowing ON applications (start_date);
CREATE INDEX idx_category ON categories(category);
CREATE INDEX idx_category ON categories(ISBN);
CREATE INDEX idx_author_name_author ON author(author_name);
CREATE INDEX idx_ISBN_author ON author(ISBN);

CREATE INDEX idx_stores_available_copies ON stores (available_copies);
CREATE INDEX idx_stores_school ON stores(school_id);
CREATE INDEX idx_book_title ON book(title);
