import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração inicial
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

# Inicialização do Tema no Session State
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# 2. CSS Dinâmico: Suporte a Modo Claro e Escuro
# Definimos variáveis para facilitar a troca de cores
dark = st.session_state.dark_mode
bg_color = "#111827" if dark else "#FFFFFF"
text_color = "#F9FAFB" if dark else "#111827"
card_bg = "#1F2937" if dark else "#FFFFFF"
border_color = "#374151" if dark else "#EEE"

st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {bg_color}; font-family: 'Inter', sans-serif; transition: 0.3s; }}
    
    /* Remove a barra lateral definitivamente */
    [data-testid="stSidebar"] {{ display: none; }}
    .main .block-container {{ padding: 2rem 5rem; max-width: 100%; color: {text_color}; }}

    /* Navbars Fixas */
    .nav-white {{ 
        position: fixed; top: 0; left: 0; width: 100%; height: 55px; 
        background: {bg_color}; display: flex; align-items: center; 
        justify-content: space-between; padding: 0 50px; z-index: 1001; 
        border-bottom: 1px solid {border_color}; transition: 0.3s;
    }}
    .brand {{ font-size: 26px; font-weight: 900; color: {text_color}; letter-spacing: -1.2px; }}
    
    .nav-orange {{ 
        position: fixed; top: 55px; left: 0; width: 100%; height: 90px; 
        background: #A33B20; display: flex; align-items: center; 
        justify-content: space-around; z-index: 1000; color: white; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
    }}
    .nav-item {{ text-align: center; }}
    .nav-label {{ font-size: 10px; text-transform: uppercase; opacity: 0.9; font-weight: 800; }}
    .nav-value {{ font-size: 17px; font-weight: 700; }}

    .main-content {{ margin-top: 170px; }}

    /* Estilo dos Cards Adaptativos */
    .card {{ 
        position: relative; background: {card_bg}; padding: 15px; 
        border-radius: 15px; border: 1px solid {border_color}; 
        text-align: center; margin-bottom: 25px; height: 180px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.04); transition: 0.3s;
        color: {text_color};
    }}
    .crown {{ position: absolute; top: -20px; left: 35%; font-size: 26px; animation: float 3s infinite ease-in-out; }}
    @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-8px) rotate(3deg); }} }}
    .av {{ width: 50px; height: 50px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }}
    
    /* Ajuste para tabelas no modo escuro */
    .stDataFrame {{ background: {card_bg}; border-radius: 10px; }}
    
    /* Botão Sair */
    .logout-btn {{ background: #EF4444; color: white !important; border: none; padding: 5px 12px; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 11px; text-decoration: none; }}
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=aba, ttl=0, header=None)

def clean_val(v):
    if pd.isna(v) or v == "": return 0.0
    return pd.to_numeric(str(v).replace('%','').replace(',','.'), errors='coerce')

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
    
    # 3. Carregamento de Dados (AJ2:AT25 do Relatório)
    df_raw = get_data("DADOS-DIA")
    df_rel = get_data("RELATÓRIO")
    
    # Ranking
    rk = df_raw.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "Meta_Str"]
    rk['Meta_Num'] = rk['Meta_Str'].apply(clean_val)
    rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)

    # Identificação do Operador
    primeiro_nome = str(u['Nome']).split()[0].upper()
    u_rk = rk[rk['Nome'].astype(str).str.upper().str.contains(primeiro_nome, na=False)]
    nome_completo = u_rk.iloc[0]['Nome'] if not u_rk.empty else u['Nome']
    colocacao = f"{u_rk.index[0] + 1}º" if not u_rk.empty else "N/A"

    # Captura AJ2:AT25 (Relatório)
    df_evol_slice = df_rel.iloc[1:25, 35:46].copy() 
    df_evol_slice.columns = df_evol_slice.iloc[0].astype(str) # Datas
    df_evol_data = df_evol_slice.iloc[1:]
    u_hist = df_evol_data[df_evol_data.iloc[:, 0].astype(str).str.upper().str.contains(primeiro_nome, na=False)]

    # 4. HEADER BRANCO/TEMA COM BOTÃO SAIR
    st.markdown(f'''
        <div class="nav-white">
            <div class="brand">🌊 EQUIPE ATLAS</div>
            <div style="display:flex; align-items:center; gap:20px;">
                <div style="font-size:12px;">{u["Nome"]} | 2026 <span style="color:#F97316">●</span></div>
                <a href="/" target="_self" class="logout-btn" onclick="window.location.reload()">SAIR</a>
            </div>
        </div>
    ''', unsafe_allow_html=True)

    # 5. BARRA LARANJA COM SINO E SELETOR DE TEMA
    # Estrutura de colunas para alinhar o Sino, Métricas e a Lua
    st.markdown('<div class="nav-orange">', unsafe_allow_html=True)
    c_sino, c_col, c_per, c_stat, c_unid = st.columns([0.5, 1.5, 1.5, 1.5, 2.5])
    
    with c_sino:
        with st.popover("🔔", help="Clique para ver notificações"):
            st.markdown(f"<h3 style='color:#111827'>📢 Informativo Geral</h3>", unsafe_allow_html=True)
            st.write("---")
            st.info("Nenhuma nova notificação do gestor no momento.")
    
    with c_col: st.markdown(f'<div class="nav-item"><div class="nav-label">SUA COLOCAÇÃO</div><div class="nav-value">🏆 {colocacao}</div></div>', unsafe_allow_html=True)
    with c_per: st.markdown(f'<div class="nav-item"><div class="nav-label">PERÍODO</div><div class="nav-value">JANEIRO / 2026</div></div>', unsafe_allow_html=True)
    with c_stat: st.markdown(f'<div class="nav-item"><div class="nav-label">STATUS</div><div class="nav-value">🟢 ONLINE</div></div>', unsafe_allow_html=True)
    
    with c_unid:
        # Coluna da Unidade + Seletor Lua
        uc1, uc2 = st.columns([0.7, 0.3])
        with uc1:
            st.markdown(f'<div class="nav-item"><div class="nav-label">UNIDADE</div><div class="nav-value">CALL CENTER PDF</div></div>', unsafe_allow_html=True)
        with uc2:
            # Chave seletora com ícone de Lua
            st.session_state.dark_mode = st.toggle("🌙", value=st.session_state.dark_mode)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # 6. CONTEÚDO PRINCIPAL (50/50)
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown(f"### 🏆 Ranking Geral")
        st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=350)
    with col_r:
        st.markdown(f"### 📈 Histórico de Performance - {nome_completo}")
        if not u_hist.empty:
            plot_df = u_hist.iloc[0:1, 1:].transpose()
            plot_df.columns = ["Meta"]
            plot_df["Meta"] = plot_df["Meta"].apply(clean_val)
            # Streamlit ajusta as cores do gráfico automaticamente baseada no tema
            st.line_chart(plot_df, height=350, color="#F97316")
        else:
            st.warning(f"Dados não encontrados para '{primeiro_nome}' em RELATÓRIO AJ2:AT25.")

    # 7. PERFORMANCE INDIVIDUAL (CARDS ADAPTATIVOS)
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
                    <div style="font-size:9px;font-weight:800;height:35px;">{" ".join(str(row["Nome"]).split()[:2])}</div>
                    <div style="font-size:22px;font-weight:800;color:{color};">{row["Meta_Str"]}</div>
                </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
