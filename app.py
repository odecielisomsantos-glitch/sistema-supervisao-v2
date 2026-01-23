import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.graph_objects as go
import base64

# 1. Configuração e Estado Inicial
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Conversão da Logo para Base64 (Certifique-se de que o arquivo existe)
def get_logo_64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

logo_code = get_logo_64("logo_atlas.png")

# Variáveis de Cores para Modo Noturno
is_dark = st.session_state.dark_mode
colors = {
    "bg": "#0E1117" if is_dark else "#FFFFFF",
    "text": "#F9FAFB" if is_dark else "#111827",
    "card_bg": "#1A1C23" if is_dark else "#FFFFFF",
    "border": "#30363D" if is_dark else "#E5E7EB",
    "info_bar": "#1F2937" if is_dark else "#F9FAFB",
    "chart_line": "#F97316", # Laranja Atlas
    "grid": "rgba(255, 255, 255, 0.1)" if is_dark else "rgba(0, 0, 0, 0.05)"
}

st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {colors['bg']}; font-family: 'Inter', sans-serif; transition: 0.2s; }}
    [data-testid="stSidebar"] {{ display: none; }}
    .main .block-container {{ padding: 0; max-width: 100%; }}

    .nav-main {{ 
        position: fixed; top: 0; left: 0; width: 100%; height: 55px; 
        background: {colors['bg']}; display: flex; align-items: center; 
        justify-content: space-between; padding: 0 40px; z-index: 1001; 
        border-bottom: 1px solid {colors['border']}; 
    }}
    .brand-logo img {{ height: 42px; width: auto; }}

    .metric-strip {{
        margin-top: 55px; padding: 15px 40px; background: {colors['info_bar']};
        display: flex; align-items: center; justify-content: space-between;
        border-bottom: 1px solid {colors['border']};
    }}
    .metric-box {{ text-align: center; }}
    .metric-label {{ font-size: 10px; color: {colors['text']}; opacity: 0.7; font-weight: 800; text-transform: uppercase; }}
    .metric-value {{ font-size: 16px; color: {colors['text']}; font-weight: 700; margin-top: 2px; }}

    .main-content {{ margin-top: 20px; padding: 0 40px; color: {colors['text']}; }}

    .card {{ 
        position: relative; background: {colors['card_bg']}; padding: 18px; 
        border-radius: 16px; border: 1px solid {colors['border']}; 
        text-align: center; margin-bottom: 30px; height: 190px;
    }}
    /* Coroa Animada */
    .crown {{ position: absolute; top: -18px; left: 35%; font-size: 24px; animation: float 3s infinite ease-in-out; }}
    @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px) rotate(3deg); }} }}
    
    .av {{ width: 50px; height: 50px; background: #22D3EE; color: #083344 !important; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }}
    .logout-btn {{ background: #EF4444; color: white !important; padding: 5px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11px; text-decoration: none; }}
    </style>
""", unsafe_allow_html=True)

def clean_numeric(val):
    if pd.isna(val) or val == "": return 0.0
    return float(str(val).replace('%', '').replace(',', '.'))

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=aba, ttl=0, header=None)

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    col_l, _ = st.columns([1, 2])
    with col_l:
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

# --- APP PRINCIPAL ---
else:
    u = st.session_state.user
    p_nome = str(u['Nome']).upper().strip()

    df_raw = get_data("DADOS-DIA")
    df_rel = get_data("RELATÓRIO")
    
    if df_raw is not None and df_rel is not None:
        # 1. Ranking Geral
        rk = df_raw.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]
        rk['Meta_Num'] = rk['Meta_Str'].apply(clean_numeric)
        rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)

        # 2. Processamento RELATÓRIO AJ1:BO24
        df_evol_raw = df_rel.iloc[0:24, 35:67].copy() 
        dates_header = df_evol_raw.iloc[0, 1:].tolist() # AK1:BO1
        operator_row = df_evol_raw[df_evol_raw.iloc[:, 0].astype(str).str.upper().str.contains(p_nome.split()[0])]
        
        u_rk_match = rk[rk['Nome'].astype(str).str.upper().str.contains(p_nome.split()[0])]
        pos = f"{u_rk_match.index[0] + 1}º" if not u_rk_match.empty else "N/A"

        # 3. HEADER E FAIXA DE MÉTRICAS
        logo_img = f'<img src="data:image/png;base64,{logo_code}">' if logo_code else '<span style="color:#F97316; font-weight:900;">ATLAS</span>'
        st.markdown(f'''
            <div class="nav-main">
                <div class="brand-logo">{logo_img}</div>
                <div style="display:flex; align-items:center; gap:20px;">
                    <div style="font-size:12px; font-weight:600;">{u["Nome"]} | 2026 ●</div>
                    <a href="/" target="_self" class="logout-btn" onclick="window.location.reload()">SAIR</a>
                </div>
            </div>
            <div class="metric-strip">
        ''', unsafe_allow_html=True)
        
        mc0, mc1, mc2, mc3, mc4, mc5 = st.columns([0.5, 1.5, 1.5, 1.5, 2.5, 0.5])
        with mc0: 
            with st.popover("🔔"): st.info("Sem avisos novos.")
        with mc1: st.markdown(f'<div class="metric-box"><div class="metric-label">SUA COLOCAÇÃO</div><div class="metric-value">🏆 {pos}</div></div>', unsafe_allow_html=True)
        with mc2: st.markdown(f'<div class="metric-box"><div class="metric-label">PERÍODO</div><div class="metric-value">JANEIRO / 2026</div></div>', unsafe_allow_html=True)
        with mc3: st.markdown(f'<div class="metric-box"><div class="metric-label">STATUS</div><div class="metric-value">🟢 ONLINE</div></div>', unsafe_allow_html=True)
        with mc4: st.markdown(f'<div class="metric-box"><div class="metric-label">UNIDADE</div><div class="metric-value">CALL CENTER PDF</div></div>', unsafe_allow_html=True)
        with mc5: st.toggle("🌙", value=st.session_state.dark_mode, on_change=toggle_theme, key="dark_tgl")
        st.markdown('</div>', unsafe_allow_html=True)

        # 4. CONTEÚDO PRINCIPAL (RANKING E GRÁFICO PLOTLY)
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        col_rank, col_chart = st.columns(2)
        
        with col_rank:
            st.markdown("### 🏆 Ranking da Equipe")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=400)
        
        with col_chart:
            st.markdown(f"### 📈 Evolução Diária - {p_nome.title()}")
            if not operator_row.empty:
                y_values = [clean_numeric(v) for v in operator_row.iloc[0, 1:].values]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates_header, y=y_values, mode='lines+markers',
                    line=dict(color=colors['chart_line'], width=3),
                    marker=dict(size=8, color=colors['chart_line'], symbol='circle'),
                    hovertemplate='Data: %{x}<br>Meta: %{y:.2f}%<extra></extra>'
                ))
                fig.update_layout(
                    margin=dict(l=0, r=0, t=20, b=0), height=400,
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, color=colors['text'], tickfont=dict(size=10)),
                    yaxis=dict(range=[0, 105], ticksuffix='%', color=colors['text'], gridcolor=colors['grid'], zeroline=False),
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            else: st.warning("Dados não localizados.")

        # 5. CARDS INDIVIDUAIS
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cols = st.columns(8)
        for idx, row in rk.iterrows():
            val, color_c = row['Meta_Num'], ("#10B981" if row['Meta_Num'] >= 80 else "#EF4444")
            crown_html = '<div class="crown">👑</div>' if val >= 80 else ''
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
