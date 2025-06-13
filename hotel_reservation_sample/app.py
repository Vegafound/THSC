from flask import Flask, render_template, request
import sqlite3
import uuid

app = Flask(__name__)

DB_NAME = 'reservations.db'
ADMIN_CODE = 'admin123'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id TEXT PRIMARY KEY,
                nickname TEXT,
                date TEXT
            )
        """)
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reserve', methods=['POST'])
def reserve():
    nickname = request.form['nickname']
    date = request.form['date']
    reservation_id = str(uuid.uuid4())[:8]

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM reservations WHERE date = ?", (date,))
        count = c.fetchone()[0]
        if count >= 5:
            return "その日は満席です。"

        c.execute("INSERT INTO reservations (id, nickname, date) VALUES (?, ?, ?)",
                  (reservation_id, nickname, date))
        conn.commit()

    return f"予約完了！予約番号: {reservation_id}"

@app.route('/cancel', methods=['POST'])
def cancel():
    reservation_id = request.form['reservation_id']
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
        conn.commit()
    return "キャンセルしました。"

@app.route('/admin')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin_panel', methods=['POST'])
def admin_panel():
    code = request.form['code']
    if code != ADMIN_CODE:
        return "認証失敗"

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM reservations ORDER BY date")
        reservations = c.fetchall()

    return render_template('admin_panel.html', reservations=reservations)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
