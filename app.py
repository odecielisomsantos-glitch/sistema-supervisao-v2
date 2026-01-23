import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide")

# CSS: Sidebar Diferenciada, Barra Laranja e Cards
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFF; font-family: 'Inter', sans-serif; }
    
    /* Barra Lateral Estilizada */
    [data-testid="stSidebar"] { background-color: #F9FAFB !important; border-right: 1px solid #E5E7EB; }
    
    .nav-white { position: fixed; top: 0; left: 0; width: 100%; height: 50px; background: #FFF; display: flex; align-items: center; padding: 0 40px; z-index: 1001; border-bottom: 1px solid #EEE; }
    .brand { font-size: 24px; font-weight: 900; color: #111827; letter-spacing: -1.2px; }
    
    .nav-orange { position: fixed; top: 50px; left: 0; width: 100%; height: 85px; background: #A33B20; display: flex; align-items: center; justify-content: space-around; z-index: 1000; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .nav-item { text-align: center; }
    .nav-label { font-size: 10px; text-transform: uppercase; opacity: 0.8; font-weight: 800; }
    .nav-value { font-size: 16px; font-weight: 700; margin-top: 2px; }

    .main-content { margin-top: 155px; }
    
    /* Cards de Performance */
    .card { position: relative; background: #FFF; padding: 15px; border-radius: 15px; border: 1px solid #F3F4F6; text-align: center; margin-bottom: 25px; height: 165px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); }
    .crown { position: absolute; top: -18px; left: 35%; font-size: 24px; animation: float 3s infinite ease-in-out; }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px) rotate(3deg); } }
    .av { width: 45px; height: 45px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet=aba, ttl=0, header=None)
    return df if aba != "Usuarios" else df.iloc[1:].copy()

def short_name(name): return " ".join(name.split()[:2])

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    with st.form("login"):
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password").strip()
        if st.form_submit_button("ACESSAR PORTAL"):
            df_u = get_data("Usuarios")
            df_u.columns = ['User', 'Pass', 'Nome', 'Func']
            m = df_u[(df_u['User'].astype(str).str.lower() == u_in) & (df_u['Pass'].astype(str) == p_in)]
            if not m.empty:
                st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                st.rerun()
            else: st.error("Dados incorretos.")
else:
    u = st.session_state.user
    
    # 1. BARRA LATERAL (SIDEBAR)
    st.sidebar.markdown(f"### 🌊 Equipe Atlas")
    st.sidebar.write(f"Usuário: **{u['Nome']}**")
    st.sidebar.write(f"Perfil: **{u['Func'].title()}**")
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sair"):
        st.session_state.auth = False
        st.rerun()

    # Processamento de Ranking
    df = get_data("DADOS-DIA")
    rk = df.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "Meta_Str"]
    rk['Meta_Num'] = rk['Meta_Str'].str.replace('%','').str.replace(',','.').astype(float)
    rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)
    
    # Cálculo de Colocação
    user_match = rk[rk['Nome'].str.contains(u['Nome'].split()[0], case=False, na=False)]
    colocacao = f"{user_match.index[0] + 1}º" if not user_match.empty else "N/A"

    # NAVBAR SUPERIOR DUPLA
    st.markdown(f'''
        <div class="nav-white"><div class="brand">🌊 EQUIPE ATLAS</div></div>
        <div class="nav-orange">
            <div class="nav-item"><div class="nav-label">SUA COLOCAÇÃO</div><div class="nav-value">🏆 {colocacao}</div></div>
            <div class="nav-item"><div class="nav-label">PERÍODO</div><div class="nav-value">JANEIRO / 2026</div></div>
            <div class="nav-item"><div class="nav-label">STATUS</div><div class="nav-value">🟢 ONLINE</div></div>
            <div class="nav-item"><div class="nav-label">UNIDADE</div><div class="nav-value">CALL CENTER PDF</div></div>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    if u['Func'].lower() == 'operador':
        st.markdown("### 🏆 Ranking da Equipe")
        st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True)

        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cols = st.columns(8)
        for idx, row in rk.iterrows():
            val, color = row['Meta_Num'], ("#10B981" if row['Meta_Num'] >= 80 else "#EF4444")
            ini = "".join([n[0] for n in row['Nome'].split()[:2]]).upper()
            crown = '<div class="crown">👑</div>' if val >= 80 else ''
            
            with cols[idx % 8]:
                st.markdown(f'''
                <div class="card">
                    {crown}<div class="av">{ini}</div>
                    <div style="font-size:9px; font-weight:800; height:25px; line-height:1.2;">{short_name(row["Nome"])}</div>
                    <div style="font-size:20px; font-weight:800; color:{color}; margin-top:5px;">{row["Meta_Str"]}</div>
                </div>
                ''', unsafe_allow_html=True)
    else:
        st.info("Painel do Gestor em desenvolvimento.")
    st.markdown('</div>', unsafe_allow_html=True)
