import streamlit as st
import openai
import os
import json
import pandas as pd
import io
from fpdf import FPDF

# 1. CONFIGURATION
st.set_page_config(page_title="Strategist AI PRO", page_icon="🚀", layout="wide")
openai.api_key = os.getenv("OPENAI_API_KEY")

if 'analyse_result' not in st.session_state:
    st.session_state['analyse_result'] = None

CODE_PRO = os.getenv("APP_ACCESS_CODE", "palaiseau2026")
CODE_PREMIUM = os.getenv("APP_PREMIUM_CODE", "palaiseau-PRO")

# 2. FONCTIONS (SÉCURISÉES)
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=16)
    pdf.cell(0, 10, txt="Rapport Strategist AI PRO", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', size=12)
    pdf.ln(10)
    pdf.cell(0, 10, txt="SYNTHESE :", ln=True)
    pdf.set_font("Arial", size=10)
    clean_synth = data['synthese'].encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 8, txt=clean_synth)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, txt="PLAN D'ACTION :", ln=True)
    pdf.set_font("Arial", size=10)
    for action in data['actions']:
        txt_action = f"- {action['Action']} | Responsable: {action['Responsable']} | Delai: {action['Delai']}"
        clean_action = txt_action.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, txt=clean_action)
    
    return bytes(pdf.output())

def create_excel(actions_list):
    output = io.BytesIO()
    df_actions = pd.DataFrame(actions_list)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_actions.to_excel(writer, index=False, sheet_name='Plan d Action')
    return output.getvalue()

# 3. SIDEBAR
st.sidebar.title("🔐 Accès Strategist AI")
user_code = st.sidebar.text_input("Entre ton code d'accès :", type="password", key="access_input")

status = "Gratuit"
if user_code == CODE_PREMIUM:
    status = "Premium"
    st.sidebar.success("🚀 ACCÈS PREMIUM")
elif user_code == CODE_PRO:
    status = "PRO"
    st.sidebar.info("✅ ACCÈS PRO")

# 4. INTERFACE
st.title("🚀 Strategist AI PRO")
user_input = st.text_area("Colle ta transcription ici :", height=200, key="main_input")

if st.button("Lancer l'Analyse Stratégique", key="main_analyse_btn"):
    if not user_input:
        st.warning("Texte vide.")
    else:
        text_to_PROcess = user_input
        if status == "Gratuit" and len(user_input.split()) > 50:
            st.error("Limite version gratuite : 50 mots.")
            st.markdown("[👉 PRO (5€)](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00) | [💎 Premium (15€)](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")
            text_to_PROcess = " ".join(user_input.split()[:50])

        with st.spinner("Analyse en cours..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Réponds EXCLUSIVEMENT en JSON avec 'synthese', 'actions', 'risques', 'recommandation'."},
                        {"role": "user", "content": text_to_PROcess}
                    ],
                    temperature=0
                )
                raw = response.choices[0].message.content.strip()
                if raw.startswith("```json"): raw = raw.replace("```json", "").replace("```", "").strip()
                st.session_state['analyse_result'] = json.loads(raw)
            except Exception as e:
                st.error(f"Erreur : {e}")

# 5. AFFICHAGE ET EXPORTS (AVEC KEYS UNIQUES)
if st.session_state['analyse_result']:
    res = st.session_state['analyse_result']
    st.divider()
    st.subheader("📝 Synthèse")
    st.write(res['synthese'])
    
    st.subheader("📊 Plan d'Action")
    df_main = pd.DataFrame(res['actions'])
    st.table(df_main)
    
    if status == "Premium":
        c1, c2 = st.columns(2)
        with c1:
            pdf_b = create_pdf(res)
            st.download_button("📥 PDF", pdf_b, "rapport.pdf", "application/pdf", key="dl_pdf_premium")
        with c2:
            excel_b = create_excel(res['actions'])
            st.download_button("📊 Excel", excel_b, "plan.xlsx", "application/vnd.ms-excel", key="dl_excel_premium")

# 6. GESTION ABONNEMENT (LA LIGNE QUE TU CHERCHES)
st.sidebar.markdown("---")
st.sidebar.markdown(f"[⚙️ Gérer/Annuler mon abonnement](https://billing.stripe.com/p/login/aFafZg6mq35D9re8xncZa00)")
