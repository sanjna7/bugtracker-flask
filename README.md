#BugTracker - Flask CRUD App

Live Demo: https://bugtracker-flask.onrender.com

## **Tech Stack**
- **Backend**: Python 3, Flask, SQLite3
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Render

## **Features**
- Create, read, update, delete bugs
- Filter bugs by status: Open, InProgress, Closed
- Search bugs by title
- Priority levels: Low, Medium, High, Critical
- Timestamps for audit trail
- REST API endpoints

## **API Endpoints**
| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/bugs` | Fetch all bugs with optional status filter |
| POST | `/add` | Create new bug |
| PUT | `/update/<id>` | Update bug status |
| DELETE | `/delete/<id>` | Delete bug by ID |

## **Deployment Notes**
Render free tier uses an ephemeral filesystem. Key fixes applied:
1. SQLite database path set to `/tmp/bugs.db` because the root directory is read-only
2. `init_db()` called on startup to create tables on cold starts
3. For production, migrate to Render PostgreSQL for data persistence

## **Run Locally**
```bash
git clone https://github.com/sanjna7/bugtracker-flask.git
cd bugtracker-flask
pip install flask
python app.py
