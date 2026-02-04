import streamlit as st
import openai
import os
import json
import pandas as pd
import io
from fpdf import FPDF

# 1. CONFIGURATION & MÉMOIRE
st.set_page_config(page_title="Strategist AI Pro", page_icon="🚀", layout="wide")
openai.api_key = os.getenv("OPENAI_API_KEY")

if 'analyse_result' not in st.session_state:
    st.session_state['analyse_result'] = None

# Codes d'accès Railway
CODE_PRO = os.getenv("APP_ACCESS_CODE", "palaiseau2026")
CODE_PREMIUM = os.getenv("APP_PREMIUM_CODE", "palaiseau-pro")

# 2. FONCTIONS DE GÉNÉRATION SÉCURISÉES
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=16)
    pdf.cell(0, 10, txt="Rapport Strategist AI Pro", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', size=12)
    pdf.ln(10)
    pdf.cell(0, 10, txt="SYNTHESE :", ln=True)
    pdf.set_font("Arial", size=10)
    synth_text = str(data.get('synthese', 'Pas de synthèse disponible.'))
    pdf.multi_cell(0, 8, txt=synth_text.encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, txt="PLAN D'ACTION :", ln=True)
    pdf.set_font("Arial", size=10)
    
    actions = data.get('actions', [])
    for action in actions:
        if isinstance(action, dict):
            nom = action.get('Action', 'Action inconnue')
            resp = action.get('Responsable', 'N/A')
            txt = f"- {nom} | Responsable: {resp}"
        else:
            txt = f"- {str(action)}"
        pdf.multi_cell(0, 7, txt=txt.encode('latin-1', 'replace').decode('latin-1'))
    
    return bytes(pdf.output())

def create_excel(actions_list):
    output = io.BytesIO()
    if isinstance(actions_list, list):
        df = pd.DataFrame(actions_list)
    else:
        df = pd.DataFrame([{"Données": str(actions_list)}])
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Plan d Action')
    return output.getvalue()

# 3. SIDEBAR & ACCÈS
st.sidebar.title("🔐 Accès Strategist AI")
user_code = st.sidebar.text_input("Entre ton code d'accès :", type="password", key="access_pwd")

status = "Gratuit"
if user_code == CODE_PREMIUM:
    status = "Premium"
    st.sidebar.success("💎 ACCÈS PREMIUM (Illimité + Exports)")
elif user_code == CODE_PRO:
    status = "Pro"
    st.sidebar.info("✅ ACCÈS PRO (Illimité)")

# 4. INTERFACE PRINCIPALE
st.title("🚀 Strategist AI Pro")
st.subheader("Transforme tes réunions en résultats concrets")

user_input = st.text_area("Colle ici la transcription de ta réunion :", height=250, key="txt_input")

if st.button("Lancer l'Analyse Stratégique", key="main_analyse_btn"):
    if not user_input:
        st.warning("Veuillez coller un texte.")
    else:
        text_to_process = user_input
        # Limitation mode gratuit
        if status == "Gratuit" and len(user_input.split()) > 50:
            st.error("Version gratuite limitée à 50 mots.")
            st.markdown("[👉 Passer à 5€ (Pro)](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00)")
            st.markdown("[💎 Passer à 15€ (Premium + Exports)](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")
            text_to_process = " ".join(user_input.split()[:50])

        with st.spinner("Analyse stratégique en cours..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Expert stratégie. Réponds UNIQUEMENT en JSON avec 'synthese', 'actions' (liste d'objets), 'risques', 'recommandation'."},
                        {"role": "user", "content": text_to_process}
                    ],
                    temperature=0
                )
                raw = response.choices[0].message.content.strip()
                if raw.startswith("```json"): raw = raw.replace("```json", "").replace("```", "").strip()
                st.session_state['analyse_result'] = json.loads(raw)
            except Exception as e:
                st.error(f"Erreur d'analyse : {e}")

# 5. AFFICHAGE DES RÉSULTATS
if st.session_state['analyse_result'] is not None:
    res = st.session_state['analyse_result']
    st.divider()
    st.write("### 📝 Synthèse")
    st.write(res.get('synthese', ''))
    
    st.write("### 📊 Plan d'Action")
    actions_data = res.get('actions', [])
    if actions_data:
        st.table(pd.DataFrame(actions_data))
    
    if status == "Premium":
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 Télécharger PDF", create_pdf(res), "rapport.pdf", "application/pdf", key="pdf_dl")
        with c2:
            st.download_button("📊 Télécharger Excel", create_excel(actions_data), "plan.xlsx", "application/vnd.ms-excel", key="xls_dl")
    elif status == "Pro":
        st.info("💡 L'export PDF/Excel est réservé aux membres Premium à 15€.")

# 6. GESTION COMPTE & ANNULATION
st.sidebar.markdown("---")
st.sidebar.markdown("[⚙️ Gérer mon abonnement](https://billing.stripe.com/p/login/aFafZg6mq35D9re8xncZa00)")
