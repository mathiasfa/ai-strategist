import streamlit as st
import openai
import os
import json
import pandas as pd
import io
from PyPDF2 import PdfReader # Nouvelle bibliothèque pour lire les PDF

# 1. CONFIGURATION
st.set_page_config(page_title="Strategist AI Pro", page_icon="🚀", layout="wide")
openai.api_key = os.getenv("OPENAI_API_KEY")

if 'analyse_result' not in st.session_state:
    st.session_state['analyse_result'] = None

CODE_PRO = os.getenv("APP_ACCESS_CODE", "palaiseau2026")
CODE_PREMIUM = os.getenv("APP_PREMIUM_CODE", "palaiseau-pro")

# 2. FONCTIONS (EXCEL & PDF)
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
    """Extrait le texte de chaque page du PDF."""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Erreur lors de la lecture du PDF : {e}")
        return None

# 3. SIDEBAR (MANAGEMENT VISUEL)
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

# 4. INTERFACE PRINCIPALE
st.title("🚀 Strategist AI Pro")
st.markdown("---")

# Zone de Glisser-Déposer PDF
st.subheader("📁 Étape 1 : Charger le document")
uploaded_file = st.file_uploader("Glisse ton compte-rendu PDF ici (Audit, Réunion, QSE...)", type="pdf")

# Zone de texte (optionnelle)
st.subheader("⌨️ Ou colle le texte manuellement")
manual_input = st.text_area("Si tu n'as pas de PDF :", height=150, placeholder="Ex: Compte-rendu d'audit à Palaiseau...")

# Bouton de lancement
if st.button("Lancer l'Analyse Stratégique", key="main_btn"):
    content_to_analyze = ""
    
    # Priorité au PDF s'il existe
    if uploaded_file is not None:
        with st.spinner("Extraction du texte du PDF..."):
            content_to_analyze = extract_text_from_pdf(uploaded_file)
    elif manual_input:
        content_to_analyze = manual_input
    
    if not content_to_analyze:
        st.warning("Veuillez charger un PDF ou coller du texte.")
    else:
        prompt = (
            "Tu es un expert en stratégie QSE. Analyse ce texte et fournis un JSON pur avec : "
            "1) 'synthese': un beau résumé structuré. "
            "2) 'actions': une liste d'objets avec 'Action', 'Responsable', 'Delai', 'Priorite', 'KPI', 'Statut'. "
            "3) 'recommandations': points de vigilance. "
            "Sois précis sur les délais et responsables mentionnés."
        )
        
        with st.spinner("Analyse experte du document en cours..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": content_to_analyze}],
                    temperature=0
                )
                raw = response.choices[0].message.content.strip()
                if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
                st.session_state['analyse_result'] = json.loads(raw)
                st.success("Analyse terminée !")
            except Exception as e:
                st.error("L'IA a eu un souci avec le contenu du PDF. Vérifie que le PDF contient bien du texte (pas seulement des images).")

# 5. AFFICHAGE DES RÉSULTATS
if st.session_state['analyse_result']:
    res = st.session_state['analyse_result']
    
    with st.expander("📝 SYNTHÈSE EXÉCUTIVE", expanded=True):
        st.write(res.get('synthese'))
    
    with st.expander("📊 PLAN D'ACTION DÉTAILLÉ", expanded=True):
        actions = res.get('actions', [])
        st.dataframe(pd.DataFrame(actions).fillna("-"), use_container_width=True)
        
        if status == "Premium":
            st.download_button(
                label="📥 Télécharger le Plan d'Action (Excel)",
                data=create_excel(actions),
                file_name="Plan_Action_StrategistAI.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    with st.expander("💡 RECOMMANDATIONS", expanded=True):
        st.write(res.get('recommandations'))
