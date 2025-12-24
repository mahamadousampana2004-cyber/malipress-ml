from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'malipress_secret_key_2024'
def get_db_connection():
    conn = sqlite3.connect('malipress.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
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

init_db()

@app.route('/')
def home():
    return render_template('choix_compte.html')

@app.route('/espace-client')
def espace_client():
    conn = get_db_connection()
    # Tri : Les Premium en haut, puis les meilleures notes
    pros = conn.execute('SELECT * FROM prestataires ORDER BY statut DESC, note DESC').fetchall()
    conn.close()
    return render_template('index.html', role='client', prestataires=pros)

@app.route('/espace-prestataire')
def espace_prestataire():
    conn = get_db_connection()
    nb = conn.execute('SELECT COUNT(*) FROM prestataires').fetchone()[0]
    conn.close()
    return render_template('index.html', role='prestataire', places=(100-nb), inscrit=request.args.get('inscrit'))

@app.route('/inscription-pro', methods=['POST'])
def inscription_pro():
    nom = request.form.get('nom')
    service = request.form.get('service')
    ville = request.form.get('ville').capitalize()
    tel = request.form.get('telephone')
    file = request.files.get('photo')
    filename = 'default.png'
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    conn = get_db_connection()
    conn.execute('INSERT INTO prestataires (nom, service, ville, telephone, photo) VALUES (?, ?, ?, ?, ?)',
                 (nom, service, ville, tel, filename))
    conn.commit()
    conn.close()
    return redirect(url_for('mon_espace'))
@app.route('/mon-espace')
def mon_espace():
    # On vérifie si le prestataire est bien connecté
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    # On récupère les messages reçus par ce prestataire
    mes_messages = conn.execute('SELECT * FROM messages WHERE destinataire = ? ORDER BY date DESC', (session['user_id'],)).fetchall()
    # On récupère la liste des autres prestataires pour pouvoir leur écrire
    autres = conn.execute('SELECT * FROM prestataires WHERE nom != ?', (session['user_id'],)).fetchall()
    conn.close()
    
    # On affiche la page chat.html avec les données
    return render_template('chat.html', messages=mes_messages, prestataires=autres)

@app.route('/envoyer', methods=['POST'])
def envoyer():
    if 'user_id' in session:
        dest = request.form.get('destinataire')
        msg = request.form.get('message')
        
        if dest and msg:
            conn = get_db_connection()
            # On enregistre la discussion dans la base malipress.db
            conn.execute('INSERT INTO messages (expediteur, destinataire, contenu) VALUES (?, ?, ?)',
                         (session['user_id'], dest, msg))
            conn.commit()
            conn.close()
            
    # Après l'envoi, on reste dans l'espace de discussion
    return redirect(url_for('mon_espace'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/mon-espace')
def mon_espace():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    conn = get_db_connection()
    # Correction : on récupère les messages et les autres prestataires
    messages = conn.execute('SELECT * FROM messages WHERE destinataire = ? ORDER BY date DESC', (session['user_id'],)).fetchall()
    autres = conn.execute('SELECT * FROM prestataires WHERE nom != ?', (session['user_id'],)).fetchall()
    conn.close()
return render_template('chat.html', messages=messages, prestataires=autres)
if __name__ == '__main__':
    app.run(debug=True)

