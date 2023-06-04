CREATE INDEX idx_user_school ON user(school_name);/*FK*/
CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_user_role_name ON user(role_name);

CREATE INDEX idx_applications_ISBN ON applications(ISBN);/*FK*/
CREATE INDEX idx_applications_user ON applications(user_id);/*FK*/
CREATE INDEX idx_applications_status_ ON applications(status_);

CREATE INDEX idx_school_principal_last_name ON school(principal_last_name);
CREATE INDEX idx_school_school_name ON school(school_name);

CREATE INDEX idx_book_title ON book(title);

CREATE INDEX idx_review_like_scale ON review(like_scale);
