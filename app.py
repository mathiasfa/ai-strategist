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

CODE_PRO = os.getenv("APP_ACCESS_CODE", "palaiseau2026")
CODE_PREMIUM = os.getenv("APP_PREMIUM_CODE", "palaiseau-pro")

# 2. FONCTIONS DE GÉNÉRATION (SÉCURISÉES)
def create_pdf(data):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', size=16)
        pdf.cell(190, 10, txt="Rapport Strategist AI Pro", ln=True, align='C')
        
        # Synthèse
        pdf.set_font("Arial", 'B', size=12)
        pdf.ln(10)
        pdf.cell(190, 10, txt="SYNTHESE EXECUTIVE :", ln=True)
        pdf.set_font("Arial", size=10)
        synth = str(data.get('synthese', 'Aucune synthèse générée.'))
        pdf.multi_cell(190, 8, txt=synth.encode('latin-1', 'replace').decode('latin-1'))
        
        # Plan d'action
        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(190, 10, txt="PLAN D'ACTION OPERATIONNEL :", ln=True)
        pdf.set_font("Arial", size=10)
        
        actions = data.get('actions', [])
        if isinstance(actions, list) and len(actions) > 0:
            for action in actions:
                if isinstance(action, dict):
                    txt = f"- {action.get('Action', 'Action')}: Resp: {action.get('Responsable', 'N/A')} | Délai: {action.get('Delai', 'N/A')} | KPI: {action.get('KPI', 'N/A')}"
                else:
                    txt = f"- {str(action)}"
                pdf.multi_cell(190, 7, txt=txt.encode('latin-1', 'replace').decode('latin-1'))
        else:
            pdf.cell(190, 10, txt="Aucune action identifiée.", ln=True)

        # Recommandations
        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=12)
        pdf.cell(190, 10, txt="RECOMMANDATIONS & VIGILANCE :", ln=True)
        pdf.set_font("Arial", size=10)
        recos = str(data.get('recommandation', 'N/A'))
        pdf.multi_cell(190, 7, txt=recos.encode('latin-1', 'replace').decode('latin-1'))
            
        return bytes(pdf.output())
    except Exception as e:
        st.error(f"Erreur PDF : {e}")
        return None

def create_excel(actions_list):
    try:
        output = io.BytesIO()
        df = pd.DataFrame(actions_list) if (isinstance(actions_list, list) and len(actions_list) > 0) else pd.DataFrame([{"Info": "Aucune action trouvée"}])
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Plan d Action')
        return output.getvalue()
    except Exception as e:
        st.error(f"Erreur Excel : {e}")
        return None

# 3. SIDEBAR & STATUT
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
    st.sidebar.warning("Mode Gratuit (Limité)")

# 4. INTERFACE PRINCIPALE
st.title("🚀 Strategist AI Pro")
user_input = st.text_area("Colle la transcription ou le compte-rendu ici :", height=250, key="main_txt")

if st.button("Lancer l'Analyse Stratégique", key="btn_go"):
    if not user_input:
        st.warning("Veuillez coller un texte.")
    else:
        # Gestion des liens business si gratuit
        if status == "Gratuit" and len(user_input.split()) > 50:
            st.error("Limite version gratuite : 50 mots.")
            st.markdown("### 💎 Débloquez la puissance totale :")
            st.markdown("- [👉 Passer à 5€ (Accès Pro)](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00)")
            st.markdown("- [🚀 Passer à 15€ (Premium + Exports PDF/Excel)](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")
            text_to_process = " ".join(user_input.split()[:50])
        else:
            text_to_process = user_input

        with st.spinner("Analyse stratégique en cours..."):
            try:
                # TON PROMPT EXPERT INTÉGRÉ ICI
                prompt_expert = (
                    "Tu es un expert en stratégie et pilotage de projets ; à partir du compte rendu de réunion fourni, "
                    "produis une synthèse exécutive courte (objectifs, décisions, points clés, risques), "
                    "puis un plan d’action clair et opérationnel sous forme de tableau JSON incluant les clés : "
                    "'synthese', 'actions' (liste avec Action, Responsable, Delai, Priorite, KPI, Statut), "
                    "'risques', 'recommandation'. Ne réponds qu'en JSON pur."
                )
                
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": prompt_expert},
                        {"role": "user", "content": text_to_process}
                    ],
                    temperature=0
                )
                raw = response.choices[0].message.content.strip()
                if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
                st.session_state['analyse_result'] = json.loads(raw)
            except Exception as e:
                st.error(f"Erreur d'analyse. Assurez-vous que le texte est clair.")

# 5. AFFICHAGE ET EXPORTS
if st.session_state['analyse_result']:
    res = st.session_state['analyse_result']
    st.divider()
    st.subheader("📝 Synthèse Exécutive")
    st.write(res.get('synthese', 'N/A'))
    
    st.subheader("📊 Plan d'Action Opérationnel")
    actions = res.get('actions', [])
    if actions:
        st.table(pd.DataFrame(actions))
    
    if status == "Premium":
        c1, c2 = st.columns(2)
        with c1:
            pdf_b = create_pdf(res)
            if pdf_b: st.download_button("📥 Télécharger PDF Pro", pdf_b, "Rapport_Strategique.pdf", key="dl_p")
        with c2:
            excel_b = create_excel(actions)
            if excel_b: st.download_button("📊 Télécharger Tableau Excel", excel_b, "Plan_Action.xlsx", key="dl_x")
    else:
        st.info("💡 Les exports PDF et Excel sont réservés aux membres Premium.")
        st.markdown("[🚀 Passer Premium pour télécharger les rapports](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")

# 6. PORTAIL CLIENT
st.sidebar.markdown("---")
st.sidebar.markdown(f"[⚙️ Gérer mon abonnement](https://billing.stripe.com/p/login/aFafZg6mq35D9re8xncZa00)")
