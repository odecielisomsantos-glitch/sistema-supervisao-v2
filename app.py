import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Team Brisa | Operador", page_icon="🌊", layout="wide")

# CSS: White Mode, Barra Superior Fixa e Detalhes Laranja
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFFFFF; font-family: 'Inter', sans-serif; color: #1F2937; }
    
    /* Barra Superior Fixa */
    .navbar {
        position: fixed; top: 0; left: 0; width: 100%; height: 65px;
        background: #F9FAFB; border-bottom: 1px solid #E5E7EB;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 40px; z-index: 1000;
    }
    .nav-logo { font-weight: 800; color: #111827; font-size: 20px; }
    .nav-info { display: flex; align-items: center; gap: 20px; }
    .orange-icon { color: #F97316; font-weight: bold; } /* Detalhe Laranja */
    
    /* Espaçamento para o conteúdo não ficar atrás da navbar */
    .main-content { margin-top: 80px; }
    
    /* Cards de Performance [cite: 23-14-21] */
    .card {
        background: #FFFFFF; padding: 20px; border-radius: 12px;
        border: 1px solid #E5E7EB; border-top: 4px solid #F97316;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: center;
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
        st.markdown("<div style='margin-top:100px; text-align:center;'><h2>Acesso Team Brisa</h2></div>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário").strip().lower()
            p = st.text_input("Senha", type="password").strip()
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                df_u = get_data("Usuarios")
                if df_u is not None:
                    # Login por posição: 0=Usuário, 1=Senha, 2=Nome
                    m = df_u[(df_u[0].astype(str).str.lower() == u) & (df_u[1].astype(str) == p)]
                    if not m.empty:
                        st.session_state.auth, st.session_state.user = True, {"Nome": m.iloc[0][2], "Funcao": m.iloc[0][3].lower()}
                        st.rerun()
                    else: st.error("Dados incorretos.")
else:
    u = st.session_state.user
    # 1. BARRA SUPERIOR (NAVBAR)
    st.markdown(f"""
        <div class="navbar">
            <div class="nav-logo">🌊 Team Brisa</div>
            <div class="nav-info">
                <span><span class="orange-icon">●</span> Conectado: <b>{u['Nome']}</b></span>
                <span><span class="orange-icon">📅</span> 2026</span>
                <span style="cursor:pointer; color:#EF4444; font-weight:bold;" onclick="window.location.reload();">SAIR</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. CONTEÚDO PARA OPERADORES [cite: 23-14-21]
    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
    if u['Funcao'] == 'operador':
        st.title(f"Olá, {u['Nome']}! 👋")
        st.write("Acompanhe aqui sua performance e ranking da equipe.")
        
        df = get_data("DADOS-DIA")
        if df is not None:
            # Ranking e Cards de Performance [cite: 23-14-21, 23-09-13]
            rk = df.iloc[1:24, [0, 1]].dropna()
            rk.columns = ["Nome", "Meta"]
            
            st.markdown("### 📊 Meta por Colaborador")
            cols = st.columns(4)
            for idx, row in rk.reset_index(drop=True).iterrows():
                with cols[idx % 4]:
                    st.markdown(f"""
                        <div class="card">
                            <p style='color:#6B7280; font-size:12px; font-weight:bold; margin-bottom:5px;'>COLABORADOR</p>
                            <p style='font-size:15px; font-weight:600; color:#111827;'>{row['Nome']}</p>
                            <p style='font-size:28px; font-weight:800; color:#F97316;'>{row['Meta']}</p>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.write("---")
            st.markdown("### 🏆 Tabela Completa")
            st.dataframe(rk, use_container_width=True, hide_index=True)
    else:
        st.warning("Acesso de Gestor detectado. O painel de gestão está sendo preparado.")
    
    st.markdown("</div>", unsafe_allow_html=True)
