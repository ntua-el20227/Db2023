/* Create the Database */

CREATE DATABASE db2023;

USE db2023;

SET GLOBAL event_scheduler = ON;

CREATE TABLE IF NOT EXISTS admin
(
    admin_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    username VARCHAR(100) DEFAULT 'admin'   NOT NULL,
    pwd      VARCHAR(100)                   NOT NULL
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS school
(
    school_id            BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    school_name          VARCHAR(100)          NOT NULL UNIQUE,
    school_email         VARCHAR(100)          NOT NULL UNIQUE,
    principal_first_name VARCHAR(100)          NOT NULL,
    principal_last_name  VARCHAR(100)          NOT NULL,
    city                 VARCHAR(100)          NOT NULL,
    address              VARCHAR(100)          NOT NULL,
    phone_number         BIGINT                NOT NULL
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS user
(
    user_id BIGINT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    pwd VARCHAR(100) NOT NULL
        CHECK (CHAR_LENGTH(pwd) > 3),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL,
    status_usr ENUM ('active','pending','removed') DEFAULT 'pending' NOT NULL,
    active_borrows TINYINT(10) DEFAULT 0 NOT NULL
        CHECK ((active_borrows < 3 AND active_borrows >= 0 AND role_name = 'student')
        OR(active_borrows < 2 AND active_borrows >=0 AND role_name = 'teacher')
        OR (active_borrows =0 AND role_name = 'handler')),
    role_name ENUM ('student', 'teacher', 'handler') NOT NULL,
    school_name VARCHAR(100) NOT NULL,
    active_reservations TINYINT(10) DEFAULT 0 NOT NULL
        CHECK ((active_reservations < 3 AND active_reservations >= 0 AND role_name = 'student')
        OR(active_reservations < 2 AND active_reservations >=0 AND role_name = 'teacher')
        OR (active_reservations =0 AND role_name = 'handler')),
    CONSTRAINT FK_school_name FOREIGN KEY (school_name)
        REFERENCES school (school_name)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS book
(
    ISBN      BIGINT        NOT NULL PRIMARY KEY,
    title     VARCHAR(100)  NOT NULL,
    summary   TEXT          NOT NULL,
    publisher VARCHAR(100)  NOT NULL,
    page_num  INT           NOT NULL CHECK (page_num > 0),
    language_ VARCHAR(50)   NOT NULL,
    image     VARCHAR(1000) NOT NULL
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS category
(
    category_id   BIGINT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    category_name VARCHAR(100) UNIQUE               NOT NULL
) ENGINE = InnoDB;

CREATE TABLE book_category
(
    category_id BIGINT NOT NULL,
    ISBN        BIGINT NOT NULL,
    CONSTRAINT FK_category FOREIGN KEY (category_id)
        REFERENCES category (category_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_book FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT compound_PK_category_book PRIMARY KEY (ISBN, category_id)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS author
(
    author_id   BIGINT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    author_name VARCHAR(100) UNIQUE                NOT NULL
) ENGINE = InnoDB;

CREATE TABLE book_author
(
    author_id BIGINT NOT NULL,
    ISBN      BIGINT NOT NULL,
    CONSTRAINT FK_author_writes FOREIGN KEY (author_id)
        REFERENCES author (author_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_book_writes FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT compound_PK_writes PRIMARY KEY (ISBN, author_id)
)ENGINE = InnoDB;
CREATE TABLE IF NOT EXISTS key_words
(
    word VARCHAR(50) NOT NULL,
    ISBN BIGINT      NOT NULL,
    CONSTRAINT book_key_words FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT compound_PK_key_words PRIMARY KEY (word, ISBN)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS stores
(
    school_id        BIGINT NOT NULL,
    ISBN             BIGINT NOT NULL,
    available_copies INT    NOT NULL CHECK (available_copies >= 0),
    CONSTRAINT school_stores_FK FOREIGN KEY (school_id)
        REFERENCES school (school_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT stores_book_FK FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT compound_PK_stores PRIMARY KEY (school_id, ISBN)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS applications
(
    application_id  BIGINT AUTO_INCREMENT                                                                    NOT NULL PRIMARY KEY,
    user_id         BIGINT                                                                                   NOT NULL,
    ISBN            BIGINT                                                                                   NOT NULL,
    start_date      DATETIME                                                                                 NOT NULL,
    expiration_date DATETIME CHECK (expiration_date >= start_date),
    status_         ENUM ('applied','borrowed','expired_borrowing','completed','queued') DEFAULT ('queued') NOT NULL,
    CONSTRAINT FK_application_user FOREIGN KEY (user_id)
        REFERENCES user (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_application_ISBN FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

CREATE TABLE review
(
    ISBN            BIGINT                         NOT NULL,
    user_id         BIGINT                         NOT NULL,
    evaluation      TEXT,
    like_scale      ENUM ('1', '2', '3', '4', '5') NOT NULL,
    approval_status ENUM ('approved','pending') DEFAULT 'pending',
    review_date     DATE                           NOT NULL,
    CONSTRAINT FK_book_review FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_user_review FOREIGN KEY (user_id)
        REFERENCES user (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT compound_PK_review PRIMARY KEY (user_id, ISBN)
) ENGINE = InnoDB;


