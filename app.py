import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Layout centralizado e tema escuro via CSS
st.set_page_config(page_title="Team Brisa | Portal", page_icon="🌊", layout="centered")

st.markdown("""
    <style>
    .stApp { background: #0f172a; color: white; }
    div.stButton > button {
        width: 100%; background: #10b981; color: white; border: none;
        height: 3em; border-radius: 8px; font-weight: bold; transition: 0.3s;
    }
    div.stButton > button:hover { background: #059669; }
    div[data-testid="stForm"] {
        background: #1e293b; padding: 40px; border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3); border: none;
    }
    input { background-color: #334155 !important; color: white !important; border-radius: 8px !important; }
    label { color: #94a3b8 !important; }
    </style>
""", unsafe_allow_html=True)

def get_db():
    try: return st.connection("gsheets", type=GSheetsConnection).read(worksheet="Usuarios", ttl=0).astype(str)
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([0.2, 1, 0.2])
    with col:
        st.markdown("<h1 style='text-align:center; margin-bottom:0;'>🌊</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align:center; margin-top:0;'>Portal do Usuário</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748b;'>Team Brisa - Gestão Inteligente</p>", unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Usuário ou CPF").strip().lower()
            p = st.text_input("Senha", type="password").strip()
            st.markdown("<p style='text-align:right; font-size:12px; color:#10b981;'>Esqueceu sua senha?</p>", unsafe_allow_html=True)
            if st.form_submit_button("ENTRAR NO PORTAL"):
                df = get_db()
                if df is not None:
                    # Limpeza para garantir match perfeito com a planilha
                    df['Usuario'] = df['Usuario'].str.strip().str.lower()
                    user = df[(df['Usuario'] == u) & (df['Senha'].str.strip() == p)]
                    if not user.empty:
                        st.session_state.auth, st.session_state.user = True, user.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Acesso Negado: Verifique seus dados.")
        st.markdown("<p style='text-align:center; font-size:13px; color:#475569; margin-top:20px;'>Entrar como Administrador</p>", unsafe_allow_html=True)

else:
    user = st.session_state.user
    st.sidebar.markdown(f"### Olá, {user['Nome']}")
    if st.sidebar.button("Logoff"): 
        st.session_state.auth = False
        st.rerun()
    
    st.title(f"Dashboard {user['Funcao'].capitalize()}")
    st.success(f"Conexão segura ativa para: {user['Nome']}")
