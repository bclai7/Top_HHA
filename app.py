from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

#Configure MySQL database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Damn@James221'
app.config['MYSQL_DB'] = 'tophha'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/mycriteria')
def mycriteria():
    return render_template('mycriteria.html')

@app.route('/artistratings')
def myratings():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT name FROM artist ORDER BY name''')
    DictArtist = cur.fetchall() # returns dictionary of artists
    ArtistList=[] # create empty list to add artist names to
    # add artists to ArtistList
    for artist in DictArtist:
        ArtistList.append(artist["name"])
    # content = [x.strip() for x in ArtistList]

    return render_template('myratings.html', artistList=ArtistList)

@app.route('/about')
def about():
    return render_template('about.html')



if __name__ == '__main__':
    app.run(debug=True)
