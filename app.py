import streamlit as st
import openai
import os

# 1. Configuration de la page
st.set_page_config(page_title="Strategist AI", page_icon="🚀")

# 2. Récupération de la clé API
openai.api_key = os.getenv("OPENAI_API_KEY")

# 3. Configuration du Code d'accès (Ton "Passphrase")
MASTER_CODE = "palaiseau2026"  # Change ce code quand tu veux sur GitHub

# Style CSS
st.markdown("""
    <style>
    .main { text-align: center; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #00ff88; color: black; font-weight: bold; }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e7bcf,#2e7bcf); color: white; }
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
st.subheader("Transforme tes réunions en plans d'action")

user_input = st.text_area("Colle ici la transcription de ta réunion :", height=250)

if st.button("Générer le Plan d'Action"):
    if not openai.api_key:
        st.error("Erreur : La clé API OpenAI n'est pas configurée dans Railway.")
    elif not user_input:
        st.warning("Veuillez entrer du texte.")
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
            with st.spinner("L'IA analyse ta réunion..."):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Tu es un expert en stratégie et pilotage de projets ; à partir du compte rendu de réunion fourni, produis une synthèse exécutive courte (objectifs, décisions, points clés, risques), puis un plan d’action clair et opérationnel sous forme de tableau incluant actions concrètes, responsables, délais, priorités, KPI et statut, ajoute les points de vigilance, risques et dépendances, puis des recommandations stratégiques et prochaines étapes, sans inventer d’informations manquantes et avec un langage professionnel, structuré et orienté décision."
                        {"role": "user", "content": text_to_process}
                    ]
                )
                result = response.choices[0].message.content
                st.markdown("### ✅ Ton Plan d'Action :")
                st.write(result)

                # Affichage du Paywall si non-premium et limite atteinte
                if limit_reached and not is_premium:
                    st.warning("⚠️ Limite de 50 mots atteinte.")
                    st.markdown("### 💎 Débloque la version illimitée")
                    st.write("Obtiens ton code d'accès instantanément après paiement.")
                    # REMPLACE PAR TON LIEN STRIPE CI-DESSOUS
                    st.markdown('[<button style="width:100%; height:50px; border-radius:10px; background-color:#6772E5; color:white; border:none; cursor:pointer; font-weight:bold;">S\'abonner pour 19€/mois</button>](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00)', unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Erreur : {e}")

st.markdown("---")
st.caption("Propulsé par Strategist AI - Mathias")


