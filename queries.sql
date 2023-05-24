/*queries*/

/*3.1.1*/
SELECT applications.application_id, applications.user_id, book.title
FROM applications
         INNER JOIN book
                    ON book.ISBN = applications.ISBN
WHERE MONTH(applications.start_date) = 1;

SELECT applications.application_id, applications.user_id, book.title
FROM applications
         INNER JOIN book
                    ON book.ISBN = applications.ISBN
WHERE YEAR(applications.start_date) = 2023;

SELECT applications.application_id, applications.user_id, book.title
FROM applications
         INNER JOIN book
                    ON book.ISBN = applications.ISBN
WHERE (YEAR(applications.start_date) = 2023
    AND MONTH(applications.start_date) = 1);

/*3.1.2*/

/* Prints the authors of the books that have a certain category*/
CREATE VIEW authors_of_category AS
SELECT book.author
FROM book
WHERE book.category = '%s';

/*Finds teachers that have applied the last year*/
CREATE VIEW teachers_of_category AS
SELECT u.first_name, u.last_name, a.ISBN
FROM user u
         INNER JOIN applications a
                    ON u.user_id = a.user_id
WHERE u.role_name = 'teacher'
  AND a.start_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR);

/*Find the title of that books borrowed by teachers and belong to certain category*/
/*CREATE VIEW book_title_borrowed_by_teacher_in_last_year_from_a_category AS*/
SELECT t.first_name, t.last_name, b.title, b.category
FROM teachers_of_category t
         INNER JOIN book b on t.ISBN = b.ISBN
WHERE b.category = '%d';

/*3.1.3*/
CREATE VIEW younger_teachers_books AS
SELECT u.*, a.ISBN
FROM user u
         INNER JOIN applications a
                    ON u.user_id = a.user_id
WHERE (u.role_name = 'teacher' AND u.age < 40);

SELECT ytb.*,b.title,COUNT(b.ISBN)
FROM book b
INNER JOIN younger_teachers_books ytb ON b.ISBN = ytb.ISBN;



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
WHERE book.title = '%d' AND book.author = '%d';

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
INNER JOIN applications_of_certain_user aocu on b.ISBN = aocu.ISBN
