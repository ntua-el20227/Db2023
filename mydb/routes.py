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
        mysession['username'] = record[1]
        mysession['status'] = "admin"
        return redirect(url_for('adminhome'))
    flash("Wrong credentials", "success")
    return redirect(url_for('index'))



@app.route('/adminhome')     #checked
def adminhome():
    if 'username' in mysession:
        if mysession['status'] == "admin":
            return render_template('adminhome.html', user = mysession['username'], title='Home Page')
    return redirect(url_for('index')) 



@app.route('/adminhome/pwd', methods = ['POST'])      #checked
def adminpwd():
    if 'username' in mysession:
        if mysession['status'] == "admin":
            pwd1 = request.form['pwd1']
            pwd2 = request.form['pwd2']
            if pwd1 == pwd2:
                cur = db.connection.cursor()
                query = f"""UPDATE admin SET pwd = '{pwd1}'
            WHERE username = '{mysession['username']}'"""
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
    if 'username' in mysession:
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
    if 'username' in mysession:
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
            INSERT INTO school (school_name, email, principal_first_name, principal_last_name, city, address, phone_number) 
            VALUES ('{name}', '{email}', '{principal_first_name}', '{principal_last_name}', '{city}', '{address}', '{(phone_number)}') """
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
    if 'username' in mysession:
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
            UPDATE school SET school_name = '{name}', email = '{email}', principal_first_name = '{principal_first_name}', principal_last_name = '{principal_last_name}', city = '{city}'
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
    if 'username' in mysession:
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
    if 'username' in mysession:
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
    if 'username' in mysession:
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
    if 'username' in mysession:
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
        query = f"INSERT INTO user (first_name, last_name, username, pwd, school_name, role_name) VALUES ('{first_name}', '{last_name}', '{username}' ,'{pwd1}', '{school_name}', 'handler')"
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
                mysession['username'] = record[1]
                mysession['status'] = record[8]
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
        query = f"INSERT INTO user (first_name, last_name, username, pwd, school_name, role_name, status_usr) VALUES ('{first_name}', '{last_name}', '{username}', '{pwd1}', '{school_name}', '{role}', 'Pending')"
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
   if 'username' and "school" in mysession:  
        return render_template('userhome.html', user = mysession['username'], status = mysession['status'], title='Home Page')
   return redirect(url_for('index')) 



@app.route('/schoolpage/userhome/pwd', methods = ['POST'])  #checked
def userpwd():
    if "username" and "school" in mysession:
        pwd1 = request.form['pwd1']
        pwd2 = request.form['pwd2']
        if pwd1 == pwd2:
            cur = db.connection.cursor()
            query = f"""UPDATE user SET pwd = '{pwd1}'
            WHERE username = '{mysession['username']}'"""
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Password successfully changed", "success")
            return redirect(url_for('userhome'))
        flash("Passwords do not match", "success")
        return redirect(url_for('userhome'))
    return redirect(url_for('index')) 



@app.route('/schoolpage/userhome/users')
def users():
    if "username" and "school" in mysession:
        if mysession["status"] == "handler":
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
            return render_template('handlerusers.html', user = mysession['username'], status = mysession['status'], title = 'Users', users = users)
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))        



@app.route('/schoolpage/userhome/users/<int:user_id>/accept')
def user_accept(user_id):
    if 'username' and "school" in mysession:
        if mysession['status'] == "handler":
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
    if 'username' and "school" in mysession:
        if mysession['status'] == "handler":
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
    if 'username' and "school" in mysession:
        if mysession['status'] == "handler":
            cur = db.connection.cursor()
            query = f" UPDATE user SET status_usr = 'pending' WHERE user_id = '{user_id}'"
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("User deactivated", "success")
            return redirect('/schoolpage/userhome/users')
        return redirect(url_for('userhome'))
    return redirect(url_for('index'))


