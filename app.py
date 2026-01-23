import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração de Layout e Tema (Sem Sidebar)
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

# Inicialização do Tema e Callback (Resolve o delay e as fontes)
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Variáveis de Cores para Modo Noturno
is_dark = st.session_state.dark_mode
colors = {
    "bg": "#0E1117" if is_dark else "#FFFFFF",
    "text": "#FFFFFF" if is_dark else "#111827",
    "card_bg": "#1A1C23" if is_dark else "#FFFFFF",
    "border": "#30363D" if is_dark else "#E5E7EB"
}

# 2. CSS Adaptativo: Fontes proporcionais e Navbars fixas
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {colors['bg']}; font-family: 'Inter', sans-serif; transition: 0.2s; }}
    
    /* Remove a barra lateral definitivamente */
    [data-testid="stSidebar"] {{ display: none; }}
    .main .block-container {{ padding: 2rem 5rem; max-width: 100%; color: {colors['text']}; }}

    /* Navbars Fixas */
    .nav-white {{ 
        position: fixed; top: 0; left: 0; width: 100%; height: 55px; 
        background: {colors['bg']}; display: flex; align-items: center; 
        justify-content: space-between; padding: 0 50px; z-index: 1001; 
        border-bottom: 1px solid {colors['border']}; 
    }}
    .brand {{ font-size: 26px; font-weight: 900; color: {colors['text']}; letter-spacing: -1.2px; }}
    
    .nav-orange {{ 
        position: fixed; top: 55px; left: 0; width: 100%; height: 90px; 
        background: #A33B20; display: flex; align-items: center; 
        justify-content: space-around; z-index: 1000; color: white !important; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1); 
    }}
    .nav-orange * {{ color: white !important; }}
    .nav-label {{ font-size: 10px; text-transform: uppercase; opacity: 0.9; font-weight: 800; }}
    .nav-value {{ font-size: 17px; font-weight: 700; }}

    .main-content {{ margin-top: 170px; }}

    /* Cards Proporcionais */
    .card {{ 
        position: relative; background: {colors['card_bg']}; padding: 15px; 
        border-radius: 15px; border: 1px solid {colors['border']}; 
        text-align: center; margin-bottom: 25px; height: 180px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.04); color: {colors['text']};
    }}
    .crown {{ position: absolute; top: -20px; left: 35%; font-size: 26px; animation: float 3s infinite ease-in-out; }}
    @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-8px) rotate(3deg); }} }}
    .av {{ width: 50px; height: 50px; background: #22D3EE; color: #083344 !important; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }}
    
    /* Botão Sair no Topo */
    .logout-btn {{ background: #EF4444; color: white !important; padding: 5px 15px; border-radius: 6px; font-weight: bold; text-decoration: none; font-size: 12px; }}
    </style>
""", unsafe_allow_html=True)

# Função de busca de dados com tratamento de erro
def get_data(aba):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(worksheet=aba, ttl=0, header=None)
    except Exception:
        st.error(f"Erro ao conectar com a planilha: {aba}. Tente recarregar a página.")
        return None

def clean_val(v):
    if pd.isna(v) or v == "": return 0.0
    return pd.to_numeric(str(v).replace('%','').replace(',','.'), errors='coerce')

if 'auth' not in st.session_state: st.session_state.auth = False

# --- TELA DE LOGIN ---
if not st.session_state.auth:
    with st.container():
        st.markdown("<div style='height: 100px'></div>", unsafe_allow_html=True)
        col_login, _ = st.columns([1, 2])
        with col_login:
            with st.form("login"):
                st.subheader("Acessar Portal")
                u_in = st.text_input("Usuário").lower().strip()
                p_in = st.text_input("Senha", type="password").strip()
                if st.form_submit_button("ACESSAR PORTAL"):
                    df_u = get_data("Usuarios")
                    if df_u is not None:
                        df_u = df_u.iloc[1:]
                        df_u.columns = ['User', 'Pass', 'Nome', 'Func']
                        m = df_u[(df_u['User'].astype(str).str.lower() == u_in) & (df_u['Pass'].astype(str) == p_in)]
                        if not m.empty:
                            st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                            st.rerun()
                        else: st.error("Dados incorretos.")

# --- TELA PRINCIPAL ---
else:
    u = st.session_state.user
    
    # Busca por Alexsandro Rocha (Primeiro + Segundo Nome)
    primeiro_nome = str(u['Nome']).split()[0].upper()
    dois_nomes = " ".join(str(u['Nome']).split()[:2]).upper()

    df_raw = get_data("DADOS-DIA")
    df_rel = get_data("RELATÓRIO")
    
    if df_raw is not None and df_rel is not None:
        # Ranking
        rk = df_raw.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]
        rk['Meta_Num'] = rk['Meta_Str'].apply(clean_val)
        rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)

        # Identificação para o Ranking e Colocação
        u_rk = rk[rk['Nome'].astype(str).str.upper().str.contains(primeiro_nome, na=False)]
        colocacao = f"{u_rk.index[0] + 1}º" if not u_rk.empty else "N/A"

        # Gráfico Relatório AJ2:AT25
        # AJ=35 (index 35), AT=45 (index 45)
        df_evol_slice = df_rel.iloc[1:25, 35:46].copy() 
        df_evol_slice.columns = df_evol_slice.iloc[0].astype(str) # Datas na linha 2
        df_evol_data = df_evol_slice.iloc[1:]
        # Busca flexível no relatório usando dois nomes
        u_hist = df_evol_data[df_evol_data.iloc[:, 0].astype(str).str.upper().str.contains(dois_nomes, na=False)]

        # --- HEADER ---
        st.markdown(f'''
            <div class="nav-white">
                <div class="brand">🌊 EQUIPE ATLAS</div>
                <div style="display:flex; align-items:center; gap:20px;">
                    <div style="font-size:12px; font-weight:600;">{u["Nome"]} | 2026 <span style="color:#F97316">●</span></div>
                    <a href="/" target="_self" class="logout-btn" onclick="window.location.reload()">SAIR</a>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        # --- BARRA LARANJA COM SINO E LUA ---
        st.markdown('<div class="nav-orange">', unsafe_allow_html=True)
        c_sino, c1, c2, c3, c_unid = st.columns([0.6, 1.5, 1.5, 1.5, 3])
        
        with c_sino:
            with st.popover("🔔", help="Clique para ver notificações"):
                st.markdown(f"<h3 style='color:#111827'>📢 Informativo</h3>", unsafe_allow_html=True)
                st.write("---")
                st.info("Sem novas notificações no momento.")
        
        with c1: st.markdown(f'<div class="nav-item"><div class="nav-label">SUA COLOCAÇÃO</div><div class="nav-value">🏆 {colocacao}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="nav-item"><div class="nav-label">PERÍODO</div><div class="nav-value">JANEIRO / 2026</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="nav-item"><div class="nav-label">STATUS</div><div class="nav-value">🟢 ONLINE</div></div>', unsafe_allow_html=True)
        
        with c_unid:
            un1, un2 = st.columns([0.8, 0.2])
            with un1: st.markdown(f'<div class="nav-item"><div class="nav-label">UNIDADE</div><div class="nav-value">CALL CENTER PDF</div></div>', unsafe_allow_html=True)
            with un2: st.toggle("🌙", value=st.session_state.dark_mode, on_change=toggle_theme, key="tgl")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        # --- CONTEÚDO PRINCIPAL (50/50) ---
        col_rank, col_graf = st.columns(2)
        with col_rank:
            st.markdown("### 🏆 Ranking Geral")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=350)
        
        with col_graf:
            st.markdown(f"### 📈 Histórico de Performance - {dois_nomes.title()}")
            if not u_hist.empty:
                plot_df = u_hist.iloc[0:1, 1:].transpose()
                plot_df.columns = ["Meta"]
                plot_df["Meta"] = plot_df["Meta"].apply(clean_val)
                st.line_chart(plot_df, height=350, color="#F97316")
            else:
                st.warning(f"Dados não encontrados para {dois_nomes} em RELATÓRIO AJ2:AT25.")

        # --- CARDS DE PERFORMANCE ---
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
                        <div style="font-size:10px;font-weight:700;height:35px;line-height:1.2;">{" ".join(str(row["Nome"]).split()[:2])}</div>
                        <div style="font-size:22px;font-weight:800;color:{color};">{row["Meta_Str"]}</div>
                    </div>
                ''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
