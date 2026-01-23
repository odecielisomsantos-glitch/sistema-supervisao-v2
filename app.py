import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Layout centralizado e remoção de elementos padrão
st.set_page_config(page_title="Team Brisa | Portal", page_icon="🌊", layout="centered")

# CSS Avançado: Cores Profissionais, Fontes e Visibilidade
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    /* Remove a linha branca superior e o menu padrão */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background: #0b0f19; font-family: 'Inter', sans-serif; }
    
    /* Card de Login */
    div[data-testid="stForm"] {
        background: #161b22; padding: 50px; border-radius: 12px;
        border: 1px solid #30363d; box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }
    
    /* Inputs Estilizados */
    input { background-color: #0d1117 !important; color: #e6edf3 !important; border: 1px solid #30363d !important; border-radius: 6px !important; height: 45px !important; }
    label { color: #8b949e !important; font-weight: 600 !important; }
    
    /* BOTÃO DE ALTA VISIBILIDADE (VERDE ESMERALDA) */
    div.stButton > button {
        width: 100%; background: #238636 !important; color: white !important;
        border: none !important; height: 50px !important; border-radius: 6px !important;
        font-size: 16px !important; font-weight: 600 !important; margin-top: 20px !important;
    }
    div.stButton > button:hover { background: #2ea043 !important; border: none !important; }
    
    /* Mensagens de Erro */
    div[data-testid="stNotification"] { border-radius: 8px !important; background: #2a1215 !important; color: #ff7b72 !important; }
    </style>
""", unsafe_allow_html=True)

def get_db():
    try: return st.connection("gsheets", type=GSheetsConnection).read(worksheet="Usuarios", ttl=0).astype(str)
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([0.1, 1, 0.1])
    with col:
        st.markdown("<h1 style='text-align:center; color:white; font-size:40px; margin-bottom:0;'>🌊</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; color:white; margin-top:10px; font-weight:600;'>Portal do Usuário</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#8b949e; margin-bottom:30px;'>Team Brisa - Gestão Inteligente</p>", unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Usuário ou CPF").strip().lower()
            p = st.text_input("Senha", type="password").strip()
            st.markdown("<div style='text-align:right;'><a href='#' style='color:#2ea043; text-decoration:none; font-size:12px;'>Esqueceu sua senha?</a></div>", unsafe_allow_html=True)
            
            if st.form_submit_button("ENTRAR NO PORTAL"):
                df = get_db()
                if df is not None:
                    df['Usuario'] = df['Usuario'].str.strip().str.lower()
                    user = df[(df['Usuario'] == u) & (df['Senha'].str.strip() == p)]
                    if not user.empty:
                        st.session_state.auth, st.session_state.user = True, user.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Acesso Negado: Credenciais incorretas.")
        
        st.markdown("<p style='text-align:center; color:#8b949e; font-size:14px; margin-top:30px;'>Ainda não tem acesso? <span style='color:#2ea043;'>Contate o Admin</span></p>", unsafe_allow_html=True)

else:
    u = st.session_state.user
    st.sidebar.markdown(f"### Olá, {u['Nome']}")
    if st.sidebar.button("Sair do Sistema"): 
        st.session_state.auth = False
        st.rerun()
    st.title(f"Dashboard {u['Funcao'].capitalize()}")
    st.success(f"Logado como: {u['Nome']}")
