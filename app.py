import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Team Brisa", page_icon="🌊")

def get_data():
    try:
        return st.connection("gsheets", type=GSheetsConnection).read(worksheet="Usuarios", ttl=0)
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🌊 Login Team Brisa")
    with st.form("l"):
        u = st.text_input("Usuário").strip().lower()
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("ENTRAR"):
            df = get_data()
            if df is not None:
                user = df[(df['Usuario'].str.lower() == u) & (df['Senha'].astype(str) == str(p))]
                if not user.empty:
                    st.session_state.auth = True
                    st.session_state.user = user.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Incorreto")
else:
    u = st.session_state.user
    st.sidebar.title(f"Oi, {u['Nome']}")
    if st.sidebar.button("Sair"):
        st.session_state.auth = False
        st.rerun()

    st.title(f"Painel {u['Funcao'].upper()}")
    
    if u['Funcao'] == 'gestor':
        st.success("Acesso Gestor Liberado")
        # Futuros gráficos aqui
    else:
        st.info("Área Operacional")
