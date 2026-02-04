import streamlit as st
import openai
import os
import json
import pandas as pd
import io
from fpdf import FPDF

# 1. CONFIGURATION
st.set_page_config(page_title="Strategist AI Pro", page_icon="🚀", layout="wide")
openai.api_key = os.getenv("OPENAI_API_KEY")

if 'analyse_result' not in st.session_state:
    st.session_state['analyse_result'] = None

CODE_PRO = os.getenv("APP_ACCESS_CODE", "palaiseau2026")
CODE_PREMIUM = os.getenv("APP_PREMIUM_CODE", "palaiseau-pro")

# 2. FONCTIONS DE GÉNÉRATION SÉCURISÉES (GESTION DÉFENSIVE)
def create_pdf(data):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(0, 10, txt="Rapport Strategist AI Pro", ln=True, align='C')
        
        pdf.set_font("Arial", 'B', size=12)
        pdf.ln(10)
        pdf.cell(0, 10, txt="SYNTHESE :", ln=True)
        pdf.set_font("Arial", size=10)
        
        # Sécurité : On force la conversion en string et on nettoie l'encodage
        synth = str(data.get('synthese', 'Synthèse non disponible.'))
        pdf.multi_cell(0, 8, txt=synth.encode('latin-1', 'replace').decode('latin-1'))
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 10, txt="PLAN D'ACTION :", ln=True)
        pdf.set_font("Arial", size=10)
        
        actions = data.get('actions', [])
        if not isinstance(actions, list): actions = [str(actions)]
        
        for action in actions:
            # Sécurité pour l'erreur "string indices must be integers"
            if isinstance(action, dict):
                txt = f"- {action.get('Action', 'Action')} | Responsable: {action.get('Responsable', 'N/A')}"
            else:
                txt = f"- {str(action)}"
            pdf.multi_cell(0, 7, txt=txt.encode('latin-1', 'replace').decode('latin-1'))
            
        return bytes(pdf.output())
    except Exception as e:
        st.error(f"Erreur technique PDF : {e}")
        return None

def create_excel(actions_list):
    try:
        output = io.BytesIO()
        # On s'assure que c'est une liste de dictionnaires pour Pandas
        data_to_df = actions_list if isinstance(actions_list, list) else [{"Actions": str(actions_list)}]
        df = pd.DataFrame(data_to_df)
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Plan d Action')
        return output.getvalue()
    except Exception:
        return None

# 3. SIDEBAR
st.sidebar.title("🔐 Accès Strategist AI")
user_code = st.sidebar.text_input("Code d'accès :", type="password", key="pwd_input")

status = "Gratuit"
if user_code == CODE_PREMIUM: status = "Premium"
elif user_code == CODE_PRO: status = "Pro"

# 4. INTERFACE & LOGIQUE
st.title("🚀 Strategist AI Pro")
user_input = st.text_area("Colle ta transcription ici :", height=200, key="main_text")

if st.button("Lancer l'Analyse Stratégique", key="go_btn"):
    if user_input:
        text_to_process = user_input
        if status == "Gratuit" and len(user_input.split()) > 50:
            st.error("Limite 50 mots en gratuit.")
            st.markdown("[👉 Version PRO (5€)](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00)")
            st.markdown("[💎 Version PREMIUM (15€)](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")
            text_to_process = " ".join(user_input.split()[:50])

        with st.spinner("Analyse..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Expert Stratégie. Réponds UNIQUEMENT en JSON. Structure: {'synthese': '', 'actions': [{'Action': '', 'Responsable': ''}], 'risques': [], 'recommandation': ''}"},
                        {"role": "user", "content": text_to_process}
                    ],
                    temperature=0
                )
                raw = response.choices[0].message.content.strip()
                if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
                st.session_state['analyse_result'] = json.loads(raw)
            except Exception as e:
                st.error(f"L'IA a envoyé un format invalide. Réessaie avec un texte plus clair.")

# 5. RÉSULTATS
if st.session_state['analyse_result']:
    res = st.session_state['analyse_result']
    st.divider()
    st.write("### 📝 Synthèse")
    st.write(res.get('synthese', ''))
    
    st.write("### 📊 Plan d'Action")
    actions = res.get('actions', [])
    if actions:
        st.table(pd.DataFrame(actions) if isinstance(actions, list) else pd.DataFrame([{"Données": str(actions)}]))
    
    if status == "Premium":
        c1, c2 = st.columns(2)
        with c1:
            pdf_file = create_pdf(res)
            if pdf_file: st.download_button("📥 PDF", pdf_file, "rapport.pdf", key="dl_pdf")
        with c2:
            xls_file = create_excel(actions)
            if xls_file: st.download_button("📊 Excel", xls_file, "plan.xlsx", key="dl_xls")

st.sidebar.markdown("---")
st.sidebar.markdown(f"[⚙️ Gérer mon abonnement](https://billing.stripe.com/p/login/aFafZg6mq35D9re8xncZa00)")
