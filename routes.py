from flask import Flask, render_template, session, request, redirect
from datetime import datetime
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
    if 'username' in session:
        print("logged in")
        conn = sqlite3.connect("mindful.db")
        cur = conn.cursor()
        sql = 'SELECT * FROM Gratitude_idea WHERE username = ? ORDER BY date DESC'
        cur.execute(sql, (session['username'],))
        results = cur.fetchall()
        return render_template("my_posts.html", results = results)
    else:
        print("not logged in")
        return redirect("loginpage")    

@app.route('/admin', methods=['GET','POST'])
def admin():
    return render_template("admin.html")

@app.post('/post_idea')
def post_idea():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    sql = 'INSERT INTO Gratitude_idea (username, date, content) VALUES (?,?,?)'
    current_time = datetime.today().strftime('%d-%m-%Y')
    cur.execute(sql, (session['username'], current_time, request.form['post_idea'])) #Get username from cookie, get date from ?, get content from the form "create post" or "post_idea"
    conn.commit()
    return redirect("my_posts")

@app.post('/like') #Create a feature where you cant keep liking a post with the same account.
def like():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    sql = "UPDATE Gratitude_idea SET like_count = like_count + 1 WHERE id = ?"
    cur.execute(sql, (request.form['like'],))
    conn.commit()
    return redirect("public_posts")

@app.route('/public_posts')
def public_posts():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    cur.execute('SELECT username, content, date, id, like_count FROM Gratitude_idea ORDER BY date DESC')
    results = cur.fetchall()
    return render_template("public_posts.html", results = results)

#Route for the login page
@app.route('/loginpage')    
def loginpage(): #If the given credentials are found in the user table then the user can login with those credentials. Loop through username column and password column until a legitimate combination has been found.   
    return render_template("loginpage.html")

@app.route('/create_or_login', methods=['POST'])
def create_or_login():
    create_or_login = request.form['create_or_login']
    if create_or_login == "create_account":
        conn = sqlite3.connect("mindful.db")
        cur = conn.cursor()
        sql = 'SELECT username FROM User WHERE username = (?)' #Database will return a username if it exists
        cur.execute(sql, (request.form['username'],))
        username = cur.fetchone() 
        if username == None: #If it doesnt exist then it will insert it into the database and the username session is filled.
            sql = 'INSERT INTO User (username, password) VALUES (?,?)'
            cur.execute(sql, (request.form['username'], request.form['password']))
            conn.commit()
            session["username"] = request.form['username']
            return redirect("/")
        else:
            msg = "Sorry, username has been taken" #tells the user that the username is already taken 
            return render_template("loginpage.html", msg = msg)
    if create_or_login == "login":
        conn = sqlite3.connect("mindful.db")
        cur = conn.cursor()
        sql = 'SELECT username, password FROM User WHERE username = (?) AND password = (?)'
        cur.execute(sql, (request.form['username'], request.form['password']))
        results = cur.fetchall()
        print(results)
        if not results:
            print("doesnt exist")
            msg = "Incorrect username or password"
            return render_template("loginpage.html", msg = msg)
        else:
            session["username"] = request.form['username']
            return redirect('/my_posts')

if __name__ == "__main__":
    app.run(debug = True)