import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Team Brisa", page_icon="🌊", layout="wide")

# CSS: Sidebar Diferenciada, Cards Minimalistas e Fontes Profissionais [cite: 22-59-42]
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #0b0f19; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1f2937; }
    div[data-testid="stForm"] { background: #161b22; border: 1px solid #30363d; border-radius: 12px; }
    /* Estilo dos Cards de Colaboradores [cite: 22-58-12] */
    .card { background: #161b22; padding: 15px; border-radius: 10px; border-left: 4px solid #238636; margin-bottom: 10px; }
    .card hp { color: #8b949e; margin: 0; font-size: 12px; }
    .card h3 { color: #fff; margin: 0; font-size: 18px; }
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
        st.markdown("<h2 style='text-align:center;color:white'>Portal Team Brisa</h2>", unsafe_allow_html=True)
        with st.form("l"):
            u = st.text_input("Usuário").strip().lower()
            p = st.text_input("Senha", type="password").strip()
            if st.form_submit_button("ENTRAR"):
                df_u = get_data("Usuarios")
                if df_u is not None:
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
            # Captura exata A2:B24 (índices 1 a 24) [cite: 23-09-13]
            rk = df.iloc[1:24, [0, 1]].dropna()
            rk.columns = ["Nome", "Meta"]
            
            st.dataframe(rk, use_container_width=True, hide_index=True)
            
            st.markdown("### 📊 Performance Individual")
            # Grid de Cards (4 colunas para economizar espaço) [cite: 22-58-12]
            cols = st.columns(4)
            for idx, row in rk.iterrows():
                with cols[idx % 4]:
                    st.markdown(f"""
                        <div class="card">
                            <p style='color:#8b949e;margin:0;font-size:11px;'>COLABORADOR</p>
                            <p style='color:white;margin:0;font-weight:bold;'>{row['Nome']}</p>
                            <p style='color:#238636;margin:5px 0 0 0;font-size:20px;font-weight:bold;'>{row['Meta']}</p>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.title("📝 Área Operacional")
        st.info("Bem-vindo! Em breve novos módulos aqui.")
