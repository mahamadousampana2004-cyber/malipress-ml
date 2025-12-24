from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'malipress_secret_key_2024'

def get_db_connection():
    conn = sqlite3.connect('malipress.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Table des prestataires
    conn.execute('''
        CREATE TABLE IF NOT EXISTS prestataires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            service TEXT NOT NULL,
            ville TEXT NOT NULL,
            telephone TEXT,
            photo TEXT DEFAULT 'default.png',
            statut TEXT DEFAULT 'gratuit',
            note REAL DEFAULT 4.5
        )
    ''')
    # Table des messages (Celle qui manquait au début)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expediteur TEXT NOT NULL,
            destinataire TEXT NOT NULL,
            contenu TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialisation au démarrage
init_db()

@app.route('/')
def home():
    conn = get_db_connection()
    prestataires = conn.execute('SELECT * FROM prestataires').fetchall()
    conn.close()
    return render_template('index.html', prestataires=prestataires)

@app.route('/inscription', methods=['POST'])
def inscription():
    nom = request.form['nom']
    service = request.form['service']
    ville = request.form['ville']
    tel = request.form['telephone']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO prestataires (nom, service, ville, telephone) VALUES (?, ?, ?, ?)',
                 (nom, service, ville, tel))
    conn.commit()
    conn.close()
    
    session['user_id'] = nom
    return redirect(url_for('mon_espace'))

@app.route('/mon-espace')
def mon_espace():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    # On récupère les messages reçus par l'utilisateur connecté
    mes_messages = conn.execute('SELECT * FROM messages WHERE destinataire = ? ORDER BY date DESC', 
                                (session['user_id'],)).fetchall()
    # On récupère les autres prestataires pour la liste de discussion
    autres = conn.execute('SELECT * FROM prestataires WHERE nom != ?', 
                          (session['user_id'],)).fetchall()
    conn.close()
    return render_template('chat.html', messages=mes_messages, prestataires=autres)

@app.route('/envoyer', methods=['POST'])
def envoyer():
    if 'user_id' in session:
        dest = request.form.get('destinataire')
        msg = request.form.get('message')
        
        if dest and msg:
            conn = get_db_connection()
            conn.execute('INSERT INTO messages (expediteur, destinataire, contenu) VALUES (?, ?, ?)',
                         (session['user_id'], dest, msg))
            conn.commit()
            conn.close()
            
    return redirect(url_for('mon_espace'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

# LE BLOC CI-DESSOUS DOIT ÊTRE COLLÉ AU BORD GAUCHE (0 ESPACE)
if __name__ == '__main__':
    app.run(debug=True)





