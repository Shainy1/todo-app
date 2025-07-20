from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connect to SQLite
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route (Login page)
@app.route('/')
def login():
    return render_template('login.html')

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        con = get_db()
        cur = con.cursor()

        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            return redirect(url_for('signup', error="Username already taken"))
        
        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        con.commit()
        con.close()
        return redirect(url_for('login'))
    return render_template('signup.html')

# Login form POST route
@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']

    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    con.close()

    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login', error="Invalid username or password"))

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM tasks WHERE user_id = ?", (session['user_id'],))
    tasks = cur.fetchall()

    # Get username to show on dashboard
    cur.execute("SELECT username FROM users WHERE id = ?", (session['user_id'],))
    username = cur.fetchone()['username']
    con.close()

    return render_template('dashboard.html', tasks=tasks, username=username)

# Add task
@app.route('/add', methods=['POST'])
def add_task():
    if 'user_id' in session:
        task = request.form['task']
        con = get_db()
        cur = con.cursor()
        cur.execute("INSERT INTO tasks (user_id, task, status) VALUES (?, ?, ?)", (session['user_id'], task, 0))
        con.commit()
        con.close()
    return redirect(url_for('dashboard'))

# Update task (mark done/undone)
@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    if 'user_id' in session:
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT status FROM tasks WHERE id = ? AND user_id = ?", (task_id, session['user_id']))
        task = cur.fetchone()
        if task:
            new_status = 0 if task['status'] else 1
            cur.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
            con.commit()
        con.close()
    return redirect(url_for('dashboard'))

# Delete task
@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user_id' in session:
        con = get_db()
        cur = con.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, session['user_id']))
        con.commit()
        con.close()
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


# Run the app
import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

