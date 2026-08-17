import streamlit as st
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import math
import database

# 1. Configuration de la page
st.set_page_config(page_title="Pharmacies CI & Urgences", page_icon="🏥", layout="wide")

import streamlit.components.v1 as components

# Balise de vérification Google
components.html("""
    <meta name="google-site-verification" content="JVHHkwdTC5NTDYRH0vI1vZ6NEu4PLBRjAt1b8shi12A" />
""", height=0)
# Initialisation de l'état de la session pour enregistrer les avis des utilisateurs
if "suggestions" not in st.session_state:
    st.session_state.suggestions = [
        {"nom": "Kouassi Jean", "message": "Serait-il possible d'ajouter les horaires exacts d'ouverture ?", "note": "⭐ 5/5"},
        {"nom": "Awa Diop", "message": "Super application ! Très pratique pour les urgences la nuit.", "note": "⭐ 5/5"}
    ]

# 2. Fonction mathématique pour calculer la distance (Formule de Haversine)
def calculer_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Rayon de la Terre en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

# 3. Styles CSS personnalisés & lisibles
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    section[data-testid="stSidebar"] { background-color: #0F172A !important; }
    section[data-testid="stSidebar"] * { color: #F8FAFC !important; }
    
    /* Titres généraux */
    h1, h2, h3 { color: #0F172A !important; font-weight: 700 !important; }
    
    /* Cartes des Pharmacies */
    .pharmacy-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        border-left: 5px solid #10B981;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    .pharmacy-title { font-size: 1.15rem; font-weight: 700; color: #1E293B; }
    .badge-garde { background-color: #DEF7EC; color: #03543F; font-size: 0.8rem; font-weight: 600; padding: 3px 10px; border-radius: 15px; }
    .badge-dist { background-color: #E0F2FE; color: #0369A1; font-size: 0.85rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; }
    .btn-call { display: inline-block; margin-top: 8px; background-color: #0284C7; color: white !important; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 0.9rem; font-weight: 600; }
    
    /* Cartes d'Urgences */
    .emergency-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 12px;
        border-left: 5px solid #EF4444;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    .emergency-name { font-size: 1.05rem; font-weight: 700; color: #0F172A; }
    .emergency-type { font-size: 0.85rem; color: #64748B; margin-top: 2px; }
    .emergency-btn { background-color: #DC2626; color: white !important; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 0.9rem; }
    
    /* Cartes de Recommandation / Suggestions */
    .feedback-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# 4. Navigation
st.sidebar.title("🏥 Pharmacies CI")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navigation", ["🟢 Pharmacies de Garde", "🔍 Recherche", "🚨 Urgences", "📊 Admin & Avis"])

# --- PAGE 1 : PHARMACIES DE GARDE ---
if menu == "🟢 Pharmacies de Garde":
    st.title("💊 Pharmacies de Garde en Côte d'Ivoire")
    
    col_filter, col_gps = st.columns([2, 1])
    
    with col_filter:
        villes_bdd = database.obtenir_villes()
        villes_disponibles = ["Toutes les villes"] + villes_bdd
        ville_selected = st.selectbox("Filtrer par ville / commune :", villes_disponibles)
    
    with col_gps:
        st.write("📍 **Activer ma Position GPS :**")
        location = streamlit_geolocation()
        user_lat = location.get("latitude")
        user_lon = location.get("longitude")

    pharmacies_brutes = database.obtenir_pharmacies(ville_selected)
    pharmacies = []

    if user_lat and user_lon:
        st.success("📍 Position GPS détectée ! Tri des pharmacies par proximité activé.")
        for p in pharmacies_brutes:
            p_list = list(p)
            if len(p_list) >= 7 and p_list[5] and p_list[6]:
                dist = calculer_distance(user_lat, user_lon, float(p_list[5]), float(p_list[6]))
                p_list.append(dist)
            else:
                p_list.append(9999)
            pharmacies.append(p_list)
        pharmacies.sort(key=lambda x: x[7])
    else:
        for p in pharmacies_brutes:
            p_list = list(p)
            p_list.append(None)
            pharmacies.append(p_list)

    st.markdown("---")

    col_map, col_list = st.columns([3, 2])

    with col_map:
        st.subheader("🗺️ Carte Interactive")
        start_center = [user_lat, user_lon] if (user_lat and user_lon) else [7.5399, -5.5470]
        start_zoom = 12 if (user_lat and user_lon) else 7
        
        m = folium.Map(location=start_center, zoom_start=start_zoom, tiles="CartoDB positron")
        
        if user_lat and user_lon:
            folium.Marker(
                [user_lat, user_lon],
                popup="Vous êtes ici",
                tooltip="Votre position",
                icon=folium.Icon(color="blue", icon="user", prefix="fa")
            ).add_to(m)

        for pharma in pharmacies:
            if len(pharma) >= 7 and pharma[5] and pharma[6]:
                try:
                    dist_txt = f" ({pharma[7]} km)" if pharma[7] is not None and pharma[7] != 9999 else ""
                    folium.Marker(
                        [float(pharma[5]), float(pharma[6])],
                        popup=f"{pharma[1]}{dist_txt}",
                        tooltip=f"{pharma[1]} - {pharma[2]}{dist_txt}",
                        icon=folium.Icon(color="green", icon="plus", prefix="fa")
                    ).add_to(m)
                except Exception:
                    pass
                    
        st_folium(m, width="100%", height=500)

    with col_list:
        st.subheader(f"📋 Liste ({len(pharmacies)} disponible(s))")
        if not pharmacies:
            st.info("Aucune pharmacie trouvée.")
        else:
            for p in pharmacies:
                dist_badge = f'<span class="badge-dist">📏 {p[7]} km</span>' if p[7] is not None and p[7] != 9999 else ''
                st.markdown(f"""
                    <div class="pharmacy-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="pharmacy-title">{p[1]}</div>
                            <div>{dist_badge} <span class="badge-garde">🟢 DE GARDE</span></div>
                        </div>
                        <p style="color:#64748B; margin: 6px 0; font-size:0.9rem;">📍 <b>{p[2]}</b> — {p[3]}</p>
                        <a href="tel:{p[4]}" class="btn-call">📞 Appeler : {p[4]}</a>
                    </div>
                """, unsafe_allow_html=True)

# --- PAGE 2 : RECHERCHE AVANCÉE ---
elif menu == "🔍 Recherche":
    st.title("🔍 Recherche de Pharmacies")
    st.write("Trouvez une pharmacie en filtrant par ville ou en recherchant par nom / quartier.")
    
    col_v, col_t = st.columns([1, 2])
    
    with col_v:
        villes_bdd = database.obtenir_villes()
        ville_filtre = st.selectbox("🏘️ Sélectionner une ville :", ["Toutes les villes"] + villes_bdd)
    
    with col_t:
        mot_cle = st.text_input("🔎 Nom de pharmacie ou quartier :", placeholder="Ex: Nouvelle Santé, Yopougon, Cocody...")
    
    st.markdown("---")
    
    recherche_query = mot_cle.strip()
    if ville_filtre != "Toutes les villes" and not recherche_query:
        recherche_query = ville_filtre
    elif ville_filtre != "Toutes les villes" and recherche_query:
        recherche_query = f"{ville_filtre} {recherche_query}"

    if recherche_query:
        res = database.rechercher_pharmacies(recherche_query)
        
        if ville_filtre != "Toutes les villes":
            res = [p for p in res if p[2].lower() == ville_filtre.lower()]

        if res:
            st.success(f"🎯 **{len(res)}** pharmacie(s) trouvée(s)")
            
            for p in res:
                nom = p[1]
                ville = p[2]
                repere = p[3] if len(p) > 3 and p[3] else "Emplacement non précisé"
                telephone = p[4] if len(p) > 4 and p[4] else "Non renseigné"
                
                st.markdown(f"""
                    <div class="pharmacy-card">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div class="pharmacy-title">{nom}</div>
                                <div style="color:#64748B; margin-top:4px; font-size:0.9rem;">
                                    📍 <b>{ville}</b> — {repere}
                                </div>
                            </div>
                            <div>
                                <a href="tel:{telephone}" class="btn-call">📞 Appeler : {telephone}</a>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("❌ Aucune pharmacie trouvée avec ces critères de recherche.")
    else:
        st.info("💡 Choisissez une ville ou saisissez un nom dans la barre de recherche ci-dessus.")

# --- PAGE 3 : URGENCES ---
elif menu == "🚨 Urgences":
    st.title("🚨 Numéros d'Urgence en Côte d'Ivoire")
    
    st.subheader("📞 Numéros Nationaux Unifiés (Gratuits 24h/24)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚒 Pompiers (GSPM)", "180 / 18")
    c2.metric("🚑 SAMU", "185")
    c3.metric("🚓 Police Secours", "100 / 111")
    c4.metric("🏛️ Gouvernement", "101")
    
    st.markdown("---")
    
    LIGNES_DIRECTES = {
        "Abidjan - Indénié (GSPM)": {"type": "🚒 Sapeurs-Pompiers", "tel": "2720211289", "affiche": "27 20 21 12 89", "repere": "Caserne Principale Plateau/Indénié"},
        "Abidjan - Yopougon (GSPM)": {"type": "🚒 Sapeurs-Pompiers", "tel": "2723451690", "affiche": "27 23 45 16 90", "repere": "Caserne Toits Rouges"},
        "Abidjan - Zone 4 (GSPM)": {"type": "🚒 Sapeurs-Pompiers", "tel": "2721357365", "affiche": "27 21 35 73 65", "repere": "Zone Marcory / Koumassi"},
        "Abidjan - CHU Cocody": {"type": "🏥 Urgences CHU", "tel": "2722481000", "affiche": "27 22 48 10 00", "repere": "Grandes Urgences Médicales"},
        "Abidjan - CHU Treichville": {"type": "🏥 Urgences CHU", "tel": "2721249122", "affiche": "27 21 24 91 22", "repere": "Pavillon des Urgences"},
        "Yamoussoukro (GSPM)": {"type": "🚒 Sapeurs-Pompiers", "tel": "2730640180", "affiche": "27 30 64 01 80", "repere": "Caserne 6è Compagnie"},
        "Bouaké (GSPM)": {"type": "🚒 Sapeurs-Pompiers", "tel": "2731633230", "affiche": "27 31 63 32 30", "repere": "Caserne 3è Compagnie"},
        "Korhogo (GSPM)": {"type": "🚒 Sapeurs-Pompiers", "tel": "2736860180", "affiche": "27 36 86 01 80", "repere": "Caserne 4è Compagnie"},
        "San-Pédro (GSPM)": {"type": "🚒 Sapeurs-Pompiers", "tel": "2734712580", "affiche": "27 34 71 25 80", "repere": "Caserne 5è Compagnie"},
        "Daloa (CHR)": {"type": "🏥 Centre Hospitalier", "tel": "2732783020", "affiche": "27 32 78 30 20", "repere": "CHR Urgences Daloa"},
        "Man (CHR)": {"type": "🏥 Centre Hospitalier", "tel": "2733791100", "affiche": "27 33 79 11 00", "repere": "CHR Urgences Man"}
    }

    st.subheader("📍 Lignes Directes Fixes & Casernes Locales")
    zone_choisie = st.selectbox("Filtrer par caserne ou hôpital :", ["Toutes les zones"] + list(LIGNES_DIRECTES.keys()))

    if zone_choisie == "Toutes les zones":
        for nom, info in LIGNES_DIRECTES.items():
            st.markdown(f"""
                <div class="emergency-card">
                    <div>
                        <div class="emergency-name">{nom}</div>
                        <div class="emergency-type">{info['type']} — 📍 {info['repere']}</div>
                    </div>
                    <a href="tel:{info['tel']}" class="emergency-btn">📞 {info['affiche']}</a>
                </div>
            """, unsafe_allow_html=True)
    else:
        info = LIGNES_DIRECTES[zone_choisie]
        st.markdown(f"""
            <div class="emergency-card" style="padding: 25px;">
                <div>
                    <div class="emergency-name" style="font-size:1.3rem;">{zone_choisie}</div>
                    <div class="emergency-type" style="font-size:1rem; margin-top:5px;">{info['type']} — 📍 {info['repere']}</div>
                </div>
                <a href="tel:{info['tel']}" class="emergency-btn" style="font-size:1.1rem; padding:12px 24px;">📞 Appeler {info['affiche']}</a>
            </div>
        """, unsafe_allow_html=True)

# --- PAGE 4 : ADMIN & BOÎTE À RECOMMANDATIONS ---
elif menu == "📊 Admin & Avis":
    st.title("📊 Administration & Recommandations")
    
    # 1. Dashboard des métriques clés
    stats = database.obtenir_statistiques()
    villes = database.obtenir_villes()
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("🏥 Pharmacies répertoriées", stats['total_pharmacies'])
    col_stat2.metric("🏙️ Villes / Communes couvertes", len(villes))
    col_stat3.metric("💬 Avis & Suggestions reçus", len(st.session_state.suggestions))
    
    st.markdown("---")
    
    # 2. Formulaire pour les visiteurs (Avis & Améliorations)
    st.subheader("💡 Laisser une recommandation ou suggestion")
    st.write("Votre avis nous aide à améliorer l'application pour l'ensemble des utilisateurs.")
    
    with st.form("form_suggestion", clear_on_submit=True):
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            nom_visiteur = st.text_input("Votre nom / prénom (optionnel) :", placeholder="Ex: Jean Kouassi")
        with col_f2:
            note_visiteur = st.selectbox("Note globale :", ["⭐ 5/5 (Excellent)", "⭐ 4/5 (Très bon)", "⭐ 3/5 (Moyen)", "⭐ 2/5 (À améliorer)", "⭐ 1/5 (Mauvais)"])
        
        message_visiteur = st.text_area("Quels points ou fonctionnalités aimeriez-vous qu'on améliore ?", placeholder="Ex: Ajoutez une option pour voir si les pharmacies livrent à domicile...")
        
        btn_envoyer = st.form_submit_button("📩 Envoyer ma recommandation")
        
        if btn_envoyer:
            if message_visiteur.strip():
                nouvel_avis = {
                    "nom": nom_visiteur.strip() if nom_visiteur.strip() else "Anonyme",
                    "message": message_visiteur.strip(),
                    "note": note_visiteur.split(" ")[0] + " " + note_visiteur.split(" ")[1]
                }
                st.session_state.suggestions.insert(0, nouvel_avis)
                st.success("✅ Merci ! Votre recommandation a bien été transmise à l'équipe.")
            else:
                st.error("⚠️ Veuillez écrire un message avant de soumettre.")

    st.markdown("---")
    
    # 3. Section de consultation des avis reçus
    st.subheader("📬 Derniers retours et suggestions reçus")
    
    if st.session_state.suggestions:
        for item in st.session_state.suggestions:
            st.markdown(f"""
                <div class="feedback-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color:#0F172A; font-size:1rem;">👤 {item['nom']}</b>
                        <span style="font-weight:700; color:#D97706;">{item['note']}</span>
                    </div>
                    <p style="color:#475569; margin-top:8px; font-size:0.95rem;">💬 « {item['message']} »</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Aucune recommandation n'a encore été enregistrée.")

    
