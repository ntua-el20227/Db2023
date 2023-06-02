/*CREATE VIEW all_students_with_age
AS
    SELECT
        FROM user u

CREATE VIEW user_details (user_id, first_name, last_name, pwd,email, role_name)
AS
SELECT
    customer_id, first_name, last_name,
    CONCAT(substr(pwd,1,2), '*****', substr(email, -4)) email
FROM user;
*/


/* FIND all the available books*/

CREATE VIEW available_books
AS
SELECT b.ISBN, b.title, b.image, s.available_copies
FROM (SELECT * FROM stores WHERE stores.available_copies > 0) s
         INNER JOIN book b
                    ON s.ISBN = b.ISBN;


CREATE VIEW expired_borrows
AS
SELECT u.username, u.first_name, u.last_name, b.ISBN, b.title
FROM (SELECT * FROM applications WHERE applications.status_ = 'expired_borrowing') a
         INNER JOIN user u ON u.user_id = a.user_id
         INNER JOIN book b ON b.ISBN = a.ISBN;
