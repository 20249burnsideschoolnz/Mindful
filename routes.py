from flask import Flask, render_template, session, request, redirect
from datetime import datetime
import sqlite3
app = Flask(__name__)

app.secret_key = '123456'

# @app.route

# Home page, displays a mindful post from a user when loading the home page.


@app.route('/')
def home():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    cur.execute('SELECT username, content, date FROM Gratitude_idea ORDER BY RANDOM() LIMIT 1')
    results = cur.fetchone()
    return render_template("home.html", results=results)

# My post page, if user is logged in, it will display all posts by the current
# user, if not it will redirect them to the login page.


@app.route('/my_posts', methods=['GET'])
def my_posts():
    if 'username' in session:
        print("logged in")
        conn = sqlite3.connect("mindful.db")
        cur = conn.cursor()
        sql = 'SELECT * FROM Gratitude_idea WHERE username = ? ORDER BY date DESC'
        cur.execute(sql, (session['username'],))
        results = cur.fetchall()
        print(results)
        return render_template("my_posts.html", results=results)
    else:
        print("not logged in")
        return redirect("loginpage")    

# Public post page, will display posts made by every user.


@app.route('/public_posts')
def public_posts():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    cur.execute('SELECT username, content, date, id, like_count FROM Gratitude_idea ORDER BY date DESC')
    results = cur.fetchall()
    return render_template("public_posts.html", results=results)

# Login page, user will input credentials to post content.


@app.route('/loginpage')
def loginpage():
    # If the given credentials are found in the user table then
    # the user can login with those credentials. Loop through username column
    # and password column until a legitimate combination has been found.
    return render_template("loginpage.html")

# Admin page, locked by specific admin/password combination, will display all
# posts and all usernames.


@app.route('/admin', methods=['GET','POST'])
def admin():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    cur.execute('SELECT username, content, date, id, like_count FROM Gratitude_idea ORDER BY date DESC')
    results = cur.fetchall()
    cur.execute('SELECT username FROM User')
    results1 = cur.fetchall()
    return render_template("admin.html", results=results, results1=results1)       


# @app.post

# If user is logged in as admin, it will redirect them to the admin page.
@app.post('/adminlogin')
def adminlogin():
    if 'username' in session:
        if session['username'] == 'admin':
            return redirect('admin')
    else:
        return redirect('loginpage')

# Allows users to insert posts into the database, requires their username, current date and post content.


@app.post('/post_idea')
def post_idea():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    sql = 'INSERT INTO Gratitude_idea (username, date, content) VALUES (?,?,?)'
    current_time = datetime.today().strftime('%d-%m-%Y')
    # Get username from cookie, get date from ?, get content from the form
    # "create post" or "post_idea"
    cur.execute(sql, (session['username'], current_time, request.form['post_idea']))
    conn.commit()
    return redirect("my_posts")       

# Admin can ban users and remove their username and posts from the database.


@app.post('/ban_user')
def ban_user():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    sql = "DELETE FROM User WHERE username = ?"
    cur.execute(sql, (request.form['username'],))
    sql = "DELETE FROM Gratitude_idea WHERE username = ?"
    cur.execute(sql, (request.form['username'],))
    conn.commit()
    return redirect("admin") 

# Allows the current user to delete their posts from the database if needed.


@app.post('/delete_my_post')
def delete_my_post():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    sql = "DELETE FROM Gratitude_idea WHERE id = ?"
    cur.execute(sql, (request.form['post_id'],))
    conn.commit()
    return redirect("my_posts")

# Allows users to "like" other posts made by users in the public posts page.


@app.post('/like') 
def like():
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    sql = "UPDATE Gratitude_idea SET like_count = like_count + 1 WHERE id = ?"
    cur.execute(sql, (request.form['like'],))
    conn.commit()
    return redirect("public_posts")

# Allows the user to create or login into thier account using thier username
# and password.


@app.post('/create_or_login')
def create_or_login():
    create_or_login = request.form['create_or_login']

    # If the user is trying to create a new account.
    if create_or_login == "create_account":
        conn = sqlite3.connect("mindful.db")
        cur = conn.cursor()
        
        # Database will return a username if it exists
        sql = 'SELECT username FROM User WHERE username = (?)' 
        cur.execute(sql, (request.form['username'],))
        username = cur.fetchone() 

        # If it doesnt exist then it will insert it into the database and the
        # username session is filled.
        if username is None:
            sql = 'INSERT INTO User (username, password) VALUES (?,?)'
            cur.execute(sql, (request.form['username'], request.form['password']))
            conn.commit()
            session["username"] = request.form['username']
            return redirect("/")
        else:

            # Alerts the user that the username is already taken
            msg = "Sorry, username has been taken"
            return render_template("loginpage.html", msg=msg)
    # If the user is attempting to login into thier existing account.
    if create_or_login == "login":
        conn = sqlite3.connect("mindful.db")
        cur = conn.cursor()
        sql = 'SELECT username, password FROM User WHERE username = (?) AND password = (?)'
        cur.execute(sql, (request.form['username'], request.form['password']))
        results = cur.fetchall()

        # If username/password combination is not found within the database.
        if not results:
            msg = "Incorrect username or password"
            return render_template("loginpage.html", msg=msg)
        # If it does exist the user can login and redirected to their posts.
        else:
            session["username"] = request.form['username']
            return redirect('/my_posts')


if __name__ == "__main__":
    app.run(debug=True)