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
    try:
        cur = conn.cursor()
        cur.execute(query, data)

        if is_insert:
            conn.commit()

        if is_single:
            result = cur.fetchone()
        else:
            result = cur.fetchall()

        return result
    finally:
        conn.close()


@app.route('/')
def home():
    idea_data = db_query("SELECT username, content, date FROM Gratitude_idea\
                          ORDER BY RANDOM() LIMIT 1", True, False, ())
    idea_data1 = db_query("SELECT username, content, date FROM Gratitude_idea\
    ORDER BY RANDOM() LIMIT 1", True, False, ())
    return render_template("home.html", idea_data=idea_data,
                           idea_data1=idea_data1)


# My post page, if user is logged in, it will display all posts by the current
# user, if not it will redirect them to the login page.

@app.route('/my_posts', methods=['GET'])
def my_posts():
    if 'username' in session:
        user_idea_data = db_query("SELECT * FROM Gratitude_idea WHERE username\
                = ? ORDER BY date DESC", False, False, (session['username'],))
        return render_template("my_posts.html", user_idea_data=user_idea_data)
    else:
        flash('First please create an account or login to an existing one.')
        return redirect("loginpage")


# Public post page, will display posts made by every user.

@app.route('/public_posts', methods=['GET', 'POST'])
def public_posts():
    global sort

    if 'username' in session:
        user_id = db_query("SELECT id FROM User WHERE username = ?", True,
                           False, (session['username'],))
        if request.method == "GET":
            if sort == 'popular':
                idea_data = db_query('SELECT username, content, date, id,\
                like_count FROM Gratitude_idea WHERE is_public = 1 ORDER BY\
                like_count DESC', False, False, ())
                liked_post = db_query('SELECT post_id FROM Liked_Posts WHERE\
                user = ?', False, False, user_id)
                liked_posts = [item[0] for item in liked_post]
                return render_template("public_posts.html",
                                       idea_data=idea_data,
                                       liked_posts=liked_posts,
                                       user_id=user_id)
            elif sort == 'newest':
                idea_data = db_query('SELECT username, content, date, id,\
                like_count FROM Gratitude_idea WHERE is_public = 1 ORDER BY\
                date DESC', False, False, ())
                liked_post = db_query('SELECT post_id FROM Liked_Posts WHERE\
                user = ?', False, False, user_id)
                liked_posts = [item[0] for item in liked_post]
                return render_template("public_posts.html",
                                       idea_data=idea_data,
                                       liked_posts=liked_posts,
                                       user_id=user_id)
            else:
                idea_data = db_query('SELECT username, content, date, id,\
                like_count FROM Gratitude_idea WHERE is_public = 1 ORDER BY\
                date ASC', False, False, ())
                liked_post = db_query('SELECT post_id FROM Liked_Posts WHERE\
                user = ?', False, False, user_id)
                liked_posts = [item[0] for item in liked_post]
                return render_template("public_posts.html",
                                       idea_data=idea_data,
                                       liked_posts=liked_posts,
                                       user_id=user_id)
        elif request.method == "POST":
            sort = request.form['sort']
            return redirect("public_posts")
        else:
            return redirect("/")
    else:
        flash('First please create an account or login to an existing one.')
        return redirect('loginpage')

# Login page, user will input credentials to post content.


@app.route('/loginpage')
def loginpage():
    return render_template("loginpage.html")


@app.route('/create_account_page')
def create_account_page():
    return render_template("create_account_page.html")


# Admin page, locked by specific admin/password combination, will display all
# posts and all usernames.

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    idea_data = db_query('SELECT username, content, date, id, like_count FROM\
                 Gratitude_idea ORDER BY date DESC', False, False, ())
    username = db_query('SELECT username FROM User', False, False, ())
    return render_template("admin.html", idea_data=idea_data,
                           username=username)

# If user is logged in as admin, it will redirect them to the admin page.


@app.post('/adminlogin')
def adminlogin():
    if session['username'] == 'admin':
        return redirect('admin')
    else:
        return redirect('loginpage')

# Allows users to insert posts into the database, requires their username,
# current date and post content.
# Get username from cookie, get date from ?, get content from the form
# "create post" or "post_idea"


@app.post('/post_idea')
def post_idea():
    current_time = datetime.today().strftime('%d-%m-%Y')
    db_query('INSERT INTO Gratitude_idea (username, date, content, is_public)\
    VALUES (?,?,?,?)', False, True, (session['username'], current_time,
                                     request.form['post_idea'],
                                     request.form['radio']))
    return redirect("my_posts")


# Admin can ban users and remove their username and posts from the database.

@app.post('/ban_user')
def ban_user():
    user_id = db_query("SELECT id FROM User WHERE username = ?", True,
                       False, (request.form['username'],))
    db_query("DELETE FROM Liked_Posts WHERE user = ?", False, True,
             (user_id))
    db_query("DELETE FROM User WHERE username = ?", False, True,
             (request.form['username'],))
    db_query("DELETE FROM Gratitude_idea WHERE username = ?", False, True,
             (request.form['username'],))
    return redirect("admin")


# Allows the current user to delete their posts from the database if needed.

@app.post('/delete_my_post')
def delete_my_post():
    db_query("DELETE FROM Gratitude_idea WHERE id = ?", False, True,
             (request.form['post_id'],))
    return redirect("my_posts")


@app.post('/delete_their_post')
def delete_their_post():
    db_query("DELETE FROM Gratitude_idea WHERE id = ?", False, True,
             (request.form['post_id'],))
    return redirect("admin")


# Allows users to "like" other posts made by users in the public posts page.

@app.post('/like')
def like():
    if 'username' in session:
        user_id = db_query("SELECT id FROM User WHERE username = ?", True,
                           False, (session['username'],))
        post_id = db_query("SELECT id FROM Liked_Posts WHERE post_id = ?\
        AND user = ?", True, False, (request.form['like'], user_id[0],))
        if post_id is None:
            # Likes a post, inserts into table, updates like count
            db_query("INSERT INTO Liked_Posts (user, post_id) \
            VALUES (?,?)", False, True, (user_id[0], request.form['like'],))
            post_id = request.form['like']
            count = db_query("SELECT COUNT(id) FROM Liked_Posts\
            WHERE post_id = ?", True, False, (post_id,))
            db_query("UPDATE Gratitude_idea SET like_count = ? WHERE id = ?",
                     False, True, (count[0], post_id))
            return redirect("public_posts")
        else:
            # Unlikes a post, removes from table, updates like count
            db_query("DELETE FROM Liked_Posts WHERE post_id = ?\
            AND user = ?", False, True, (request.form['like'],
                                         user_id[0],))
            post_id = request.form['like']
            count = db_query("SELECT COUNT(id) FROM Liked_Posts WHERE \
            post_id = ?", True, False, (post_id,))
            db_query("UPDATE Gratitude_idea SET like_count = ? WHERE id = ?",
                     False, True, (count[0], post_id))
            return redirect("public_posts")
    else:
        return redirect('loginpage')


# Allows the user to create or login into thier account using thier username
# and password.

@app.post('/login')
def login():
    global first_login
    results = db_query('SELECT username, password FROM User WHERE username = ?\
    AND password = ?', False, False, (request.form['username'],
                                      request.form['password']))

    # If username/password combination is not found within the database.
    if not results:
        flash("Incorrect username or password.")
        return render_template("loginpage.html")
    # If it does exist the user can login and redirected to their posts.
    elif request.form['username'] == 'admin':
        session["username"] = request.form['username']
        return redirect('admin')
    else:
        session["username"] = request.form['username']
        first_login = False
        return redirect('/my_posts')


@app.post('/create_account')
def create_account():
    global first_login
    # Database will return a username if it exists
    username = db_query('SELECT username FROM User WHERE username = ?', True,
                        False, (request.form['username'],))
    if request.form['password'] == request.form['confirm_password']:
        # If it doesnt exist then it will insert it into the database and the
        # username session is filled.
        if username is None:
            db_query('INSERT INTO User (username, password) VALUES (?,?)',
                     False, True, (request.form['username'],
                                   request.form['password']))
            session["username"] = request.form['username']
            first_login = False
            flash('You have created an account! \
            Redirecting you to your page.')
            return redirect("/my_posts")
        else:
            # Alerts the user that the username is already taken
            flash('Sorry, that username has been taken.')
            return redirect('/create_account_page')
    else:
        flash('Passwords do not match.')
        return redirect('/create_account_page')


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


def session_username():
    if 'username' in session:
        return {'username': session['username']}

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
