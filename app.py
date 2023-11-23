import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort

# make a Flask application object called app
app = Flask(__name__)
app.config["DEBUG"] = True

#flash  the secret key to secure sessions
app.config['SECRET_KEY'] = 'your secret key'

# open connection to database.db file
def get_db_connection():
    conn = sqlite3.connect('database.db')
    # allows us to have name based access to columns
    # will return rows we can access like dictionaries
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    query = 'SELECT * FROM posts WHERE id = ?'
    post = conn.execute(query, (post_id,)).fetchone()
    conn.close()

    if post is None:
        abort(404)
    return post

# use the app.route() decorator to create a Flask view function called index()
@app.route('/')
def index():
    conn = get_db_connection()
    query = 'SELECT * FROM posts'
    posts = conn.execute(query).fetchall()
    conn.close()
    
    return render_template('index.html', posts=posts)

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        
        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)', (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    
    return render_template('create.html')

#route to edit post
@app.route('/<int:id>/edit/', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        
        if not title:
            flash('Title is required!')
        elif not content:
            flash('Content is required!')
        else:
            conn = get_db_connection()
            query = 'UPDATE posts SET title = ?, content = ? WHERE id = ?'
            conn.execute(query, (title, content, id))
            conn.commit()
            conn.close()
           
            return redirect(url_for('index'))
    
    return render_template('edit.html', post=post)

# route to delete a post
@app.route('/<int:id>/delete/', methods=('POST',))
def delete(id):
    post = get_post(id)

    conn = get_db_connection()
    query = 'DELETE FROM posts WHERE id = ?'
    conn.execute(query, (id,))
    conn.commit()
    conn.close()

    flash(f'Post {post["title"]} was successfully deleted!')

    return redirect(url_for('index'))


app.run(host="0.0.0.0")