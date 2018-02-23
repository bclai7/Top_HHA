from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from flask.ext.bcrypt import Bcrypt
from functools import wraps
import config as cf


app = Flask(__name__)

#Configure MySQL database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = cf.DATABASE_USER
app.config['MYSQL_PASSWORD'] = cf.DATABASE_PW
app.config['MYSQL_DB'] = cf.DATABASE_NAME
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)

# init bcrypt for hashing
bcrypt = Bcrypt(app)

# Home Page
@app.route('/')
def index():
    return render_template('home.html')

# Criteria Settings
@app.route('/mycriteria')
def mycriteria():
    return render_template('mycriteria.html')

# Page for rating artists
@app.route('/artistratings')
def myratings():
    # Create MySQL Cursor
    cur = mysql.connection.cursor()
    # Execute MySQL Query
    cur.execute("SELECT name FROM artist ORDER BY name")
    DictArtist = cur.fetchall() # returns dictionary of artists
    ArtistList=[] # create empty list to add artist names to
    # add artists to ArtistList
    for artist in DictArtist:
        ArtistList.append(artist["name"])
    # content = [x.strip() for x in ArtistList]

    return render_template('myratings.html', artistList=ArtistList)

# Rankings page
@app.route('/rankings')
def rankings():
    return render_template('rankings.html')

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Registration Form
class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        password = pw_hash = bcrypt.generate_password_hash(str(form.password.data)).decode('utf-8')

        # Create MySQL Cursor
        cur = mysql.connection.cursor()
        # Execute MySQL Query
        cur.execute("INSERT INTO user(name, email, password) VALUES(%s, %s, %s)", (name, email, password))
        # Commit to MySQL database
        mysql.connection.commit()
        # Close connection
        cur.close()
        # Thank you message
        flash('Thank you for registering. You may now log in.', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form fields
        email = request.form['email']
        password_candidate = request.form['password']

        # Create MySQL Cursor
        cur = mysql.connection.cursor()

        # Find user by email in database
        result = cur.execute("SELECT * FROM user WHERE email=%s", [email])

        if result > 0:
            data = cur.fetchone()
            password = data['password']
            name = data['name']

            # Compare entered password to hash value
            if (bcrypt.check_password_hash(password, password_candidate)):
                session['logged_in']=True
                session['email']=email
                session['name']=name

                flash('Successfully Logged In', 'success')
                return redirect(url_for('rankings'))
            else:
                return render_template('login.html', error = 'Email and password combination is incorrect')
            # Close connection
            cur.close()
        else:
            return render_template('login.html', error = 'No user found with that email address')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.clear()
        flash('You have been logged out', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key=cf.SECRET_KEY
    app.run(debug=True)
