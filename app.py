import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração de Layout e Sidebar
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

# 2. CSS: Navbars que respeitam a Sidebar e Cards Premium
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFF; font-family: 'Inter', sans-serif; }
    
    /* Barra Lateral Escura (Área Vermelha) */
    [data-testid="stSidebar"] { background-color: #1e293b !important; border-right: 1px solid #334155; }
    [data-testid="stSidebar"] * { color: #f8fafc !important; }
    [data-testid="stSidebar"] .stButton > button { background: #ef4444; color: white !important; border: none; font-weight: bold; width: 100%; }

    /* Ajuste de Alinhamento das Navbars (Fix para descentralização) */
    .nav-white { position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: #FFF; display: flex; align-items: center; justify-content: space-between; padding: 0 40px 0 290px; z-index: 1001; border-bottom: 1px solid #EEE; }
    .brand { font-size: 26px; font-weight: 900; color: #111827; letter-spacing: -1.2px; }
    .nav-orange { position: fixed; top: 55px; left: 0; width: 100%; height: 85px; background: #A33B20; display: flex; align-items: center; justify-content: space-around; padding-left: 250px; z-index: 1000; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    
    .nav-item { text-align: center; }
    .nav-label { font-size: 10px; text-transform: uppercase; opacity: 0.9; font-weight: 800; }
    .nav-value { font-size: 17px; font-weight: 700; }
    .main-content { margin-top: 160px; }

    /* Cards e Coroa */
    .card { position: relative; background: #FFF; padding: 15px; border-radius: 15px; border: 1px solid #F3F4F6; text-align: center; margin-bottom: 25px; height: 180px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); }
    .crown { position: absolute; top: -20px; left: 35%; font-size: 26px; animation: float 3s infinite ease-in-out; }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px) rotate(3deg); } }
    .av { width: 50px; height: 50px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=aba, ttl=0, header=None)

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
    u = st.session_state.user
    # 3. BARRA LATERAL (Agora Colorida e Fixa)
    with st.sidebar:
        st.markdown("## 🌊 MENU ATLAS")
        st.markdown(f"**{u['Nome']}**")
        st.write("---")
        if st.button("🚪 SAIR DA CONTA"):
            st.session_state.auth = False
            st.rerun()

    # 4. PROCESSAMENTO DE DADOS (DADOS-DIA e RELATÓRIO)
    df_raw = get_data("DADOS-DIA")
    df_rel = get_data("RELATÓRIO")

    # Ranking Geral
    rk = df_raw.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "Meta_Str"]
    rk['Meta_Num'] = rk['Meta_Str'].astype(str).str.replace('%','').str.replace(',','.').apply(pd.to_numeric, errors='coerce')
    rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)

    # Lógica de Match de Nome Completo (Ponte entre Login e Planilha)
    search_term = str(u['Nome']).split()[0].upper() # Pega "ALEXSANDRO"
    match_row = rk[rk['Nome'].astype(str).str.upper().str.contains(search_term, na=False)]
    
    if not match_row.empty:
        nome_completo_oficial = match_row.iloc[0]['Nome'] # Pega "ALEXSANDRO ROCHA DOS SANTOS"
        colocacao = f"{match_row.index[0] + 1}º"
    else:
        nome_completo_oficial = u['Nome']
        colocacao = "N/A"

    # Gráfico do Relatório (AJ2:AT25)
    df_evol = df_rel.iloc[1:25, 35:46].copy() 
    df_evol.columns = df_evol.iloc[0].astype(str) # Datas
    df_evol_data = df_evol.iloc[1:]
    
    # Filtro usando o Nome Completo que achamos no Ranking
    u_evol = df_evol_data[df_evol_data.iloc[:, 0].astype(str).str.upper().str.contains(search_term, na=False)]

    # 5. NAVBARS ALINHADAS
    st.markdown(f'''
        <div class="nav-white">
            <div class="brand">🌊 EQUIPE ATLAS</div>
            <div style="font-size:12px;">{u["Nome"]} | 2026 <span style="color:#F97316">●</span></div>
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
        # 6. LAYOUT 50/50
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 🏆 Ranking Geral")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=300)
        with c2:
            st.markdown(f"### 📈 Histórico de Performance - {nome_completo_oficial}")
            if not u_evol.empty:
                # Transposição para o gráfico
                plot_df = u_evol.iloc[0:1, 1:].transpose()
                plot_df.columns = ["Meta"]
                plot_df["Meta"] = plot_df["Meta"].astype(str).str.replace('%','').str.replace(',','.').apply(pd.to_numeric, errors='coerce')
                st.line_chart(plot_df, height=300, color="#F97316")
            else: st.warning(f"Dados não localizados para {nome_completo_oficial}.")

        # 7. CARDS INDIVIDUAIS
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cols = st.columns(8)
        for idx, row in rk.iterrows():
            val, color = row['Meta_Num'], ("#10B981" if row['Meta_Num'] >= 80 else "#EF4444")
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            crown = f'<div class="crown">👑</div>' if val >= 80 else ''
            with cols[idx % 8]:
                st.markdown(f'''<div class="card">{crown}<div class="av">{ini}</div><div style="font-size:9px;font-weight:800;height:30px;">{" ".join(str(row["Nome"]).split()[:2])}</div><div style="font-size:20px;font-weight:800;color:{color};">{row["Meta_Str"]}</div></div>''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
