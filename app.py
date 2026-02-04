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

# Codes Railway
CODE_PRO = os.getenv("APP_ACCESS_CODE", "palaiseau2026")
CODE_PREMIUM = os.getenv("APP_PREMIUM_CODE", "palaiseau-pro")

# 2. FONCTION PDF QUALI (COULEURS ET STRUCTURE)
def create_pdf(data):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # En-tête avec couleur
        pdf.set_fill_color(31, 73, 125) # Bleu marine pro
        pdf.rect(0, 0, 210, 40, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', size=24)
        pdf.cell(190, 30, txt="RAPPORT STRATÉGIQUE", ln=True, align='C')
        
        # Retour au noir pour le contenu
        pdf.set_text_color(0, 0, 0)
        pdf.ln(20)
        
        # Fonction pour nettoyer le texte (enlève les résidus de JSON)
        def clean(text):
            t = str(text).replace('{', '').replace('}', '').replace("'", "").replace("[", "").replace("]", "")
            return t.encode('latin-1', 'replace').decode('latin-1')

        # SECTION SYNTHÈSE
        pdf.set_font("Arial", 'B', size=14)
        pdf.set_text_color(31, 73, 125)
        pdf.cell(190, 10, txt="I. SYNTHÈSE EXÉCUTIVE", ln=True)
        pdf.set_draw_color(31, 73, 125)
        pdf.line(10, pdf.get_y(), 60, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=11)
        synth = data.get('synthese', 'Analyse en cours...')
        pdf.multi_cell(190, 7, txt=clean(synth))
        
        # SECTION PLAN D'ACTION
        pdf.ln(10)
        pdf.set_font("Arial", 'B', size=14)
        pdf.set_text_color(31, 73, 125)
        pdf.cell(190, 10, txt="II. PLAN D'ACTION OPÉRATIONNEL", ln=True)
        pdf.line(10, pdf.get_y(), 85, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=10)
        actions = data.get('actions', [])
        for act in actions:
            if isinstance(act, dict):
                title = act.get('Action', 'Action')
                detail = f"Responsable: {act.get('Responsable', 'N/A')} | Délai: {act.get('Delai', 'N/A')}"
                pdf.set_font("Arial", 'B', size=10)
                pdf.multi_cell(190, 6, txt=f"> {clean(title)}")
                pdf.set_font("Arial", 'I', size=9)
                pdf.multi_cell(190, 5, txt=f"  {clean(detail)}")
                pdf.ln(2)
        
        # RECOMMANDATIONS
        pdf.ln(5)
        pdf.set_font("Arial", 'B', size=14)
        pdf.set_text_color(31, 73, 125)
        pdf.cell(190, 10, txt="III. RECOMMANDATIONS & VIGILANCE", ln=True)
        pdf.line(10, pdf.get_y(), 90, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=11)
        recos = data.get('recommandation', 'N/A')
        pdf.multi_cell(190, 7, txt=clean(recos))

        return bytes(pdf.output())
    except Exception as e:
        st.error(f"Erreur PDF : {e}")
        return None

# (Garder create_excel identique car tu as dit qu'il était bon)
def create_excel(actions_list):
    output = io.BytesIO()
    df = pd.DataFrame(actions_list)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Plan d Action')
    return output.getvalue()

# 3. INTERFACE (SIDEBAR ET LIENS STRIPE)
st.sidebar.title("🔐 Accès Strategist AI")
user_code = st.sidebar.text_input("Code d'accès :", type="password")

status = "Gratuit"
if user_code == CODE_PREMIUM: status = "Premium"
elif user_code == CODE_PRO: status = "Pro"

# Liens d'abonnement toujours visibles si non Premium
if status != "Premium":
    st.sidebar.markdown("---")
    st.sidebar.write("⭐ **Améliorer mon compte**")
    st.sidebar.markdown("[👉 Passer à 5€ (Pro)](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00)")
    st.sidebar.markdown("[🚀 Passer à 15€ (Premium)](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")

# 4. LOGIQUE PRINCIPALE
st.title("🚀 Strategist AI Pro")
user_input = st.text_area("Colle ta transcription ici :", height=250)

if st.button("Lancer l'Analyse Stratégique"):
    if user_input:
        # Prompt Ultra-Précis pour éviter le JSON brut dans le texte
        sys_prompt = (
            "Tu es un consultant expert. Produis un JSON pur. "
            "IMPORTANT : La valeur de 'synthese' et 'recommandation' doit être du texte rédigé proprement, "
            "sans accolades, sans listes techniques. 'actions' doit être une liste d'objets."
        )
        
        with st.spinner("Analyse en cours..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0
                )
                raw = response.choices[0].message.content.strip()
                if "```json" in raw: raw = raw.split("```json")[1].split("```")[0].strip()
                st.session_state['analyse_result'] = json.loads(raw)
            except Exception as e:
                st.error("Erreur de format IA. Réessaie.")

# 5. AFFICHAGE
if st.session_state['analyse_result']:
    res = st.session_state['analyse_result']
    st.divider()
    
    col_res, col_dl = st.columns([3, 1])
    with col_res:
        st.subheader("📝 Synthèse")
        st.write(res.get('synthese'))
    
    if status == "Premium":
        with col_dl:
            st.write("### 📥 Exports")
            pdf_b = create_pdf(res)
            st.download_button("📕 Rapport PDF Pro", pdf_b, "Rapport_Strategique.pdf", "application/pdf")
            st.download_button("📗 Tableau Excel", create_excel(res.get('actions', [])), "Plan_Action.xlsx")
    else:
        with col_dl:
            st.info("Exports réservés aux membres Premium.")
            st.markdown("[🚀 Passer Premium](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")

st.sidebar.markdown("---")
st.sidebar.markdown(f"[⚙️ Gérer mon abonnement](https://billing.stripe.com/p/login/aFafZg6mq35D9re8xncZa00)")
