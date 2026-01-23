import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração de Página (Deve ser a primeira coisa)
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

# 2. CSS: Sidebar Slate, Navbars e Grid
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFF; font-family: 'Inter', sans-serif; }
    
    /* BARRA LATERAL (Área Vermelha) */
    [data-testid="stSidebar"] { background-color: #1e293b !important; border-right: 1px solid #334155; min-width: 260px !important; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    [data-testid="stSidebar"] .stButton > button { background: #ef4444; color: white !important; border: none; font-weight: bold; width: 100%; margin-top: 20px; }

    /* Navbars Fixas */
    .nav-white { position: fixed; top: 0; left: 0; width: 100%; height: 50px; background: #FFF; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid #EEE; }
    .brand { font-size: 24px; font-weight: 900; color: #111827; letter-spacing: -1.2px; }
    .nav-orange { position: fixed; top: 50px; left: 0; width: 100%; height: 85px; background: #A33B20; display: flex; align-items: center; justify-content: space-around; z-index: 1000; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    
    .nav-item { text-align: center; }
    .nav-label { font-size: 10px; text-transform: uppercase; opacity: 0.9; font-weight: 800; }
    .nav-value { font-size: 17px; font-weight: 700; margin-top: 3px; }
    .main-content { margin-top: 155px; }

    /* Cards e Coroa */
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
    parts = str(name).strip().split()
    return " ".join(parts[:2]).upper() if len(parts) >= 2 else str(name).upper()

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
            else: st.error("Dados incorretos.")
else:
    u = st.session_state.user
    
    # 3. BARRA LATERAL (A ÁREA CIRCULADA)
    with st.sidebar:
        st.markdown("## 🌊 MENU ATLAS")
        st.markdown(f"**{short_name(u['Nome'])}**")
        st.write(f"Perfil: {u['Func']}")
        st.write("---")
        if st.button("🚪 SAIR DA CONTA"):
            st.session_state.auth = False
            st.rerun()

    # 4. PROCESSAMENTO DE DADOS (RANKING E RELATÓRIO)
    df_raw = get_data("DADOS-DIA")
    df_rel_raw = get_data("RELATÓRIO")
    
    # Ranking Geral (DADOS-DIA A1:B24)
    rk = df_raw.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "Meta_Str"]
    rk['Meta_Num'] = rk['Meta_Str'].astype(str).str.replace('%','').str.replace(',','.').apply(pd.to_numeric, errors='coerce')
    rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)
    
    # BUSCA FLEXÍVEL DO NOME (Busca Alexsandro dentro de ALEXSANDRO ROCHA DOS SANTOS)
    primeiro_nome = str(u['Nome']).split()[0].upper()
    
    # Histórico de Performance (RELATÓRIO AJ2:AT25)
    # AJ=35, AT=45. Linha 2=index 1.
    df_evol = df_rel_raw.iloc[1:25, 35:46].copy()
    df_evol.columns = df_evol.iloc[0] # AJ2:AT2 como cabeçalho
    df_evol = df_evol.iloc[1:] # Dados reais
    
    # Filtro inteligente para o gráfico
    u_evol_data = df_evol[df_evol.iloc[:, 0].astype(str).str.upper().str.contains(primeiro_nome, na=False)]
    
    # Colocação
    u_rk_match = rk[rk['Nome'].astype(str).str.upper().str.contains(primeiro_nome, na=False)]
    colocacao = f"{u_rk_match.index[0] + 1}º" if not u_rk_match.empty else "N/A"

    # 5. NAVBARS FIXAS
    st.markdown(f'''
        <div class="nav-white">
            <div class="brand">🌊 EQUIPE ATLAS</div>
            <div style="font-size:12px; color:#111827;">{u["Nome"]} | 2026 <span style="color:#F97316">●</span></div>
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
        # 6. LAYOUT DIVIDIDO (Ranking vs Gráfico)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🏆 Ranking Geral")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=330)
        
        with c2:
            # Título Dinâmico
            st.markdown(f"### 📈 Histórico de Performance - {short_name(u['Nome'])}")
            if not u_evol_data.empty:
                try:
                    # Limpeza e Transposição para o gráfico
                    plot_df = u_evol_data.iloc[0:1, 1:].transpose()
                    plot_df.columns = ["Meta"]
                    plot_df["Meta"] = plot_df["Meta"].astype(str).str.replace('%','').str.replace(',','.').apply(pd.to_numeric, errors='coerce')
                    st.line_chart(plot_df, height=330, color="#F97316")
                except: st.error("Erro ao formatar dados numéricos.")
            else:
                st.info(f"Dados não encontrados para {primeiro_nome} no intervalo AJ2:AT25.")

        # 7. PERFORMANCE INDIVIDUAL (CARDS)
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cols = st.columns(8)
        for idx, row in rk.iterrows():
            val, color = row['Meta_Num'], ("#10B981" if row['Meta_Num'] >= 80 else "#EF4444")
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            crown = f'<div class="crown">👑</div>' if val >= 80 else ''
            with cols[idx % 8]:
                st.markdown(f'''
                <div class="card">
                    {crown}<div class="av">{ini}</div>
                    <div style="font-size:9px; font-weight:800; height:25px; line-height:1.2;">{short_name(row["Nome"])}</div>
                    <div style="font-size:20px; font-weight:800; color:{color}; margin-top:5px;">{row["Meta_Str"]}</div>
                </div>
                ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
