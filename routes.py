from flask import Flask, render_template, session, request, redirect
from datetime import date
import sqlite3
app = Flask(__name__)

app.secret_key = '123456'

@app.route('/')
def home():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    cur.execute('SELECT username, content, date FROM Gratitude_idea ORDER BY RANDOM() LIMIT 1')
    results = cur.fetchone()
    return render_template("home.html", results = results)

@app.route('/my_posts', methods=['GET'])
def my_posts():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    sql = 'SELECT * FROM Gratitude_idea WHERE username = ?'
    cur.execute(sql, (session['username'],))
    results = cur.fetchall()
    print(results)
    return render_template("my_posts.html", results = results)

@app.post('/post_idea')
def post_idea():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    sql = 'INSERT INTO Gratitude_idea (username, date, content) VALUES (?,?,?)'
    cur.execute(sql, (session['username'], date.today(), request.form['post_idea'])) #Get username from cookie, get date from ?, get content from the form "create post" or "post_idea"
    print(cur.execute(sql, (session['username'], date.today(), request.form['post_idea'])))
    conn.commit()
    return redirect("my_posts")

@app.route('/public_posts')
def public_posts():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    cur.execute('SELECT username, content, date FROM Gratitude_idea ORDER BY date DESC')
    results = cur.fetchall()
    return render_template("public_posts.html", results = results)

#Route for the login page
@app.route('/login', methods=['GET', 'POST'])    
def login(): #If the given credentials are found in the user table then the user can login with those credentials. Loop through username column and password column until a legitimate combination has been found.
    return render_template("login.html")

@app.post('/create_account')
def create_account():
    session['username'] = request.form['username']
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    sql = 'INSERT INTO User (username, password) VALUES (?,?)'
    cur.execute(sql, (request.form['username'], request.form['password']))
    conn.commit()
    session["username"] = request.form['username']
    print(session["username"])
    return redirect("/")
    

if __name__ == "__main__":
    app.run(debug = True)