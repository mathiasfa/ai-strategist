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

# Codes d'accès (à configurer dans Railway)
CODE_PRO = os.getenv("APP_ACCESS_CODE", "palaiseau2026")
CODE_PREMIUM = os.getenv("APP_PREMIUM_CODE", "palaiseaupro")

# 2. FONCTIONS DE GÉNÉRATION
def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=16)
    pdf.cell(200, 10, txt="Rapport Strategist AI Pro", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"SYNTHÈSE :\n{data['synthese']}".encode('latin-1', 'replace').decode('latin-1'))
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, txt="PLAN D'ACTION :", ln=True)
    pdf.set_font("Arial", size=10)
    for action in data['actions']:
        line = f"- {action['Action']} (Responsable: {action['Responsable']}, Délai: {action['Delai']})"
        pdf.multi_cell(0, 8, txt=line.encode('latin-1', 'replace').decode('latin-1'))
    
    return bytes(pdf.output())

def create_excel(actions_list):
    output = io.BytesIO()
    df_actions = pd.DataFrame(actions_list)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_actions.to_excel(writer, index=False, sheet_name='Plan d Action')
    return output.getvalue()

# 3. SIDEBAR ET ACCÈS
st.sidebar.title("🔐 Accès Strategist AI")
user_code = st.sidebar.text_input("Entre ton code d'accès :", type="password")

status = "Gratuit"
if user_code == CODE_PREMIUM:
    status = "Premium"
    st.sidebar.success("🚀 ACCÈS PREMIUM (Illimité + PDF + Excel)")
elif user_code == CODE_PRO:
    status = "PRO"
    st.sidebar.info("✅ ACCÈS PRO (Illimité)")

# 4. INTERFACE PRINCIPALE
st.title("🚀 Strategist AI Pro")
st.subheader("Transforme tes réunions en résultats concrets")

user_input = st.text_area("Colle ici la transcription de ta réunion :", height=250)

if st.button("Lancer l'Analyse Stratégique"):
    if not user_input:
        st.warning("Veuillez coller un texte.")
    else:
        # Restriction mode gratuit
        if status == "Gratuit" and len(user_input.split()) > 50:
            st.error("Version gratuite limitée à 50 mots.")
            st.markdown("[👉 Passer à 5€ (PRO)](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00)")
            st.markdown("[💎 Passer à 15€ (Premium + Exports)](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")
            text_to_process = " ".join(user_input.split()[:50])
        else:
            text_to_process = user_input

        with st.spinner("L'IA analyse et structure les données..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": """Tu es un expert en stratégie. 
                        Réponds UNIQUEMENT en format JSON :
                        {
                          "synthese": "Texte court",
                          "actions": [{"Action": "...", "Responsable": "...", "Delai": "...", "KPI": "..."}],
                          "risques": ["...", "..."],
                          "recommandation": "..."
                        }"""},
                        {"role": "user", "content": text_to_process}
                    ]
                )
                
                data = json.loads(response.choices[0].message.content)
                
                # Affichage des résultats
                st.success("Analyse terminée !")
                st.markdown(f"### 📝 Synthèse\n{data['synthese']}")
                
                st.markdown("### 📊 Plan d'Action")
                df = pd.DataFrame(data["actions"])
                st.table(df)
                
                # EXPORTS PREMIUM
                if status == "Premium":
                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        pdf_data = create_pdf(data)
                        st.download_button("📥 Télécharger PDF", pdf_data, "rapport.pdf", "application/pdf")
                    with col2:
                        excel_data = create_excel(data["actions"])
                        st.download_button("📊 Télécharger Excel", excel_data, "plan.xlsx", "application/vnd.ms-excel")
                elif status == "PRO":
                    st.info("💡 L'export PDF/Excel est réservé aux membres Premium.")

            except Exception as e:
                st.error(f"Erreur lors de l'analyse : {e}")

# Gestion Compte
st.sidebar.markdown("---")
st.sidebar.markdown(f"[Gérer mon abonnement](https://billing.stripe.com/p/login/aFafZg6mq35D9re8xncZa00)")
