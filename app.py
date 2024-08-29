from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    city_query = request.args.get('city', '')

    conn = get_db_connection()
    if search_query or city_query:
        offers = conn.execute('''
            SELECT * FROM offers 
            WHERE title LIKE ? AND city LIKE ?
        ''', ('%' + search_query + '%', '%' + city_query + '%')).fetchall()
    else:
        offers = conn.execute('SELECT * FROM offers').fetchall()
    conn.close()
    return render_template('index.html', offers=offers)

@app.route('/inbox')
def inbox():
    return render_template('inbox.html')

@app.route('/account', methods=['GET', 'POST'])
def account():
    if request.method == 'POST':
        if 'username' in request.form:  # Rejestracja
            username = request.form['username']
            password = request.form['password']
            conn = get_db_connection()
            existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'error')
                return redirect(url_for('account'))
            
            hashed_password = generate_password_hash(password)
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('account'))
        
        elif 'loginUsername' in request.form:  # Logowanie
            username = request.form['loginUsername']
            password = request.form['loginPassword']
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Login failed. Please check your username and password.', 'error')
                return redirect(url_for('account'))
    
    return render_template('account.html')

@app.route('/new_offer', methods=['GET', 'POST'])
def new_offer():
    if request.method == 'POST':
        title = request.form['title']
        city = request.form['city']
        description = request.form['description']

        if not session.get('username'):
            flash('You need to log in to add an offer.', 'error')
            return redirect(url_for('account'))

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()

        conn.execute('INSERT INTO offers (title, city, description, user_id) VALUES (?, ?, ?, ?)',
                     (title, city, description, user['id']))
        conn.commit()
        conn.close()
        flash('Offer added successfully!', 'success')
        return redirect(url_for('new_offer'))
    
    return render_template('new_offer.html')

if __name__ == '__main__':
    app.run(debug=True)
