from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_DB"] = 'db2023'
app.config["MYSQL_HOST"] = '127.0.0.1'
app.config["SECRET_KEY"] = 'eee' ## secret key for sessions (signed cookies). Flask uses it to protect the contents of the user session against tampering.
app.config["WTF_CSRF_SECRET_KEY"] = '' ## token for csrf protection of forms.

db = MySQL(app)
from mydb import routes