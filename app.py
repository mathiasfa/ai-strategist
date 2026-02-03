import streamlit as st
import openai
import os

# Configuration de la page
st.set_page_config(page_title="Strategist AI - Optimisez vos réunions", page_icon="🚀")

# Style CSS pour rendre l'app plus pro
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .pay-button { background-color: #28a745 !important; color: white !important; font-weight: bold; text-decoration: none; padding: 10px; border-radius: 5px; display: block; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Strategist AI")
st.subheader("Transformez vos paroles en actions concrètes")

# Récupération de la clé API depuis Railway
openai.api_key = os.getenv("OPENAI_API_KEY")
stripe_link = "https://buy.stripe.com/aFafZg6mq35D9re8xncZa00"

# Interface de saisie
text_input = st.text_area("Collez la transcription de votre réunion (Zoom, Teams, Mobile...) :", height=250)

# Logique de limitation
if text_input:
    word_count = len(text_input.split())
    
    if word_count > 50:
        st.info(f"📏 Longueur détectée : {word_count} mots.")
        st.warning("⚠️ La version gratuite est limitée aux 50 premiers mots. Pour analyser l'intégralité de votre document et générer un plan d'action complet :")
        st.markdown(f'<a href="{stripe_link}" target="_blank" class="pay-button">🔓 Débloquer la version PRO (19€/mois)</a>', unsafe_allow_html=True)
        
        # On ne traite que le début pour la démo
        text_to_process = " ".join(text_input.split()[:50])
    else:
        text_to_process = text_input

    if st.button("Lancer l'analyse intelligente"):
        with st.spinner('Analyse par Strategist AI en cours...'):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Tu es un expert en management. Produit un compte-rendu ultra-structuré : 1. Résumé Exécutif, 2. Décisions Clés, 3. To-Do List par personne."},
                        {"role": "user", "content": text_to_process}
                    ]
                )
                st.markdown("---")
                st.markdown("### 📄 Résultat de l'analyse")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error("Configuration en cours... Revenez dans quelques minutes.")

else:
    st.write("💡 *Astuce : Copiez-collez le texte brut de votre enregistrement mobile ou de votre logiciel de visio.*")

# Sidebar infos
st.sidebar.title("À propos")
st.sidebar.info("Strategist AI aide les managers et les entrepreneurs à ne plus perdre de temps en rédaction de comptes-rendus.")
