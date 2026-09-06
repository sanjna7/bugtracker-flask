from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('bugs.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS bugs (id INTEGER PRIMARY KEY, title TEXT, priority TEXT, status TEXT)')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db()
    bugs = conn.execute('SELECT * FROM bugs').fetchall()
    conn.close()
    return render_template('index.html', bugs=bugs)

@app.route('/add', methods=['POST'])
def add():
    conn = get_db()
    conn.execute('INSERT INTO bugs (title, priority, status) VALUES (?,?,?)',
                 (request.form['title'], request.form['priority'], request.form['status']))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/analytics')
def analytics():
    conn = get_db()
    status_data = conn.execute('SELECT status, COUNT(*) as count FROM bugs GROUP BY status').fetchall()
    priority_data = conn.execute('SELECT priority, COUNT(*) as count FROM bugs GROUP BY priority').fetchall()
    total = conn.execute('SELECT COUNT(*) as total FROM bugs').fetchone()['total']
    conn.close()
    return render_template('analytics.html', status_data=status_data, priority_data=priority_data, total=total)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    conn.execute('DELETE FROM bugs WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))