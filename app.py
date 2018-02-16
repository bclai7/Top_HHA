from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/mycriteria')
def mycriteria():
    return render_template('mycriteria.html')

@app.route('/artistratings', methods=['GET','POST'])
def myratings():
    with open("Resources/RapperList.txt", "r") as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    return render_template('myratings.html', artistList=content)

@app.route('/about')
def about():
    return render_template('about.html')



if __name__ == '__main__':
    app.run(debug=True)
