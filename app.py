from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DATABASE='/tmp/bugs.db'
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bugs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  status TEXT DEFAULT 'Open',
                  priority TEXT DEFAULT 'Medium',
                  created_at TEXT)''')
    conn.commit()
    conn.close()
init_db()

# HTML template embedded so it's 1 file only
HTML = '''
<!DOCTYPE html>
<html>
<head><title>BugTracker</title>
<style>
body{font-family:Arial;margin:20px} table{border-collapse:collapse;width:100%}
td,th{border:1px solid #ddd;padding:8px} .Open{background:#ffebee} .InProgress{background:#fff3e0} .Closed{background:#e8f5e8}
input,select,textarea{margin:5px;padding:5px} button{padding:8px 12px;margin:5px}
</style>
</head>
<body>
<h2>Accenture BugTracker</h2>
<form id="bugForm">
<input id="title" placeholder="Bug Title" required>
<textarea id="desc" placeholder="Description"></textarea>
<select id="priority"><option>Low</option><option selected>Medium</option><option>High</option></select>
<button type="submit">Add Bug</button>
</form>
<br>
<input id="search" placeholder="Search bugs..." onkeyup="loadBugs()">
<select id="filterStatus" onchange="loadBugs()">
    <option value="">All Status</option><option>Open</option><option>InProgress</option><option>Closed</option>
</select>
<table id="bugTable"><thead><tr><th>ID</th><th>Title</th><th>Status</th><th>Priority</th><th>Created</th><th>Action</th></tr></thead><tbody></tbody></table>

<script>
async function loadBugs(){
    let q = document.getElementById('search').value
    let s = document.getElementById('filterStatus').value
    let res = await fetch(`/api/bugs?q=${q}&status=${s}`)
    let bugs = await res.json()
    let tbody = document.querySelector('#bugTable tbody')
    tbody.innerHTML = ''
    bugs.forEach(b => {
        tbody.innerHTML += `<tr class="${b.status}">
        <td>${b.id}</td><td>${b.title}</td><td>${b.status}</td><td>${b.priority}</td>
        <td>${b.created_at}</td>
        <td>
        <button onclick="updateStatus(${b.id}, 'InProgress')">Start</button>
        <button onclick="updateStatus(${b.id}, 'Closed')">Close</button>
        <button onclick="deleteBug(${b.id})">Delete</button>
        </td></tr>`
    })
}

async function updateStatus(id, status){
    await fetch(`/api/bugs/${id}`, {method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify({status})})
    loadBugs()
}

async function deleteBug(id){
    await fetch(`/api/bugs/${id}`, {method:'DELETE'})
    loadBugs()
}

document.getElementById('bugForm').onsubmit = async (e) => {
    e.preventDefault()
    let data = {
        title: document.getElementById('title').value,
        description: document.getElementById('desc').value,
        priority: document.getElementById('priority').value
    }
    await fetch('/api/bugs', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)})
    e.target.reset()
    loadBugs()
}
loadBugs()
</script>
</body></html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/bugs', methods=['GET'])
def get_bugs():
    q = request.args.get('q', '')
    status = request.args.get('status', '')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    query = "SELECT * FROM bugs WHERE 1=1"
    params = []
    if q:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f'%{q}%', f'%{q}%'])
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY id DESC"
    c.execute(query, params)
    bugs = [{'id':r[0],'title':r[1],'description':r[2],'status':r[3],'priority':r[4],'created_at':r[5]} for r in c.fetchall()]
    conn.close()
    return jsonify(bugs)

@app.route('/api/bugs', methods=['POST'])
def add_bug():
    data = request.json
    if not data.get('title'):
        return jsonify({'error':'Title required'}), 400
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("INSERT INTO bugs (title, description, priority, created_at) VALUES (?,?,?,?)",
              (data['title'], data.get('description',''), data.get('priority','Medium'), datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    bug_id = c.lastrowid
    conn.close()
    return jsonify({'id':bug_id}), 201

@app.route('/api/bugs/<int:bug_id>', methods=['PUT'])
def update_bug(bug_id):
    data = request.json
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("UPDATE bugs SET status=? WHERE id=?", (data['status'], bug_id))
    conn.commit()
    conn.close()
    return jsonify({'success':True})

@app.route('/api/bugs/<int:bug_id>', methods=['DELETE'])
def delete_bug(bug_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("DELETE FROM bugs WHERE id=?", (bug_id,))
    conn.commit()
    conn.close()
    return jsonify({'success':True})

if __name__ == '__main__':
    port=int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    