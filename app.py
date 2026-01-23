import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

# CSS: Navbar, Barra Laranja Larga e Gráficos Integrados
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFF; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #F8F9FA !important; border-right: 1px solid #E5E7EB; }
    .nav-white { position: fixed; top: 0; left: 0; width: 100%; height: 50px; background: #FFF; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid #EEE; }
    .brand { font-size: 24px; font-weight: 900; color: #111827; letter-spacing: -1.2px; }
    .nav-orange { position: fixed; top: 50px; left: 0; width: 100%; height: 85px; background: #A33B20; display: flex; align-items: center; justify-content: space-around; z-index: 1000; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .nav-item { text-align: center; }
    .nav-label { font-size: 10px; text-transform: uppercase; opacity: 0.9; font-weight: 800; }
    .nav-value { font-size: 17px; font-weight: 700; margin-top: 3px; }
    .main-content { margin-top: 155px; }
    .card { position: relative; background: #FFF; padding: 15px; border-radius: 15px; border: 1px solid #F3F4F6; text-align: center; margin-bottom: 25px; height: 165px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); }
    .crown { position: absolute; top: -18px; left: 35%; font-size: 24px; animation: float 3s infinite ease-in-out; }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-7px) rotate(3deg); } }
    .av { width: 45px; height: 45px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=aba, ttl=0, header=None)

def short_name(name):
    return " ".join(name.split()[:2]) if len(name.split()) >= 2 else name

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    with st.form("login"):
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password").strip()
        if st.form_submit_button("ACESSAR PORTAL"):
            df_u = get_data("Usuarios").iloc[1:]
            df_u.columns = ['User', 'Pass', 'Nome', 'Func']
            m = df_u[(df_u['User'].astype(str).str.lower() == u_in) & (df_u['Pass'].astype(str) == p_in)]
            if not m.empty:
                st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                st.rerun()
            else: st.error("Incorreto")
else:
    u = st.session_state.user
    with st.sidebar:
        st.markdown("### 🌊 EQUIPE ATLAS")
        st.write(f"Olá, **{short_name(u['Nome'])}**")
        st.write("---")
        if st.button("🚪 Sair da Conta", use_container_width=True):
            st.session_state.auth = False
            st.rerun()

    # Processamento Ranking e Gráfico
    df_raw = get_data("DADOS-DIA")
    
    # 1. Ranking (A1:B24)
    rk = df_raw.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "Meta_Str"]
    rk['Meta_Num'] = rk['Meta_Str'].str.replace('%','').str.replace(',','.').astype(float)
    rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)
    
    # 2. Dados Gráfico (A27:AG209)
    df_hist = df_raw.iloc[26:209].copy()
    df_hist.columns = df_raw.iloc[26] # Usa a linha 27 como cabeçalho (Datas)
    df_hist = df_hist.iloc[1:] # Remove a linha do cabeçalho
    
    # Filtra dados do Arthur Lola logado
    u_hist = df_hist[df_hist.iloc[:, 0].str.contains(u['Nome'].split()[0], case=False, na=False)]
    
    # Colocação
    u_match = rk[rk['Nome'].str.contains(u['Nome'].split()[0], case=False, na=False)]
    colocacao = f"{u_match.index[0] + 1}º" if not u_match.empty else "N/A"

    st.markdown(f'''
        <div class="nav-white"><div class="brand">🌊 EQUIPE ATLAS</div><div style="font-size:12px;">{u["Nome"]} | 2026 <span style="color:#F97316">●</span></div></div>
        <div class="nav-orange">
            <div class="nav-item"><div class="nav-label">SUA COLOCAÇÃO</div><div class="nav-value">🏆 {colocacao}</div></div>
            <div class="nav-item"><div class="nav-label">PERÍODO</div><div class="nav-value">JANEIRO / 2026</div></div>
            <div class="nav-item"><div class="nav-label">STATUS</div><div class="nav-value">🟢 ONLINE</div></div>
            <div class="nav-item"><div class="nav-label">UNIDADE</div><div class="nav-value">CALL CENTER PDF</div></div>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    if u['Func'].lower() == 'operador':
        col_rank, col_chart = st.columns([1, 1])
        with col_rank:
            st.markdown("### 🏆 Ranking Geral")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=300)
        
        with col_chart:
            st.markdown("### 📈 Sua Evolução Diária")
            if not u_hist.empty:
                # Transpõe os dados para formato de gráfico (Dias vs Porcentagem)
                plot_data = u_hist.iloc[:, 1:].transpose()
                plot_data.columns = ["Meta"]
                plot_data["Meta"] = plot_data["Meta"].str.replace('%','').str.replace(',','.').astype(float)
                st.line_chart(plot_data, height=300, color="#F97316")
            else: st.info("Dados de evolução não encontrados.")

        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cols = st.columns(8)
        for idx, row in rk.iterrows():
            color = "#10B981" if row['Meta_Num'] >= 80 else "#EF4444"
            crown = '<div class="crown">👑</div>' if row['Meta_Num'] >= 80 else ''
            with cols[idx % 8]:
                st.markdown(f'''<div class="card">{crown}<div class="av">{"".join([n[0] for n in row['Nome'].split()[:2]]).upper()}</div><div style="font-size:9px; font-weight:800; height:25px;">{short_name(row["Nome"])}</div><div style="font-size:20px; font-weight:800; color:{color};">{row["Meta_Str"]}</div></div>''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
