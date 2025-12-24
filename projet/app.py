from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'malipress_final_secure_2025'

def get_db_connection():
    conn = sqlite3.connect('malipress.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialisation des tables
def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS prestataires (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL, service TEXT NOT NULL, ville TEXT NOT NULL,
        telephone TEXT, statut TEXT DEFAULT 'gratuit', note REAL DEFAULT 4.5)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT, expediteur TEXT,
        destinataire TEXT, contenu TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = get_db_connection()
    nb = conn.execute('SELECT COUNT(*) FROM prestataires').fetchone()[0]
    prestataires = conn.execute('SELECT * FROM prestataires ORDER BY statut DESC, note DESC').fetchall()
    conn.close()
    return render_template('index.html', prestataires=prestataires, promo_active=(nb < 100), places=(100-nb))

@app.route('/inscription', methods=['POST'])
def inscription():
    conn = get_db_connection()
    conn.execute('INSERT INTO prestataires (nom, service, ville, telephone) VALUES (?, ?, ?, ?)',
                 (request.form['nom'], request.form['service'], request.form['ville'], request.form['telephone']))
    conn.commit()
    conn.close()
    session['user_id'] = request.form['nom']
    return redirect(url_for('mon_espace'))

@app.route('/mon-espace')
def mon_espace():
    if 'user_id' not in session: return redirect(url_for('home'))
    conn = get_db_connection()
    msgs = conn.execute('SELECT * FROM messages WHERE destinataire = ?', (session['user_id'],)).fetchall()
    autres = conn.execute('SELECT * FROM prestataires WHERE nom != ?', (session['user_id'],)).fetchall()
    mon_p = conn.execute('SELECT * FROM prestataires WHERE nom = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('chat.html', messages=msgs, prestataires=autres, profil=mon_p)

@app.route('/envoyer', methods=['POST'])
def envoyer():
    if 'user_id' in session:
        conn = get_db_connection()
        conn.execute('INSERT INTO messages (expediteur, destinataire, contenu) VALUES (?, ?, ?)',
                     (session['user_id'], request.form.get('destinataire'), request.form.get('message')))
        conn.commit()
        conn.close()
    return redirect(url_for('mon_espace'))

@app.route('/premium')
def premium():
    return render_template('conditions_premium.html')

@app.route('/valider-premium', methods=['POST'])
def valider_premium():
    if 'user_id' in session:
        conn = get_db_connection()
        conn.execute('UPDATE prestataires SET statut = "premium" WHERE nom = ?', (session['user_id'],))
        conn.commit()
        conn.close()
    return redirect(url_for('mon_espace'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/admin-malipress')
def admin():
    conn = get_db_connection()
    tous = conn.execute('SELECT * FROM prestataires ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin.html', prestataires=tous, total=len(tous))

@app.route('/jeu')
def jeu():
    return render_template('jeu.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))
    @app.route('/choix-compte')
def choix_compte():
    # Cette page permet de choisir entre l'inscription gratuite (promo) ou payante
    return render_template('choix_compte.html')@app.route('/choix-compte')
def choix_compte():
    # Cette page permet de choisir entre l'inscription gratuite (promo) ou payante
    return render_template('choix_compte.html')@app.route('/choix-compte')
def choix_compte():
    # Cette page permet de choisir entre l'inscription gratuite (promo) ou payante
    return render_template('choix_compte.html')@app.route('/choix-compte')
def choix_compte():
    # Cette page permet de choisir entre l'inscription gratuite (promo) ou payante
    return render_template('choix_compte.html')@app.route('/choix-compte')
def choix_compte():
    # Cette page permet de choisir entre l'inscription gratuite (promo) ou payante
    return render_template('choix_compte.html')@app.route('/choix-compte')
def choix_compte():
    # Cette page permet de choisir entre l'inscription gratuite (promo) ou payante
    return render_template('choix_compte.html')@app.route('/choix-compte')
def choix_compte():
    # Cette page permet de choisir entre l'inscription gratuite (promo) ou payante
    return render_template('choix_compte.html')v

if __name__ == '__main__':
    app.run(debug=True)v
