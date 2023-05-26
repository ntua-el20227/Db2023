/*queries*/

/*3.1.1*/
SELECT u.username, b.title, s.school_name
FROM applications a
         INNER JOIN user u
                    ON u.user_id = a.user_id
         INNER JOIN book b
                    ON b.ISBN = a.ISBN
         INNER JOIN school s
                    ON s.school_id = u.school_id
WHERE YEAR(a.start_date) = '{2010}';

SELECT u.username, b.title, s.school_name
FROM applications a
         INNER JOIN user u
                    ON u.user_id = a.user_id
         INNER JOIN book b
                    ON b.ISBN = a.ISBN
         INNER JOIN school s
                    ON s.school_id = u.school_id
WHERE YEAR(a.start_date) = '{2023}'
  AND MONTH(a.start_date) = '{1,2,3,...,12}';

/*3.1.2*/

/* Prints the authors of the books that have a certain category*/
SELECT book.ISBN
FROM book
WHERE book.category = '%s';

/*Finds teachers that have applied the last year*/

SELECT au.author_name, u.first_name, u.last_name
FROM user u
         INNER JOIN applications a
                    ON u.user_id = a.user_id
         INNER JOIN (SELECT book.ISBN
                     FROM book
                     WHERE book.category = 'horror') category
                    ON category.ISBN = a.ISBN
         INNER JOIN writes w
                    ON category.ISBN = w.ISBN
        INNER JOIN author au
                    ON w.author_id = au.author_id
WHERE u.role_name = 'teacher'
  AND a.start_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR);

/*3.1.3*/
SELECT u.username, u.first_name, u.last_name, COUNT(a.ISBN)
FROM user u
         INNER JOIN applications a
                    ON u.user_id = a.user_id
WHERE u.role_name = 'teacher' AND YEAR(CURRENT_DATE()-u.birth_date) < 40;


/*DONE*/


/*3.1.4*/

SELECT b.author
FROM book b
         LEFT JOIN applications a
                   ON a.ISBN = b.ISBN
WHERE a.ISBN IS NULL;

/*3.1.5*/

CREATE VIEW applications_per_school AS
SELECT a.application_id, u.school_email
FROM applications a
         INNER JOIN user u ON u.user_id = a.user_id;


/*3.2.1*/

SELECT book.title, book.author
FROM book
WHERE book.title = '%d';


SELECT book.title, book.author
FROM book
WHERE book.title = '%d'
  AND book.author = '%d';

/*3.3.1*/
SELECT *
FROM book
WHERE book.author = '%d';

/*3.3.2*/
CREATE VIEW applications_of_certain_user AS
SELECT applications.ISBN, applications.expiration_date
FROM applications
WHERE applications.user_id = 'login username';

SELECT b.title, aocu.expiration_date
FROM book b
         INNER JOIN applications_of_certain_user aocu on b.ISBN = aocu.ISBN;

SELECT b.*, a.author_name
FROM (SELECT stores.ISBN FROM stores WHERE stores.school_id = '') q
         INNER JOIN book b
                    ON b.ISBN = q.ISBN
         INNER JOIN writes w
                    ON w.ISBN = b.ISBN
         INNER JOIN author a
                    ON a.author_id = w.author_id


