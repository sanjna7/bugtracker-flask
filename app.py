from flask import Flask, jsonify, request, render_template_string
import sqlite3, os
from datetime import datetime

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('bugs.db')
    conn.execute("CREATE TABLE IF NOT EXISTS bugs (id INTEGER PRIMARY KEY, title TEXT, description TEXT, status TEXT DEFAULT 'Open', priority TEXT DEFAULT 'Medium', created_at TEXT)")
    return conn

HTML = """<h2>Project BugTracker</h2>
<form id="f"><input id="title" placeholder="Bug Title" required><input id="desc" placeholder="Desc"><select id="p"><option>Low</option><option selected>Medium</option><option>High</option></select><button>Add</button></form>
<table border=1 id="t" style="margin-top:20px; border-collapse:collapse; width:100%"><tr><th>ID</th><th>Title</th><th>Action</th></tr></table>
<script>
async function load(){let r=await fetch('/api/bugs');let b=await r.json();let t=document.getElementById('t');t.innerHTML='<tr><th>ID</th><th>Title</th><th>Action</th></tr>';b.forEach(x=>{t.innerHTML+=`<tr><td>${x.id}</td><td>${x.title}</td><td><button onclick="fetch('/api/bugs/${x.id}',{method:'DELETE'}).then(()=>load())">Delete</button></td></tr>`})}
document.getElementById('f').onsubmit=async(e)=>{e.preventDefault();await fetch('/api/bugs',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:title.value,description:desc.value,priority:p.value})});e.target.reset();load()};load()
</script>
"""

@app.route('/')
def home(): return render_template_string(HTML)

@app.route('/api/bugs')
def list_bugs():
    conn = get_db()
    rows = conn.execute("SELECT * FROM bugs ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([{"id":r[0],"title":r[1]} for r in rows])

@app.route('/api/bugs', methods=['POST'])
def add():
    d=request.json
    conn=get_db()
    conn.execute("INSERT INTO bugs (title, description, priority, created_at) VALUES (?,?,?,?)",(d['title'],d.get('description',''),d.get('priority','Medium'),datetime.now().strftime("%Y-%m-%d")))
    conn.commit(); conn.close()
    return jsonify({"ok":True}),201

@app.route('/api/bugs/<int:id>', methods=['DELETE'])
def delete(id):
    conn=get_db(); conn.execute("DELETE FROM bugs WHERE id=?",(id,)); conn.commit(); conn.close()
    return jsonify({"ok":True})

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))