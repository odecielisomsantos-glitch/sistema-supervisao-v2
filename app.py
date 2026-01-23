import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. CONFIGURAÇÃO DE TEMA E INTERFACE
st.set_page_config(page_title="Team Brisa | Gestão", page_icon="🌊", layout="centered")

st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #0b0f19; font-family: 'Inter', sans-serif; }
    div[data-testid="stForm"] { background: #161b22; padding: 40px; border-radius: 12px; border: 1px solid #30363d; }
    input { background-color: #0d1117 !important; color: white !important; border: 1px solid #30363d !important; }
    div.stButton > button { 
        width: 100%; background: #238636 !important; color: white !important; 
        font-weight: bold; height: 45px; border-radius: 6px; border: none;
    }
    .ranking-card { background: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. FUNÇÃO DE CONEXÃO MULTI-ABA
def get_sheet_data(aba, range_alvo=None):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Se range_alvo for definido, ele pega apenas aquele pedaço (ex: A2:B24)
        df = conn.read(worksheet=aba, ttl=0, header=None)
        if aba == "Usuarios":
            df = df.iloc[1:].copy() # Remove cabeçalho apenas para login
        return df
    except Exception as e:
        st.error(f"Erro na aba {aba}: {e}")
        return None

# 3. SISTEMA DE AUTENTICAÇÃO
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([0.1, 1, 0.1])
    with col:
        st.markdown("<h2 style='text-align:center; color:white;'>Portal Team Brisa</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u_in = st.text_input("Usuário").strip().lower()
            p_in = st.text_input("Senha", type="password").strip()
            if st.form_submit_button("ENTRAR"):
                df_user = get_sheet_data("Usuarios")
                if df_user is not None:
                    # 0=Usuario, 1=Senha, 2=Nome, 3=Funcao 
                    user_match = df_user[(df_user[0].astype(str).str.lower() == u_in) & (df_user[1].astype(str) == p_in)]
                    if not user_match.empty:
                        st.session_state.auth = True
                        st.session_state.user = {"Nome": user_match.iloc[0][2], "Funcao": user_match.iloc[0][3].lower()}
                        st.rerun()
                    else: st.error("Dados incorretos.")
else:
    # 4. DASHBOARD DO GESTOR - RANKING TAM
    u = st.session_state.user
    st.sidebar.title(f"🌊 {u['Nome']}")
    if st.sidebar.button("Sair"):
        st.session_state.auth = False
        st.rerun()

    if u['Funcao'] == 'gestor':
        st.title("🏆 Painel do Gestor")
        st.subheader("Ranking TAM")
        
        # Busca os dados da equipe na página DADOS-DIA 
        df_equipe = get_sheet_data("DADOS-DIA")
        
        if df_equipe is not None:
            # Filtra o intervalo A2:B24 (considerando que header=None, A2 é índice 1)
            # Coluna 0 (A) = Nome do Agente, Coluna 1 (B) = Valor TAM 
            ranking = df_equipe.iloc[1:24, [0, 1]] 
            ranking.columns = ["Colaborador", "TAM"]
            
            # Exibição Profissional em Tabela Minimalista
            st.dataframe(ranking, use_container_width=True, hide_index=True)
            
            # Destaque para o Top 1
            top_1 = ranking.iloc[0]
            st.info(f"🥇 Destaque do Dia: **{top_1['Colaborador']}** com TAM de **{top_1['TAM']}**")
    else:
        st.title("🚀 Área do Operador")
        st.write("Bem-vindo ao sistema de registros.")
