import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# 1. Configuração de Layout
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Função para converter a Logo em Base64
def get_image_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

# Tente carregar o arquivo 'logo_atlas.png' (sua logo laranja)
logo_64 = get_image_base64("logo_atlas.png")

# Variáveis de Cores Adaptativas
is_dark = st.session_state.dark_mode
colors = {
    "bg": "#0E1117" if is_dark else "#FFFFFF",
    "text": "#F9FAFB" if is_dark else "#111827",
    "card_bg": "#1F2937" if is_dark else "#FFFFFF",
    "border": "#374151" if is_dark else "#E5E7EB",
    "chart": "#F97316"
}

# 2. CSS: Navbars Fixas, Cards e Coroa Animada
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {colors['bg']}; font-family: 'Inter', sans-serif; transition: 0.2s; }}
    [data-testid="stSidebar"] {{ display: none; }}
    
    /* Remove margens do Streamlit para as barras fixas */
    .main .block-container {{ padding: 0; max-width: 100%; }}

    /* Navbar Superior Branca */
    .header-white {{ 
        position: fixed; top: 0; left: 0; width: 100%; height: 55px; 
        background: {colors['bg']}; display: flex; align-items: center; 
        justify-content: space-between; padding: 0 50px; z-index: 1001; 
        border-bottom: 1px solid {colors['border']}; 
    }}
    .logo-container img {{ height: 45px; width: auto; }}

    /* Barra Laranja Fixa */
    .header-orange {{ 
        position: fixed; top: 55px; left: 0; width: 100%; height: 90px; 
        background: #A33B20; z-index: 1000; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        display: flex; align-items: center; justify-content: center;
    }}
    
    /* Estilo dos itens dentro da barra laranja */
    .orange-item {{ text-align: center; color: white !important; }}
    .orange-label {{ font-size: 10px; text-transform: uppercase; font-weight: 800; opacity: 0.9; }}
    .orange-value {{ font-size: 16px; font-weight: 700; }}

    .main-content {{ margin-top: 175px; padding: 20px 50px; color: {colors['text']}; }}

    /* Cards e Coroa Restaurada */
    .card {{ 
        position: relative; background: {colors['card_bg']}; padding: 15px; 
        border-radius: 15px; border: 1px solid {colors['border']}; 
        text-align: center; margin-bottom: 30px; height: 185px; color: {colors['text']};
    }}
    .crown {{ position: absolute; top: -18px; left: 35%; font-size: 24px; animation: float 3s infinite ease-in-out; }}
    @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px) rotate(3deg); }} }}
    
    .av {{ width: 50px; height: 50px; background: #22D3EE; color: #083344 !important; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }}
    .logout-btn {{ background: #EF4444; color: white !important; padding: 5px 15px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11px; text-decoration: none; }}
    
    /* Ajuste para o popover do sino na barra laranja */
    div[data-testid="stPopover"] button {{ background: transparent !important; border: none !important; color: white !important; font-size: 24px !important; }}
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(worksheet=aba, ttl=0, header=None)
    except: return None

def clean_p(v):
    if pd.isna(v) or v == "": return 0.0
    return pd.to_numeric(str(v).replace('%','').replace(',','.'), errors='coerce')

if 'auth' not in st.session_state: st.session_state.auth = False

# --- TELA DE LOGIN ---
if not st.session_state.auth:
    col_l, _ = st.columns([1, 2])
    with col_l:
        with st.form("login"):
            u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password").strip()
            if st.form_submit_button("ACESSAR PORTAL"):
                df_u = get_data("Usuarios")
                if df_u is not None:
                    df_u = df_u.iloc[1:]; df_u.columns = ['User', 'Pass', 'Nome', 'Func']
                    m = df_u[(df_u['User'].astype(str).str.lower() == u_in) & (df_u['Pass'].astype(str) == p_in)]
                    if not m.empty:
                        st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                        st.rerun()
                    else: st.error("Dados incorretos.")

# --- PORTAL PRINCIPAL ---
else:
    user = st.session_state.user
    p_nome = str(user['Nome']).split()[0].upper()

    # 3. Processamento AJ1:BO24 (RELATÓRIO)
    df_raw = get_data("DADOS-DIA")
    df_rel = get_data("RELATÓRIO")
    
    if df_raw is not None and df_rel is not None:
        # Ranking Geral
        rk = df_raw.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]
        rk['Meta_Num'] = rk['Meta_Str'].apply(clean_p)
        rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)

        # Gráfico: AJ1:BO24
        df_ev = df_rel.iloc[0:24, 35:67].copy() # AJ(35) até BO(66)
        df_ev.columns = df_ev.iloc[0].astype(str) # Datas (AK1:BO1)
        # Filtra o colaborador pelo nome na coluna AJ
        u_ev_row = df_ev[df_ev.iloc[:, 0].astype(str).str.upper().str.contains(p_nome, na=False)]
        
        u_match = rk[rk['Nome'].astype(str).str.upper().str.contains(p_nome, na=False)]
        posicao = f"{u_match.index[0] + 1}º" if not u_match.empty else "N/A"

        # 4. NAVBAR SUPERIOR BRANCA (Logo Atlas e Sair)
        logo_html = f'<img src="data:image/png;base64,{logo_64}">' if logo_64 else '<span style="color:#F97316; font-weight:900; font-size:24px;">ATLAS</span>'
        st.markdown(f'''
            <div class="header-white">
                <div class="logo-container">{logo_html}</div>
                <div style="display:flex; align-items:center; gap:20px;">
                    <div style="font-size:12px; color:{colors['text']};">{user["Nome"]} | 2026 <span style="color:#F97316">●</span></div>
                    <a href="/" target="_self" class="logout-btn" onclick="window.location.reload()">SAIR</a>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        # 5. BARRA LARANJA INTEGRADA (Sino, Dados e Tema)
        # Usamos st.container com colunas para simular a barra
        with st.container():
            st.markdown('<div class="header-orange">', unsafe_allow_html=True)
            # Colunas proporcionais para caber tudo
            c_sino, c_col, c_per, c_stat, c_unid, c_lua = st.columns([0.6, 1.2, 1.4, 1.2, 2.5, 0.6])
            
            with c_sino:
                with st.popover("🔔", help="Informativos"):
                    st.markdown("<h3 style='color:#111827'>📢 Notificações</h3>", unsafe_allow_html=True)
                    st.info("Nenhuma nova notificação do gestor.")
            
            with c_col: st.markdown(f'<div class="orange-item"><div class="orange-label">SUA COLOCAÇÃO</div><div class="orange-value">🏆 {posicao}</div></div>', unsafe_allow_html=True)
            with c_per: st.markdown(f'<div class="orange-item"><div class="orange-label">PERÍODO</div><div class="orange-value">JANEIRO / 2026</div></div>', unsafe_allow_html=True)
            with c_stat: st.markdown(f'<div class="orange-item"><div class="orange-label">STATUS</div><div class="orange-value">🟢 ONLINE</div></div>', unsafe_allow_html=True)
            with c_unid: st.markdown(f'<div class="orange-item"><div class="orange-label">UNIDADE</div><div class="orange-value">CALL CENTER PDF</div></div>', unsafe_allow_html=True)
            with c_lua: st.toggle("🌙", value=st.session_state.dark_mode, on_change=toggle_theme, key="dark_tgl")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        # 6. RANKING E GRÁFICO (50/50)
        col_rank, col_chart = st.columns(2)
        with col_rank:
            st.markdown("### 🏆 Ranking da Equipe")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=350)
        
        with col_chart:
            st.markdown(f"### 📈 Histórico de Performance - {p_nome.title()}")
            if not u_ev_row.empty:
                # Prepara dados para o gráfico AJ1:BO24
                plot_df = u_ev_row.iloc[0:1, 1:].transpose()
                plot_df.columns = ["Meta"]
                plot_df["Meta"] = plot_df["Meta"].apply(clean_p)
                st.line_chart(plot_df, height=350, color=colors["chart"])
            else: st.warning(f"Aguardando dados de {p_nome} no relatório.")

        # 7. PERFORMANCE INDIVIDUAL COM COROAS RESTAURADAS
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cols = st.columns(8)
        for idx, row in rk.iterrows():
            val, color_c = row['Meta_Num'], ("#10B981" if row['Meta_Num'] >= 0.8 else "#EF4444")
            # Lógica da Coroa: 80% ou mais
            crown_html = '<div class="crown">👑</div>' if val >= 0.8 else ''
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            
            with cols[idx % 8]:
                st.markdown(f'''
                    <div class="card">
                        {crown_html}<div class="av">{ini}</div>
                        <div style="font-size:10px;font-weight:700;height:35px;line-height:1.2;">{" ".join(str(row["Nome"]).split()[:2])}</div>
                        <div style="font-size:22px;font-weight:800;color:{color_c};">{row["Meta_Str"]}</div>
                    </div>
                ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
