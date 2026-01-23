import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide")

# CSS: Barra Laranja Larga, Navbar Equipe Atlas e Cards
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFF; font-family: 'Inter', sans-serif; }
    
    .nav-white { position: fixed; top: 0; left: 0; width: 100%; height: 50px; background: #FFF; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid #EEE; }
    .brand { font-size: 24px; font-weight: 900; color: #111827; letter-spacing: -1px; }
    
    /* BARRA LARANJA LARGA (Requisito 2) */
    .nav-orange { position: fixed; top: 50px; left: 0; width: 100%; height: 80px; background: #A33B20; display: flex; align-items: center; justify-content: space-around; padding: 0 20px; z-index: 1000; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.15); }
    .nav-item { text-align: center; }
    .nav-label { font-size: 11px; text-transform: uppercase; opacity: 0.8; font-weight: bold; }
    .nav-value { font-size: 16px; font-weight: 700; }

    .main-content { margin-top: 150px; }
    
    .card { position: relative; background: #FFF; padding: 15px; border-radius: 15px; border: 1px solid #F3F4F6; text-align: center; margin-bottom: 20px; height: 170px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .crown { position: absolute; top: -15px; left: 35%; font-size: 22px; animation: float 3s infinite; }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
    .av { width: 45px; height: 45px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet=aba, ttl=0, header=None)
    return df if aba != "Usuarios" else df.iloc[1:].copy()

def short_name(name): # Requisito 1: Primeiro e Segundo nome
    return " ".join(name.split()[:2])

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    with st.form("login"):
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password").strip()
        if st.form_submit_button("ENTRAR NO SISTEMA"):
            df_u = get_data("Usuarios")
            df_u.columns = ['User', 'Pass', 'Nome', 'Func']
            m = df_u[(df_u['User'].astype(str).str.lower() == u_in) & (df_u['Pass'].astype(str) == p_in)]
            if not m.empty:
                st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                st.rerun()
            else: st.error("Dados incorretos.")
else:
    u = st.session_state.user
    df = get_data("DADOS-DIA")
    
    # Processamento do Ranking
    rk = df.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "Meta_Str"]
    rk['Meta_Num'] = rk['Meta_Str'].str.replace('%','').str.replace(',','.').astype(float)
    rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)
    
    # Lógica de Colocação (Requisito 7 & 8)
    # Busca o nome do usuário (parcial) dentro do ranking da planilha
    user_row = rk[rk['Nome'].str.contains(u['Nome'].split()[0], case=False, na=False)]
    colocacao = f"{user_row.index[0] + 1}º" if not user_row.empty else "N/A"

    # BARRA SUPERIOR DUPLA
    st.markdown(f'''
        <div class="nav-white">
            <div class="brand">🌊 EQUIPE ATLAS</div>
            <div style="font-size:12px;">{u["Nome"]} | ID: 2026 <span style="color:#F97316">●</span></div>
        </div>
        <div class="nav-orange">
            <div class="nav-item"><div class="nav-label">SUA COLOCAÇÃO</div><div class="nav-value">🏆 {colocacao}</div></div>
            <div class="nav-item"><div class="nav-label">PERÍODO</div><div class="nav-value">JANEIRO / 2026</div></div>
            <div class="nav-item"><div class="nav-label">STATUS</div><div class="nav-value">🟢 ONLINE</div></div>
            <div class="nav-item"><div class="nav-label">UNIDADE</div><div class="nav-value">CALL CENTER PDF</div></div>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    if u['Func'].lower() == 'operador':
        st.subheader("🏆 Ranking Geral")
        st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True)

        st.subheader("📊 Performance da Equipe")
        cols = st.columns(8)
        for idx, row in rk.iterrows():
            val, color = row['Meta_Num'], ("#10B981" if row['Meta_Num'] >= 80 else "#EF4444")
            ini = "".join([n[0] for n in row['Nome'].split()[:2]]).upper()
            crown = '<div class="crown">👑</div>' if val >= 80 else ''
            
            with cols[idx % 8]:
                st.markdown(f'''
                <div class="card">
                    {crown}<div class="av">{ini}</div>
                    <div style="font-size:9px; font-weight:bold; height:25px;">{short_name(row["Nome"])}</div>
                    <div style="font-size:20px; font-weight:800; color:{color};">{row["Meta_Str"]}</div>
                </div>
                ''', unsafe_allow_html=True)
    else:
        st.warning("Painel do Gestor em manutenção.")
    st.markdown('</div>', unsafe_allow_html=True)
