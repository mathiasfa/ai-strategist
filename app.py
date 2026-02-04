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

# 2. FONCTIONS DE GÉNÉRATION (VERSION BLINDÉE)
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
        
        # Sécurité : on remplace les caractères problématiques et on limite la largeur
        synth = str(data.get('synthese', ''))
        pdf.multi_cell(190, 8, txt=synth.encode('latin-1', 'replace').decode('latin-1'))
        
        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(0, 10, txt="PLAN D'ACTION :", ln=True)
        pdf.set_font("Arial", size=10)
        
        actions = data.get('actions', [])
        for action in actions:
            if isinstance(action, dict):
                nom = action.get('Action', 'Action')
                resp = action.get('Responsable', 'N/A')
                txt = f"- {nom} (Responsable: {resp})"
            else:
                txt = f"- {str(action)}"
            # Correction : on fixe la largeur à 190mm pour éviter l'erreur d'espace
            pdf.multi_cell(190, 7, txt=txt.encode('latin-1', 'replace').decode('latin-1'))
            
        return bytes(pdf.output())
    except Exception as e:
        return None

def create_excel(actions_list):
    output = io.BytesIO()
    df = pd.DataFrame(actions_list) if isinstance(actions_list, list) else pd.DataFrame([{"Data": str(actions_list)}])
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Plan d Action')
    return output.getvalue()

# 3. SIDEBAR & ACCÈS (CORRIGÉ POUR LE MESSAGE PREMIUM)
st.sidebar.title("🔐 Accès Strategist AI")
user_code = st.sidebar.text_input("Entre ton code d'accès :", type="password", key="access_pwd")

status = "Gratuit"
if user_code == CODE_PREMIUM:
    status = "Premium"
    st.sidebar.success("💎 ACCÈS PREMIUM ACTIVÉ")
elif user_code == CODE_PRO:
    status = "Pro"
    st.sidebar.info("✅ ACCÈS PRO ACTIVÉ")
else:
    st.sidebar.warning("Mode Gratuit limité")

# 4. INTERFACE
st.title("🚀 Strategist AI Pro")
user_input = st.text_area("Colle ta transcription ici :", height=200, key="main_txt")

if st.button("Lancer l'Analyse Stratégique", key="btn_go"):
    if user_input:
        with st.spinner("Analyse en cours..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Réponds EXCLUSIVEMENT en JSON."},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0
                )
                raw = response.choices[0].message.content.strip()
                if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
                st.session_state['analyse_result'] = json.loads(raw)
            except Exception as e:
                st.error("L'IA a fait une erreur de format. Réessaie.")

# 5. RÉSULTATS & EXPORTS
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
            if pdf_file:
                st.download_button("📥 Télécharger PDF", pdf_file, "rapport.pdf", key="dl_p")
            else:
                st.error("Erreur de génération PDF")
        with c2:
            st.download_button("📊 Télécharger Excel", create_excel(actions), "plan.xlsx", key="dl_x")
    elif status == "Pro":
        st.info("💡 Version Pro : Passage en Premium requis pour les exports.")
        st.markdown("[💎 Devenir Premium](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")

# 6. GESTION
st.sidebar.markdown("---")
st.sidebar.markdown(f"[⚙️ Gérer mon abonnement](https://billing.stripe.com/p/login/aFafZg6mq35D9re8xncZa00)")
