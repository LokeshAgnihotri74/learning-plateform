from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'
DB_FILE = 'edustream.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tables creation
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT DEFAULT "student"
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, category TEXT, description TEXT
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS site_content (
        id INTEGER PRIMARY KEY, hero_title TEXT, hero_desc TEXT
    )''')
    
    # Insert Dummy Data if empty
    cursor.execute("SELECT COUNT(*) FROM site_content")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO site_content (id, hero_title, hero_desc) VALUES (1, 'Unlock Your Potential with EduStream', 'Access high-quality courses, track your progress, and learn from industry experts today.')")
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE email='admin@gmail.com'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name, email, password, role) VALUES ('Admin User', 'admin@gmail.com', 'admin123', 'admin')")
        
    conn.commit()
    conn.close()

# Run database initializer
init_db()

@app.route('/')
def home():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, hero_title, hero_desc FROM site_content WHERE id = 1")
    content = cursor.fetchone()
    conn.close()
    return render_template('index.html', content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, role FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_role'] = user[2]
            
            if user[2] == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('dashboard'))
        else:
            return "Invalid Credentials! Please try again."
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('student-dashboard.html')

@app.route('/courses')
def courses():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, category, description FROM courses")
    all_courses = cursor.fetchall()
    conn.close()
    return render_template('courses.html', courses=all_courses)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session or session.get('user_role') != 'admin':
        return "Access Denied! Admins only.", 403
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_course':
            title = request.form['course_title']
            cat = request.form['course_category']
            desc = request.form['course_description']
            cursor.execute("INSERT INTO courses (title, category, description) VALUES (?, ?, ?)", (title, cat, desc))
            conn.commit()
            
        elif action == 'update_content':
            h_title = request.form['hero_title']
            h_desc = request.form['hero_desc']
            cursor.execute("UPDATE site_content SET hero_title = ?, hero_desc = ? WHERE id = 1", (h_title, h_desc))
            conn.commit()
            
        conn.close()
        return redirect(url_for('admin'))

    cursor.execute("SELECT id, title, category FROM courses")
    courses_list = cursor.fetchall()
    
    cursor.execute("SELECT id, name, email, role FROM users")
    users_list = cursor.fetchall()
    
    cursor.execute("SELECT id, hero_title, hero_desc FROM site_content WHERE id = 1")
    site_content = cursor.fetchone()
    
    conn.close()
    return render_template('admin-panel.html', courses=courses_list, users=users_list, content=site_content)

if __name__ == '__main__':
    app.run(debug=True)