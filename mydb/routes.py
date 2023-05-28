from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from mydb import app, db 
from mydb.forms import *

mysession = {}

@app.route('/', methods = ['GET', 'POST'])       #checked
def index():
    mysession.clear()
    cur = db.connection.cursor()
    if request.method == 'POST':
        school_name = request.form['school']
        query = f"SELECT * FROM school WHERE school_name='{school_name}'"
        cur.execute(query)
        record=cur.fetchone()
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



@app.route('/adminlogin', methods =['POST'])  #checked
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



@app.route('/adminhome')     #checked
def adminhome():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            return render_template('adminhome.html', title='Home Page')
    return redirect(url_for('index')) 



@app.route('/adminhome/pwd', methods = ['POST'])      #checked
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



@app.route('/adminhome/schools')  #checked
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
            return render_template('adminschools.html', title = 'Schools', schools = schools) 
    return redirect(url_for('index'))





@app.route("/adminhome/schools/create", methods=["POST"])   #checked
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



@app.route("/adminhome/schools/<int:school_id>/edit", methods=["POST"])   #checked
def school_edit(school_id):
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



@app.route("/adminhome/schools/<int:school_id>/delete")  #checked
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





@app.route('/adminhome/handlers')  #checked
def handlers():
    if 'status' in mysession:
        if mysession['status'] == "admin":
            cur = db.connection.cursor()
            query = " SELECT * FROM user where role_name = 'handler'"
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            handlers = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()
            return render_template('adminhandlers.html', title = 'Handlers', handlers = handlers) 
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



@app.route('/handlerapplication', methods =['POST']) #birthday missing, rest is checked
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



@app.route('/schoolpage')   #checked
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
        return render_template('schoolpage.html', school = school,  title = 'School Page')
    return redirect(url_for('index'))



@app.route('/schoolpage/login', methods =['POST'])  #checked
def login():
    if "school" in mysession:    
        username = request.form['username']
        password = request.form['password']
        cur = db.connection.cursor()
        id = mysession["school"]
        query = f"SELECT * FROM school WHERE school_id='{id}'"
        cur.execute(query)
        record=cur.fetchone()
        school_name=record[1]
        query = f"SELECT * FROM user WHERE username='{username}' AND pwd='{password}' AND school_name='{school_name}'"
        cur.execute(query)
        record = cur.fetchone()
        cur.close()
        if record:
            is_active = record[6]
            if is_active == "active":
                mysession['user'] = [record[i] for i in range(1, 10)]
                return redirect(url_for('userhome'))
            flash("User is not activated yet", "success")
            return redirect(url_for('schoolpage'))
        flash("Wrong credentials", "success")
        return redirect(url_for('schoolpage'))
    return redirect(url_for('index'))



@app.route('/schoolpage/register', methods =['POST'])  #birthday missing, rest is checked
def register():
    if "school" in mysession:  
        cur = db.connection.cursor()
        id = mysession["school"]
        query = f"SELECT * FROM school WHERE school_id='{id}'"
        cur.execute(query)
        record=cur.fetchone()
        cur.close()
        school_name=record[1]
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



@app.route('/schoolpage/userhome')   #checked
def userhome():
   if 'user' and "school" in mysession:  
        return render_template('userhome.html', user = mysession['user'], status=mysession['user'][7] , title='Home Page')
   return redirect(url_for('index')) 



@app.route('/schoolpage/userhome/pwd', methods = ['POST'])  #checked
def userpwd():
    if "user" and "school" in mysession:
        pwd1 = request.form['pwd1']
        pwd2 = request.form['pwd2']
        if pwd1 == pwd2:
            cur = db.connection.cursor()
            query = f"""UPDATE user SET pwd = '{pwd1}'
            WHERE username = '{mysession['user'][0]}'"""
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Password successfully changed", "success")
            mysession["user"][1]=pwd1
            return redirect(url_for('userhome'))
        flash("Passwords do not match", "success")
        return redirect(url_for('userhome'))
    return redirect(url_for('index')) 



@app.route('/schoolpage/userhome/editprofile', methods = ['POST'])  #checked
def profile():
    if "user" and "school" in mysession:
        username = request.form['username']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        birthday = request.form['birthday']
        cur = db.connection.cursor()
        query = f"""UPDATE user SET username = '{username}', first_name = '{first_name}', last_name = '{last_name}', birth_date = DATE '{birthday}' 
             WHERE username = '{mysession['user'][0]}'"""
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            mysession['user'][0]=username
            mysession['user'][2]=first_name
            mysession['user'][3]=last_name
            mysession['user'][4]=birthday
            flash("Profile updated successfully", "success")
        except Exception as e:
            flash(str(e), "success")
        return redirect(url_for('userhome'))
    return redirect(url_for('index')) 



@app.route('/schoolpage/userhome/users')
def users():
    if "user" and "school" in mysession:
        if mysession["user"][7] == "handler":
            cur = db.connection.cursor()
            id = mysession["school"]
            query = f"SELECT * FROM school WHERE school_id='{id}'"
            cur.execute(query)
            record=cur.fetchone()
            school_name=record[1]
            query = f" SELECT * FROM user where role_name != 'handler' and school_name= '{school_name}'"
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            users = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()
            return render_template('handlerusers.html', user = mysession['user'], title = 'Users', users = users)
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))        



@app.route('/schoolpage/userhome/users/<int:user_id>/accept')
def user_accept(user_id):
    if 'user' and "school" in mysession:
        if mysession['user'][7] == "handler":
            cur = db.connection.cursor()
            query = f" UPDATE user SET status_usr = 'active' WHERE user_id = '{user_id}'"
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("User added", "success")
            return redirect('/schoolpage/userhome/users')
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/users/<int:user_id>/reject')
def user_reject(user_id):
    if 'user' and "school" in mysession:
        if mysession['user'][7] == "handler":
            cur = db.connection.cursor()
            query = f"DELETE FROM user WHERE user_id = '{user_id}'"
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("User discarded", "success")
            return redirect('/schoolpage/userhome/users')
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/users/<int:user_id>/deactivate')
def user_deactivate(user_id):
    if 'user' and "school" in mysession:
        if mysession['user'][7] == "handler":
            cur = db.connection.cursor()
            query = f" UPDATE user SET status_usr = 'pending' WHERE user_id = '{user_id}'"
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("User deactivated", "success")
            return redirect('/schoolpage/userhome/users')
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/books', methods=['GET', 'POST'])  #checked
def books():
    if 'user' and "school" in mysession:
        if request.method == 'POST':
            ISBN = request.form['book'] 
            cur = db.connection.cursor()
            query = f"SELECT * FROM book WHERE ISBN='{ISBN}'"
            cur.execute(query)
            record=cur.fetchone()
            if record:
                return redirect(f'/schoolpage/userhome/books/{ISBN}/add')  
            flash("ISBN does not exists in database.") 
            return  redirect('/schoolpage/userhome/books')
        cur = db.connection.cursor()
        school_id = mysession["school"]
        query = f"""SELECT b.*, q.available_copies, GROUP_CONCAT(a.author_name SEPARATOR ', ') AS author_names, GROUP_CONCAT(c.category SEPARATOR ', ') AS book_categories
        FROM (SELECT stores.ISBN, stores.available_copies FROM stores WHERE stores.school_id = '{school_id}') q 
        INNER JOIN book b ON b.ISBN = q.ISBN INNER JOIN categories c ON q.ISBN = c.ISBN
        INNER JOIN author a on q.ISBN = a.ISBN
        GROUP BY b.ISBN, b.title
        """
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        books = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()
        return render_template('books.html', user = mysession['user'], status = mysession['user'][7], title = 'Books',books = books)
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/books/<int:ISBN>/add', methods=['GET', 'POST'])  #checked
def add_book(ISBN):
    if 'user' and "school" in mysession:
        if mysession['user'][7] == "handler":
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
            query = f"""SELECT b.*, a.author_name,c.category FROM book b INNER JOIN author a ON b.ISBN = a.ISBN
                    INNER JOIN categories c ON c.ISBN = b.ISBN WHERE b.ISBN = '{ISBN}'"""
            cur.execute(query)
            column_names = [i[0] for i in cur.description]
            book = dict(zip(column_names, cur.fetchone()))
            return render_template('bookadd.html', book = book)
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))



@app.route('/schoolpage/userhome/books/create', methods=['GET', 'POST'])  
def new_book():
    if 'user' and "school" in mysession:
        if mysession['user'][7] == "handler":
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
                language = request.form['language']
                image = request.form['image']
                copies = request.form['copies']
                id = mysession["school"]
                
                
                try:
                    cur = db.connection.cursor()
                    query = f"""INSERT INTO book (ISBN, title, summary, publisher, page_num, language_, image) VALUES ({ISBN},"{title}","{summary}","{publisher}",{pages_num},"{language}","{image}")"""
                    cur.execute(query)
                    db.connection.commit()
                    for category in category_names:
                        query = f"""INSERT INTO categories(category, ISBN) VALUES ("{category}",{ISBN})"""
                        cur.execute(query)
                        db.connection.commit()
                    for author in author_names:    
                        query = f"""INSERT INTO author(ISBN, author_name) VALUES ({ISBN},"{author}")"""
                        cur.execute(query)
                        db.connection.commit()
                    query = f"""INSERT INTO stores(school_id, ISBN, available_copies) VALUES ("{id}", "{ISBN}","{copies}")"""
                    cur.execute(query)
                    db.connection.commit()
                    flash("New Book added successfully!", "success") 
                except Exception as e:
                    flash(str(e), "success")
                return redirect(url_for('books'))
                    
                    
            return render_template('bookcreate.html', title = 'Add a Book')
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))


@app.route('/schoolpage/userhome/books/<int:ISBN>/details', methods=['GET', 'POST'])  #checked
def bookdetails(ISBN):
    if 'user' and "school" in mysession:
        if request.method == 'POST':
            if mysession['user'][7] == "handler":
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
                    image = request.form['image']
                    copies = request.form['copies']
                    id = mysession["school"]
                    
                    try:
                        cur = db.connection.cursor()
                        query = f"""UPDATE book SET ISBN={new_ISBN},title='{title}',summary="{summary}",publisher='{publisher}',page_num={pages_num},language_='{language}',image='{image}' WHERE ISBN = {ISBN}"""
                        cur.execute(query)
                        db.connection.commit()                        
                        query = f"""DELETE FROM categories WHERE ISBN = {new_ISBN}"""
                        cur.execute(query)
                        db.connection.commit()
                        for category in category_names:
                            query = f"""INSERT INTO categories(category, ISBN) VALUES ("{category}",{new_ISBN})"""
                            cur.execute(query)
                            db.connection.commit()                           
                        query = f"""DELETE FROM author WHERE ISBN = {new_ISBN}"""
                        cur.execute(query)
                        db.connection.commit()   
                        for author in author_names:    
                            query = f"""INSERT INTO author(ISBN, author_name) VALUES ({new_ISBN},"{author}")"""
                            cur.execute(query)
                            db.connection.commit()                    
                        query = f"""UPDATE  stores SET available_copies = {copies} WHERE school_id = {id} AND ISBN = {new_ISBN} """
                        cur.execute(query)
                        db.connection.commit  
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

        cur = db.connection.cursor()
        school_id = mysession["school"]
        query = f""" SELECT b.*, s.available_copies, GROUP_CONCAT(DISTINCT a.author_name ORDER BY a.author_name SEPARATOR ', ') AS author_names, 
                     GROUP_CONCAT(DISTINCT c.category ORDER BY c.category SEPARATOR ', ') AS book_categories
                     FROM (SELECT book.* FROM book WHERE book.ISBN = {ISBN}) b INNER JOIN author a on  a.ISBN = b.ISBN
                     INNER JOIN categories c on c.ISBN = b.ISBN
                     INNER JOIN stores s on s.ISBN = b.ISBN 
                     WHERE s.school_id = {school_id}
                     GROUP BY b.ISBN, b.title"""
        cur.execute(query)
        column_names = [i[0] for i in cur.description]
        book = dict(zip(column_names, cur.fetchone()))
        return render_template('bookdetails.html', user = mysession['user'], status = mysession['user'][7], title = 'Details',book = book)
    return redirect(url_for('index'))






