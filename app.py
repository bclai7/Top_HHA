from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
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
@app.route('/mycriteria', methods=['GET', 'POST'])
def mycriteria():
    if request.method == 'POST':

        # get criteria values from form
        content = request.form['content']
        delivery = request.form['delivery']
        hits = request.form['hits']
        albums = request.form['albums']
        consistency = request.form['consistency']
        longevity = request.form['longevity']
        impact = request.form['impact']
        sales = request.form['sales']
        personality = request.form['personality']
        creativity = request.form['creativity']
        popularity = request.form['popularity']

        # Load criteria values into session
        session['content']=content
        session['delivery']=delivery
        session['hits']=hits
        session['albums']=albums
        session['consistency']=consistency
        session['longevity']=longevity
        session['impact']=impact
        session['sales']=sales
        session['personality']=personality
        session['creativity']=creativity
        session['popularity']=popularity

        if 'logged_in' in session and session['logged_in'] == True:
            user_id = session['user_id']
            # Create MySQL Cursor
            cur = mysql.connection.cursor()

            # Update Values
            query = """UPDATE user SET criteria_content = %s, criteria_delivery=%s,
                    criteria_hits=%s, criteria_albums=%s, criteria_consistency=%s,
                    criteria_longevity=%s, criteria_impact=%s,  criteria_sales=%s,
                    criteria_personality=%s,  criteria_creativity=%s,
                    criteria_popularity=%s WHERE id = %s"""
            # Execute Query
            cur.execute(query, (content, delivery, hits, albums, consistency, longevity, impact, sales, personality, creativity, popularity, user_id))
            # Commit to MySQL database
            mysql.connection.commit()

            # Close DB
            cur.close()
        flash('Saved', 'success')
        return redirect(url_for('mycriteria'))
    else:
        # If user is not logged in, default the count to 0
        if 'content' not in session:
            session['content'] = 0
        if 'delivery' not in session:
            session['delivery'] = 0
        if 'hits' not in session:
            session['hits'] = 0
        if 'albums' not in session:
            session['albums'] = 0
        if 'consistency' not in session:
            session['consistency'] = 0
        if 'longevity' not in session:
            session['longevity'] = 0
        if 'impact' not in session:
            session['impact'] = 0
        if 'sales' not in session:
            session['sales'] = 0
        if 'personality' not in session:
            session['personality'] = 0
        if 'creativity' not in session:
            session['creativity'] = 0
        if 'popularity' not in session:
            session['popularity'] = 0
    return render_template('mycriteria.html', methods=['GET', 'POST'])

# Page for rating artists
@app.route('/artistratings')
def myratings():
    # Create MySQL Cursor
    cur = mysql.connection.cursor()

    # Detect onchange of <select> object, whenever there is a change:
    # If user is logged in
    #   get rating values from database based off of selected artist and user
    #   then store the values into session variables (with artist name as key)
    # else if not logged in
    #    just load the current session variables based off of the selected artist (artist name as key)

    # After the ratings variables are found, load the values into the slider objects in the HTML

    # MySQL query to get list of artist names from database
    query="SELECT name FROM artist ORDER BY name"
    cur.execute(query)
    DictArtist = cur.fetchall() # returns dictionary of artists
    ArtistList=[] # create empty list to add artist names to
    # add artists to ArtistList
    for artist in DictArtist:
        ArtistList.append(artist["name"])
    # Rating Category list
    categoryList = ['content', 'delivery', 'hits', 'albums', 'consistency', 'longevity', 'impact', 'sales', 'personality', 'creativity', 'popularity']

    # Close DB
    cur.close()

    return render_template('myratings.html', artistList=ArtistList, categoryList=categoryList, selected_artist='-- select an artist --')

# rated
@app.route('/rated', methods=['POST'])
def rated():
    # Create MySQL Cursor
    cur = mysql.connection.cursor()

    # Get selected artist name
    artist_name = request.form.get('artist_name')
    artist_name = str(artist_name)

    # Get rating values from sliders
    content_rating = request.form['slider_content']
    delivery_rating = request.form['slider_delivery']
    hits_rating = request.form['slider_hits']
    albums_rating = request.form['slider_albums']
    consistency_rating = request.form['slider_consistency']
    longevity_rating = request.form['slider_longevity']
    impact_rating = request.form['slider_impact']
    sales_rating = request.form['slider_sales']
    personality_rating = request.form['slider_personality']
    creativity_rating = request.form['slider_creativity']
    popularity_rating = request.form['slider_popularity']

    # is user is registered and logged in, store values to data base
    if 'logged_in' in session and session['logged_in']:
        # first check if there are any ratings already for that artist on that account
        query = """SELECT artist_name, content, delivery, hits, albums,
                        consistency, longevity, impact, sales,
                        personality, creativity, popularity
                    FROM rating WHERE user_id = %s AND artist_name = %s"""
        result = cur.execute(query, [session['user_id'], artist_name])
        #   if so, then do an UPDATE query to edit table row for that rating
        if result > 0:
            # save artist id
            data = cur.fetchone()
            # Write query to update the table
            query = """UPDATE rating SET content = %s, delivery = %s,
                            hits = %s, albums = %s, consistency = %s,
                            longevity = %s, impact = %s, sales = %s,
                            personality = %s, creativity = %s, popularity = %s
                        WHERE rating.user_id = %s AND rating.artist_name = %s"""
            cur.execute(query, [content_rating, delivery_rating, hits_rating,
                                albums_rating, consistency_rating, longevity_rating,
                                impact_rating, sales_rating, personality_rating,
                                creativity_rating, popularity_rating, session['user_id'],
                                artist_name])

            # Commit to MySQL database
            mysql.connection.commit()
        # else, do an INSERT INTO query to enter new rating into the database
        else:
            # Write query to insert into the table
            query = """INSERT INTO rating(user_id, artist_name, content, delivery,
                        hits, albums, consistency, longevity, impact, sales,
                        personality, creativity, popularity)
                        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            cur.execute(query, [session['user_id'], artist_name, content_rating,
                                delivery_rating, hits_rating, albums_rating,
                                consistency_rating, longevity_rating,
                                impact_rating, sales_rating, personality_rating,
                                creativity_rating, popularity_rating])
            # Commit to MySQL database
            mysql.connection.commit()

    # Save the rating info to the corresponding session variables (whether or not user is registered)
    session[artist_name] = [content_rating, delivery_rating, hits_rating, albums_rating,
                            consistency_rating, longevity_rating, impact_rating,
                            sales_rating, personality_rating, creativity_rating,
                            popularity_rating]
    # filler


    # Close DB
    cur.close()
    return jsonify({'success': 'Saved'})

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
    name = StringField('Name', [validators.Length(min=4, max=50)])
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
        # clear session just in case user made changes before logging in
        session.clear()
        # Get form fields
        email = request.form['email']
        password_candidate = request.form['password']

        # Create MySQL Cursor
        cur = mysql.connection.cursor()

        # Find user by email in database
        query = "SELECT * FROM user WHERE email=%s"
        em = [email]
        result = cur.execute(query, em)

        if result > 0:
            data = cur.fetchone()
            password = data['password']
            name = data['name']
            user_id = data['id']

            # Load criteria values
            content = data['criteria_content']
            delivery = data['criteria_delivery']
            hits = data['criteria_hits']
            albums = data['criteria_albums']
            consistency = data['criteria_consistency']
            longevity = data['criteria_longevity']
            impact = data['criteria_impact']
            sales = data['criteria_sales']
            personality = data['criteria_personality']
            creativity = data['criteria_creativity']
            popularity = data['criteria_popularity']

            # Compare entered password to hash value
            if (bcrypt.check_password_hash(password, password_candidate)):
                session['logged_in']=True
                session['email']=email
                session['name']=name
                session['user_id']=user_id

                # Load criteria values into session
                session['content']=content
                session['delivery']=delivery
                session['hits']=hits
                session['albums']=albums
                session['consistency']=consistency
                session['longevity']=longevity
                session['impact']=impact
                session['sales']=sales
                session['personality']=personality
                session['creativity']=creativity
                session['popularity']=popularity

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
