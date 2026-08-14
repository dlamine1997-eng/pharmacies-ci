import sqlite3
import os

# Chemin absolu garanti vers analytics.db dans le dossier du script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "analytics.db")

def initialiser_et_remplir():
    """Crée la table et injecte des données de test si la base est vide"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Création de la table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pharmacies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            ville TEXT NOT NULL,
            quartier_repere TEXT,
            telephone TEXT,
            latitude REAL,
            longitude REAL
        )
    """)
    conn.commit()
    
    # 2. Vérification si la base est vide
    cursor.execute("SELECT COUNT(*) FROM pharmacies")
    total = cursor.fetchone()[0]
    
    # 3. Auto-remplissage si vide
    if total == 0:
        exemples = [
            ("Pharmacie de Morofé", "Yamoussoukro", "Carrefour Banny", "0757492313", 6.8276, -5.2893),
            ("Pharmacie du Banco", "Abidjan", "Yopougon", "0102030405", 5.3453, -4.0244),
            ("Pharmacie Centrale", "Bouaké", "Commerce", "0506070809", 7.6938, -5.0303),
            ("Pharmacie Saint-Joseph", "Korhogo", "Quartier Résidentiel", "0708091011", 9.4580, -5.6296),
            ("Pharmacie de la Paix", "Daloa", "Centre Ville", "0123456789", 6.8773, -6.4502),
            ("Pharmacie d'Abengourou", "Abengourou", "Grand Marché", "0505050505", 6.7297, -3.4964)
        ]
        cursor.executemany("""
            INSERT INTO pharmacies (nom, ville, quartier_repere, telephone, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?)
        """, exemples)
        conn.commit()
        
    conn.close()

# Exécution systématique au chargement
initialiser_et_remplir()

def obtenir_villes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT ville FROM pharmacies ORDER BY ville ASC")
    villes = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    return villes

def obtenir_pharmacies(ville="Toutes les villes"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if not ville or ville == "Toutes les villes":
        cursor.execute("SELECT * FROM pharmacies")
    else:
        cursor.execute("SELECT * FROM pharmacies WHERE ville = ?", (ville,))
    pharmacies = cursor.fetchall()
    conn.close()
    return pharmacies

def rechercher_pharmacies(mot_cle):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = "%" + mot_cle + "%"
    cursor.execute("""
        SELECT * FROM pharmacies 
        WHERE nom LIKE ? OR ville LIKE ? OR quartier_repere LIKE ?
    """, (query, query, query))
    pharmacies = cursor.fetchall()
    conn.close()
    return pharmacies

def obtenir_statistiques():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM pharmacies")
    total = cursor.fetchone()[0]
    conn.close()
    return {"total_pharmacies": total}