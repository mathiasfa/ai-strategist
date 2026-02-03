import streamlit as st
import openai
import os

# 1. Configuration de la page
st.set_page_config(page_title="Strategist AI", page_icon="🚀")

# 2. Récupération de la clé API depuis les variables d'environnement Railway
openai.api_key = os.getenv("OPENAI_API_KEY")

# Style CSS pour un look pro
st.markdown("""
    <style>
    .main { text-align: center; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #00ff88; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Strategist AI")
st.subheader("Transforme tes réunions en plans d'action")

# 3. Zone de saisie
user_input = st.text_area("Colle ici la transcription de ta réunion (Zoom, Teams, etc.) :", height=250)

if st.button("Générer le Plan d'Action"):
    if not openai.api_key:
        st.error("La clé API OpenAI est manquante dans les variables Railway.")
    elif not user_input:
        st.warning("Veuillez entrer du texte pour commencer.")
    else:
        # 4. Logique du Paywall (Limite à 50 mots pour la version gratuite)
        words = user_input.split()
        is_limited = len(words) > 50
        
        text_to_process = " ".join(words[:50]) if is_limited else user_input

        try:
            with st.spinner("L'IA analyse ta réunion..."):
                # Utilisation de la syntaxe compatible openai==0.28
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Tu es un expert en stratégie et gestion de projet. Analyse le texte suivant et crée un compte-rendu structuré avec : 1. Résumé, 2. Décisions prises, 3. Liste de tâches (To-Do list) avec responsables."},
                        {"role": "user", "content": text_to_process}
                    ]
                )
                
                result = response.choices[0].message.content
                st.markdown("### ✅ Ton Plan d'Action :")
                st.write(result)

                # 5. Affichage du bouton Stripe si le texte était trop long
                if is_limited:
                    st.warning("⚠️ Tu as atteint la limite de la version gratuite (50 mots).")
                    st.markdown("### 💎 Débloque la puissance totale")
                    st.write("Pour analyser des réunions complètes sans limite, passe à la version Pro.")
                    # Remplace par ton vrai lien de paiement Stripe ci-dessous
                    st.markdown('[<button style="width:100%; height:50px; border-radius:10px; background-color:#6772E5; color:white; border:none; cursor:pointer; font-weight:bold;">S\'abonner pour 19€/mois</button>](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00)', unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Une erreur est survenue avec l'IA : {e}")

st.markdown("---")
st.caption("Propulsé par Strategist AI - Mathias")

