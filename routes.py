from flask import Flask, render_template, session, request, redirect, flash
from datetime import datetime
import sqlite3
import random
import os
app = Flask(__name__)

app.secret_key = 'VyG00hNWF10sa1DduxPpi2vXV195DGnoKj5HzNoqk\
v0UiWOMf47UW4TYzBrSlJzAkf5alfe5enGNNaZHk6NqcjJDEqQQ80L9NyCv'
conn = sqlite3.connect("mindful.db")
conn = sqlite3.connect('mindful.db', check_same_thread=False)
cur = conn.cursor()

sort = 'popular'
first_login = True

# Home page, displays a mindful post from a user when loading the home page.


def db_query(query, is_single, is_insert, data):
    conn = sqlite3.connect("mindful.db")
    cur = conn.cursor()
    cur.execute(query, data)
    if is_single is True:
        cur.fetchone()
    else:
        cur.fetchall()
    if is_insert is True:
        conn.commit()


@app.route('/')
def home():
    cur.execute('SELECT username, content, date FROM Gratitude_idea ORDER BY\
                 RANDOM() LIMIT 1')
    idea_data = cur.fetchone()
    cur.execute('SELECT username, content, date FROM Gratitude_idea ORDER BY\
                 RANDOM() LIMIT 1')
    idea_data1 = cur.fetchone()
    return render_template("home.html", idea_data=idea_data,
                           idea_data1=idea_data1)


# My post page, if user is logged in, it will display all posts by the current
# user, if not it will redirect them to the login page.

@app.route('/my_posts', methods=['GET'])
def my_posts():
    if 'username' in session:
        sql = 'SELECT * FROM Gratitude_idea WHERE username = ?\
                                            ORDER BY date DESC'
        cur.execute(sql, (session['username'],))
        user_idea_data = cur.fetchall()
        return render_template("my_posts.html", user_idea_data=user_idea_data)
    else:
        return redirect("loginpage")


# Public post page, will display posts made by every user.

@app.route('/public_posts', methods=['GET', 'POST'])
def public_posts():
    global sort
    if request.method == "GET":
        if sort == 'popular':
            cur.execute('SELECT username, content, date, id, like_count FROM\
                 Gratitude_idea WHERE is_public = 1 ORDER BY like_count DESC ')
            idea_data = cur.fetchall()
            return render_template("public_posts.html", idea_data=idea_data)
        elif sort == 'newest':
            cur.execute('SELECT username, content, date, id, like_count FROM\
                 Gratitude_idea WHERE is_public = 1 ORDER BY date DESC ')
            idea_data = cur.fetchall()
            return render_template("public_posts.html", idea_data=idea_data)
        else:
            cur.execute('SELECT username, content, date, id, like_count FROM\
                 Gratitude_idea WHERE is_public = 1 ORDER BY date ASC ')
            idea_data = cur.fetchall()
            return render_template("public_posts.html", idea_data=idea_data)

    elif request.method == "POST":
        sort = request.form['sort']
        return redirect("public_posts")
    else:
        return redirect("/")

# Login page, user will input credentials to post content.


@app.route('/loginpage')
def loginpage():
    return render_template("loginpage.html")


# Admin page, locked by specific admin/password combination, will display all
# posts and all usernames.

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    cur.execute('SELECT username, content, date, id, like_count FROM\
                 Gratitude_idea ORDER BY date DESC')
    idea_data = cur.fetchall()
    cur.execute('SELECT username FROM User')
    username = cur.fetchall()
    return render_template("admin.html", idea_data=idea_data,
                           username=username)


# If user is logged in as admin, it will redirect them to the admin page.
@app.post('/adminlogin')
def adminlogin():
    global first_login
    if first_login is True:
        return redirect('loginpage')
    elif session['username'] == 'admin':
        return redirect('admin')
    else:
        return redirect('loginpage')

# Allows users to insert posts into the database, requires their username,
# current date and post content.


@app.post('/post_idea')
def post_idea():
    sql = 'INSERT INTO Gratitude_idea (username, date, content, is_public)\
            VALUES (?,?,?,?)'
    current_time = datetime.today().strftime('%d-%m-%Y')
    # Get username from cookie, get date from ?, get content from the form
    # "create post" or "post_idea"
    cur.execute(sql, (session['username'], current_time,
                      request.form['post_idea'], request.form['radio']))
    conn.commit()
    return redirect("my_posts")


# Admin can ban users and remove their username and posts from the database.

@app.post('/ban_user')
def ban_user():
    sql = "DELETE FROM User WHERE username = ?"
    cur.execute(sql, (request.form['username'],))
    sql = "DELETE FROM Gratitude_idea WHERE username = ?"
    cur.execute(sql, (request.form['username'],))
    conn.commit()
    return redirect("admin")


# Allows the current user to delete their posts from the database if needed.

@app.post('/delete_my_post')
def delete_my_post():
    sql = "DELETE FROM Gratitude_idea WHERE id = ?"
    cur.execute(sql, (request.form['post_id'],))
    conn.commit()
    return redirect("my_posts")


@app.post('/delete_their_post')
def delete_their_post():
    sql = "DELETE FROM Gratitude_idea WHERE id = ?"
    cur.execute(sql, (request.form['post_id'],))
    conn.commit()
    return redirect("admin")


# Allows users to "like" other posts made by users in the public posts page.

@app.post('/like')
def like():
    if 'username' in session:
        cur.execute("SELECT id FROM User WHERE username = ?",
                    (session['username'],))
        user_id = cur.fetchone()
        liked_query = "SELECT id FROM Liked_Posts WHERE post_id = ?\
                                                        AND user = ?"
        cur.execute(liked_query, (request.form['like'], user_id[0],))
        post_id = cur.fetchone()

        if post_id is None:

            # Likes a post, inserts into table, updates like count

            like_a_post_query = "INSERT INTO Liked_Posts (user, post_id) \
                                                         VALUES (?,?)"
            cur.execute(like_a_post_query, (user_id[0], request.form['like'],))
            post_id = request.form['like']
            select_count_query = "SELECT COUNT(id) FROM Liked_Posts\
                                                   WHERE post_id = ?"
            cur.execute(select_count_query, (post_id,))
            count = cur.fetchone()
            print(count)
            set_like = "UPDATE Gratitude_idea SET like_count = ? WHERE id = ?"
            cur.execute(set_like, (count[0], post_id))
            conn.commit()
            print(post_id)
            return redirect("public_posts")
        else:
            # Unlikes a post, removes from table, updates like count
            unlike_a_post_query = "DELETE FROM Liked_Posts WHERE post_id = ?\
                                                                AND user = ?"
            cur.execute(unlike_a_post_query, (request.form['like'],
                                              user_id[0],))
            post_id = request.form['like']
            select_count_query = "SELECT COUNT(id) FROM Liked_Posts WHERE \
                                                                post_id = ?"
            cur.execute(select_count_query, (post_id,))
            count = cur.fetchone()
            set_like = "UPDATE Gratitude_idea SET like_count = ? WHERE id = ?"
            cur.execute(set_like, (count[0], post_id))
            conn.commit()
            return redirect("public_posts")

    else:
        return redirect('loginpage')


# Allows the user to create or login into thier account using thier username
# and password.

@app.post('/create_or_login')
def create_or_login():
    global first_login
    create_or_login = request.form['create_or_login']

    # If the user is trying to create a new account.
    if create_or_login == "create_account":

        # Database will return a username if it exists
        sql = 'SELECT username FROM User WHERE username = ?'
        cur.execute(sql, (request.form['username'],))
        username = cur.fetchone()

        # If it doesnt exist then it will insert it into the database and the
        # username session is filled.
        if username is None:
            sql = 'INSERT INTO User (username, password) VALUES (?,?)'
            cur.execute(sql, (request.form['username'],
                              request.form['password']))
            conn.commit()
            session["username"] = request.form['username']
            first_login = False
            flash('You have been logged in, redirecting you to home page')
            return redirect("/")
        else:

            # Alerts the user that the username is already taken
            msg = "Sorry, username has been taken"
            return render_template("loginpage.html", msg=msg)

    # If the user is attempting to login into thier existing account.
    if create_or_login == "login":
        sql = 'SELECT username, password FROM User WHERE username = ?\
                                                     AND password = ?'
        cur.execute(sql, (request.form['username'], request.form['password']))
        results = cur.fetchall()

        # If username/password combination is not found within the database.
        if not results:
            msg = "Incorrect username or password"
            return render_template("loginpage.html", msg=msg)
        # If it does exist the user can login and redirected to their posts.
        elif request.form['username'] == 'admin':
            return redirect('admin')
        else:
            session["username"] = request.form['username']
            first_login = False
            return redirect('/my_posts')


@app.post('/logout')
def logout():
    session.clear()
    return redirect('/')


# Chooses a random image from /static/images folder
def get_random_image():
    image_folder = os.path.join(app.static_folder, 'images')
    images = os.listdir(image_folder)
    random_image = random.choice(images)
    return f"static/images/{random_image}"


# Allows random images to be used by all pages.


@app.context_processor
def inject_random_image():
    return {'random_image': get_random_image(),
            'random_image1': get_random_image()}

# Error pages


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(debug=True)
