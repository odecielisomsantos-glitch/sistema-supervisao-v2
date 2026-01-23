import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Team Brisa", page_icon="🌊")

def get_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="Usuarios", ttl=0)
        # Limpeza de dados: remove espaços e padroniza tipos
        df['Usuario'] = df['Usuario'].astype(str).str.strip().str.lower()
        df['Senha'] = df['Senha'].astype(str).str.strip()
        return df
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🌊 Login Team Brisa")
    with st.form("l"):
        u = st.text_input("Usuário").strip().lower()
        p = st.text_input("Senha", type="password").strip()
        if st.form_submit_button("ENTRAR"):
            df = get_data()
            if df is not None:
                user = df[(df['Usuario'] == u) & (df['Senha'] == p)]
                if not user.empty:
                    st.session_state.auth = True
                    st.session_state.user = user.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Usuário ou Senha Incorretos")
            else: st.error("Erro ao conectar na Planilha")
else:
    u = st.session_state.user
    st.sidebar.title(f"Oi, {u['Nome']}")
    if st.sidebar.button("Sair"):
        st.session_state.auth = False
        st.rerun()

    st.title(f"Painel {u['Funcao'].upper()}")
    
    if u['Funcao'] == 'gestor':
        st.success(f"Bem-vindo Gestor {u['Nome']}! Seu painel está pronto.")
        # Espaço para futuros gráficos e dashboards
    else:
        st.info(f"Olá {u['Nome']}, você está na área operacional.")
        # Espaço para formulários de entrada de dados
