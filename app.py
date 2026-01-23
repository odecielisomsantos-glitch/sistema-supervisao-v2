import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import re

# 1. Configuração de Layout e Sidebar (Estado inicial expandido) 
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

# 2. CSS: Navbars, Sidebar Colorida (Slate) e Layout Wide 
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFF; font-family: 'Inter', sans-serif; }
    
    /* Força a Sidebar a ser visível e colorida  */
    [data-testid="stSidebar"] { background-color: #1e293b !important; min-width: 250px !important; display: block !important; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    
    /* Navbars Fixas  */
    .nav-white { position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: #FFF; display: flex; align-items: center; justify-content: space-between; padding: 0 50px; z-index: 1001; border-bottom: 1px solid #EEE; }
    .nav-orange { position: fixed; top: 55px; left: 0; width: 100%; height: 90px; background: #A33B20; display: flex; align-items: center; justify-content: space-around; z-index: 1000; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    
    .main-content { margin-top: 170px; }
    .logout-box { background: #EF4444; color: white !important; padding: 6px 15px; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 12px; }
    
    /* Cards de Performance  */
    .card { position: relative; background: #FFF; padding: 15px; border-radius: 15px; border: 1px solid #F3F4F6; text-align: center; margin-bottom: 25px; height: 180px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); }
    .crown { position: absolute; top: -20px; left: 35%; font-size: 26px; animation: float 3s infinite ease-in-out; }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px) rotate(3deg); } }
    .av { width: 50px; height: 50px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=aba, ttl=0, header=None)

# Função para limpar texto (remove pontos e deixa em maiúsculo) 
def clean_text(t):
    return re.sub(r'[^A-Z0-9 ]', ' ', str(t).upper())

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
            else: st.error("Dados incorretos")
else:
    user = st.session_state.user
    # Busca inteligente: pega os dois primeiros nomes limpos 
    search_parts = clean_text(user['Nome']).split()[:2] 

    # 3. BARRA LATERAL (Agora com cor Slate e Sair) 
    with st.sidebar:
        st.markdown("## 🌊 MENU ATLAS")
        st.markdown(f"**{user['Nome']}**")
        st.write("---")
        if st.button("🚪 SAIR DA CONTA", key="side_exit"):
            st.session_state.auth = False
            st.rerun()

    # 4. PROCESSAMENTO DE DADOS 
    df_raw = get_data("DADOS-DIA")
    df_rel = get_data("RELATÓRIO")

    # Ranking Geral
    rk = df_raw.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "Meta_Str"]
    rk['Meta_Num'] = rk['Meta_Str'].astype(str).str.replace('%','').str.replace(',','.').apply(pd.to_numeric, errors='coerce')
    rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)

    # Gráfico RELATÓRIO (AJ2:AT25) 
    df_evol = df_rel.iloc[1:25, 35:46].copy() 
    df_evol.columns = df_evol.iloc[0].astype(str) # Datas da linha 2
    df_evol_data = df_evol.iloc[1:]
    
    # Filtro Dinâmico: Verifica se as partes do nome existem na célula 
    u_evol = df_evol_data[df_evol_data.iloc[:, 0].apply(lambda x: all(p in clean_text(x) for p in search_parts))]

    # Sua Colocação
    u_rk = rk[rk['Nome'].apply(lambda x: all(p in clean_text(x) for p in search_parts))]
    colocacao = f"{u_rk.index[0] + 1}º" if not u_rk.empty else "N/A"

    # Navbar Superior com Backup do Sair 
    st.markdown(f'''
        <div class="nav-white">
            <div style="font-size:24px; font-weight:900;">🌊 EQUIPE ATLAS</div>
            <div style="display:flex; align-items:center; gap:20px;">
                <div style="font-size:12px;">{user["Nome"]} | 2026 <span style="color:#F97316">●</span></div>
                <a href="/" target="_self" class="logout-box" onclick="window.location.reload()">SAIR</a>
            </div>
        </div>
        <div class="nav-orange">
            <div class="nav-item"><div class="nav-label">SUA COLOCAÇÃO</div><div class="nav-value">🏆 {colocacao}</div></div>
            <div class="nav-item"><div class="nav-label">PERÍODO</div><div class="nav-value">JANEIRO / 2026</div></div>
            <div class="nav-item"><div class="nav-label">STATUS</div><div class="nav-value">🟢 ONLINE</div></div>
            <div class="nav-item"><div class="nav-label">UNIDADE</div><div class="nav-value">CALL CENTER PDF</div></div>
        </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # 5. LAYOUT 50/50 (Ranking vs Evolução) 
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🏆 Ranking Geral")
        st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=330)
    with c2:
        st.markdown(f"### 📈 Histórico de Performance - {user['Nome']}")
        if not u_evol.empty:
            plot_df = u_evol.iloc[0:1, 1:].transpose()
            plot_df.columns = ["Meta"]
            plot_df["Meta"] = plot_df["Meta"].astype(str).str.replace('%','').str.replace(',','.').apply(pd.to_numeric, errors='coerce')
            st.line_chart(plot_df, height=330, color="#F97316")
        else:
            st.warning(f"Dados não localizados para {search_parts} no intervalo AJ2:AT25.")

    # 6. CARDS DE PERFORMANCE 
    st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
    cols = st.columns(8)
    for idx, row in rk.iterrows():
        color = "#10B981" if row['Meta_Num'] >= 80 else "#EF4444"
        crown = f'<div class="crown">👑</div>' if row['Meta_Num'] >= 80 else ''
        with cols[idx % 8]:
            st.markdown(f'''<div class="card">{crown}<div class="av">{"".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()}</div><div style="font-size:9px;font-weight:800;height:30px;">{" ".join(str(row["Nome"]).split()[:2])}</div><div style="font-size:22px;font-weight:800;color:{color};">{row["Meta_Str"]}</div></div>''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
