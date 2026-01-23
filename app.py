import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Team Brisa", page_icon="🌊")

def get_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # Forçamos o Pandas a ler tudo como string (texto) na importação
        df = conn.read(worksheet="Usuarios", ttl=0).astype(str)
        # Limpeza total: remove espaços extras e padroniza para minúsculas no Usuario
        df['Usuario'] = df['Usuario'].str.strip().str.lower()
        df['Senha'] = df['Senha'].str.strip()
        return df
    except Exception as e:
        st.error(f"Erro de leitura: {e}")
        return None

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🌊 Login Team Brisa")
    with st.form("l"):
        u_input = st.text_input("Usuário").strip().lower()
        p_input = st.text_input("Senha", type="password").strip()
        if st.form_submit_button("ENTRAR"):
            df = get_data()
            if df is not None and not df.empty:
                # Verificação exata
                user_match = df[(df['Usuario'] == u_input) & (df['Senha'] == p_input)]
                if not user_match.empty:
                    st.session_state.auth = True
                    st.session_state.user = user_match.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("Usuário ou Senha Incorretos")
            else:
                st.warning("Banco de dados vazio ou inacessível.")
else:
    u = st.session_state.user
    st.sidebar.title(f"Oi, {u['Nome']}")
    if st.sidebar.button("Sair"):
        st.session_state.auth = False
        st.rerun()

    # ÁREA DO DASHBOARD / OPERACIONAL
    st.title(f"Painel {u['Funcao'].upper()}")
    st.write(f"Bem-vindo(a), **{u['Nome']}**!")
    
    if u['Funcao'] == 'gestor':
        st.success("Visualização de Gestão Ativada.")
        # O código do seu Dashboard entrará aqui
    else:
        st.info("Área de Lançamentos Operacionais.")
        # O código dos seus formulários entrará aqui
