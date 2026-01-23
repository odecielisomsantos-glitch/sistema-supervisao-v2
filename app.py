import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração de Layout Total (Wide)
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide")

# 2. CSS: Centralização, Navbar Laranja e Remoção de espaços laterais
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFF; font-family: 'Inter', sans-serif; }
    
    /* Remove espaço da sidebar fantasma se ela não carregar */
    section[data-testid="stSidebar"] { display: none; }
    .main .block-container { padding-left: 5rem; padding-right: 5rem; max-width: 100%; }

    /* Navbars Fixas e Robustas */
    .nav-white { position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: #FFF; display: flex; align-items: center; justify-content: space-between; padding: 0 50px; z-index: 1001; border-bottom: 1px solid #EEE; }
    .brand { font-size: 26px; font-weight: 900; color: #111827; letter-spacing: -1.2px; }
    
    .nav-orange { position: fixed; top: 55px; left: 0; width: 100%; height: 90px; background: #A33B20; display: flex; align-items: center; justify-content: space-around; z-index: 1000; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .nav-item { text-align: center; }
    .nav-label { font-size: 11px; text-transform: uppercase; opacity: 0.9; font-weight: 800; }
    .nav-value { font-size: 18px; font-weight: 700; margin-top: 3px; }

    .main-content { margin-top: 170px; }

    /* Estilo dos Cards */
    .card { position: relative; background: #FFF; padding: 15px; border-radius: 15px; border: 1px solid #F3F4F6; text-align: center; margin-bottom: 25px; height: 175px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); }
    .crown { position: absolute; top: -20px; left: 35%; font-size: 26px; animation: float 3s infinite ease-in-out; }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px) rotate(3deg); } }
    .av { width: 50px; height: 50px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; font-size: 18px; }
    
    /* Botão Sair no Topo */
    .logout-box { background: #EF4444; color: white !important; padding: 6px 15px; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 13px; }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=aba, ttl=0, header=None)

def clean_val(v):
    return pd.to_numeric(str(v).replace('%','').replace(',','.'), errors='coerce')

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    with st.form("login"):
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password").strip()
        if st.form_submit_button("ACESSAR PORTAL"):
            df_u = get_data("Usuarios").iloc[1:]
            df_u.columns = ['User', 'Pass', 'Nome', 'Func']
            m = df_u[(df_u['User'].astype(str).str.lower() == u_in) & (df_u['Pass'].astype(str) == p_in)]
            if m.empty: st.error("Incorreto")
            else: 
                st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                st.rerun()
else:
    u = st.session_state.user
    primeiro_nome = str(u['Nome']).split()[0].upper() # Ex: ALEXSANDRO

    # Carregamento de dados
    df_raw = get_data("DADOS-DIA")
    df_rel_raw = get_data("RELATÓRIO")

    # 1. Ranking Geral
    rk = df_raw.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "Meta_Str"]
    rk['Meta_Num'] = rk['Meta_Str'].apply(clean_val)
    rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)

    # 2. Histórico Evolução (RELATÓRIO AJ2:AT25)
    # AJ=35, AT=45. Linha 2=cabeçalho
    df_evol_slice = df_rel_raw.iloc[1:25, 35:46].copy()
    df_evol_slice.columns = df_evol_slice.iloc[0] # Cabeçalho com as datas
    df_evol_data = df_evol_slice.iloc[1:]
    
    # Busca flexível por Alexsandro
    u_evol = df_evol_data[df_evol_data.iloc[:, 0].astype(str).str.upper().str.contains(primeiro_nome, na=False)]

    # Colocação
    u_rk = rk[rk['Nome'].astype(str).str.upper().str.contains(primeiro_nome, na=False)]
    colocacao = f"{u_rk.index[0] + 1}º" if not u_rk.empty else "N/A"

    # NAVBAR SUPERIOR COM SAIR
    st.markdown(f'''
        <div class="nav-white">
            <div class="brand">🌊 EQUIPE ATLAS</div>
            <div style="display:flex; align-items:center; gap:20px;">
                <div style="font-size:12px;">{u["Nome"]} | 2026 <span style="color:#F97316">●</span></div>
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
    
    # 3. CONTEÚDO OPERADOR
    if u['Func'].lower() == 'operador':
        col_r, col_c = st.columns(2)
        with col_r:
            st.markdown("### 🏆 Ranking Geral")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=330)
        
        with col_c:
            st.markdown(f"### 📈 Histórico de Performance - {primeiro_nome.title()}")
            if not u_evol.empty:
                # Transpõe datas para o eixo X e porcentagens para o Y
                plot_df = u_evol.iloc[0:1, 1:].transpose()
                plot_df.columns = ["Meta"]
                plot_df["Meta"] = plot_df["Meta"].apply(clean_val)
                st.line_chart(plot_df, height=330, color="#F97316")
            else:
                st.info(f"Dados não encontrados para {u['Nome']} no Relatório AJ2:AT25.")

        # 4. CARDS DE PERFORMANCE
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cols = st.columns(8)
        for idx, row in rk.iterrows():
            color = "#10B981" if row['Meta_Num'] >= 80 else "#EF4444"
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            crown = f'<div class="crown">👑</div>' if row['Meta_Num'] >= 80 else ''
            with cols[idx % 8]:
                st.markdown(f'''
                <div class="card">
                    {crown}<div class="av">{ini}</div>
                    <div style="font-size:9px;font-weight:800;height:30px;">{" ".join(str(row["Nome"]).split()[:2])}</div>
                    <div style="font-size:22px;font-weight:800;color:{color};">{row["Meta_Str"]}</div>
                </div>
                ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
