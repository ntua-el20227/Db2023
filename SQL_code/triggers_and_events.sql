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
        SET NEW.start_date = NOW();
        SET NEW.expiration_date = DATE_ADD(NOW(), INTERVAL 3 MINUTE);
    END IF;
END;

/*Automatically changes the status of the applications to 'expired_borrowing' that expired by checking their expiration date each day*/
CREATE EVENT check_not_returned_books
    ON SCHEDULE
        EVERY 2 MINUTE
            STARTS NOW()
    DO
    UPDATE applications
    SET status_ = 'expired_borrowing'
    WHERE expiration_date < NOW()
      AND status_ = 'borrowed';

CREATE EVENT check_applications
    ON SCHEDULE
        EVERY 5 MINUTE
            STARTS NOW()
    DO
    DELETE
    FROM applications
    WHERE expiration_date < NOW()
      AND status_ = 'applied';

CREATE TRIGGER trigger_update_active_reservations_on_applying
    BEFORE INSERT
    ON applications
    FOR EACH ROW
BEGIN
    IF NEW.status_ = 'applied' THEN
        UPDATE user
        SET active_reservations = active_reservations + 1
        WHERE user_id = NEW.user_id;
    END IF;
END;

/* checks if the orders is right on the application table applied->borrowed
   borrowed->completed
   borrowed->expired_borrowing
   expired_borrowing->completed
*/
CREATE TRIGGER trigger_update_active_borrows
    BEFORE UPDATE
    ON applications
    FOR EACH ROW
BEGIN
    IF NEW.status_ = 'borrowed' AND OLD.status_ = 'applied' AND NEW.application_id != OLD.application_id THEN
        UPDATE user
        SET active_borrows = active_borrows + 1, active_reservations = active_reservations - 1
        WHERE user.user_id = NEW.user_id;

    ELSEIF NEW.status_ = 'completed' AND OLD.status_ = 'borrowed' AND NEW.application_id != OLD.application_id THEN
        UPDATE user
        SET active_borrows = active_borrows - 1
        WHERE user.user_id = NEW.user_id;

    ELSEIF NEW.status_= 'completed' AND OLD.status_ = 'expired_borrowing' AND NEW.application_id != OLD.application_id THEN
        UPDATE user
        SET active_borrows = active_borrows-1
        WHERE user.user_id = NEW.user_id;
    ELSE
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Invalid order in application';
    END IF;
END;


CREATE TRIGGER check_if_the_book_has_been_reserved_first
    BEFORE INSERT
    ON applications
    FOR EACH ROW
BEGIN
    IF NEW.status_ != 'applied' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You have to apply first';
    END IF;
END;

/*yet to see what happens if you brutally delete a borrowed book*/
CREATE TRIGGER trigger_update_active_reservations_on_delete
    AFTER DELETE
    ON applications
    FOR EACH ROW
BEGIN
    IF OLD.status_ = 'applied' THEN
        UPDATE user
        SET active_reservations = active_reservations - 1
        WHERE user.user_id = OLD.user_id;
    END IF;
END;

CREATE TRIGGER enforce_one_reservation_for_teacher
    BEFORE INSERT
    ON applications
    FOR EACH ROW
BEGIN
    IF (SELECT u.role_name FROM user u WHERE u.user_id = NEW.user_id) = 'teacher' AND
       (SELECT u.active_reservations FROM user u WHERE u.user_id = NEW.user_id) = 1 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Teacher can only borrow 1 book';
    END IF;
END;


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

CREATE TRIGGER sdoghodsigosd
    BEFORE INSERT
    ON applications
    FOR EACH ROW
BEGIN

        IF  (SELECT COUNT(*) FROM applications WHERE status_ != 'completed' AND NEW.user_id = user_id AND NEW.ISBN = ISBN) > 0 THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You have already applied/borrowed this book';
    END IF;
END;
