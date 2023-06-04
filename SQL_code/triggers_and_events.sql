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


CREATE TRIGGER trigger_update_active_borrows
    BEFORE UPDATE
    ON applications
    FOR EACH ROW
BEGIN

    IF NEW.status_ = 'borrowed' AND OLD.status_ = 'applied' THEN
	    SET NEW.start_date = NOW();
        SET NEW.expiration_date = DATE_ADD(NOW(), INTERVAL 1 WEEK);
        UPDATE user
        SET active_borrows      = active_borrows + 1,
            active_reservations = active_reservations - 1
        WHERE user.user_id = NEW.user_id;



    ELSEIF NEW.status_ = 'completed' AND OLD.status_ = 'borrowed' THEN
        UPDATE user
        SET active_borrows = active_borrows - 1
        WHERE user_id = NEW.user_id;
        
        UPDATE stores
        SET available_copies = available_copies + 1
        WHERE stores.ISBN = NEW.ISBN
          AND school_id = (SELECT s.school_id
                          FROM (SELECT user.school_name FROM user WHERE user_id = NEW.user_id) u
                          INNER JOIN school s ON s.school_name = u.school_name);
        
                                        
    ELSEIF NEW.status_ = 'completed' AND OLD.status_ = 'expired_borrowing' THEN
        UPDATE user
        SET active_borrows = active_borrows - 1
        WHERE user.user_id = NEW.user_id;
        UPDATE stores
        SET available_copies = available_copies + 1
        WHERE stores.ISBN = NEW.ISBN
          AND stores.school_id = (SELECT s.school_id
                                  FROM (SELECT user.school_name FROM user WHERE user.user_id = NEW.user_id) u
                                           INNER JOIN school s ON s.school_name = u.school_name);
 
    END IF;                                   
   
END;

CREATE TRIGGER trigger_update_dates_available_copies_on_applying
    BEFORE INSERT
    ON applications
    FOR EACH ROW
BEGIN
    IF (SELECT available_copies
        FROM stores
        WHERE ISBN = NEW.ISBN
          AND school_id = (SELECT s.school_id
                           FROM (SELECT user.school_name FROM user WHERE user.user_id = NEW.user_id) u
                                    INNER JOIN school s ON s.school_name = u.school_name)) > 0 THEN
        SET NEW.status_ = 'applied';
        SET NEW.start_date = NOW();
        SET NEW.expiration_date = DATE_ADD(NOW(), INTERVAL 3 MINUTE);
    END IF;

    IF NEW.status_ = 'applied' THEN
        SET NEW.start_date = NOW();
        SET NEW.expiration_date = DATE_ADD(NOW(), INTERVAL 3 MINUTE);
        UPDATE stores
        SET stores.available_copies = stores.available_copies - 1
        WHERE stores.ISBN = NEW.ISBN
          AND stores.school_id = (SELECT s.school_id
                                  FROM (SELECT user.school_name FROM user WHERE user.user_id = NEW.user_id) u
                                           INNER JOIN school s ON s.school_name = u.school_name);
        UPDATE user
        SET active_reservations = active_reservations + 1
        WHERE user_id = NEW.user_id;
    END IF;

    IF NEW.status_ = 'queued' THEN
        UPDATE user
        SET active_reservations = active_reservations + 1 WHERE user_id = NEW.user_id;
        SET NEW.start_date = NOW();
        SET NEW.expiration_date = DATE_ADD(NOW(), INTERVAL 3 MINUTE);
    END IF;

    IF (NEW.status_ != 'applied' AND NEW.status_ != 'queued') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You have to apply first';
    END IF;

    IF (SELECT u.role_name FROM user u WHERE u.user_id = NEW.user_id) = 'teacher' AND
       (SELECT u.active_reservations FROM user u WHERE u.user_id = NEW.user_id) = 2 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Teacher can only borrow 1 book';
    END IF;

    IF (SELECT COUNT(*)
        FROM applications
        WHERE status_ != 'completed'
          AND NEW.user_id = user_id
          AND NEW.ISBN = ISBN) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You have already applied/borrowed this book';
    END IF;

    IF (SELECT COUNT(*)
        FROM applications
        WHERE status_ = 'expired_borrowing'
          AND NEW.user_id = user_id
          AND NEW.ISBN = ISBN) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You cannot apply for borrow when u have an expired borrowing';
    END IF;

    IF (SELECT u.role_name FROM user u WHERE NEW.user_id = u.user_id) = 'handler' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Handlers cannot borrow books!';
    END IF;
END;


CREATE TRIGGER trigger_update_active_reservations_on_delete
    AFTER DELETE
    ON applications
    FOR EACH ROW
BEGIN
    IF OLD.status_ = 'applied' OR OLD.status_ = 'queued' THEN
        UPDATE user
        SET active_reservations = active_reservations - 1
        WHERE user.user_id = OLD.user_id;
    END IF;
    IF OLD.status_ = 'applied' THEN
        UPDATE stores
        SET available_copies = available_copies + 1
        WHERE ISBN = OLD.ISBN
          AND school_id = (SELECT school_id FROM school WHERE school_name = (SELECT school_name FROM user WHERE user_id = OLD.user_id));
    END IF;
END;


CREATE EVENT check_not_returned_books
    ON SCHEDULE
        EVERY 30 SECOND
            STARTS NOW()
    DO
    UPDATE applications
    SET status_ = 'expired_borrowing'
    WHERE expiration_date < NOW()
      AND status_ = 'borrowed';

CREATE EVENT event_check_book_availability
    ON SCHEDULE
        EVERY 30 SECOND
            STARTS NOW()
    DO
    BEGIN
        UPDATE applications a
            INNER JOIN stores s ON a.ISBN = s.ISBN
        SET a.status_ = 'applied',s.available_copies = s.available_copies - 1
        WHERE a.status_ = 'queued'
          AND s.available_copies > 0
         ORDER BY a.start_date ASC
        LIMIT 1;
    END;

CREATE TRIGGER expired_borrow_penalty
    BEFORE INSERT
    ON applications
    FOR EACH ROW
BEGIN
    IF (SELECT COUNT(*)
        FROM applications
        WHERE status_ = 'expired_borrowing'
          AND NEW.user_id = user_id
          AND NEW.ISBN = ISBN) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You cannot apply for borrow when u have an expired borrowing';
    END IF;
END;



CREATE TRIGGER duplicate_apply_borrow
    BEFORE INSERT
    ON applications
    FOR EACH ROW
BEGIN
    IF (SELECT COUNT(*)
        FROM applications
        WHERE status_ != 'completed'
          AND NEW.user_id = user_id
          AND NEW.ISBN = ISBN) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'You have already applied/borrowed this book';
    END IF;
END;

CREATE TRIGGER trigger_check_handler_school
BEFORE INSERT ON user
FOR EACH ROW
BEGIN
    IF (SELECT COUNT(*) FROM user WHERE school_name = NEW.school_name AND NEW.role_name = 'handler') > 0  THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Only one handler can be assigned to this school';
    END IF;
END;
