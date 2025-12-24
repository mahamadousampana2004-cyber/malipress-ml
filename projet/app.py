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
# Ligne 71 de ta photo b8f0a393
@app.route('/envoyer', methods=['POST'])
def envoyer():
    # On vérifie si l'utilisateur est connecté
    if 'user_id' in session:
        destinataire = request.form.get('destinataire')
        message_contenu = request.form.get('message')
        expediteur = session['user_id']
        
        conn = get_db_connection()
        # On enregistre le message dans la table que tu as créée
        conn.execute('INSERT INTO messages (expediteur, destinataire, contenu) VALUES (?, ?, ?)',
                     (expediteur, destinataire, message_contenu))
        conn.commit()
        conn.close()
    
    return redirect(url_for('mon_espace'))
