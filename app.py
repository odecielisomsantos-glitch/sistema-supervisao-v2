import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configurações de Página e Estética Profissional
st.set_page_config(page_title="Team Brisa | Acesso", page_icon="🌊", layout="centered")

st.markdown("""
    <style>
    /* Reset de UI para visual limpo e profissional */
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #0b101a; font-family: 'Inter', sans-serif; }
    
    /* Centralização e Estilo do Card */
    div[data-testid="stForm"] { 
        background: #161b22; padding: 40px; border-radius: 12px; 
        border: 1px solid #30363d; box-shadow: 0 15px 35px rgba(0,0,0,0.5); 
    }
    
    /* Input com foco e contraste elevado */
    input { background-color: #0d1117 !important; color: #fff !important; border: 1px solid #30363d !important; }
    label { color: #8b949e !important; font-size: 14px !important; }

    /* BOTÃO COM CONTROLE DE COR (VERDE DE ALTA VISIBILIDADE) */
    div.stButton > button { 
        width: 100%; background: #238636 !important; color: white !important; 
        font-weight: 700; height: 48px; border: none; border-radius: 6px; 
        margin-top: 15px; cursor: pointer;
    }
    div.stButton > button:hover { background: #2ea043 !important; }
    </style>
""", unsafe_allow_html=True)

def carregar_usuarios():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # ttl=0 garante que ele leia a planilha AGORA, sem usar memória antiga
        df = conn.read(worksheet="Usuarios", ttl=0).astype(str)
        # Normalização total para evitar erro de "Incorreto"
        df['Usuario'] = df['Usuario'].str.strip().str.lower()
        df['Senha'] = df['Senha'].str.strip()
        return df
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([0.1, 1, 0.1])
    with col:
        st.markdown("<h2 style='text-align:center; color:white; margin-bottom:25px;'>Portal Team Brisa</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u_in = st.text_input("Usuário").strip().lower()
            p_in = st.text_input("Senha", type="password").strip()
            
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                df = carregar_usuarios()
                if df is not None:
                    # Comparação blindada contra erros de digitação na planilha
                    user = df[(df['Usuario'] == u_in) & (df['Senha'] == p_in)]
                    if not user.empty:
                        st.session_state.auth, st.session_state.user = True, user.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Usuário ou senha não conferem.")
                else: st.error("Erro ao ler banco de dados.")
else:
    # Área interna após login bem sucedido
    u = st.session_state.user
    st.sidebar.title(f"Olá, {u['Nome']}")
    if st.sidebar.button("Sair"): 
        st.session_state.auth = False
        st.rerun()
    
    st.title(f"Painel de {u['Funcao'].title()}")
    st.success(f"Acesso autorizado para: {u['Nome']}")
