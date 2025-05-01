from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key
DATABASE = 'blog.db'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin789'  # You can change this

# Database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Home page
@app.route('/')
def home():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('home.html', posts=posts)

# View a single post
@app.route('/post/<int:id>')
def post(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (id,)).fetchone()
    conn.close()
    if post is None:
        return "Post not found", 404
    return render_template('post.html', post=post)

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('Logged out', 'info')
    return redirect(url_for('home'))

# Create post
@app.route('/create', methods=['GET', 'POST'])
def create():
    if not session.get('admin'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title or not content:
            return "Title and Content are required!", 400
        conn = get_db_connection()
        conn.execute('INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)',
                     (title, content, datetime.now()))
        conn.commit()
        conn.close()
        flash('Post created!', 'success')

        return redirect(url_for('home'))
    return render_template('create_post.html')

# Edit post
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (id,)).fetchone()
    if post is None:
        return "Post not found", 404
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title or not content:
            return "Title and Content are required!", 400
        conn.execute('UPDATE posts SET title = ?, content = ? WHERE id = ?',
                     (title, content, id))
        conn.commit()
        conn.close()
        flash('Post updated!', 'success')

        return redirect(url_for('post', id=id))
    conn.close()
    return render_template('edit_post.html', post=post)

# Delete post
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if not session.get('admin'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('Post deleted.', 'warning')

    return redirect(url_for('home'))

# Initialize database
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
