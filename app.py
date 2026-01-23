import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração com Layout Centralizado
st.set_page_config(page_title="Team Brisa | Login", page_icon="🌊", layout="centered")

# CSS Personalizado para Visual Profissional e Minimalista
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
    }
    .main { background-color: #ffffff; padding: 30px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    div[data-testid="stForm"] { border: none !important; padding: 0; }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(worksheet=aba, ttl=0)
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    # Container centralizado para o login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='text-align: center; color: #1c1c1c;'>TEAM BRISA</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6c757d;'>Portal de Acesso Seguro</p>", unsafe_allow_html=True)
        st.write("---")
        
        with st.form("login_form"):
            u_in = st.text_input("Usuário").strip().lower()
            p_in = st.text_input("Senha", type="password").strip()
            
            st.write("") # Espaçamento
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                df = get_data("Usuarios")
                if df is not None:
                    df = df.astype(str)
                    user = df[(df['Usuario'].str.lower() == u_in) & (df['Senha'] == p_in)]
                    if not user.empty:
                        st.session_state.auth = True
                        st.session_state.user = user.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Credenciais inválidas. Tente novamente.")
                else: st.error("Erro técnico: Banco de dados inacessível.")
        
        st.markdown("<p style='text-align: center; font-size: 12px; color: #adb5bd; margin-top: 50px;'>© 2026 Team Brisa Tecnologia</p>", unsafe_allow_html=True)

else:
    # Interface do Sistema após o login
    u = st.session_state.user
    st.sidebar.title("🌊 MENU")
    st.sidebar.write(f"Conectado: **{u['Nome']}**")
    if st.sidebar.button("Encerrar Sessão"):
        st.session_state.auth = False
        st.rerun()

    st.title(f"Painel de Controle: {u['Funcao'].capitalize()}")
    st.info(f"Bem-vindo de volta, {u['Nome']}!")

    # Exemplo de conteúdo minimalista baseado na função
    if u['Funcao'] == 'gestor':
        st.subheader("Indicadores de Hoje")
        kpi1, kpi2 = st.columns(2)
        kpi1.metric("Status da Rede", "Ativa", "100%")
        kpi2.metric("Chamados Pendentes", "4", "-2")
    else:
        st.subheader("Suas Atividades")
        st.button("Iniciar Novo Registro")
