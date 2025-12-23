from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    return redirect(url_for('espace_prestataire', inscrit='oui'))

@app.route('/admin-malipress-2025')
def admin():
    conn = get_db_connection()
    pros = conn.execute('SELECT * FROM prestataires').fetchall()
    conn.close()
    return render_template('admin.html', pros=pros)

@app.route('/valider-pro/<int:id>')
def valider(id):
    conn = get_db_connection()
    conn.execute("UPDATE prestataires SET statut = 'premium' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/supprimer-pro/<int:id>')
def supprimer_pro(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM prestataires WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/discuter/<nom>')
def discuter(nom):
    conn = get_db_connection()
    pro = conn.execute('SELECT telephone FROM prestataires WHERE nom = ?', (nom,)).fetchone()
    conn.close()
    tel = pro['telephone'] if pro else ""
    return render_template('chat.html', prestataire=nom, telephone=tel)
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/conditions-premium')
def conditions_premium():
    return render_template('conditions_premium.html')    
if __name__ == '__main__':
    app.run(debug=True)