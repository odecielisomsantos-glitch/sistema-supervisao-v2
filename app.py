import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Força a barra lateral a começar aberta (initial_sidebar_state)
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

# CSS: Navbar Superior, Barra Laranja Larga e Cards Premium
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFF; font-family: 'Inter', sans-serif; }
    
    /* Barra Lateral com tom diferenciado */
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E5E7EB; }
    
    /* Topo: Equipe Atlas (Maior) */
    .nav-white { position: fixed; top: 0; left: 0; width: 100%; height: 60px; background: #FFF; display: flex; align-items: center; padding: 0 40px; z-index: 1001; border-bottom: 1px solid #EEE; }
    .brand { font-size: 28px; font-weight: 900; color: #111827; letter-spacing: -1.5px; }
    
    /* Barra Laranja Larga e Informativa */
    .nav-orange { position: fixed; top: 60px; left: 0; width: 100%; height: 90px; background: #A33B20; display: flex; align-items: center; justify-content: space-around; z-index: 1000; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
    .nav-item { text-align: center; }
    .nav-label { font-size: 11px; text-transform: uppercase; opacity: 0.9; font-weight: 800; letter-spacing: 0.5px; }
    .nav-value { font-size: 18px; font-weight: 700; margin-top: 4px; }

    .main-content { margin-top: 170px; }
    
    /* Cards Compactos e Animados */
    .card { position: relative; background: #FFF; padding: 15px; border-radius: 15px; border: 1px solid #F3F4F6; text-align: center; margin-bottom: 25px; height: 165px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); transition: 0.3s; }
    .card:hover { transform: translateY(-3px); box-shadow: 0 10px 15px rgba(0,0,0,0.08); }
    .crown { position: absolute; top: -20px; left: 35%; font-size: 26px; animation: float 3s infinite ease-in-out; }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px) rotate(5deg); } }
    .av { width: 45px; height: 45px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet=aba, ttl=0, header=None)
    return df if aba != "Usuarios" else df.iloc[1:].copy()

# Requisito: Primeiro e Segundo nome apenas
def short_name(name):
    parts = name.split()
    return " ".join(parts[:2]) if len(parts) >= 2 else name

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    with st.form("login"):
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password").strip()
        if st.form_submit_button("ACESSAR SISTEMA"):
            df_u = get_data("Usuarios")
            df_u.columns = ['User', 'Pass', 'Nome', 'Func']
            m = df_u[(df_u['User'].astype(str).str.lower() == u_in) & (df_u['Pass'].astype(str) == p_in)]
            if not m.empty:
                st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                st.rerun()
            else: st.error("Dados incorretos.")
else:
    u = st.session_state.user
    
    # BARRA LATERAL (Sidebar) - Agora visível e funcional
    with st.sidebar:
        st.markdown(f"### 🌊 Painel de Acesso")
        st.info(f"Logado como: **{u['Nome']}**")
        st.write(f"Sua função: {u['Func'].upper()}")
        st.write("---")
        if st.button("🚪 Encerrar Sessão", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    # Processamento do Ranking
    df = get_data("DADOS-DIA")
    rk = df.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "Meta_Str"]
    rk['Meta_Num'] = rk['Meta_Str'].str.replace('%','').str.replace(',','.').astype(float)
    rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)
    
    # Lógica de Colocação Automática
    user_match = rk[rk['Nome'].str.contains(u['Nome'].split()[0], case=False, na=False)]
    colocacao = f"{user_match.index[0] + 1}º" if not user_match.empty else "N/A"

    # NAVBAR DUPLA
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
        st.markdown("### 🏆 Ranking Geral da Equipe")
        st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True)

        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cols = st.columns(8)
        for idx, row in rk.iterrows():
            val = row['Meta_Num']
            # Verde >= 80%, Vermelho abaixo
            color = "#10B981" if val >= 80 else "#EF4444"
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
        st.warning("Área do Gestor em desenvolvimento.")
    st.markdown('</div>', unsafe_allow_html=True)
