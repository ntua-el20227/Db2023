CREATE INDEX idx_date_of_borrowing ON applications (start_date);
CREATE INDEX idx_book_category ON book (category);
CREATE INDEX idx_stores_available_copies ON stores (available_copies);
CREATE INDEX idx_stores_school ON stores(school_id);
CREATE INDEX idx_book_title ON book(title);
