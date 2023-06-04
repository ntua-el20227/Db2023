from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from mydb import app, db
from mydb import utils
from datetime import datetime

mysession = {}


@app.route('/', methods=['GET', 'POST'])  #checked
def index():
    mysession.clear()
    cur = db.connection.cursor()
    if request.method == 'POST':
        school_name = request.form['school']
        query = f"SELECT * FROM school WHERE school_name='{school_name}'"
        cur.execute(query)
        record = cur.fetchone()
        if record:
            cur.close()
            school_id = record[0]
            mysession["school"] = school_id
            return redirect(url_for('schoolpage'))
        flash("Choose a School", "success")
    query = " SELECT * FROM school"
    cur.execute(query)
    record = cur.fetchall()
    school_names = [entry[1] for entry in record]
    return render_template('index.html', title='Landing Page', school_names=school_names)


@app.route('/adminlogin', methods=['POST'])  # checked
def adminlogin():
    username = request.form['username']
    password = request.form['password']
    cur = db.connection.cursor()
    query = f"SELECT * FROM admin WHERE username='{username}' AND pwd='{password}'"
    cur.execute(query)
    record = cur.fetchone()
    cur.close()
    if record:
        mysession['status'] = "admin"
        mysession['user'] = username
        return redirect(url_for('adminhome'))
    flash("Wrong credentials", "success")
    return redirect(url_for('index'))



@app.route('/adminhome')  # checked
def adminhome():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            return render_template('adminhome.html', title='Home Page')
    return redirect(url_for('index'))



@app.route("/adminhome/backup")
def adminbackup():   
    if 'status' in mysession:
        if mysession['status'] == "admin":
            utils.backup()
            flash("Database backup created", "success")
            return redirect(url_for('adminhome'))
    return redirect(url_for('index'))

@app.route("/adminhome/restore")
def adminrestore():   
    if 'status' in mysession:
        if mysession['status'] == "admin":
            utils.restore()
            flash("Databased restored", "success")
            return redirect(url_for('adminhome'))
    return redirect(url_for('index'))

@app.route('/adminhome/pwd', methods=['POST'])  # checked
def adminpwd():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            pwd1 = request.form['pwd1']
            pwd2 = request.form['pwd2']
            if pwd1 == pwd2:
                cur = db.connection.cursor()
                query = f"""UPDATE admin SET pwd = '{pwd1}'
            WHERE username = '{mysession['user']}'"""
                cur.execute(query)
                db.connection.commit()
                cur.close()
                flash("Password successfully changed", "success")
                return redirect(url_for('adminhome'))
            flash("Passwords do not match", "success")
            return redirect(url_for('adminhome'))
    return redirect(url_for('index'))


@app.route('/adminhome/schools')  # checked
def schools():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            query = " SELECT * FROM school"
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            schools = []
            info = cur.fetchall()
            for entry in info:
                x = dict(zip(column_names, entry))
                query = f"SELECT * FROM user WHERE role_name = 'handler' and school_name = '{entry[1]}'"
                cur.execute(query)
                record = cur.fetchone()
                if record:
                    x["handler_first_name"] = record[3]
                    x["handler_last_name"] = record[4]
                else:
                    x["handler_first_name"] = '-'
                    x["handler_last_name"] = ''
                schools.append(x)
            cur.close()
            return render_template('adminschools.html', title='Schools', schools=schools)
    return redirect(url_for('index'))


@app.route("/adminhome/schools/create", methods=["POST"])  # checked
def new_school():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            name = request.form['name']
            email = request.form['email']
            principal_first_name = request.form['principal_first_name']
            principal_last_name = request.form['principal_last_name']
            city = request.form['city']
            address = request.form['address']
            phone_number = request.form['phone_number']
            query = f"""
            INSERT INTO school (school_name, school_email, principal_first_name, principal_last_name, city, address, phone_number) 
            VALUES ('{name}', '{email}', '{principal_first_name}', '{principal_last_name}', '{city}', '{address}', '{phone_number}') """
            try:
                cur = db.connection.cursor()
                cur.execute(query)
                db.connection.commit()
                cur.close()
                flash("School added successfully", "success")
            except Exception as e:
                flash(str(e), "success")
            return redirect('/adminhome/schools')
    return redirect(url_for('index'))


@app.route("/adminhome/schools/<int:school_id>/edit", methods=["GET" , "POST"])  # checked
def school_edit(school_id):
    if 'status' in mysession:
        if mysession['status'] == "admin":
            if request.method=="GET":
                cur = db.connection.cursor()
                query = f" SELECT * FROM school where school_id={school_id}"
                cur.execute(query)
                column_names = [i[0] for i in cur.description]
                record = cur.fetchone()
                school = dict(zip(column_names, record))
                cur.close()
                return render_template('admineditschool.html', title='School', school=school)
            if request.method=="POST":
                cur = db.connection.cursor()
                name = request.form['name']
                email = request.form['email']
                principal_first_name = request.form['principal_first_name']
                principal_last_name = request.form['principal_last_name']
                city = request.form['city']
                address = request.form['address']
                phone_number = request.form['phone_number']
                query = f"""
                UPDATE school SET school_name = '{name}', school_email = '{email}', principal_first_name = '{principal_first_name}', principal_last_name = '{principal_last_name}', city = '{city}'
                , address = '{address}', phone_number = '{phone_number}' WHERE school_id='{school_id}'"""
                try:
                    cur = db.connection.cursor()
                    cur.execute(query)
                    db.connection.commit()
                    cur.close()
                    flash("School edited successfully", "success")
                except Exception as e:
                    flash(str(e), "success")
                return redirect('/adminhome/schools')
    return redirect(url_for('index'))


@app.route("/adminhome/schools/<int:school_id>/delete")  # checked
def school_delete(school_id):
    if 'status' in mysession:
        if mysession['status'] == "admin":
            query = f"DELETE FROM school WHERE school_id = '{school_id}'"
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("School deleted", "success")
            return redirect('/adminhome/schools')
    return redirect(url_for('index'))


@app.route('/adminhome/handlers')  # checked
def handlers():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            query = " SELECT * FROM user where role_name = 'handler'"
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            handlers = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()
            return render_template('adminhandlers.html', title='Handlers', handlers=handlers)
    return redirect(url_for('index'))


@app.route('/adminhome/handlers/<int:handler_id>/accept')
def handler_accept(handler_id):
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            query = f" UPDATE user SET status_usr = 'active' WHERE user_id = '{handler_id}'"
            try:
                cur.execute(query)
                db.connection.commit()
                cur.close()
                flash("Handler added", "success")
            except Exception as e:
                flash(str(e), "success")
            return redirect('/adminhome/handlers')
    return redirect(url_for('index'))


@app.route('/adminhome/handlers/<int:handler_id>/reject')
def handler_reject(handler_id):
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            query = f"DELETE FROM user WHERE user_id = '{handler_id}'"
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Handler discarded", "success")
            return redirect('/adminhome/handlers')
    return redirect(url_for('index'))



@app.route('/handlerapplication', methods=['POST'])  # birthday missing, rest is checked
def handlerapplication():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form['username']
    birthday = request.form['birthday']
    pwd1 = request.form['pwd1']
    pwd2 = request.form['pwd2']
    if pwd1 != pwd2:
        flash("Passwords do not match", "success")
        return redirect(url_for('index'))
    try:
        cur = db.connection.cursor()
        school_name = request.form['school_list']
        query = f"INSERT INTO user (first_name, last_name, birth_date, username, pwd, school_name, role_name) VALUES ('{first_name}', '{last_name}', DATE '{birthday}', '{username}' ,'{pwd1}', '{school_name}', 'handler')"
        cur.execute(query)
        db.connection.commit()
        cur.close()
        flash("Application sent", "success")
    except Exception as e:
        flash(str(e), "success")
        return redirect('/')
    return redirect(url_for('index'))


@app.route('/schoolpage')  # checked
def schoolpage():
    if 'school' in mysession:
        id = mysession["school"]
        cur = db.connection.cursor()
        query = f"SELECT * FROM school WHERE school_id='{id}'"
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        record = cur.fetchone()
        school = dict(zip(column_names, record))
        cur.close()
        return render_template('schoolpage.html', school=school, title='School Page')
    return redirect(url_for('index'))



@app.route('/schoolpage/login', methods=['POST'])  # checked
def login():
    if "school" in mysession:
        username = request.form['username']
        password = request.form['password']
        cur = db.connection.cursor()
        id = mysession["school"]
        query = f"SELECT * FROM school WHERE school_id='{id}'"
        cur.execute(query)
        record = cur.fetchone()
        school_name = record[1]
        query = f"SELECT * FROM user WHERE username='{username}' AND pwd='{password}' AND school_name='{school_name}'"
        cur.execute(query)
        record = cur.fetchone()
        cur.close()
        if record:
            is_active = record[6]
            if is_active == "active":
                mysession['user'] = {'user_id': record[0], 'username': record[1], 'pwd': record[2],
                                     'first_name': record[3], 'last_name': record[4], 'birthday': record[5],
                                     'active_borrows': record[7], 'role': record[8], 'school_name': record[9],
                                     'active_reservations': record[10]}
                return redirect(url_for('userhome'))
            flash("User is not activated yet", "success")
            return redirect(url_for('schoolpage'))
        flash("Wrong credentials", "success")
        return redirect(url_for('schoolpage'))
    return redirect(url_for('index'))


@app.route('/schoolpage/register', methods=['POST'])  # birthday missing, rest is checked
def register():
    if "school" in mysession:
        cur = db.connection.cursor()
        id = mysession["school"]
        query = f"SELECT * FROM school WHERE school_id='{id}'"
        cur.execute(query)
        record = cur.fetchone()
        cur.close()
        school_name = record[1]
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        pwd1 = request.form['pwd1']
        pwd2 = request.form['pwd2']
        birthday = request.form['birthday']
        role = request.form['role']
        if pwd1 != pwd2:
            flash("Passwords do not match", "success")
            return redirect(url_for('schoolpage'))
        query = f"INSERT INTO user (first_name, last_name, birth_date, username, pwd, school_name, role_name, status_usr) VALUES ('{first_name}', '{last_name}', '{birthday}' ,'{username}', '{pwd1}', '{school_name}', '{role}', 'Pending')"
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Request sent", "success")
            return redirect(url_for('schoolpage'))
        except Exception as e:
            flash(str(e), "success")
        return redirect(url_for('schoolpage'))
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome')  # checked
def userhome():
    if 'user' in mysession and 'school' in mysession:
        return redirect(url_for('books'))


@app.route('/schoolpage/userhome/pwd', methods=['POST'])  # checked
def userpwd():
    if 'user' in mysession and 'school' in mysession:
        pwd1 = request.form['pwd1']
        pwd2 = request.form['pwd2']
        if pwd1 == pwd2:
            cur = db.connection.cursor()
            query = f"""UPDATE user SET pwd = '{pwd1}'
            WHERE user_id = {mysession['user']['user_id']}"""
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Password successfully changed", "success")
            mysession["user"]['pwd'] = pwd1
            return redirect(url_for('userhome'))
        flash("Passwords do not match", "success")
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/editprofile', methods=['POST'])  # checked
def profile():
    if 'user' in mysession and 'school' in mysession:
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthday = request.form['birthday']
        cur = db.connection.cursor()
        query = f"""UPDATE user SET username = '{username}', first_name = '{first_name}', last_name = '{last_name}', birth_date = DATE '{birthday}' 
             WHERE user_id = '{mysession['user']['user_id']}'"""
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            mysession['user']['username'] = username
            mysession['user']['first_name'] = first_name
            mysession['user']['last_name'] = last_name
            mysession['user']['birthday'] = birthday
            flash("Profile updated successfully", "success")
        except Exception as e:
            flash(str(e), "success")
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/users')
def users():
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            cur = db.connection.cursor()
            school_name = mysession["user"]["school_name"]
            query = f" SELECT * FROM user where role_name != 'handler' and school_name= '{school_name}'"
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            users = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()
            return render_template('handlerusers.html', title='Users', users=users)
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/users/<int:user_id>/accept')
def user_accept(user_id):
    if 'user' in mysession and 'school' in mysession:
        if mysession['user']['role'] == "handler":
            cur = db.connection.cursor()
            query = f" UPDATE user SET status_usr = 'active' WHERE user_id = '{user_id}'"
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("User added", "success")
            return redirect('/schoolpage/userhome/users')
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/users/<int:user_id>/remove')
def user_remove(user_id):
    if 'user' in mysession and 'school' in mysession:
        if mysession['user']['role'] == "handler":
            cur = db.connection.cursor()
            query = f" UPDATE user SET status_usr = 'removed' WHERE user_id = '{user_id}'"
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("User removed", "success")
            return redirect('/schoolpage/userhome/users')
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/users/<int:user_id>/deactivate')
def user_deactivate(user_id):
    if 'user' in mysession and 'school' in mysession:
        if mysession['user']['role'] == "handler":
            cur = db.connection.cursor()
            query = f" UPDATE user SET status_usr = 'pending' WHERE user_id = '{user_id}'"
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("User deactivated", "success")
            return redirect('/schoolpage/userhome/users')
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/books', methods=['GET', 'POST'])  # checked
def books():
    if 'user' in mysession and 'school' in mysession:
        if request.method == 'POST':
            ISBN = request.form['book']
            cur = db.connection.cursor()
            query = f"SELECT * FROM book WHERE ISBN='{ISBN}'"
            cur.execute(query)
            record = cur.fetchone()
            if record:
                return redirect(f'/schoolpage/userhome/books/{ISBN}/add')
            flash("ISBN does not exists in database.")
            return redirect('/schoolpage/userhome/books')
        cur = db.connection.cursor()
        school_id = mysession["school"]
        query = f"""SELECT b.*, q.available_copies,
        GROUP_CONCAT(DISTINCT a.author_name ORDER BY a.author_name SEPARATOR ',') AS author_names, 
        GROUP_CONCAT(DISTINCT c.category_name ORDER BY c.category_name SEPARATOR ',') AS book_categories
        FROM (SELECT stores.ISBN, stores.available_copies FROM stores WHERE stores.school_id = '{school_id}') q 
        INNER JOIN book b ON b.ISBN = q.ISBN
        INNER JOIN book_category bc ON q.ISBN = bc.ISBN
        INNER JOIN category c ON bc.category_id = c.category_id
        INNER JOIN book_author ba ON q.ISBN = ba.ISBN
        INNER JOIN author a ON a.author_id = ba.author_id
        GROUP BY b.ISBN, b.title"""
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        books = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        query = f"""SELECT DISTINCT a.author_name 
                    FROM book_author ba 
                    INNER JOIN (SELECT ISBN FROM stores WHERE school_id = {school_id}) s
                    ON ba.ISBN = s.ISBN
                    INNER JOIN author a
                    ON a.author_id = ba.author_id
                    ORDER BY a.author_name"""
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        authors = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        query = f"""SELECT DISTINCT c.category_name 
                    FROM book_category bc 
                    INNER JOIN (SELECT ISBN FROM stores WHERE school_id = {school_id}) s
                    ON bc.ISBN = s.ISBN
                    INNER JOIN category c
                    ON c.category_id = bc.category_id
                    ORDER BY c.category_name"""
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        categories = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()
        return render_template('books.html', user=mysession['user'], title='Books', books=books, authors=authors, categories=categories)
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/books/<int:ISBN>/add', methods=['GET', 'POST'])  # checked
def add_book(ISBN):
    if 'user' in mysession and 'school' in mysession:
        if mysession['user']['role'] == "handler":
            if request.method == 'POST':
                ISBN = request.form['isbn']
                copies = request.form["copies"]
                id = mysession["school"]
                try:
                    cur = db.connection.cursor()
                    query = f"""INSERT INTO stores(school_id, ISBN, available_copies) VALUES ('{id}',{ISBN},{copies})"""
                    cur.execute(query)
                    db.connection.commit()
                    flash("Book added successfully!", "success")
                except Exception as e:
                    flash(str(e), "success")
                return redirect(url_for('books'))

            cur = db.connection.cursor()
            query = f"""SELECT b.*, 
                    GROUP_CONCAT(DISTINCT a.author_name ORDER BY a.author_name SEPARATOR ',') AS author_names, 
                    GROUP_CONCAT(DISTINCT c.category_name ORDER BY c.category_name SEPARATOR ',') AS book_categories, 
                    GROUP_CONCAT(DISTINCT kw.word ORDER BY kw.word SEPARATOR ',') AS key_words
                    FROM book b
                    INNER JOIN book_author ba on b.ISBN = ba.ISBN 
                    INNER JOIN author a ON ba.author_id = a.author_id
                    INNER JOIN book_category bc ON bc.ISBN = b.ISBN
                    INNER JOIN category c ON c.category_id = bc.category_id
                    INNER JOIN key_words kw  ON kw.ISBN = b.ISBN
                    WHERE b.ISBN = '{ISBN}'"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            book = dict(zip(column_names, cur.fetchone()))
            return render_template('bookadd.html', book=book)
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/books/create', methods=['GET', 'POST'])
def new_book():
    if 'user' in mysession and 'school' in mysession:
        if mysession['user']['role'] == "handler":
            if request.method == 'POST':
                ISBN = request.form['isbn']
                title = request.form['title']
                summary = request.form['summary']
                authors = request.form['author']
                author_names = authors.split(',')
                publisher = request.form['publisher']
                pages_num = request.form['pages']
                categories = request.form['category']
                category_names = categories.split(',')
                keywords = request.form['keyword']
                keyword_names = keywords.split(',')
                language = request.form['language']
                image = request.form['image']
                copies = request.form['copies']
                id = mysession["school"]
                try:
                    cur = db.connection.cursor()
                    query = f"""INSERT INTO book (ISBN, title, summary, publisher, page_num, language_, image) 
                    VALUES ({ISBN},"{title}","{summary}","{publisher}",{pages_num},"{language}","{image}")"""
                    cur.execute(query)
                    db.connection.commit()
                    for category in category_names:
                        query = f"""INSERT IGNORE INTO category(category_name) VALUES ('{category.strip()}')"""
                        cur.execute(query)
                        db.connection.commit()
                        query = f"""  SELECT category_id FROM category WHERE category_name = '{category.strip()}' """
                        cur.execute(query)
                        record = cur.fetchone()
                        query = f"""INSERT IGNORE INTO book_category(ISBN,category_id) VALUES ({ISBN},{record[0]})"""
                        cur.execute(query)
                        db.connection.commit()
                    for author in author_names:
                        query = f"""INSERT IGNORE INTO author(author_name) VALUES ('{author.strip()}')"""
                        cur.execute(query)
                        db.connection.commit()
                        query = f"""  SELECT author_id FROM author WHERE author_name = '{author.strip()}' """
                        cur.execute(query)
                        record = cur.fetchone()
                        query = f"""INSERT IGNORE INTO book_author(ISBN,author_id) VALUES ({ISBN},{record[0]})"""
                        cur.execute(query)
                        db.connection.commit()
                    for keyword in keyword_names:
                        query = f"""INSERT INTO key_words(word, ISBN) VALUES ('{keyword.strip()}',{ISBN})"""
                        cur.execute(query)
                        db.connection.commit()
                    query = f"""INSERT INTO stores(school_id, ISBN, available_copies) VALUES ('{id}', '{ISBN}','{copies}')"""
                    cur.execute(query)
                    db.connection.commit()
                    flash("New Book added successfully!", "success")
                except Exception as e:
                    flash(str(e), "success")
                return redirect(url_for('books'))
            return render_template('bookcreate.html', title='Add a Book')
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/books/<int:ISBN>/details', methods=['GET', 'POST'])  # checked
def bookdetails(ISBN):
    if 'user' in mysession and 'school' in mysession:
        if request.method == 'POST':
            if mysession['user']['role'] == "handler":
                if "update" in request.form:
                    new_ISBN = request.form['isbn']
                    title = request.form['title']
                    summary = request.form['summary']
                    authors = request.form['authors']
                    author_names = authors.split(',')
                    publisher = request.form['publisher']
                    pages_num = request.form['pages']
                    categories = request.form['category']
                    category_names = categories.split(',')
                    language = request.form['language']
                    keywords = request.form['keyword']
                    keyword_names = keywords.split(',')
                    image = request.form['image']
                    copies = request.form['copies']
                    id = mysession["school"]

                    try:
                        cur = db.connection.cursor()
                        query = f"""UPDATE book SET ISBN={new_ISBN},title='{title}',
                                    summary='{summary}',publisher='{publisher}',
                                    page_num={pages_num},language_='{language}',image='{image}' 
                                    WHERE ISBN = {ISBN}"""
                        cur.execute(query)
                        db.connection.commit()
                        query = f"""DELETE FROM book_category WHERE ISBN = {new_ISBN}"""
                        cur.execute(query)
                        db.connection.commit()
                        for category in category_names:
                            query = f"""INSERT IGNORE INTO category(category_name) VALUES ('{category.strip()}')"""
                            cur.execute(query)
                            db.connection.commit()
                            query = f"""SELECT category_id FROM category WHERE category_name = '{category.strip()}' """
                            cur.execute(query)
                            record = cur.fetchone()
                            query = f"""INSERT INTO book_category(ISBN,category_id) VALUES ({new_ISBN},{record[0]})"""
                            cur.execute(query)
                            db.connection.commit()
                        query = f"""DELETE FROM book_author WHERE ISBN = {new_ISBN}"""
                        cur.execute(query)
                        db.connection.commit()
                        for author in author_names:
                            query = f"""INSERT IGNORE INTO author(author_name) VALUES ('{author.strip()}')"""
                            cur.execute(query)
                            db.connection.commit()
                            query = f"""SELECT author_id FROM author WHERE author_name = '{author.strip()}' """
                            cur.execute(query)
                            record = cur.fetchone()
                            query = f"""INSERT INTO book_author(ISBN,author_id) VALUES ({ISBN},{record[0]})"""
                            cur.execute(query)
                            db.connection.commit()
                        query = f"""DELETE FROM key_words WHERE ISBN = {new_ISBN}"""
                        cur.execute(query)
                        db.connection.commit()
                        for keyword in keyword_names:
                            query = f"""INSERT INTO key_words(word,ISBN) VALUES ('{keyword.strip()}',{new_ISBN})"""
                            cur.execute(query)
                            db.connection.commit()
                        query = f"""UPDATE  stores SET available_copies = {copies} WHERE school_id = {id} AND ISBN = {new_ISBN} """
                        cur.execute(query)
                        db.connection.commit()
                        flash("Book edited successfully!", "success")
                    except Exception as e:
                        flash(str(e), "success")
                    return redirect(url_for('books'))
                if "delete" in request.form:
                    id = mysession["school"]
                    cur = db.connection.cursor()
                    query = f"""DELETE FROM stores WHERE ISBN = {ISBN} AND school_id = {id}"""
                    cur.execute(query)
                    db.connection.commit()
                    flash("Book deleted successfully!", "success")
                    return redirect(url_for('books'))
            if "reserve" in request.form:
                try:
                    id = mysession["user"]['user_id']
                    cur = db.connection.cursor()
                    query = f"""INSERT INTO applications(user_id, ISBN, start_date) VALUES ('{id}', '{ISBN}',CURDATE())"""
                    cur.execute(query)
                    db.connection.commit()
                    mysession['user']['active_reservations'] += 1

                    flash("Book reserved successfully!", "success")
                except Exception as e:
                    flash(str(e), "success")
                return redirect(url_for('books'))

        cur = db.connection.cursor()
        school_id = mysession["school"]
        query = f""" SELECT b.*, s.available_copies, 
                     GROUP_CONCAT(DISTINCT a.author_name ORDER BY a.author_name SEPARATOR ',') AS author_names, 
                     GROUP_CONCAT(DISTINCT c.category_name ORDER BY c.category_name SEPARATOR ',') AS book_categories, 
                     GROUP_CONCAT(DISTINCT kw.word ORDER BY kw.word SEPARATOR ',') AS key_words
                     FROM (SELECT book.* FROM book WHERE book.ISBN = {ISBN}) b 
                     INNER JOIN book_author ba on b.ISBN = ba.ISBN 
                     INNER JOIN author a ON ba.author_id = a.author_id
                     INNER JOIN book_category bc ON bc.ISBN = b.ISBN
                     INNER JOIN category c ON c.category_id = bc.category_id
                     INNER JOIN key_words kw on kw.ISBN = b.ISBN
                     INNER JOIN stores s on s.ISBN = b.ISBN
                     WHERE s.school_id = {school_id}
                     GROUP BY b.ISBN, b.title"""
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        book = dict(zip(column_names, cur.fetchone()))
        query = f"""SELECT approved_reviews.like_scale
                    FROM (SELECT * FROM review WHERE approval_status = 'approved' AND ISBN = {ISBN}) 
                    approved_reviews
                    INNER JOIN user u 
                    ON u.user_id = approved_reviews.user_id"""
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        score = 0
        size = 0
        for entry in cur.fetchall():
            x = dict(zip(column_names, entry))
            score += int(x["like_scale"])
            size += 1
        if size:
            average = str(round(score/size, 2))
        else:
            average = 0
        return render_template('bookdetails.html', user=mysession['user'], title='Details',book=book, average=average, size=size)
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/reservations')
def reservations():
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            cur = db.connection.cursor()
            school_name = mysession["user"]['school_name']
            query = f""" SELECT u.user_id,u.first_name,u.last_name,u.role_name,
            b.ISBN,b.title,a.start_date
            ,a.expiration_date,a.application_id
            FROM applications a
            INNER JOIN user u ON a.user_id = u.user_id 
            INNER JOIN book b ON a.ISBN = b.ISBN
            WHERE a.status_ = 'applied' AND u.school_name = '{school_name}' 
            ORDER BY a.start_date;"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            reservations = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            school_id = mysession["school"]
            query = f"""SELECT b.*, q.available_copies,
        GROUP_CONCAT(DISTINCT a.author_name ORDER BY a.author_name SEPARATOR ',') AS author_names, 
        GROUP_CONCAT(DISTINCT c.category_name ORDER BY c.category_name SEPARATOR ',') AS book_categories
        FROM (SELECT stores.ISBN, stores.available_copies FROM stores WHERE stores.school_id = '{school_id}') q 
        INNER JOIN book b ON b.ISBN = q.ISBN
        INNER JOIN book_category bc ON q.ISBN = bc.ISBN
        INNER JOIN category c ON bc.category_id = c.category_id
        INNER JOIN book_author ba ON q.ISBN = ba.ISBN
        INNER JOIN author a ON a.author_id = ba.author_id
        GROUP BY b.ISBN, b.title"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            books = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()
            return render_template('handlerreservations.html', title='Reservations', reservations=reservations, books=books)
        user_id = mysession["user"]["user_id"]
        cur = db.connection.cursor()
        query = f""" SELECT b.ISBN,b.title,a.start_date,a.expiration_date
                     FROM applications a
                     INNER JOIN user u ON a.user_id = u.user_id
                     INNER JOIN book b ON a.ISBN = b.ISBN
                     WHERE a.status_ = 'applied' AND u.user_id = {user_id} """
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        reservations = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        return render_template('myreservations.html', title='Reservations', reservations=reservations, user=mysession["user"])
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/reservations/<int:application_id>/accept')
def reservation_accept(application_id):
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            cur = db.connection.cursor()
            query = f""" UPDATE applications SET status_ = 'borrowed' WHERE application_id = {application_id}"""
            try:
                cur.execute(query)
                db.connection.commit()
                cur.close()
                flash("Book is borrowed", "success")
            except Exception as e:
                flash("This book has no available copies", "success")
                query = """UPDATE applications 
                            SET applications.expiration_date = DATE_ADD(applications.start_date,INTERVAL 2 MONTH); 
                        """
                cur.execute(query)
                db.connection.commit()
                cur.close()
            return redirect('/schoolpage/userhome/reservations')
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/reservations/<int:application_id>/reject')
def reservation_reject(application_id):
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            cur = db.connection.cursor()
            query = f"DELETE FROM applications WHERE application_id = {application_id} "
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Reservation discarded", "success")
            return redirect('/schoolpage/userhome/reservations')
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/borrows')
def borrows():
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            cur = db.connection.cursor()
            school_name = mysession["user"]['school_name']
            query = f""" SELECT u.user_id,u.first_name,u.last_name,u.role_name,b.ISBN,b.title,a.start_date,a.expiration_date,a.application_id
FROM applications a
INNER JOIN user u ON a.user_id = u.user_id 
INNER JOIN book b ON a.ISBN = b.ISBN
WHERE (a.status_ = 'borrowed' OR a.status_ = 'expired_borrowing')  AND u.school_name = '{school_name}'
 ORDER BY a.start_date;
 """
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            borrows = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()
            return render_template('handlerborrows.html', title='Borrows', borrows=borrows)
        user_id = mysession["user"]["user_id"]
        cur = db.connection.cursor()
        query = f""" SELECT b.ISBN,b.title,a.start_date,a.expiration_date
FROM applications a
INNER JOIN user u ON a.user_id = u.user_id
INNER JOIN book b ON a.ISBN = b.ISBN
WHERE (a.status_ = 'borrowed' OR a.status_ = 'expired_borrowing') AND u.user_id = {user_id} """
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        borrows = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()
        return render_template('myborrows.html', title='Borrows', borrows=borrows, user=mysession["user"])
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/history')
def history():
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            cur = db.connection.cursor()
            school_name = mysession["user"]['school_name']
            query = f""" SELECT a.application_id, u.user_id,u.first_name,u.last_name,u.role_name,b.ISBN,b.title
FROM applications a
INNER JOIN user u ON a.user_id = u.user_id 
INNER JOIN book b ON a.ISBN = b.ISBN
WHERE a.status_ = 'completed' AND u.school_name = '{school_name}' """
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            history = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()
            return render_template('handlerhistory.html', title='History', history=history)
        user_id = mysession["user"]["user_id"]
        cur = db.connection.cursor()
        query = f""" SELECT a.application_id, b.ISBN,b.title
FROM applications a
INNER JOIN user u ON a.user_id = u.user_id
INNER JOIN book b ON a.ISBN = b.ISBN
WHERE a.status_ = 'completed' AND u.user_id = {user_id} """
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        history = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        query = f"""SELECT * from review WHERE user_id={user_id}"""
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        reviews = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()
        return render_template('myhistory.html', title='History', history=history, reviews=reviews, revsISBN=[review["ISBN"] for review in reviews], user=mysession["user"])
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/borrows/<int:application_id>/completed')
def borrows_completed(application_id):
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            cur = db.connection.cursor()
            query = f""" UPDATE applications SET status_ = 'completed' WHERE application_id = {application_id} AND (status_ = 'borrowed' OR status_ = 'expired_borrowing') """
            try:
                cur.execute(query)
                db.connection.commit()
                cur.close()
                flash("Book is returned", "success")
            except Exception as e:
                flash(str(e), "success")
            return redirect('/schoolpage/userhome/borrows')
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/reservations/create', methods=['POST'])
def new_reservation():
    if 'user' in mysession and 'school' in mysession:
        if mysession['user']['role'] == "handler":
            if request.method == 'POST':
                username = request.form['username']
                ISBN = request.form['isbn']
                try:
                    cur = db.connection.cursor()
                    query = f"""Select user_id FROM user WHERE username = '{username}' """
                    cur.execute(query)
                    record = cur.fetchone()
                    if record:
                        id = record[0]
                        query = f"""INSERT INTO applications(user_id, ISBN, start_date) VALUES ('{id}', '{ISBN}',CURDATE())"""
                        cur.execute(query)
                        db.connection.commit()
                        flash("Book reserved successfully!", "success")
                    else:
                        flash("Username does not exist in database", "success")
                except Exception as e:
                    flash(str(e), "success")
                return redirect(url_for('reservations'))
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/<int:ISBN>/new_review', methods=["GET", "POST"])
def new_review(ISBN):
    if 'user' in mysession and 'school' in mysession:
        if request.method == "POST":
            opinion = request.form["opinion"]
            rating = request.form["star_b"]
            id = mysession["user"]["user_id"]
            cur = db.connection.cursor()
            if mysession['user']['role'] == "student":
                query = f"""INSERT INTO review (ISBN, user_id, evaluation, like_scale, review_date) VALUES ({ISBN}, {id}, "{opinion}", {rating}, CURDATE())"""
            else:
                query = f"""INSERT INTO review (ISBN, user_id, evaluation, like_scale, review_date,approval_status) VALUES ({ISBN}, {id}, "{opinion}", {rating}, CURDATE(),'approved') """
            cur.execute(query)
            db.connection.commit()
            flash("Book Review sent", "success")
            return redirect('/schoolpage/userhome/history')
        return render_template('mynewreview.html', ISBN=ISBN, title='Review', user=mysession["user"])
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/<int:ISBN>/update_review', methods=["GET", "POST"])
def update_review(ISBN):
    if 'user' in mysession and 'school' in mysession:
        id = mysession["user"]["user_id"]
        cur = db.connection.cursor()
        if request.method == "POST":
            opinion = request.form["opinion"]
            rating = request.form["star_a"]
            if mysession['user']['role'] == "student":
                query = f"""UPDATE review SET evaluation='{opinion}', like_scale={rating}, approval_status='pending', review_date=CURDATE() WHERE ISBN={ISBN} AND user_id={id}"""
            else:
                query = f"""UPDATE review SET evaluation='{opinion}', like_scale={rating}, approval_status='approved', review_date=CURDATE() WHERE ISBN={ISBN} AND user_id={id}"""

            cur.execute(query)
            db.connection.commit()
            flash("Book Review sent", "success")
            return redirect('/schoolpage/userhome/history')
        query=f"""SELECT * FROM review where user_id={id} and ISBN={ISBN}"""
        cur.execute(query)
        record = cur.fetchone()
        column_names = [i[0] for i in cur.description]
        review = dict(zip(column_names, record))
        return render_template('myupdatedreview.html', review=review, title='Review', user=mysession["user"])
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/reviews', methods=["GET", "POST"])
def reviews():
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            school_name =  mysession["user"]['school_name']
            cur = db.connection.cursor()
            query = f"""SELECT u.user_id, u.first_name, u.last_name,b.title, r.ISBN, r.evaluation, r.like_scale, r.review_date
FROM user u
INNER JOIN review r ON u.user_id = r.user_id
INNER JOIN book b ON r.ISBN = b.ISBN
WHERE r.approval_status = 'pending' AND u.school_name = '{school_name}'
ORDER BY r.review_date DESC """
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            reviews = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()
            return render_template('handlerreviews.html', title='Reviews', reviews=reviews)
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/reviews/<int:ISBN>/<int:id>')
def review_details(ISBN, id):
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            cur = db.connection.cursor()
            query = f"""SELECT u.user_id, u.first_name, u.last_name, b.title, r.ISBN, r.evaluation, r.like_scale, r.review_date
FROM user u
INNER JOIN review r ON u.user_id = r.user_id
INNER JOIN book b ON r.ISBN = b.ISBN WHERE r.user_id={id} AND r.ISBN={ISBN}"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            record = cur.fetchone()
            review = dict(zip(column_names, record))
            return render_template('handlerreviewaccept.html', title='Review', review=review)
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/reviews/<int:ISBN>/<int:id>/accept')
def approve_review(ISBN, id):
    cur = db.connection.cursor()
    query = f"UPDATE review SET approval_status='approved' WHERE ISBN={ISBN} and user_id={id}"
    cur.execute(query)
    db.connection.commit()
    flash("Review Approved", "success")
    return redirect('/schoolpage/userhome/reviews')



@app.route('/<int:ISBN>/reviews')
def book_reviews(ISBN):
    if 'user' in mysession and 'school' in mysession:
        cur = db.connection.cursor()
        query = f"""SELECT u.first_name, u.last_name, u.username, u.school_name, approved_reviews.like_scale, 
        approved_reviews.evaluation, approved_reviews.review_date
        FROM (SELECT * FROM review WHERE approval_status = 'approved' AND ISBN = {ISBN}) approved_reviews
        INNER JOIN user u 
        ON u.user_id = approved_reviews.user_id"""
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        reviews = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        return render_template('bookreviews.html', title='Book Reviews', reviews=reviews, user = mysession["user"])
    return redirect(url_for('userhome'))



@app.route('/schoolpage/userhome/stats')
def school_stats():
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            cur = db.connection.cursor()
            query = f"""SELECT u.username, c.category_name, AVG(r.like_scale) AS average_rating
                            FROM user u
                            INNER JOIN (SELECT a.user_id, a.ISBN FROM applications a GROUP BY a.user_id, a.ISBN) AS distinct_borrowings
                            ON u.user_id = distinct_borrowings.user_id
                            INNER JOIN review r ON distinct_borrowings.ISBN = r.ISBN AND u.user_id = r.user_id
                            INNER JOIN book_category bc ON distinct_borrowings.ISBN = bc.ISBN
                            INNER JOIN category c ON bc.category_id = c.category_id
                            WHERE  1=1
                            GROUP BY u.username, c.category_name"""
            cur.execute(query)  
            column_names = [i[0] for i in cur.description]
            records = [dict(zip(column_names, entry)) for entry in cur.fetchall()]             
            school_id = mysession['school']
            query = f"""SELECT DISTINCT c.category_name 
                    FROM book_category bc 
                    INNER JOIN (SELECT ISBN FROM stores WHERE school_id = {school_id}) s
                    ON bc.ISBN = s.ISBN
                    INNER JOIN category c
                    ON c.category_id = bc.category_id
                    ORDER BY c.category_name"""                
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            categories = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            return render_template('handlerstats.html', categories = categories, records = records)
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))    



@app.route('/schoolpage/userhome/apply_stats', methods=['POST'])
def school_applied_stats():
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            cur = db.connection.cursor()
            username = request.form['username']
            category = request.form['category']
            params = []
            query = """SELECT u.username, c.category_name, AVG(r.like_scale) AS average_rating
                       FROM user u
                       INNER JOIN (SELECT a.user_id, a.ISBN FROM applications a GROUP BY a.user_id, a.ISBN) AS distinct_borrowings
                           ON u.user_id = distinct_borrowings.user_id
                       INNER JOIN review r ON distinct_borrowings.ISBN = r.ISBN AND u.user_id = r.user_id
                       INNER JOIN book_category bc ON distinct_borrowings.ISBN = bc.ISBN
                       INNER JOIN category c ON bc.category_id = c.category_id
                       WHERE 1=1 """
            if username:
                query += " AND u.username LIKE %s"
                username_term = '%' + username + '%'
                params.append(username_term)
            if category:
                query += " AND c.category_name LIKE %s"
                category_term = '%' + category + '%'
                params.append(category_term)
            query += " GROUP BY u.username, c.category_name"
            cur.execute(query, tuple(params))
            column_names = [i[0] for i in cur.description]
            records = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            school_id = mysession['school']
            query = f"""SELECT DISTINCT c.category_name
                        FROM book_category bc
                        INNER JOIN (SELECT ISBN FROM stores WHERE school_id = {school_id}) s
                            ON bc.ISBN = s.ISBN
                        INNER JOIN category c
                            ON c.category_id = bc.category_id
                        ORDER BY c.category_name"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            categories = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            return render_template('handlerstats.html', categories=categories, records=records)
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/books/apply_stats/title', methods=['POST'])
def book_title():
    if 'user' in mysession and 'school' in mysession:
        cur = db.connection.cursor()
        school_id = mysession["school"]
        title = request.form['booktitle']
        if title:
            query = f"""SELECT b.*,
GROUP_CONCAT(DISTINCT a.author_name ORDER BY a.author_name SEPARATOR ',') AS author_names
FROM (SELECT stores.ISBN FROM stores WHERE stores.school_id = '{school_id}') q
INNER JOIN (SELECT * FROM book WHERE title = '{title}') b ON b.ISBN = q.ISBN
INNER JOIN book_author ba ON q.ISBN = ba.ISBN
INNER JOIN author a ON a.author_id = ba.author_id
GROUP BY b.title"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            books = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            query = f"""SELECT DISTINCT a.author_name 
                        FROM book_author ba 
                        INNER JOIN (SELECT ISBN FROM stores WHERE school_id = {school_id}) s
                        ON ba.ISBN = s.ISBN
                        INNER JOIN author a
                        ON a.author_id = ba.author_id
                        ORDER BY a.author_name"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            authors = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            query = f"""SELECT DISTINCT c.category_name 
                        FROM book_category bc 
                        INNER JOIN (SELECT ISBN FROM stores WHERE school_id = {school_id}) s
                        ON bc.ISBN = s.ISBN
                        INNER JOIN category c
                        ON c.category_id = bc.category_id
                        ORDER BY c.category_name"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            categories = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()
            return render_template('books.html', user=mysession['user'], title='Books', books=books, authors=authors, categories=categories)
        return redirect(url_for('books'))
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/books/apply_stats/filter', methods=['POST'])
def book_filter():
    if 'user' in mysession and 'school' in mysession:
        cur = db.connection.cursor()
        school_id = mysession["school"]
        category = request.form['bookcategory']
        author = request.form['bookauthor']
        number = request.form['copies']
        params = []

        query = f"""
        SELECT b.*, q.available_copies,
        GROUP_CONCAT(DISTINCT a.author_name ORDER BY a.author_name SEPARATOR ',') AS author_names, 
        GROUP_CONCAT(DISTINCT c.category_name ORDER BY c.category_name SEPARATOR ',') AS book_categories
        FROM (SELECT stores.ISBN, stores.available_copies FROM stores WHERE stores.school_id = '{school_id}') q 
        INNER JOIN book b ON b.ISBN = q.ISBN
        INNER JOIN book_category bc ON q.ISBN = bc.ISBN
        INNER JOIN category c ON bc.category_id = c.category_id
        INNER JOIN book_author ba ON q.ISBN = ba.ISBN
        INNER JOIN author a ON a.author_id = ba.author_id
        WHERE 1=1
        """

        if author:
            query += "AND a.author_name LIKE %s "
            author_term = '%' + author + '%'
            params.append(author_term)

        if category:
            query += "AND c.category_name LIKE %s "
            category_term = '%' + category + '%'
            params.append(category_term)

        if number:
            query += "AND q.available_copies LIKE %s "
            params.append(number)

        query += "GROUP BY b.ISBN"

        cur.execute(query, tuple(params))

        column_names = [i[0] for i in cur.description]
        books = [dict(zip(column_names, entry)) for entry in cur.fetchall()]

        query = """
        SELECT DISTINCT a.author_name
        FROM book_author AS ba
        INNER JOIN stores AS s ON ba.ISBN = s.ISBN
        INNER JOIN author AS a ON a.author_id = ba.author_id
        WHERE s.school_id = %s
        ORDER BY a.author_name
        """

        cur.execute(query, (school_id,))

        column_names = [i[0] for i in cur.description]
        authors = [dict(zip(column_names, entry)) for entry in cur.fetchall()]

        query = """
        SELECT DISTINCT c.category_name
        FROM book_category AS bc
        INNER JOIN stores AS s ON bc.ISBN = s.ISBN
        INNER JOIN category AS c ON c.category_id = bc.category_id
        WHERE s.school_id = %s
        ORDER BY c.category_name
        """

        cur.execute(query, (school_id,))

        column_names = [i[0] for i in cur.description]
        categories = [dict(zip(column_names, entry)) for entry in cur.fetchall()]

        cur.close()

        return render_template('books.html', user=mysession['user'], title='Books', books=books, authors=authors, categories=categories)

    return redirect(url_for('index'))

@app.route('/schoolpage/userhome/borrows/filter', methods=['POST'])
def borrow_filter():
    if 'user' in mysession and 'school' in mysession:
        if mysession["user"]['role'] == "handler":
            cur = db.connection.cursor()
            school_name = mysession["user"]['school_name']
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            days = request.form["days"]
            params = []
            query = f""" SELECT u.username, u.first_name, u.last_name, u.role_name, expired_applications.ISBN
FROM (SELECT *
FROM applications WHERE status_ IN ('expired_borrowing', 'borrowed')) expired_applications
INNER JOIN user u
ON u.user_id = expired_applications.user_id
WHERE 1=1"""
            if first_name:
                query += " AND u.first_name LIKE %s"
                first_term = '%' + first_name + '%'
                params.append(first_term)
            if last_name:
                query += " AND u.last_name LIKE %s"
                last_term = '%' + last_name + '%'
                params.append(last_term)
            if days:
                query += " AND DAY(DATEDIFF(NOW(), expired_applications.expiration_date)) >= %s"
                day_term = '%' + days + '%'
                params.append(day_term)
            cur.execute(query, tuple(params))
            column_names = [i[0] for i in cur.description]
            borrows = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()
            return render_template('handlerborrows.html', title='Borrows', borrows=borrows)
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))



@app.route('/adminhome/stats/1')
def stats1():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            return render_template("adminstat1.html", title="Stat1", schools=[])
    return redirect(url_for('index'))



@app.route('/adminhome/stats/1/filter', methods=["POST"])
def stats1_applied():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            fullmonth = request.form["month"]
            dt=datetime.strptime(fullmonth, "%Y-%m")
            cur = db.connection.cursor()
            if fullmonth:
                query = f"""SELECT school.school_name, COUNT(a.application_id) AS total_borrows FROM school LEFT JOIN user ON school.school_name = user.school_name 
                LEFT JOIN applications a ON user.user_id = a.user_id AND a.status_!='applied' AND MONTH(a.start_date) = '{dt.month}' AND YEAR(a.start_date) = "{dt.year}" GROUP BY school.school_name"""
                cur.execute(query)
                column_names = [i[0] for i in cur.description]
                schools = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
                return render_template("adminstat1.html", title="Stat1", schools=schools)
    return redirect(url_for('index'))



@app.route('/adminhome/stats/2')
def stats2():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            query = """SELECT category_name from category"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            categories = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            return render_template("adminstat2.html", title="Stat2", categories=categories, teachers=[], authors=[])
    return redirect(url_for('index'))




@app.route('/adminhome/stats/2/filter', methods=["POST"])
def stats2_applied():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            category=request.form["bookcategory"]
            query = f"""SELECT DISTINCT author.author_name
FROM author JOIN book_author ON author.author_id = book_author.author_id JOIN book_category ON book_author.ISBN = book_category.ISBN JOIN category ON book_category.category_id = category.category_id WHERE category.category_name = '{category}'"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            authors = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            query= f"""SELECT DISTINCT user.first_name, user.last_name, user.school_name
FROM user
INNER JOIN applications ON user.user_id = applications.user_id
INNER JOIN book ON applications.ISBN = book.ISBN
INNER JOIN book_category ON book.ISBN = book_category.ISBN
INNER JOIN category ON book_category.category_id = category.category_id
WHERE category.category_name = '{category}'
AND applications.start_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
AND user.role_name = 'teacher'"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            teachers = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            query = """SELECT category_name from category"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            categories = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            return render_template("adminstat2.html", title="Stat2", categories=categories, authors=authors, teachers=teachers)
    return redirect(url_for('index'))



@app.route('/adminhome/stats/3')
def stats3():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            query="""SELECT u.birth_date, u.first_name, u.last_name, num_books
FROM user u
INNER JOIN (SELECT a.user_id, COUNT(*) AS num_books
FROM applications a
INNER JOIN user u ON u.user_id = a.user_id
WHERE u.role_name = 'teacher'
AND TIMESTAMPDIFF(YEAR, u.birth_date, CURRENT_DATE()) < 40
AND a.status_ IN ('borrowed', 'completed','expired_borrowing')
GROUP BY a.user_id
HAVING COUNT(*) = (SELECT COUNT(*) AS max_books
FROM applications a
INNER JOIN user u ON u.user_id = a.user_id
WHERE u.role_name = 'teacher'
AND TIMESTAMPDIFF(YEAR, u.birth_date, CURRENT_DATE()) < 40
AND a.status_ IN ('borrowed', 'completed', 'expired_borrowing')
GROUP BY a.user_id
ORDER BY max_books DESC
LIMIT 1)) counts_the_most ON u.user_id = counts_the_most.user_id"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            teachers = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            return render_template("adminstat3.html", title="Stat3", teachers=teachers)
    return redirect(url_for('index'))    



@app.route('/adminhome/stats/4')
def stats4():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            query = """SELECT DISTINCT a.author_name
FROM author a
LEFT JOIN book_author ba ON a.author_id = ba.author_id
LEFT JOIN applications app ON ba.ISBN = app.ISBN
WHERE app._status NOT IN ('borrowed','expired_borrowing','completed')"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            authors = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            return render_template("adminstat4.html", title="Stat4", authors=authors)
    return redirect(url_for('index'))    



@app.route('/adminhome/stats/5')
def stats5():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            query = """SELECT s.school_name,
COUNT(*) AS books_borrowed,
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
HAVING COUNT(*) > 20"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            handlers = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            return render_template("adminstat5.html", title="Stat5", handlers=handlers)
    return redirect(url_for('index'))    



@app.route('/adminhome/stats/6')
def stats6_applied():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            query = """SELECT c1.category_name, c2.category_name, COUNT(app.ISBN) AS pair_count
FROM book_category bc1
JOIN book_category bc2 ON bc1.ISBN = bc2.ISBN AND bc1.category_id < bc2.category_id
JOIN category c1 ON bc1.category_id = c1.category_id
JOIN category c2 ON bc2.category_id = c2.category_id
JOIN applications app ON bc1.ISBN = app.ISBN
WHERE app.status_ IN ('borrowed','expired_borrowing','completed')
GROUP BY c1.category_name, c2.category_name
ORDER BY pair_count DESC
LIMIT 3"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            category_pairs = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            return render_template("adminstat6.html", title="Stat6", category_pairs=category_pairs)
    return redirect(url_for('index'))    



@app.route('/adminhome/stats/7')
def stats7():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            query="""SELECT a.author_name, COUNT(*) AS book_count
FROM book_author ba
INNER JOIN author a ON ba.author_id = a.author_id
GROUP BY a.author_id
ORDER BY COUNT(*) DESC
LIMIT 1"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            topauthor = dict(zip(column_names, cur.fetchone())) 
            query = """SELECT a.author_name, COUNT(*) AS book_count
FROM book_author ba
INNER JOIN author a on ba.author_id = a.author_id
GROUP BY author_name
HAVING book_count <= (
SELECT COUNT(*)-5
FROM book_author ba
INNER JOIN author a ON ba.author_id = a.author_id
GROUP BY a.author_id
ORDER BY COUNT(*) DESC
LIMIT 1
)
ORDER BY book_count"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            authors = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            return render_template("adminstat7.html", title="Stat7", authors=authors, topauthor=topauthor)
    return redirect(url_for('index'))    




