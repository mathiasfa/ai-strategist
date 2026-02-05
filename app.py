import streamlit as st
import openai
import os
import json
import pandas as pd
import io

# 1. CONFIGURATION
st.set_page_config(page_title="Strategist AI Pro", page_icon="🚀", layout="wide")
openai.api_key = os.getenv("OPENAI_API_KEY")

if 'analyse_result' not in st.session_state:
    st.session_state['analyse_result'] = None

CODE_PRO = os.getenv("APP_ACCESS_CODE", "palaiseau2026")
CODE_PREMIUM = os.getenv("APP_PREMIUM_CODE", "palaiseau-pro")

# 2. FONCTION EXCEL (BOOSTÉE)
def create_excel(actions_list):
    output = io.BytesIO()
    # On s'assure que c'est une liste et on remplace les valeurs manquantes
    df = pd.DataFrame(actions_list)
    # Force l'ordre des colonnes pour un rendu pro
    cols = ['Action', 'Responsable', 'Delai', 'Priorite', 'KPI', 'Statut']
    # On n'ajoute que les colonnes qui existent vraiment dans le retour IA
    existing_cols = [c for c in cols if c in df.columns]
    df = df[existing_cols].fillna("À définir")
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Plan d Action')
    return output.getvalue()

# 3. SIDEBAR & ACCÈS (AVEC MANAGEMENT VISUEL)
st.sidebar.title("🔐 Accès Strategist AI")
user_code = st.sidebar.text_input("Entre ton code d'accès :", type="password", key="access_pwd")

# Logique de Badge Visuel
if user_code == CODE_PREMIUM:
    status = "Premium"
    st.sidebar.markdown("""
        <div style="background-color:#1f497d; padding:15px; border-radius:10px; border:2px solid #ffd700; text-align:center;">
            <h2 style="color:white; margin:0;">💎 PREMIUM</h2>
            <p style="color:#ffd700; margin:0; font-weight:bold;">Accès Illimité + Exports Excel</p>
        </div>
        """, unsafe_allow_html=True)
    st.sidebar.success("✅ Identité vérifiée : Bienvenue Mathias.")

elif user_code == CODE_PRO:
    status = "Pro"
    st.sidebar.markdown("""
        <div style="background-color:#2e7d32; padding:15px; border-radius:10px; text-align:center;">
            <h2 style="color:white; margin:0;">✅ VERSION PRO</h2>
            <p style="color:#e8f5e9; margin:0;">Analyses Illimitées activées</p>
        </div>
        """, unsafe_allow_html=True)

else:
    status = "Gratuit"
    st.sidebar.markdown("""
        <div style="background-color:#f5f5f5; padding:15px; border-radius:10px; border:1px solid #ccc; text-align:center;">
            <h2 style="color:#333; margin:0;">⚪ GRATUIT</h2>
            <p style="color:#666; margin:0;">Version de démonstration</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    st.sidebar.write("🚀 **Débloquer la puissance :**")
    st.sidebar.markdown(f"[👉 Passer à 5€ (Pro)](https://buy.stripe.com/aFafZg6mq35D9re8xncZa00)")
    st.sidebar.markdown(f"[💎 Passer à 15€ (Premium)](https://buy.stripe.com/7sY6oG3aegWtgTGeVLcZa01)")

# 4. INTERFACE PRINCIPALE
st.title("🚀 Strategist AI Pro")
st.markdown("---")

user_input = st.text_area("Colle ta transcription de réunion ici :", height=250, placeholder="Ex: Compte-rendu d'audit QSE à Palaiseau...")

if st.button("Lancer l'Analyse Stratégique", key="main_btn"):
    if not user_input:
        st.warning("Le champ est vide.")
    else:
        # Prompt corrigé pour une réponse web structurée
        prompt = (
            "Tu es un expert en stratégie. Analyse ce texte et fournis un JSON pur avec : "
            "1) 'synthese': un beau résumé structuré. "
            "2) 'actions': une liste d'objets avec 'Action', 'Responsable', 'Delai', 'Priorite', 'KPI', 'Statut'. "
            "3) 'recommandations': texte libre sur les points de vigilance. "
            "Remplis TOUTES les infos pour chaque action."
        )
        
        with st.spinner("Analyse experte en cours..."):
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
                st.error("Désolé, l'IA a eu un problème de format. Réessaie avec un texte plus court ou plus clair.")

# 5. AFFICHAGE DES RÉSULTATS (STYLE QUALI)
if st.session_state['analyse_result']:
    res = st.session_state['analyse_result']
    
    with st.expander("📝 SYNTHÈSE EXÉCUTIVE", expanded=True):
        st.write(res.get('synthese'))
    
    with st.expander("📊 PLAN D'ACTION DÉTAILLÉ", expanded=True):
        actions = res.get('actions', [])
        df_display = pd.DataFrame(actions).fillna("-")
        st.dataframe(df_display, use_container_width=True)
        
        if status == "Premium":
            st.download_button(
                label="📥 Télécharger le Plan d'Action (Excel)",
                data=create_excel(actions),
                file_name="Plan_Action_StrategistAI.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_excel"
            )
        else:
            st.info("💡 L'export Excel est réservé aux membres Premium.")

    with st.expander("💡 RECOMMANDATIONS & POINTS DE VIGILANCE", expanded=True):
        st.write(res.get('recommandations', res.get('recommandation', 'N/A')))

# 6. BAS DE PAGE
st.sidebar.markdown("---")
st.sidebar.markdown(f"[⚙️ Gérer mon abonnement](https://billing.stripe.com/p/login/aFafZg6mq35D9re8xncZa00)")
