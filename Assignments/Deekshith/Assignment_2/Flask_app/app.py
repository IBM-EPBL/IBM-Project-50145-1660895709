from flask import Flask,render_template, request, redirect, url_for, session
import re
import ibm_db

app = Flask(__name__)
app.secret_key = 'your secret key'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=2f3279a5-73d1-4859-88f0-a6c3e6b4b907.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=30756;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;PROTOCOL=TCPIP;UID=bkq23793;PWD=6sWRxHNJMuQyhfqs;", "", "")


@app.route("/")
def home():
    return redirect(url_for('register'))

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
        name = request.form['name']
        password = request.form['password']
        query = "SELECT * FROM user WHERE name = '{}' AND password = '{}'".format(name,password)
        out = ibm_db.exec_immediate(conn,query)
        account = ibm_db.fetch_assoc(out)
        if account:
            session['loggedin'] = True
            session['name'] = account['NAME']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form :
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        queryfind = "SELECT * FROM user WHERE name = '{}'".format(name)
        out = ibm_db.exec_immediate(conn,queryfind)
        account = ibm_db.fetch_assoc(out)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Username must contain only characters and numbers !'
        elif not name or not password or not email:
            msg = 'Please fill out the form !'
        else:
            query3 = "INSERT INTO user VALUES ('{}', '{}', '{}')".format(name,email,password)
            ibm_db.exec_immediate(conn,query3)
            msg = 'You have successfully registered !'
            return redirect(url_for('login'))
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

if(__name__ == "__main__"):
    app.run(debug=True)
