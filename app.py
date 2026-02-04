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

# 2. FONCTION PDF (MISE EN PAGE RÉPARÉE)
def create_pdf(data):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # En-tête Premium
        pdf.set_fill_color(31, 73, 125)
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', size=22)
        pdf.cell(190, 30, txt="RAPPORT STRATÉGIQUE PROFESSIONNEL", ln=True, align='C')
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln(20)
        
        def clean(text):
            return str(text).encode('latin-1', 'replace').decode('latin-1')

        # I. SYNTHÈSE
        pdf.set_font("Arial", 'B', size=14)
        pdf.set_text_color(31, 73, 125)
        pdf.cell(190, 10, txt="I. SYNTHÈSE EXÉCUTIVE", ln=True)
        pdf.ln(2)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(190, 7, txt=clean(data.get('synthese', 'N/A')))
        
        # II. PLAN D'ACTION (REFAIT)
        pdf.ln(10)
        pdf.set_font("Arial", 'B', size=14)
        pdf.set_text_color(31, 73, 125)
        pdf.cell(190, 10, txt="II. PLAN D'ACTION OPÉRATIONNEL", ln=True)
        pdf.ln(2)
        
        pdf.set_text_color(0, 0, 0)
        actions = data.get('actions', [])
        for act in actions:
            pdf.set_font("Arial", 'B', size=11)
            # On récupère les infos avec des valeurs par défaut pour éviter le vide
            desc = act.get('Action', act.get('action', 'Action sans titre'))
            resp = act.get('Responsable', act.get('responsable', 'Non assigné'))
            delai = act.get('Delai', act.get('date', 'À définir'))
            
            pdf.multi_cell(190, 7, txt=f"• {clean(desc)}")
            pdf.set_font("Arial", 'I', size=10)
            pdf.cell(190, 6, txt=f"  Responsable: {clean(resp)} | Délai: {clean(delai)}", ln=True)
            pdf.ln(2)
            
        return bytes(pdf.output())
    except Exception as e:
        st.error(f"Erreur PDF : {e}")
        return None

# 3. FONCTION EXCEL (COMPLÈTE)
def create_excel(actions_list):
    output = io.BytesIO()
    # On force la conversion en DataFrame et on remplit les vides par "N/A"
    df = pd.DataFrame(actions_list).fillna("À préciser")
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Plan d Action')
    return output.getvalue()

# 4. SIDEBAR (FIX MESSAGE PREMIUM)
st.sidebar.title("🔐 Accès Strategist AI")
user_code = st.sidebar.text_input("Entre ton code d'accès :", type="password")

status = "Gratuit"
if user_code == CODE_PREMIUM:
    status = "Premium"
    st.sidebar.success("💎 COMPTE PREMIUM : TOUTES FONCTIONS OK")
elif user_code == CODE_PRO:
    status = "Pro"
    st.sidebar.info("✅ COMPTE PRO : ANALYSE ILLIMITÉE")
else:
    st.sidebar.warning("Mode Gratuit : Limité")

# 5. LOGIQUE PRINCIPALE
st.title("🚀 Strategist AI Pro")
user_input = st.text_area("Colle ta transcription ici :", height=250)

if st.button("Lancer l'Analyse Stratégique"):
    if user_input:
        # Prompt corrigé pour l'IA
        prompt = (
            "Tu es un expert en stratégie. Analyse ce texte et fournis un JSON avec : "
            "1) 'synthese': un texte rédigé. "
            "2) 'actions': une liste d'objets avec 'Action', 'Responsable', 'Delai', 'KPI'. "
            "Remplis TOUTES les cases pour chaque action, ne laisse rien de vide."
        )
        
        with st.spinner("Analyse en cours..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": prompt}, {"role": "user", "content": user_input}],
                    temperature=0
                )
                raw = response.choices[0].message.content.strip()
                if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
                st.session_state['analyse_result'] = json.loads(raw)
            except Exception as e:
                st.error("Erreur de format. Réessaie.")

# 6. AFFICHAGE ET EXPORTS
if st.session_state['analyse_result']:
    res = st.session_state['analyse_result']
    st.divider()
    
    st.subheader("📝 Synthèse")
    st.write(res.get('synthese'))
    
    if status == "Premium":
        st.subheader("📊 Plan d'Action & Exports")
        st.table(pd.DataFrame(res.get('actions', [])).fillna("-"))
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📕 Rapport PDF Premium", create_pdf(res), "Rapport_Strategique.pdf", "application/pdf")
        with c2:
            st.download_button("📗 Tableau Excel Complet", create_excel(res.get('actions', [])), "Plan_Action.xlsx")
    else:
        st.info("Exports PDF/Excel réservés au Premium.")
        st.markdown("[🚀 Passer Premium](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")

st.sidebar.markdown("---")
st.sidebar.markdown(f"[⚙️ Gérer l'abonnement](https://billing.stripe.com/p/login/aFafZg6mq35D9re8xncZa00)")
