import streamlit as st
import openai
import os

# 1. Configuration de la page
st.set_page_config(page_title="Strategist AI", page_icon="🚀", layout="wide")

# 2. Récupération de la clé API
openai.api_key = os.getenv("OPENAI_API_KEY")

# 3. Configuration du Code d'accès
MASTER_CODE = "palaiseau2026"

# Style CSS pour un rendu pro et épuré
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #00ff88; color: black; font-weight: bold; border: none; }
    .stTextArea>div>div>textarea { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Gestion de l'accès) ---
st.sidebar.title("🔐 Accès Client")
user_code = st.sidebar.text_input("Entre ton code d'accès :", type="password")

if user_code == MASTER_CODE:
    st.sidebar.success("Accès ILLIMITÉ activé ✅")
    is_premium = True
else:
    st.sidebar.info("Mode gratuit : limité à 50 mots.")
    is_premium = False

# --- ZONE PRINCIPALE ---
st.title("🚀 Strategist AI")
st.subheader("Expert en stratégie et pilotage de projets")

user_input = st.text_area("Colle ici la transcription ou le compte-rendu de ta réunion :", height=300, placeholder="Ex: Réunion de pilotage du 03/02...")

if st.button("Générer l'Analyse Stratégique"):
    if not openai.api_key:
        st.error("Erreur : La clé API OpenAI n'est pas configurée dans Railway.")
    elif not user_input:
        st.warning("Veuillez entrer du texte pour lancer l'analyse.")
    else:
        # Logique de limitation
        words = user_input.split()
        
        if is_premium:
            text_to_process = user_input
            limit_reached = False
        else:
            limit_reached = len(words) > 50
            text_to_process = " ".join(words[:50]) if limit_reached else user_input

        try:
            with st.spinner("Analyse stratégique en cours..."):
                # Utilisation de ton nouveau prompt ultra-complet
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": """Tu es un expert en stratégie et pilotage de projets ; 
                        à partir du compte rendu de réunion fourni, produis une synthèse exécutive courte (objectifs, décisions, points clés, risques), 
                        puis un plan d’action clair et opérationnel sous forme de tableau incluant actions concrètes, responsables, délais, priorités, KPI et statut, 
                        ajoute les points de vigilance, risques et dépendances, puis des recommandations stratégiques et prochaines étapes, 
                        sans inventer d’informations manquantes et avec un langage professionnel, structuré et orienté décision."""},
                        {"role": "user", "content": text_to_process}
                    ]
                )
                
                result = response.choices[0].message.content
                st.markdown("---")
                st.markdown("## 📊 Rapport de Pilotage")
                st.markdown(result)

                # Affichage du Paywall si besoin
                if limit_reached and not is_premium:
                    st.warning("⚠️ Limite de la version gratuite atteinte (50 mots).")
                    st.markdown("### 💎 Débloque l'analyse complète")
                    st.write("Pour traiter des réunions entières et obtenir le tableau de bord complet, passe à la version Pro.")
                    # LIEN STRIPE
                    st.markdown('[<button style="width:100%; height:50px; border-radius:10px; background-color:#6772E5; color:white; border:none; cursor:pointer; font-weight:bold;">S\'abonner pour 19€/mois</button>](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00)', unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")

st.markdown("---")
st.caption("Strategist AI - Solution de pilotage autonome")
