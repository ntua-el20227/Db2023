/* Create the Database */

USE db2023;

SET GLOBAL event_scheduler = ON;

CREATE TABLE IF NOT EXISTS admin
(
    admin_id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
    username VARCHAR(50) DEFAULT 'admin'    NOT NULL,
    pwd      VARCHAR(50)                    NOT NULL
);

CREATE TABLE IF NOT EXISTS school
(
    school_id            BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    school_name          VARCHAR(60)           NOT NULL UNIQUE,
    school_email         VARCHAR(60)           NOT NULL UNIQUE,
    principal_first_name VARCHAR(60)           NOT NULL,
    principal_last_name  VARCHAR(60)           NOT NULL,
    city                 VARCHAR(60)           NOT NULL,
    address              VARCHAR(60)           NOT NULL,
    phone_number         TINYINT(20)           NOT NULL
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
    school_name     VARCHAR(60)                                      NOT NULL,
    CONSTRAINT FK_school_name FOREIGN KEY (school_name)
        REFERENCES school (school_name)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS book
(
    ISBN      BIGINT        NOT NULL PRIMARY KEY,
    title     VARCHAR(100)   NOT NULL,
    summary   TEXT          NOT NULL,
    publisher VARCHAR(50)   NOT NULL,
    page_num  INT           NOT NULL CHECK (page_num > 0),
    category  VARCHAR(50)   NOT NULL,
    language_ VARCHAR(50)   NOT NULL,
    image     VARCHAR(1000) NOT NULL
);

CREATE TABLE IF NOT EXISTS author
(
    author_id   BIGINT    AUTO_INCREMENT NOT NULL PRIMARY KEY,
    author_name VARCHAR(100) NOT NULL UNIQUE
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
    word VARCHAR(50) NOT NULL,
    ISBN BIGINT      NOT NULL,
    CONSTRAINT book_key_words FOREIGN KEY (ISBN)
        REFERENCES book (ISBN),
    CONSTRAINT compound_PK_key_words PRIMARY KEY (word, ISBN)
);

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
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT compound_PK_stores PRIMARY KEY (school_id, ISBN)
);


CREATE TABLE IF NOT EXISTS applications
(
    user_id         BIGINT                                                      NOT NULL,
    ISBN            BIGINT                                                      NOT NULL,
    start_date      DATE                                                        NOT NULL,
    expiration_date DATE                                                        NOT NULL CHECK (expiration_date > start_date),
    status_         ENUM ('applied','borrowed','expired_borrowing','completed') NOT NULL,
    CONSTRAINT FK_application_user FOREIGN KEY (user_id)
        REFERENCES user (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_application_ISBN FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT compound_PK_applications PRIMARY KEY (user_id, ISBN)
);

CREATE TABLE review
(
    ISBN            BIGINT                         NOT NULL,
    user_id         BIGINT                         NOT NULL,
    evaluation      TEXT,
    like_scale      ENUM ('1', '2', '3', '4', '5') NOT NULL,
    approval_status ENUM ('approved','pending') DEFAULT 'pending',

    CONSTRAINT FK_book_review FOREIGN KEY (ISBN)
        REFERENCES book (ISBN)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT FK_user_review FOREIGN KEY (user_id)
        REFERENCES user (user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT compound_PK_review PRIMARY KEY (user_id, ISBN)
);

/* If a teacher uploads review then automatically make it active */
CREATE TRIGGER review_upload
    BEFORE INSERT
    ON review
    FOR EACH ROW
BEGIN
    IF NEW.approval_status = 'pending' AND (SELECT user.role_name
                                            FROM user
                                            WHERE user.user_id = NEW.user_id) = 'teacher'
    THEN
        SET NEW.approval_status = 'approved';
    END IF;
END;

CREATE TRIGGER trigger_update_dates_on_borrowing
    BEFORE UPDATE
    ON applications
    FOR EACH ROW
BEGIN
    IF NEW.status_ = 'borrowed' THEN
        SET NEW.start_date = CURRENT_DATE();
        SET NEW.expiration_date = DATE_ADD(CURRENT_DATE(), INTERVAL 1 WEEK);
    END IF;
END;

CREATE TRIGGER trigger_update_dates_on_applying
    BEFORE INSERT
    ON applications
    FOR EACH ROW
BEGIN
    IF NEW.status_ = 'applied' THEN
        SET NEW.start_date = CURRENT_DATE();
        SET NEW.expiration_date = DATE_ADD(CURRENT_DATE(), INTERVAL 1 WEEK);
    END IF;
END;

/*Automatically changes the status of the applications to 'expired_borrowing' that expired by checking their expiration date each day*/
CREATE EVENT check_not_returned_books
    ON SCHEDULE
        EVERY 1 DAY
            STARTS CURRENT_TIMESTAMP
    DO
    UPDATE applications
    SET status_ = 'expired_borrowing'
    WHERE expiration_date <= NOW()
      AND status_ = 'borrowed';

/*Automatically deletes the applications of the previous year*/
CREATE EVENT flush_cache
    ON SCHEDULE
        EVERY 1 DAY
            STARTS CURRENT_TIMESTAMP
    DO
    BEGIN
        DELETE
        FROM applications
        WHERE expiration_date <= MONTH(NOW()) - INTERVAL 3 YEAR
          AND status_ = 'completed';
    END;





