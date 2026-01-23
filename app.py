import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Team Brisa", page_icon="🌊", layout="wide")

# CSS: White Mode Profissional e Sidebar Diferenciada
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFFFFF; color: #1F2937; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #F9FAFB !important; border-right: 1px solid #E5E7EB; }
    div[data-testid="stForm"] { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 40px; }
    
    /* Botão Verde de Alta Visibilidade */
    div.stButton > button { 
        width: 100%; background: #10B981 !important; color: white !important; 
        font-weight: bold; border-radius: 6px; border: none; height: 45px;
    }
    
    /* Cards de Colaboradores (Light Mode) */
    .card { 
        background: #FFFFFF; padding: 15px; border-radius: 8px; 
        border: 1px solid #E5E7EB; border-left: 5px solid #10B981; 
        margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=aba, ttl=0, header=None)
        return df if aba != "Usuarios" else df.iloc[1:].copy()
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h2 style='text-align:center;color:#111827'>Portal Team Brisa</h2>", unsafe_allow_html=True)
        with st.form("l"):
            u = st.text_input("Usuário").strip().lower()
            p = st.text_input("Senha", type="password").strip()
            if st.form_submit_button("ENTRAR NO PORTAL"):
                df_u = get_data("Usuarios")
                if df_u is not None:
                    # Login por posição: 0=Usuário, 1=Senha
                    m = df_u[(df_u[0].astype(str).str.lower() == u) & (df_u[1].astype(str) == p)]
                    if not m.empty:
                        st.session_state.auth, st.session_state.user = True, {"Nome": m.iloc[0][2], "Funcao": m.iloc[0][3].lower()}
                        st.rerun()
                    else: st.error("Acesso negado.")
else:
    u = st.session_state.user
    st.sidebar.markdown(f"### 🌊 Team Brisa\n**{u['Nome']}**")
    if st.sidebar.button("Sair"): st.session_state.auth = False; st.rerun()

    if u['Funcao'] == 'gestor':
        st.title("🏆 Ranking TAM")
        df = get_data("DADOS-DIA")
        if df is not None:
            # Captura exata A2:B24
            rk = df.iloc[1:24, [0, 1]].dropna()
            rk.columns = ["Nome", "Meta"]
            st.dataframe(rk, use_container_width=True, hide_index=True)
            
            st.markdown("### 📊 Performance Individual")
            cols = st.columns(4)
            for idx, row in rk.reset_index(drop=True).iterrows():
                with cols[idx % 4]:
                    st.markdown(f"""
                        <div class="card">
                            <p style='color:#6B7280;margin:0;font-size:11px;font-weight:bold;'>COLABORADOR</p>
                            <p style='color:#111827;margin:0;font-size:14px;'>{row['Nome']}</p>
                            <p style='color:#10B981;margin:5px 0 0 0;font-size:22px;font-weight:bold;'>{row['Meta']}</p>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.title("📝 Operação")
        st.info("Área restrita para registros.")
