import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

# Tworzymy tabelę offers, jeśli nie istnieje
cursor.execute('''
    CREATE TABLE IF NOT EXISTS offers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        city TEXT NOT NULL,
        description TEXT NOT NULL,
        user_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

connection.commit()
connection.close()
