import streamlit as st
import openai
import os
import json
import pandas as pd
import io
from PyPDF2 import PdfReader

# 1. CONFIGURATION
st.set_page_config(page_title="Strategist AI Pro", page_icon="🚀", layout="wide")
openai.api_key = os.getenv("OPENAI_API_KEY")

if 'analyse_result' not in st.session_state:
    st.session_state['analyse_result'] = None

CODE_PRO = os.getenv("APP_ACCESS_CODE", "palaiseau2026")
CODE_PREMIUM = os.getenv("APP_PREMIUM_CODE", "palaiseau-pro")

# 2. FONCTIONS
def create_excel(actions_list):
    output = io.BytesIO()
    df = pd.DataFrame(actions_list)
    cols = ['Action', 'Responsable', 'Delai', 'Priorite', 'KPI', 'Statut']
    existing_cols = [c for c in cols if c in df.columns]
    df = df[existing_cols].fillna("À définir")
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Plan d Action')
    return output.getvalue()

def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n"
        return text
    except Exception as e:
        st.error(f"Erreur lecture PDF : {e}")
        return None

# 3. SIDEBAR & LIENS STRIPE (RÉTABLIS)
st.sidebar.title("🔐 Accès Strategist AI")
user_code = st.sidebar.text_input("Entre ton code d'accès :", type="password", key="access_pwd")

if user_code == CODE_PREMIUM:
    status = "Premium"
    st.sidebar.markdown('<div style="background-color:#1f497d; padding:15px; border-radius:10px; border:2px solid #ffd700; text-align:center;"><h2 style="color:white; margin:0;">💎 PREMIUM</h2></div>', unsafe_allow_html=True)
    st.sidebar.success("✅ Bienvenue Mathias.")
elif user_code == CODE_PRO:
    status = "Pro"
    st.sidebar.markdown('<div style="background-color:#2e7d32; padding:15px; border-radius:10px; text-align:center;"><h2 style="color:white; margin:0;">✅ VERSION PRO</h2></div>', unsafe_allow_html=True)
else:
    status = "Gratuit"
    st.sidebar.info("Version de démonstration")
    st.sidebar.markdown("---")
    st.sidebar.write("🚀 **Débloquer la puissance :**")
    st.sidebar.markdown("[👉 Passer à 5€ (Pro)](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00)")
    st.sidebar.markdown("[💎 Passer à 15€ (Premium)](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")

# 4. INTERFACE PRINCIPALE
st.title("🚀 Strategist AI Pro")
st.markdown("---")

uploaded_file = st.file_uploader("📁 Dépose ton rapport PDF QSE ici", type="pdf")
manual_input = st.text_area("⌨️ Ou colle le texte ici :", height=150)

if st.button("Lancer l'Analyse Stratégique", key="main_btn"):
    content = ""
    if uploaded_file:
        content = extract_text_from_pdf(uploaded_file)
    elif manual_input:
        content = manual_input

    if not content or len(content.strip()) < 10:
        st.warning("Document vide ou illisible.")
    else:
        # PROMPT RENFORCÉ POUR LE TABLEAU
        prompt = (
           "Tu es un expert consultant en QSE et stratégie d'entreprise. Ton objectif est d'extraire une analyse EXHAUSTIVE du texte fourni.\n\n"
            "INSTRUCTIONS CRUCIALES :\n"
            "1. NE RÉSUME PAS grossièrement. Analyse chaque paragraphe.\n"
            "2. EXTRAIS TOUTES les actions correctives, les décisions prises et les missions évoquées.\n"
            "3. Si un responsable ou une date est mentionné, note-le. Sinon, mets 'À définir'.\n"
            "4. Structure ta réponse en JSON PUR avec :\n"
            "   - 'synthese': Un compte-rendu détaillé structuré par thématiques (ex: Sécurité, Environnement, Planning).\n"
            "   - 'actions': Une liste complète d'objets (Action, Responsable, Delai, Priorite, KPI, Statut).\n"
            "   - 'recommandations': Une analyse approfondie des risques et des opportunités.\n\n"
            "REMPLIS LE TABLEAU D'ACTIONS AVEC TOUS LES POINTS RELEVÉS, SANS EXCEPTION."
        )
        
        with st.spinner("Analyse en cours..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content}],
                    temperature=0.2 # Un peu de créativité pour ne pas rater d'actions
                )
                raw = response.choices[0].message.content.strip()
                if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
                
                parsed = json.loads(raw)
                st.session_state['analyse_result'] = parsed
                st.success("Analyse terminée !")
            except Exception as e:
                st.error(f"Erreur d'analyse : {e}")

# 5. AFFICHAGE DES RÉSULTATS
if st.session_state['analyse_result']:
    res = st.session_state['analyse_result']
    
    with st.expander("📝 SYNTHÈSE", expanded=True):
        st.write(res.get('synthese', 'Pas de synthèse disponible.'))
    
    with st.expander("📊 PLAN D'ACTION DÉTAILLÉ", expanded=True):
        actions_data = res.get('actions', [])
        if actions_data:
            df = pd.DataFrame(actions_data).fillna("-")
            st.dataframe(df, use_container_width=True)
            
            if status == "Premium":
                st.download_button("📥 Télécharger l'Excel", data=create_excel(actions_data), file_name="Plan_Action.xlsx")
        else:
            st.warning("L'IA n'a pas trouvé d'actions précises dans ce document.")

    with st.expander("💡 RECOMMANDATIONS", expanded=True):
        st.write(res.get('recommandations', 'N/A'))

# 6. BAS DE PAGE (LIEN GESTION RÉTABLI)
st.sidebar.markdown("---")
st.sidebar.markdown("[⚙️ Gérer mon abonnement](https://billing.stripe.com/p/login/aFafZg6mq35D9re8xncZa00)")

