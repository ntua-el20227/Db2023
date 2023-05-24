/* Create the Database */

USE db2023;
CREATE TABLE IF NOT EXISTS admin
(
    admin_id INT AUTO_INCREMENT          NOT NULL,
    username VARCHAR(50) DEFAULT 'admin' NOT NULL,
    pwd      VARCHAR(50)                 NOT NULL
);

CREATE TABLE IF NOT EXISTS school
(
    school_id            BIGINT      NOT NULL PRIMARY KEY,
    school_name          VARCHAR(60) NOT NULL UNIQUE,
    school_email         VARCHAR(60) NOT NULL UNIQUE,
    principal_first_name VARCHAR(60) NOT NULL,
    principal_last_name  VARCHAR(60) NOT NULL,
    city                 VARCHAR(60) NOT NULL,
    address              VARCHAR(60) NOT NULL,
    phone_number         TINYINT(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS user
(
    user_id        BIGINT                                      NOT NULL PRIMARY KEY AUTO_INCREMENT,
    username       VARCHAR(50)                                 NOT NULL UNIQUE,
    pwd            VARCHAR(50)                                 NOT NULL,
    first_name     VARCHAR(50)                                 NOT NULL,
    last_name      VARCHAR(50)                                 NOT NULL,
    birth_date     DATE                                        NOT NULL,
    status_usr     ENUM ('active','pending') DEFAULT 'pending' NOT NULL,
    active_borrows TINYINT(5)                DEFAULT 0,
    role_name      ENUM ('student', 'teacher', 'handler')      NOT NULL,
    school_name    VARCHAR(60)                                 NOT NULL,
    CONSTRAINT FK_school_name FOREIGN KEY (school_name)
        REFERENCES school (school_name)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE VIEW user_age AS
SELECT YEAR(CURDATE()) - YEAR(birth_date)
FROM user;

CREATE TABLE IF NOT EXISTS book
(
    ISBN      BIGINT      NOT NULL PRIMARY KEY,
    title     VARCHAR(50) NOT NULL,
    summary   TEXT        NOT NULL,
    /*author    VARCHAR(50) NOT NULL,*/
    publisher VARCHAR(50) NOT NULL,
    page_num  INT         NOT NULL CHECK (page_num > 0),
    category  VARCHAR(50) NOT NULL,
    language_ VARCHAR(50) NOT NULL,
    image     VARCHAR(1000)
);

CREATE TABLE IF NOT EXISTS author
(
    author_id   BIGINT      NOT NULL AUTO_INCREMENT PRIMARY KEY,
    author_name VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS writes
(
    ISBN      BIGINT NOT NULL,
    author_id BIGINT NOT NULL,
    CONSTRAINT book_written FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT author_writes FOREIGN KEY (author_id)
        REFERENCES author (author_id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT compound_PK_writes PRIMARY KEY (ISBN, author_id)
);



CREATE TABLE IF NOT EXISTS key_words
(
    word VARCHAR(50) NOT NULL PRIMARY KEY UNIQUE,
    ISBN BIGINT      NOT NULL,
    CONSTRAINT book_key_words FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
);

CREATE TABLE IF NOT EXISTS stores
(
    school_id        VARCHAR(60) NOT NULL,
    ISBN             BIGINT      NOT NULL,
    available_copies INT         NOT NULL CHECK (available_copies >= 0),
    CONSTRAINT school_stores_FK FOREIGN KEY (school_id)
        REFERENCES school (school_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT stores_book_FK FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT compound_PK_stores PRIMARY KEY (school_id, ISBN)
);


CREATE TABLE IF NOT EXISTS applications
(
    application_id  BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    ISBN            BIGINT NOT NULL,
    start_date      DATE   NOT NULL,
    expiration_date DATE   NOT NULL CHECK (expiration_date > start_date),
    status_         ENUM ('applied','borrowed','expired_borrowing','completed'),
    CONSTRAINT FK_application_user FOREIGN KEY (user_id)
        REFERENCES user (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_application_ISBN FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE RESTRICT ON UPDATE CASCADE

);

CREATE TABLE review
(
    review_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    ISBN       BIGINT  NOT NULL,
    user_id    BIGINT  NOT NULL,
    evaluation TEXT,
    like_scale ENUM ('1', '2', '3', '4', '5'),
    status_    BOOLEAN NOT NULL,
    CONSTRAINT FK_book_review FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_user_review FOREIGN KEY (user_id)
        REFERENCES user (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

/*
CREATE TRIGGER trigger_update_dates_on_borrowing
    AFTER UPDATE
    ON applications
    FOR EACH ROW
BEGIN
    IF NEW.status_ = 'borrowed' THEN
        SET NEW.start_date = CURRENT_DATE();
        SET NEW.expiration_date = DATE_ADD(CURRENT_DATE(), INTERVAL 1 WEEK);
    END IF;
END;


/* just a query */
/*


CREATE TRIGGER trigger_update_dates_on_applying
    AFTER INSERT
    ON applications
    FOR EACH ROW
BEGIN
    IF NEW.status_ = 'applied' THEN
        SET NEW.start_date = CURRENT_DATE();
        SET NEW.expiration_date = DATE_ADD(CURRENT_DATE(), INTERVAL 1 WEEK);
    END IF;
END;

/*
CREATE EVENT check_not_returned
    ON SCHEDULE EVERY 1 DAY
        STARTS '2023-05-14 00:00:00'
    DO
    BEGIN
        -- Enter the SQL query you want to run here
        SELECT IF book.status_ = 'borrowed' AND new.expiration_date >=  CURRENT_DATE()

    END;
 */

