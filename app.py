import streamlit as st
import openai
import os
from fpdf import FPDF

# 1. Configuration
st.set_page_config(page_title="Strategist AI Pro", page_icon="🚀", layout="wide")
openai.api_key = os.getenv("OPENAI_API_KEY")

# 2. Codes d'accès (à configurer dans Railway)
CODE_PRO = os.getenv("APP_ACCESS_CODE", "palaiseau2026")
CODE_PREMIUM = os.getenv("APP_PREMIUM_CODE", "palaiseaupro")

# --- FONCTION PDF CORRIGÉE ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # On utilise encode('latin-1', 'replace').decode('latin-1') 
    # pour éviter les crashs sur les caractères bizarres
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 10, txt=clean_text)
    
    # Avec fpdf2, output() sans argument renvoie directement les bytes
    return pdf.output()

# --- SIDEBAR ---
st.sidebar.title("🔐 Accès Strategist AI")
user_code = st.sidebar.text_input("Entre ton code d'accès :", type="password")

status = "Gratuit"
if user_code == CODE_PREMIUM:
    status = "Premium"
    st.sidebar.success("🚀 ACCÈS PREMIUM (Illimité + PDF)")
elif user_code == CODE_PRO:
    status = "PRO"
    st.sidebar.info("✅ ACCÈS PRO (Illimité)")

# --- INTERFACE ---
st.title("🚀 Strategist AI Pro")
st.subheader("L'IA qui pilote vos projets")

user_input = st.text_area(" transcription de réunion :", height=250)

if st.button("Lancer l'Analyse"):
    if not user_input:
        st.warning("Texte manquant.")
    else:
        # Logique de limitation pour les gratuits
        if status == "Gratuit" and len(user_input.split()) > 50:
            st.error("Version gratuite limitée à 50 mots.")
            st.markdown("[👉 Passer à 5€ (PRO)](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00)")
            st.markdown("[💎 Passer à 15€ (Premium + PDF)](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")
            text_to_process = " ".join(user_input.split()[:50])
        else:
            text_to_process = user_input

        with st.spinner("Analyse en cours..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "Expert en stratégie. Produis une synthèse exécutive et un plan d'action structuré."},
                          {"role": "user", "content": text_to_process}]
            )
            result = response.choices[0].message.content
            st.markdown(result)

            # --- OPTION PREMIUM : EXPORT PDF ---
            if status == "Premium":
                pdf_data = create_pdf(result)
                st.download_button(label="📥 Télécharger le Plan d'Action (PDF)", 
                                   data=pdf_data, 
                                   file_name="plan_daction_strategist_ai.pdf", 
                                   mime="application/pdf")
            elif status == "PRO":
                st.success("Analyse terminée. L'export PDF est réservé aux membres Premium.")

st.sidebar.markdown("---")
st.sidebar.markdown(f"[Gérer mon abonnement](https://billing.stripe.com/p/login/aFafZg6mq35D9re8xncZa00)")


