import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Team Brisa", page_icon="🌊")

def get_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Lendo sem cabeçalho para evitar erro de nome de coluna e limpando cache (ttl=0)
        df = conn.read(worksheet="Usuarios", ttl=0, header=None)
        
        # Remove a primeira linha (onde estão os títulos) e redefine os dados
        df = df.iloc[1:].copy()
        
        # Forçamos a conversão de todas as células para texto limpo
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🌊 Login Team Brisa")
    with st.form("l"):
        u_input = st.text_input("Usuário").strip().lower()
        p_input = st.text_input("Senha", type="password").strip()
        
        if st.form_submit_button("ENTRAR"):
            df = get_data()
            if df is not None:
                # Na sua planilha: Coluna 0=Usuario, 1=Senha, 2=Nome, 3=Funcao
                # Comparamos ignorando maiúsculas no usuário
                user_match = df[(df[0].str.lower() == u_input) & (df[1] == p_input)]
                
                if not user_match.empty:
                    st.session_state.auth = True
                    # Guardamos os dados em um formato fácil de usar
                    st.session_state.user = {
                        "Nome": user_match.iloc[0][2],
                        "Funcao": user_match.iloc[0][3]
                    }
                    st.rerun()
                else:
                    st.error("Dados incorretos. Verifique usuário e senha.")
else:
    u = st.session_state.user
    st.sidebar.title(f"Oi, {u['Nome']}")
    if st.sidebar.button("Sair"):
        st.session_state.auth = False
        st.rerun()

    st.title(f"Painel {u['Funcao'].upper()}")
    st.success(f"Logado com sucesso como {u['Nome']}!")
