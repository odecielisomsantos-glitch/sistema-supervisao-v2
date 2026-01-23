import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import base64

# 1. Configuração de Layout e Tema Adaptativo
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Função para carregar a Logo via Base64 (Certifique-se de ter o arquivo 'logo_atlas.png')
def get_logo_64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

logo_code = get_logo_64("logo_atlas.png")

# Variáveis de Cores para Modo Escuro e Fontes
is_dark = st.session_state.dark_mode
colors = {
    "bg": "#0E1117" if is_dark else "#FFFFFF",
    "text": "#F9FAFB" if is_dark else "#111827",
    "card_bg": "#1A1C23" if is_dark else "#FFFFFF",
    "border": "#30363D" if is_dark else "#E5E7EB",
    "info_bar": "#1F2937" if is_dark else "#F9FAFB",
    "chart": "#F97316"
}

# 2. CSS Profissional: Cabeçalho, Faixa de Métricas e Coroas
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {colors['bg']}; font-family: 'Inter', sans-serif; transition: 0.1s; }}
    [data-testid="stSidebar"] {{ display: none; }}
    .main .block-container {{ padding: 0; max-width: 100%; }}

    /* Cabeçalho Superior Branco */
    .nav-main {{ 
        position: fixed; top: 0; left: 0; width: 100%; height: 55px; 
        background: {colors['bg']}; display: flex; align-items: center; 
        justify-content: space-between; padding: 0 40px; z-index: 1001; 
        border-bottom: 1px solid {colors['border']}; 
    }}
    .brand-logo img {{ height: 42px; width: auto; }}

    /* Faixa de Métricas (Substituta da Barra Laranja) */
    .metric-strip {{
        margin-top: 55px; padding: 15px 40px; background: {colors['info_bar']};
        display: flex; align-items: center; justify-content: space-between;
        border-bottom: 1px solid {colors['border']};
    }}
    .metric-box {{ text-align: center; }}
    .metric-label {{ font-size: 10px; color: {colors['text']}; opacity: 0.7; font-weight: 800; text-transform: uppercase; }}
    .metric-value {{ font-size: 16px; color: {colors['text']}; font-weight: 700; margin-top: 2px; }}

    .main-content {{ margin-top: 20px; padding: 0 40px; color: {colors['text']}; }}

    /* Cards e Coroa Restaurada */
    .card {{ 
        position: relative; background: {colors['card_bg']}; padding: 18px; 
        border-radius: 16px; border: 1px solid {colors['border']}; 
        text-align: center; margin-bottom: 30px; height: 190px;
    }}
    .crown {{ position: absolute; top: -18px; left: 35%; font-size: 24px; animation: float 3s infinite ease-in-out; }}
    @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px) rotate(3deg); }} }}
    
    .av {{ width: 50px; height: 50px; background: #22D3EE; color: #083344 !important; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }}
    .logout-btn {{ background: #EF4444; color: white !important; padding: 5px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11px; text-decoration: none; }}
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(worksheet=aba, ttl=0, header=None)
    except: return None

def clean_v(v):
    if pd.isna(v) or v == "": return 0.0
    return pd.to_numeric(str(v).replace('%','').replace(',','.'), errors='coerce')

if 'auth' not in st.session_state: st.session_state.auth = False

# --- LOGIN ---
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

# --- APP PRINCIPAL ---
else:
    u = st.session_state.user
    p_nome = str(u['Nome']).split()[0].upper()

    # 3. Processamento de Dados (Intervalo AJ1:BO24)
    df_raw = get_data("DADOS-DIA")
    df_rel = get_data("RELATÓRIO")
    
    if df_raw is not None and df_rel is not None:
        rk = df_raw.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]
        rk['Meta_Num'] = rk['Meta_Str'].apply(clean_v)
        rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)

        # Gráfico AJ1:BO24
        df_ev = df_rel.iloc[0:24, 35:67].copy() 
        df_ev.columns = df_ev.iloc[0].astype(str) # Datas (AK1:BO1)
        u_ev_row = df_ev[df_ev.iloc[:, 0].astype(str).str.upper().str.contains(p_nome, na=False)]
        
        u_rk = rk[rk['Nome'].astype(str).str.upper().str.contains(p_nome, na=False)]
        pos = f"{u_rk.index[0] + 1}º" if not u_rk.empty else "N/A"

        # 4. CABEÇALHO SUPERIOR (Logo Atlas e Sair)
        logo_img = f'<img src="data:image/png;base64,{logo_code}">' if logo_code else '<span style="color:#F97316; font-weight:900; font-size:22px;">ATLAS</span>'
        st.markdown(f'''
            <div class="nav-main">
                <div class="brand-logo">{logo_img}</div>
                <div style="display:flex; align-items:center; gap:20px;">
                    <div style="font-size:12px; font-weight:600;">{u["Nome"]} | 2026 <span style="color:#F97316">●</span></div>
                    <a href="/" target="_self" class="logout-btn" onclick="window.location.reload()">SAIR</a>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        # 5. FAIXA DE MÉTRICAS INTEGRADA (Sino, Colocação, Período, Status, Unidade, Tema)
        st.markdown('<div class="metric-strip">', unsafe_allow_html=True)
        # 6 Colunas para as informações
        mc0, mc1, mc2, mc3, mc4, mc5 = st.columns([0.5, 1.5, 1.5, 1.5, 2.5, 0.5])
        
        with mc0:
            with st.popover("🔔", help="Informativos"):
                st.markdown("<h3 style='color:#111827'>📢 Avisos</h3>", unsafe_allow_html=True)
                st.info("Nenhuma nova notificação.")
        
        with mc1: st.markdown(f'<div class="metric-box"><div class="metric-label">SUA COLOCAÇÃO</div><div class="metric-value">🏆 {pos}</div></div>', unsafe_allow_html=True)
        with mc2: st.markdown(f'<div class="metric-box"><div class="metric-label">PERÍODO</div><div class="metric-value">JANEIRO / 2026</div></div>', unsafe_allow_html=True)
        with mc3: st.markdown(f'<div class="metric-box"><div class="metric-label">STATUS</div><div class="metric-value">🟢 ONLINE</div></div>', unsafe_allow_html=True)
        with mc4: st.markdown(f'<div class="metric-box"><div class="metric-label">UNIDADE</div><div class="metric-value">CALL CENTER PDF</div></div>', unsafe_allow_html=True)
        with mc5: st.toggle("🌙", value=st.session_state.dark_mode, on_change=toggle_theme, key="dark_tgl")
        st.markdown('</div>', unsafe_allow_html=True)

        # 6. CONTEÚDO PRINCIPAL (Ranking e Gráfico AJ1:BO24)
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        col_rank, col_chart = st.columns(2)
        
        with col_rank:
            st.markdown("### 🏆 Ranking da Equipe")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=350)
        
        with col_chart:
            st.markdown(f"### 📈 Histórico de Performance - {p_nome.title()}")
            if not u_ev_row.empty:
                # Transposição para o gráfico de linhas
                plot_df = u_ev_row.iloc[0:1, 1:].transpose()
                plot_df.columns = ["Meta"]
                plot_df["Meta"] = plot_df["Meta"].apply(clean_v)
                st.line_chart(plot_df, height=350, color=colors["chart"])
            else: st.warning(f"Dados não localizados para {p_nome} no relatório AJ1:BO24.")

        # 7. PERFORMANCE INDIVIDUAL (Cards com Coroa Restaurada)
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
