import streamlit as st
import openai

# Configuration de la page
st.set_page_config(page_title="AI Strategist - Compte-rendu Express", layout="centered")

st.title("🚀 AI Strategist : Transformez vos réunions en actions")
st.subheader("Gagnez 1h par réunion")

# Récupération de la clé API de manière sécurisée
api_key = st.text_input("Entrez votre clé API OpenAI pour activer l'IA", type="password")

if api_key:
    openai.api_key = api_key
    
    # Zone de saisie
    text_input = st.text_area("Collez la transcription de votre réunion ici :", height=300)
    
    if st.button("Générer le rapport stratégique"):
        if text_input:
            with st.spinner('Analyse en cours...'):
                # Mon "Prompt" optimisé pour un résultat pro
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Tu es un expert en management et stratégie d'entreprise."},
                        {"role": "user", "content": f"Analyse ce texte et fais-en un compte-rendu structuré avec : 1/ Résumé exécutif, 2/ Décisions prises, 3/ Liste des actions (To-Do) par personne, 4/ Prochaine étape.\n\nTexte : {text_input}"}
                    ]
                )
                
                result = response.choices[0].message.content
                st.markdown("---")
                st.markdown(result)
                
                # Option de téléchargement
                st.download_button("Télécharger le rapport", result, file_name="compte_rendu.txt")
        else:
            st.warning("Veuillez entrer du texte.")