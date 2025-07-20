import sqlite3

# Connect to database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Create users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')
# Create tasks table
c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT NOT NULL,
    status INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

print("✅ users table created.")

# Close connection
conn.commit()
conn.close()
