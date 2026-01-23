import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Team Brisa | Operação", page_icon="🌊", layout="wide")

# CSS: White Mode, Navbar e Cards Reorganizados
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFFFFF; font-family: 'Inter', sans-serif; color: #1F2937; }
    .navbar {
        position: fixed; top: 0; left: 0; width: 100%; height: 60px;
        background: #F9FAFB; border-bottom: 1px solid #E5E7EB;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 40px; z-index: 1000;
    }
    .orange-text { color: #F97316; font-weight: bold; } /* Detalhe Laranja */
    .main-content { margin-top: 70px; }
    .card {
        background: #FFFFFF; padding: 15px; border-radius: 10px;
        border: 1px solid #E5E7EB; border-top: 4px solid #F97316;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; margin-bottom: 20px;
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
            if st.form_submit_button("ENTRAR"):
                df_u = get_data("Usuarios")
                if df_u is not None:
                    # Login por posição
                    m = df_u[(df_u[0].astype(str).str.lower() == u) & (df_u[1].astype(str) == p)]
                    if not m.empty:
                        st.session_state.auth, st.session_state.user = True, {"Nome": m.iloc[0][2], "Funcao": m.iloc[0][3].lower()}
                        st.rerun()
                    else: st.error("Dados incorretos.")
else:
    u = st.session_state.user
    # 1. BARRA SUPERIOR
    st.markdown(f"""
        <div class="navbar">
            <div style="font-weight:800; font-size:18px;">🌊 Team Brisa</div>
            <div style="font-size:14px;">
                <span class="orange-text">●</span> Colaborador: <b>{u['Nome']}</b> &nbsp;&nbsp;
                <span class="orange-text">📅</span> 2026 &nbsp;&nbsp;
                <span style="cursor:pointer; color:#EF4444; font-weight:bold;" onclick="window.location.reload();">SAIR</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
    if u['Funcao'] == 'operador':
        st.title(f"Olá, {u['Nome']}! 👋")
        
        df = get_data("DADOS-DIA")
        if df is not None:
            # Dados A2:B24 [cite: 23-09-13, 23-14-21]
            rk = df.iloc[1:24, [0, 1]].dropna()
            rk.columns = ["Nome", "Meta %"]
            
            # RANKING NO TOPO [cite: 23-09-13]
            st.markdown("### 🏆 Ranking da Equipe")
            st.dataframe(rk, use_container_width=True, hide_index=True)
            
            st.write("") # Espaço
            
            # CARDS EMBAIXO [cite: 23-20-06]
            st.markdown("### 📊 Sua Performance Individual")
            cols = st.columns(5) # 5 colunas para otimizar espaço
            for idx, row in rk.reset_index(drop=True).iterrows():
                with cols[idx % 5]:
                    st.markdown(f"""
                        <div class="card">
                            <p style='color:#6B7280; font-size:10px; font-weight:bold; margin:0;'>COLABORADOR</p>
                            <p style='font-size:13px; font-weight:600; color:#111827; margin:5px 0;'>{row['Nome']}</p>
                            <p style='font-size:24px; font-weight:800; color:#F97316; margin:0;'>{row['Meta %']}</p>
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("Aguardando liberação do Painel do Gestor.")
    
    st.markdown("</div>", unsafe_allow_html=True)
