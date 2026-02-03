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
def create_excel(actions_list):
    output = io.BytesIO()
    df_actions = pd.DataFrame(actions_list)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_actions.to_excel(writer, index=False, sheet_name='Plan d Action')
    return output.getvalue()

def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    # Titre
    pdf.set_font("Arial", 'B', size=16)
    pdf.cell(0, 10, txt="Rapport Strategist AI Pro", ln=True, align='C')
    
    # Synthèse
    pdf.set_font("Arial", 'B', size=12)
    pdf.ln(10)
    pdf.cell(0, 10, txt="SYNTHESE :", ln=True)
    pdf.set_font("Arial", size=10)
    # Le '0' ici dit au PDF d'utiliser toute la largeur de la page
    pdf.multi_cell(0, 8, txt=data['synthese'].encode('latin-1', 'replace').decode('latin-1'))
    
    # Actions
    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, txt="PLAN D'ACTION :", ln=True)
    pdf.set_font("Arial", size=10)
    
    for action in data['actions']:
        # On construit une phrase simple par action pour éviter les débordements de tableau
        txt_action = f"• {action['Action']} | Responsable: {action['Responsable']} | Delai: {action['Delai']} | KPI: {action['KPI']}"
        pdf.multi_cell(0, 7, txt=txt_action.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(2)
    
    # Risques
    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(0, 10, txt="RISQUES IDENTIFIES :", ln=True)
    pdf.set_font("Arial", size=10)
    for risque in data['risques']:
        pdf.cell(0, 8, txt=f"- {risque}".encode('latin-1', 'replace').decode('latin-1'), ln=True)

    return bytes(pdf.output())

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
                        {"role": "system", "content": "Tu es un expert en stratégie. Tu réponds EXCLUSIVEMENT par un objet JSON sans aucun texte avant ou après."},
                        {"role": "user", "content": f"Analyse cette réunion et fournis un JSON avec les clés 'synthese', 'actions', 'risques' et 'recommandation'. Les 'actions' doivent être une liste d'objets avec 'Action', 'Responsable', 'Delai', 'KPI'. Voici le texte : {text_to_process}"}
                    ],
                    temperature=0 # On met la température à 0 pour qu'elle soit plus stricte
                )
                
                raw_content = response.choices[0].message.content.strip()
                
                # Petit hack pour nettoyer si l'IA met des balises ```json ... ```
                if raw_content.startswith("```json"):
                    raw_content = raw_content.replace("```json", "").replace("```", "").strip()
                
                data = json.loads(raw_content)
                
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




