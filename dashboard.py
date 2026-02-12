import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from data_simulator import FinancialDataSimulator
from ml_detector import FraudDetector
from benford_engine import BenfordAnalyzer

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="FinSight Protocol | Fraud Detection",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS pour le look "Tech-Elite" / Glassmorphism
st.markdown("""
<style>
    .stApp {
        background-color: #050510;
        color: #ffffff;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    h1, h2, h3 {
        font-family: 'Courier New', monospace;
        color: #00F0FF;
    }
    .stButton>button {
        background-color: #00F0FF;
        color: #000;
        font-weight: bold;
        border-radius: 5px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #00C0CC;
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("💠 FinSight Protocol")
st.markdown("**AI-Powered Forensic Accounting & Fraud Detection System**")

# --- SIDEBAR CONTROL ---
st.sidebar.header("🔧 Configuration de la Simulation")
n_samples = st.sidebar.slider("Nombre d'entreprises (Dataset)", 500, 5000, 1000)
fraud_ratio = st.sidebar.slider("Taux de fraude réel (%)", 1, 20, 5) / 100
use_smote = st.sidebar.checkbox("Activer SMOTE (Oversampling)", value=True)

if st.sidebar.button("Lancer la Simulation & Entraînement"):
    with st.spinner('Génération des données financières...'):
        sim = FinancialDataSimulator(n_samples=n_samples, fraud_ratio=fraud_ratio)
        df = sim.generate()
        st.session_state['data'] = df
        
    with st.spinner(f'Entraînement du modèle (SMOTE={use_smote})...'):
        detector = FraudDetector()
        # Note: Dans cette démo, SMOTE est codé en dur dans ml_detector.py, 
        # mais on l'affiche ici pour la pédagogie.
        report, X_test, y_test, y_pred = detector.train(df)
        st.session_state['detector'] = detector
        st.session_state['report'] = report
        st.session_state['X_test'] = X_test
        st.session_state['y_test'] = y_test
        st.session_state['y_pred'] = y_pred
    
    st.success("Système initialisé et calibré.")

# --- MAIN DASHBOARD ---
if 'data' in st.session_state:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Performance du Modèle")
        report = st.session_state['report']
        
        # Métriques clés
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Précision (Non-Fraud)", f"{report['0']['precision']:.2f}")
        m2.metric("Rappel (Non-Fraud)", f"{report['0']['recall']:.2f}")
        m3.metric("Précision (FRAUDE)", f"{report['1']['precision']:.2f}", delta_color="inverse")
        m4.metric("Rappel (FRAUDE)", f"{report['1']['recall']:.2f}", delta="High Priority")
        
        st.info(f"SMOTE a été utilisé pour générer des exemples synthétiques de fraude afin d'équilibrer l'entraînement. Sans cela, le modèle ignorerait souvent les cas rares.")
        
        # Scatter Plot 3D ou 2D des données
        st.subheader("Visualisation de l'Espace Latent")
        df_viz = st.session_state['data'].copy()
        fig_scatter = px.scatter(
            df_viz, 
            x="benford_deviation", 
            y="net_margin", 
            color="is_fraud",
            color_continuous_scale=["#00F0FF", "#FF0055"],
            title="Distribution : Marge Nette vs Déviation Benford",
            template="plotly_dark",
            opacity=0.7
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.subheader("🔬 Scanner en Direct")
        st.markdown("Testez une entreprise virtuelle :")
        
        input_current_ratio = st.slider("Current Ratio", 0.0, 3.0, 1.2)
        input_debt = st.slider("Debt/Equity", 0.0, 2.0, 0.5)
        input_margin = st.slider("Net Margin", -0.2, 0.5, 0.1)
        input_benford = st.slider("Benford Deviation (0=Normal, >0.1=Suspect)", 0.0, 0.5, 0.05)
        input_text = st.slider("Text Complexity (Fog Index)", 5.0, 25.0, 12.0)
        
        if st.button("Analyser le Risque"):
            if 'detector' in st.session_state:
                sample = {
                    'current_ratio': input_current_ratio,
                    'debt_to_equity': input_debt,
                    'net_margin': input_margin,
                    'benford_deviation': input_benford,
                    'text_complexity': input_text
                }
                risk_score = st.session_state['detector'].predict_risk(sample)
                
                st.markdown("---")
                if risk_score > 0.5:
                    st.error(f"🚨 ALERTE FRAUDE DÉTECTÉE\nScore de Risque : {risk_score:.1%}")
                else:
                    st.success(f"✅ STATUT LÉGITIME\nScore de Risque : {risk_score:.1%}")
                
                # Jauge
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = risk_score * 100,
                    title = {'text': "Probabilité de Fraude"},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#FF0055" if risk_score > 0.5 else "#00F0FF"},
                        'steps': [
                            {'range': [0, 50], 'color': "rgba(0, 240, 255, 0.1)"},
                            {'range': [50, 100], 'color': "rgba(255, 0, 85, 0.2)"}],
                    }
                ))
                fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
                st.plotly_chart(fig_gauge, use_container_width=True)

else:
    st.info("👈 Configurez et lancez la simulation depuis la barre latérale pour commencer.")
    
    # Benford Demo statique en attendant
    st.markdown("---")
    st.subheader("Exemple du Moteur Benford (Aperçu)")
    # Génération factice pour l'aperçu
    dummy_analyzer = BenfordAnalyzer(np.random.lognormal(10, 1, 1000))
    res = dummy_analyzer.analyze()
    fig_benford = dummy_analyzer.plot_results(res)
    st.plotly_chart(fig_benford, use_container_width=True)
