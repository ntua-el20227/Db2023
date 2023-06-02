/*queries*/

/*3.1.1*/
SELECT u.username, b.title, u.school_name
FROM applications a
         INNER JOIN user u
                    ON u.user_id = a.user_id
         INNER JOIN book b
                    ON b.ISBN = a.ISBN
WHERE YEAR(a.start_date) = '{2010}'
GROUP BY u.school_name;

SELECT u.username, b.title, u.school_name
FROM applications a
         INNER JOIN user u
                    ON u.user_id = a.user_id
         INNER JOIN book b
                    ON b.ISBN = a.ISBN
         INNER JOIN school s
                    ON s.school_name = u.school_name
WHERE YEAR(a.start_date) = '{2023}'
  AND MONTH(a.start_date) = '{1,2,3,...,12}'
GROUP BY u.school_name;

/*3.1.2*/

/* Prints the authors of the books that have a certain category*/

SELECT DISTINCT authors.ISBN, authors.author_name, teachers_last_year.first_name, teachers_last_year.last_name
FROM (SELECT au.author_name, book_from_category.ISBN
      FROM author au
               INNER JOIN (SELECT categories.ISBN
                           FROM categories
                           WHERE categories.category = 'Αστρονομία') book_from_category
                          ON au.ISBN = book_from_category.ISBN) authors
         LEFT OUTER JOIN (SELECT teachers.first_name, teachers.last_name, a.ISBN
                          FROM (SELECT user_id, username, first_name, last_name
                                FROM user
                                WHERE role_name = 'teacher') teachers
                                   INNER JOIN (SELECT user_id, ISBN
                                               FROM applications
                                               WHERE applications.start_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)) a
                                              ON teachers.user_id = a.user_id) teachers_last_year
                         ON authors.ISBN = teachers_last_year.ISBN
ORDER BY authors.author_name;

/*3.1.3*/
SELECT u.user_id, u.username, u.first_name, u.last_name, num_books
FROM user u
         INNER JOIN (SELECT a.user_id, COUNT(*) AS num_books
                     FROM applications a
                              INNER JOIN user u ON u.user_id = a.user_id
                     WHERE u.role_name = 'teacher'
                       AND TIMESTAMPDIFF(YEAR, u.birth_date, CURRENT_DATE()) < 40
                       AND a.status_ IN ('borrowed', 'completed')
                     GROUP BY a.user_id
                     HAVING COUNT(*) = (SELECT COUNT(*) AS max_books
                                        FROM applications a
                                                 INNER JOIN user u ON u.user_id = a.user_id
                                        WHERE u.role_name = 'teacher'
                                          AND TIMESTAMPDIFF(YEAR, u.birth_date, CURRENT_DATE()) < 40
                                          AND a.status_ IN ('borrowed', 'completed', 'expired_borrowing')
                                        GROUP BY a.user_id
                                        ORDER BY max_books DESC
                                        LIMIT 1)) counts_the_most ON u.user_id = counts_the_most.user_id;


/*3.1.4*/
SELECT DISTINCT author_name
FROM author
WHERE author_name NOT IN
      (SELECT au.author_name
       FROM author au
                INNER JOIN (SELECT *
                            FROM applications
                            WHERE status_ IN ('borrowed', 'completed', 'expired_borrowing')) a
                           ON au.ISBN = a.ISBN);

/*3.1.5*/
/*DONE*/
SELECT s.school_name,
       COUNT(*)                                                                                       AS books_borrowed,
       GROUP_CONCAT(DISTINCT CONCAT(u_handlers.first_name, ' ', u_handlers.last_name) SEPARATOR ', ') AS handlers
FROM school s
         INNER JOIN
     user u_handlers ON s.school_name = u_handlers.school_name AND u_handlers.role_name = 'handler'
         INNER JOIN
     user u_students ON s.school_name = u_students.school_name AND u_students.role_name IN ('student', 'teacher')
         INNER JOIN
     applications a ON u_students.user_id = a.user_id
WHERE a.status_ IN ('borrowed', 'completed', 'expired_borrowing')
  AND a.start_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
GROUP BY s.school_name
HAVING COUNT(*) > 20;
/*3.1.6*/
SELECT b.*
FROM book b
         INNER JOIN applications a ON b.ISBN = a.ISBN
         INNER JOIN categories c ON b.ISBN = c.ISBN
WHERE c.category IN ('Αστρονομία', 'abc')
GROUP BY b.ISBN
HAVING COUNT(DISTINCT c.category) = 2
ORDER BY COUNT(a.ISBN) DESC
LIMIT 3;

/*3.1.7*/
SELECT a.author_name,
       COUNT(*) AS num_books
FROM author a
         INNER JOIN
     book b ON a.ISBN = b.ISBN
GROUP BY a.author_name
HAVING COUNT(*) >= (SELECT COUNT(*) - 5 FROM author GROUP BY author_name ORDER BY COUNT(*) DESC LIMIT 1);

/*3.2.1*/

SELECT b.title, a.author_name, s.available_copies
FROM book b
         INNER JOIN categories c ON b.ISBN = c.ISBN
         INNER JOIN author a ON b.ISBN = a.ISBN
         INNER JOIN stores s ON s.ISBN = b.ISBN
WHERE a.author_name = ''
   OR c.category = ''
   OR b.title = ''
   OR s.available_copies = '';

/*3.2.2*/
SELECT u.username, u.first_name, u.last_name
FROM (SELECT *
      FROM applications
      WHERE status_ = 'expired_borrowing'
        AND DATEDIFF(NOW(), expiration_date) > '<0>') expired_applications
         INNER JOIN user u
                    ON u.user_id = expired_applications.user_id;

SELECT u.username, u.first_name, u.last_name
FROM (SELECT *
      FROM applications
      WHERE status_ = 'expired_borrowing') expired_applications
         INNER JOIN user u
                    ON u.user_id = expired_applications.user_id
WHERE u.username = '<>';


/*3.2.3*/
SELECT u.username, c.category, AVG(r.like_scale) AS average_rating
FROM user u
         INNER JOIN (SELECT a.user_id, a.ISBN FROM applications a GROUP BY a.user_id, a.ISBN) AS distinct_borrowings
                    ON u.user_id = distinct_borrowings.user_id
         INNER JOIN review r ON distinct_borrowings.ISBN = r.ISBN AND u.user_id = r.user_id
         INNER JOIN categories c ON distinct_borrowings.ISBN = c.ISBN
WHERE u.username = 'Your Username'
  AND c.category = 'Your Category'
GROUP BY u.username, c.category;

/*3.3.1*/
SELECT *
FROM book
WHERE title = '';

SELECT b.ISBN, b.title, c.category
FROM book b
         INNER JOIN categories c ON b.ISBN = c.ISBN
WHERE c.category = '';
/**/
SELECT b.ISBN, b.title
FROM book b
         INNER JOIN author a ON b.ISBN = a.ISBN
WHERE a.author_name = '';
/**/
SELECT b.ISBN, b.title, a.author_name
FROM book b
         INNER JOIN categories c ON b.ISBN = c.ISBN
         INNER JOIN author a ON b.ISBN = a.ISBN
WHERE a.author_name = ''
   OR c.category = ''
   OR b.title = '';


/*3.3.2*/
SELECT b.title
FROM book b
         JOIN applications a ON a.ISBN = b.ISBN
         JOIN user u ON u.user_id = a.user_id
WHERE u.username = 'christos';