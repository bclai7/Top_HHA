from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify, g
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from flask.ext.bcrypt import Bcrypt
from functools import wraps
import simplejson as json
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
import sys
from _mysql_exceptions import IntegrityError


app = Flask(__name__)

# Load from config file
app.config.from_pyfile('config.cfg')

#Configure MySQL database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = app.config['DATABASE_USER']
app.config['MYSQL_PASSWORD'] = app.config['DATABASE_PW']
app.config['MYSQL_DB'] = app.config['DATABASE_NAME']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MySQL
mysql = MySQL(app)

# init Mail
mail = Mail(app)

# init serializer
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# init bcrypt for hashing
bcrypt = Bcrypt(app)

def getCategoryList():
    # Rating Category list
    categoryList = ['content', 'delivery', 'hits', 'albums', 'consistency',
        'longevity', 'impact', 'sales', 'personality', 'creativity',
        'popularity']
    return categoryList
def getArtistList():
    # Create MySQL Cursor
    cur = mysql.connection.cursor()

    # MySQL query to get list of artist names from database
    query="SELECT name FROM artist ORDER BY name"
    cur.execute(query)
    DictArtist = cur.fetchall() # returns dictionary of artists
    artistList=[] # create empty list to add artist names to
    # add artists to ArtistList
    for artist in DictArtist:
        artistList.append(artist["name"])
    # Close DB
    cur.close()
    return artistList

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('You must be logged in to access that page', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Home Page
@app.route('/')
def index():
    return render_template('home.html')

# Criteria Settings
@app.route('/mycriteria')
def mycriteria():
    # If user is not logged in and has not yet set criteria ratings,
    # default the sliders to 0
    for category in getCategoryList():
        if category not in session:
            session[category] = 0
    return render_template('mycriteria.html', categoryList=getCategoryList())

# Saves artist rating when clicking the save button, called through AJAX
@app.route('/changecriteria', methods=['POST'])
def changecriteria():
    # Create MySQL Cursor
    cur = mysql.connection.cursor()
    totalValue=0
    for category in getCategoryList():
        formName = 'criteria_'+category
        totalValue += int(request.form[formName])

    # If combined total is not equal to 100, return error
    if totalValue != 100:
        return jsonify({'error': 'Category scores must add up to 100'})

    # get criteria values from form
    content = request.form['criteria_content']
    delivery = request.form['criteria_delivery']
    hits = request.form['criteria_hits']
    albums = request.form['criteria_albums']
    consistency = request.form['criteria_consistency']
    longevity = request.form['criteria_longevity']
    impact = request.form['criteria_impact']
    sales = request.form['criteria_sales']
    personality = request.form['criteria_personality']
    creativity = request.form['criteria_creativity']
    popularity = request.form['criteria_popularity']

    # Load criteria values into session variables
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
        cur.execute(query, (content, delivery, hits, albums, consistency,
        longevity, impact, sales, personality, creativity, popularity, user_id))
        # Commit to MySQL database
        mysql.connection.commit()

        # Close DB
        cur.close()

    # Boolean to check if user has set a criteria. Used for ranking page
    session['saved_criteria']=True
    return jsonify({'success': 'Saved'})

# Page for rating artists
@app.route('/artistratings')
def myratings():
    if 'rated_artists' not in session:
        # Keep list of rated artists for offline users so its easier to keep
        # track of who they rated
        session['rated_artists']=[]
    return render_template('myratings.html', artistList=getArtistList(),
        categoryList=getCategoryList())

# Saves artist rating when clicking the save button, called through AJAX
@app.route('/rated', methods=['POST'])
def rated():
    # Create MySQL Cursor
    cur = mysql.connection.cursor()

    # Get selected artist name
    artist_name = request.form.get('artist_name')
    artist_name = str(artist_name)

    # Get rating values from sliders
    content_rating = request.form['rating_content']
    delivery_rating = request.form['rating_delivery']
    hits_rating = request.form['rating_hits']
    albums_rating = request.form['rating_albums']
    consistency_rating = request.form['rating_consistency']
    longevity_rating = request.form['rating_longevity']
    impact_rating = request.form['rating_impact']
    sales_rating = request.form['rating_sales']
    personality_rating = request.form['rating_personality']
    creativity_rating = request.form['rating_creativity']
    popularity_rating = request.form['rating_popularity']

    # is user is registered and logged in, store values to data base
    if 'logged_in' in session and session['logged_in']:
        # first check if there are any ratings already for that artist on that
        # account
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
                                albums_rating, consistency_rating,
                                longevity_rating, impact_rating, sales_rating,
                                personality_rating, creativity_rating,
                                popularity_rating, session['user_id'],
                                artist_name])

            # Commit to MySQL database
            mysql.connection.commit()
        # else, do an INSERT INTO query to enter new rating into the database
        else:
            # Write query to insert into the table
            query = """INSERT INTO rating(user_id, artist_name, content,
                    delivery, hits, albums, consistency, longevity, impact,
                    sales, personality, creativity, popularity)
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s)"""
            cur.execute(query, [session['user_id'], artist_name, content_rating,
                                delivery_rating, hits_rating, albums_rating,
                                consistency_rating, longevity_rating,
                                impact_rating, sales_rating, personality_rating,
                                creativity_rating, popularity_rating])
            # Commit to MySQL database
            mysql.connection.commit()
    else:
        # Add artist to list of rated artists
        # This check is to see if the artist has been rated at least once before
        # if so, then it will not add to the list of rated artists again,
        # otherise the rankings page will show duplicates of the same artists
        if artist_name not in session:
            session['rated_artists'].append(artist_name)

        # Save the list into a session variable with the artist name as the key
        session[artist_name] = [content_rating, delivery_rating, hits_rating,
                                albums_rating, consistency_rating,
                                longevity_rating, impact_rating, sales_rating,
                                personality_rating, creativity_rating,
                                popularity_rating]

    # Close DB
    cur.close()
    return jsonify({'success': 'Saved'})

# AJAX calls this function whenever the artist changes in the dropdown to load
# their rating values
@app.route('/artistchanged', methods=['GET'])
def artistchanged():
    # Get selected artist name
    artist_name = request.args.get('artist_name')
    artist_name = str(artist_name)

    # Default list of ratings for if the user has not yet rated this artist
    rating_list = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    # Check if user is logged in
    if 'logged_in' in session:
        # If so, check database to see if they have rated the artist
        # Create MySQL Cursor
        cur = mysql.connection.cursor()
        query = "SELECT * FROM rating WHERE user_id=%s AND artist_name=%s"
        result = cur.execute(query, (session['user_id'], artist_name))
        if result > 0:
            data = cur.fetchone()
            rating_list = [data['content'], data['delivery'], data['hits'],
                        data['albums'], data['consistency'], data['longevity'],
                        data['impact'], data['sales'], data['personality'],
                        data['creativity'], data['popularity']]
            # close connection
            cur.close()

    else:
        # Otherwise check session variable to see if they have rated artist
        if artist_name in session:
            # If so, load rating list from session variable
            rating_list = session[artist_name]

    # return as json list, will be parsed in AJAX function
    return json.dumps(rating_list)

# Page to display top artist rankings
@app.route('/rankings', methods=['GET', 'POST'])
def rankings():
    # List of artists containing tuples with artist name and their overall score
    ranking_list = []
    # Boolean checking whether or not list is empty
    isEmpty = True

    # check if user is logged in
    if 'logged_in' in session:
        # MySQL cursor
        cur = mysql.connection.cursor()

        # Find all ratings made by user
        query = "SELECT * FROM rating WHERE user_id = %s"
        result = cur.execute(query, [str(session['user_id'])])

        # For each rating, calculate total score for that artist
        for row in cur.fetchall():
            totalScore = 0
            for category in getCategoryList():
                categoryScore = int(session[category]) * int(row[category])
                totalScore += categoryScore
            ranking_list.append((row['artist_name'], totalScore))

    else:
        # check if user has visited criteria page, if not then criteria session
        # values will be null
        if 'saved_criteria' not in session:
            return render_template('rankings.html', rankingList=[],
                isEmpty=True)
        if 'rated_artists' in session:
            for artist in session['rated_artists']:
                artist_ratings=session[artist]
                totalScore = 0
                count=0
                for category in getCategoryList():
                    categoryScore = int(session[category]) * int(artist_ratings[count])
                    totalScore += categoryScore
                    count +=1
                ranking_list.append((artist, totalScore))

    # Check if rated artist list is empty (AKA user hasnt rated any artists yet)
    if ranking_list:
        isEmpty=False
    # Sort rated artist list by score from largest to smallest
    sorted_ranking_list = sorted(ranking_list, key=lambda tup: tup[1])[::-1]

    # Check for button clicks from POST
    if request.method == 'POST':
        # Button clicked to delete all artist ratings
        if request.form['action_button'] == 'all_ratings_delete':
            # If user is logged in
            if 'logged_in' in session:
                # Run query to delete all ratings tied to their user id
                cur = mysql.connection.cursor()
                query = """DELETE FROM rating
                            WHERE user_id = %s """
                cur.execute(query, (str(session['user_id'])))
                mysql.connection.commit()
                cur.close()
            # If user is not logged in
            else:
                for artist in session['rated_artists']:
                    # Remove artist key from session dict
                    session.pop(artist, None)
                session['rated_artists'].clear()

        # Button clicked to delete single artist rating
        if request.form['action_button'][0:7] == 'delete_' and request.form['action_button']:
            artist_to_delete = request.form['action_button'][7:]
            # If artist is logged in
            if 'logged_in' in session:
                # Run query to delete single artist from database
                cur = mysql.connection.cursor()
                query = """DELETE FROM rating
                            WHERE user_id = %s AND artist_name=%s"""
                cur.execute(query, (str(session['user_id']), artist_to_delete))
                mysql.connection.commit()
                cur.close()
            # if artist is not logged in
            else:
                # Remove artist key from session dictionary
                session.pop(artist_to_delete, None)
                # And remove him from list of artists
                session['rated_artists'].remove(artist_to_delete)

        return redirect(url_for('rankings'))

    return render_template('rankings.html', rankingList=sorted_ranking_list,
        isEmpty=isEmpty)

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Registration Form
class RegistrationForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email Address', [validators.Length(min=6, max=35),
        validators.email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')

# Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already registered, redirect them to home page
    if 'logged_in' in session:
        flash('You are already registered', 'danger')
        return redirect(url_for('index'))
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        password = bcrypt.generate_password_hash(str(form.password.data)).decode('utf-8')

        try:
            # Add user to database
            cur = mysql.connection.cursor()
            query = "INSERT INTO user(name, email, password) VALUES(%s, %s, %s)"
            cur.execute(query, (name, email, password))
            mysql.connection.commit()
            cur.close()

            # Verify Email
            # First create token for email link
            token = s.dumps(email)

            # Create email message
            msg = Message('Confirm Email at MyTopHHA.com',
                sender=app.config['MAIL_USERNAME'], recipients=[email])
            # Create confirmation link
            link = url_for('confirm_email', token=token, _external=True)

            # Message body
            msg.html = """Hello {}, <br /><br /> Thank you for registering at
                        MyTopHHA.com. Please confirm your email by clicking the
                        link below: <br /><br />{}<br /><br />This link will
                        expire after 24 hours and you will have to request a new
                         one.<br /> <br />If you feel this email is in error,
                        please contact us at
                        support@mytophha.com.""".format(name, link)
            # Finally, send confirmation email
            mail.send(msg)

        except IntegrityError:
            # Error thrown if email is already tied to another account
            flash('Email aready in use', 'danger')
            return redirect(url_for('register'))

        # Thank you message
        flash("""Thank you for registering. You may now log in. Please confirm
                your email in case you forget your password.', 'success""")

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token)

        confirmed = '1'
        # Set email confirmed to true in database
        cur = mysql.connection.cursor()
        query = "UPDATE user SET email_confirmed=%s WHERE email=%s"
        cur.execute(query, (confirmed, email))
        mysql.connection.commit()
        cur.close()
        flash('Email Confirmed. Thank You.', 'success')
        return redirect(url_for('index'))
    except SignatureExpired:
        flash("""Confirmation Link has expired. Please request another
                confirmation email on the \"My Account\" page', 'danger""")
        return redirect(url_for('index'))
    except BadTimeSignature:
        flash('Invalid confirmation link', 'danger')
        return redirect(url_for('index'))


# Login
@app.route('/login', methods = ['GET', 'POST'])
def login():
    # If user is already logged in, redirect them to home page
    if 'logged_in' in session:
        flash('You are already logged in', 'danger')
        return redirect(url_for('index'))
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
            email_confirmed = data['email_confirmed']

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
                session['email_confirmed']=email_confirmed

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
                return render_template('login.html',
                    error = 'Email and password combination is incorrect')
            # Close connection
            cur.close()
        else:
            return render_template('login.html',
                error = 'No user found with that email address')
    return render_template('login.html')

# User Dashboard
@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    # Check if email is verified and store in session variable
    # Also store email in session variable
    cur = mysql.connection.cursor()
    query = "SELECT * FROM user WHERE id=%s"
    result = cur.execute(query, [str(session['user_id'])])
    if result > 0:
        data=cur.fetchone()
        session['email_confirmed']=data['email_confirmed']
        session['email']=data['email']
    cur.close()

    emailForm = EmailForm(request.form, email=session['email'])
    passwordForm = ChangePasswordForm(request.form)

    if request.method == 'POST':
        user_id = str(session['user_id'])
        if request.form['save_button'] == 'change_name':
            new_name = str(request.form['name'])
            if str(session['name']) == new_name:
                flash('You are already using that name', 'danger')
                return redirect(url_for('dashboard'))

            # Change name for account in database
            cur = mysql.connection.cursor()
            query = "UPDATE user SET name=%s WHERE id=%s"
            cur.execute(query, (new_name, user_id))
            mysql.connection.commit()
            cur.close()

            # Update name for session as well
            session['name'] = new_name
            flash('Name Changed', 'success')
            return redirect(url_for('dashboard'))
        elif request.form['save_button'] == 'send_verification':
            email = str(session['email'])
            name = str(session['name'])
            # Send verifcation email
            # First create token for email link
            token = s.dumps(email)

            # Create email message to NEW email
            msg = Message('Confirm Email at MyTopHHA.com',
                sender=app.config['MAIL_USERNAME'],
                recipients=[email])
            # Create confirmation link
            link = url_for('confirm_email', token=token, _external=True)

            # Message body
            msg.html = """Hello {}, <br /><br /> You have requested a
                        confirmation link be sent to this email
                        address for your account at MyTopHHA.com. Please
                        confirm your email by clicking the link
                        below: <br /><br />{}<br /><br />This link will
                        expire after 24 hours and you will have to request
                        a new one. <br /> <br /> If you feel this email is
                        in error, please contact us at
                        support@mytophha.com.""".format(name, link)
            # Finally, send confirmation email
            mail.send(msg)
            flash("""Your confirmation link has been sent. Please confirm at
                    your email address""", 'warning')
            return redirect(url_for('dashboard'))

        elif request.form['save_button'] == 'change_email' and emailForm.validate():
            old_email = session['email']
            new_email = emailForm.email.data
            name =  session['name']
            user_id = str(session['user_id'])
            # Make sure you aren't using the previous email
            if new_email == old_email:
                flash('You are already using that email', 'danger')
                return redirect(url_for('dashboard'))
            try:
                cur = mysql.connection.cursor()
                query = "UPDATE user SET email=%s WHERE id=%s"
                cur.execute(query, (new_email, user_id))
                mysql.connection.commit()
                cur.close()
                session['email']=new_email

                # If not, then send verifcation email
                # First create token for email link
                token = s.dumps(new_email)

                # Create email message to NEW email
                msg1 = Message('Confirm Email at MyTopHHA.com',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[new_email])
                # Create confirmation link
                link = url_for('confirm_email', token=token, _external=True)

                # Message body
                msg1.html = """Hello {}, <br /><br /> You have set this email
                            address for your account at MyTopHHA.com. Please
                            confirm your email by clicking the link
                            below: <br /><br />{}<br /><br />This link will
                            expire after 24 hours and you will have to request
                            a new one. <br /> <br /> If you feel this email is
                            in error, please contact us at
                            support@mytophha.com.""".format(name, link)
                # Finally, send confirmation email
                mail.send(msg1)

                #------------------------------------------------------------#

                # If their old email was previously confirmed, send the old
                # email a message saying that their password was changed,
                # otherwise, don't bother
                if session['email_confirmed'] == '1':
                    # Create email message to OLD email
                    msg2 = Message('Email changed at MyTopHHA.com',
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[old_email])

                    # Message body
                    msg2.html = """Hello {}, <br /><br /> You have changed your
                                email address for your account at MyTopHHA.com.
                                Please confirm by clinking the confirmation link
                                 sent to the new email address. <br /> <br />
                                If you feel this email is in error, please
                                contact us at
                                support@mytophha.com.""".format(name)
                    # Finally, send email
                    mail.send(msg2)

                # also set  email_confirmed flag to false
                unconfirmed = '0'
                cur = mysql.connection.cursor()
                query = "UPDATE user SET email_confirmed=%s WHERE id=%s"
                cur.execute(query, (unconfirmed, user_id))
                mysql.connection.commit()
                cur.close()
                session['email_confirmed']=0

                flash("""Your email changed. Please click the confirmation
                        link at your new email""", 'warning')
                return redirect(url_for('dashboard'))
            except IntegrityError:
                # Error thrown if email is already tied to another account
                flash('Email aready in use', 'danger')
                cur.close()
                return redirect(url_for('dashboard'))
        elif request.form['save_button'] == 'change_password' and passwordForm.validate():
            pw = passwordForm.password.data
            password = bcrypt.generate_password_hash(pw).decode('utf-8')

            # change password in databse
            cur = mysql.connection.cursor()
            query = "UPDATE user SET password=%s WHERE id=%s"
            cur.execute(query, [password, str(session['user_id'])])
            mysql.connection.commit()
            cur.close()

            # If user has confirmed their email, send them an email saying
            # that their password has changed. Otherwise don't bother
            if session['email_confirmed'] != '1':
                # Send email notifying them that their password has changed
                # Create email message to
                msg = Message('Password changed at MyTopHHA.com',
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[str(session['email'])])

                # Message body
                msg.html = """Hello {}, <br /><br /> This is an email
                            notifying you that the password has been changed
                            for your account at MyTopHHA.com. If you did not
                            make this change. Please contact us immediately at
                            support@mytophha.com. Otherwise you may ignore
                            this message""".format(str(session['name']))
                # Finally, send email
                mail.send(msg)
            flash('Password changed', 'success')
            return redirect(url_for('dashboard'))

    return render_template('dashboard.html', emailForm=emailForm,
        current_email=str(session['email']), passwordForm=passwordForm)

# Change Email Form
class EmailForm(Form):
    email = StringField('Email Address', [validators.Length(min=6, max=35),
        validators.email()])

# Change Password Form
class ChangePasswordForm(Form):
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Confirm Password')

# Logout
@app.route('/forgot_password', methods = ['GET', 'POST'])
def forgot_password():
    if 'logged_in' in session:
        flash('Cannot access that page', 'danger')
        return redirect(url_for('index'))
    # Form for sending reset link
    forgotPasswordForm = EmailForm(request.form)

    if request.method == 'POST' and forgotPasswordForm.validate():
        app.logger.info('IN POST')
        email = forgotPasswordForm.email.data

        # First make sure email has been verified
        cur = mysql.connection.cursor()
        query = "SELECT * FROM user WHERE email=%s"
        result = cur.execute(query, [email])
        if result > 0:
            data=cur.fetchone()
            email_confirmed=str(data['email_confirmed'])
            name = data['name']
            if email_confirmed != '1':
                flash("""You must verify your email first before resetting
                        your password. If your verification link has expired,
                        please contact us at Support@MyTopHHA.com""", 'danger')
                cur.close()
                return redirect(url_for('forgot_password'))
        else:
            flash('That email address is not registered to this website',
                'danger')
            cur.close()
            return redirect(url_for('forgot_password'))

        # Send reset link
        # First create token for email link
        token = s.dumps(email, salt='password_recovery')

        # Create email message to NEW email
        msg = Message('Reset Password at MyTopHHA.com',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email])
        # Create confirmation link
        link = url_for('reset_with_token', token=token, _external=True)

        # Message body
        msg.html = """Hello {}, <br /><br /> You have requested a
                    password reset link be sent to this email
                    address for your account at MyTopHHA.com. You can click the
                    link below to reset your password<br /><br />{}<br /><br />
                    This link will expire after 24 hours and you will have to
                    request a new one. <br /> <br /> If you feel this email is
                    in error, please contact us at
                    support@mytophha.com.""".format(name, link)
        # Finally, send pw reset email
        mail.send(msg)
        flash("""Password Reset Link has been sent. Click the link in your email
                to reset your password""", 'warning')
        return redirect(url_for('forgot_password'))

    return render_template('forgot_password.html',
        forgotPasswordForm=forgotPasswordForm)

@app.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    if 'logged_in' in session:
        flash('Cannot access that page', 'danger')
        return redirect(url_for('index'))
    try:
        email = s.loads(token, salt="password_recovery", max_age=86400)
        passwordResetForm = ChangePasswordForm(request.form)

        if passwordResetForm.validate():
            pw = passwordResetForm.password.data
            password = bcrypt.generate_password_hash(pw).decode('utf-8')

            # change password in databse
            cur = mysql.connection.cursor()
            query = "UPDATE user SET password=%s WHERE email=%s"
            cur.execute(query, [password, email])
            mysql.connection.commit()
            cur.close()

            flash('Password successfully reset. You may now log in', 'success')
            return redirect(url_for('login'))
    except:
        abort(404)



    return render_template('reset_password.html',
        passwordResetForm=passwordResetForm,
        token=token)

# Logout
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.clear()
        flash('You have been logged out', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key=app.config['SECRET_KEY']
    app.run(debug=True)
