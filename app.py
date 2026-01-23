import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração de Layout
st.set_page_config(page_title="Equipe Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Variáveis de Cores
is_dark = st.session_state.dark_mode
colors = {
    "bg": "#0E1117" if is_dark else "#FFFFFF",
    "text": "#F9FAFB" if is_dark else "#111827",
    "card_bg": "#1A1C23" if is_dark else "#FFFFFF",
    "border": "#30363D" if is_dark else "#E5E7EB",
    "strip": "#1F2937" if is_dark else "#F9FAFB",
    "accent": "#F97316" # Laranja Atlas
}

# CSS Profissional
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {colors['bg']}; font-family: 'Inter', sans-serif; transition: 0.1s; }}
    [data-testid="stSidebar"] {{ display: none; }}
    .main .block-container {{ padding: 0; max-width: 100%; }}
    .nav-main {{ position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: {colors['bg']}; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid {colors['border']}; }}
    .metric-strip {{ margin-top: 55px; padding: 15px 40px; background: {colors['strip']}; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid {colors['border']}; }}
    .metric-box {{ text-align: center; }}
    .metric-label {{ font-size: 10px; opacity: 0.7; font-weight: 800; text-transform: uppercase; color: {colors['text']}; }}
    .metric-value {{ font-size: 16px; font-weight: 700; color: {colors['text']}; }}
    .main-content {{ margin-top: 20px; padding: 0 40px; color: {colors['text']}; }}
    .card {{ position: relative; background: {colors['card_bg']}; padding: 18px; border-radius: 16px; border: 1px solid {colors['border']}; text-align: center; margin-bottom: 30px; height: 190px; }}
    .crown {{ position: absolute; top: -18px; left: 35%; font-size: 24px; animation: float 3s infinite ease-in-out; }}
    @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px) rotate(3deg); }} }}
    .av {{ width: 50px; height: 50px; background: #22D3EE; color: #083344 !important; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }}
    .logout-btn {{ background: #EF4444; color: white !important; padding: 5px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11px; text-decoration: none; }}
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read(worksheet=aba, ttl=0, header=None)

def clean_p(v):
    if pd.isna(v) or v == "" or str(v).strip() == "0%": return 0.0
    try:
        val = str(v).replace('%', '').replace(',', '.').strip()
        return float(val) / 100 if float(val) > 1 else float(val)
    except: return 0.0

if 'auth' not in st.session_state: st.session_state.auth = False

# --- LOGIN ---
if not st.session_state.auth:
    col_l, _ = st.columns([1, 2])
    with col_l:
        with st.form("login"):
            st.subheader("Acesso Portal Atlas")
            u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password").strip()
            if st.form_submit_button("ACESSAR"):
                df_u = get_data("Usuarios").iloc[1:]
                df_u.columns = ['User', 'Pass', 'Nome', 'Func']
                m = df_u[(df_u['User'].astype(str).str.lower() == u_in) & (df_u['Pass'].astype(str) == p_in)]
                if not m.empty:
                    st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Incorreto.")
else:
    u = st.session_state.user
    p_match = str(u['Nome']).upper().split()[0]

    df_raw = get_data("DADOS-DIA")
    
    if df_raw is not None:
        # Ranking
        rk = df_raw.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]
        rk['Meta_Num'] = rk['Meta_Str'].apply(lambda x: clean_p(x) * 100)
        rk = rk.sort_values(by='Meta_Num', ascending=False).reset_index(drop=True)

        # 3. Histórico Ajustado (A27:AG211)
        df_hist = df_raw.iloc[26:211, 0:33].copy()
        df_hist.columns = ["Nome", "Metrica"] + [f"{i:02d}" for i in range(1, 32)] # Força 01 a 31
        
        u_meta = df_hist[(df_hist['Nome'].astype(str).str.upper().str.contains(p_match)) & 
                         (df_hist['Metrica'].astype(str).str.upper() == "META")]

        u_rk_row = rk[rk['Nome'].astype(str).str.upper().str.contains(p_match)]
        pos = f"{u_rk_row.index[0] + 1}º" if not u_rk_row.empty else "N/A"

        # 4. NAVBAR E MÉTODOS
        st.markdown(f'''
            <div class="nav-main">
                <div class="brand-logo"><span style="color:#F97316; font-weight:900; font-size:22px;">ATLAS</span></div>
                <div style="display:flex; align-items:center; gap:20px;">
                    <div style="font-size:12px; font-weight:600; color:{colors['text']};">{u["Nome"]} | 2026 ●</div>
                    <a href="/" target="_self" class="logout-btn" onclick="window.location.reload()">SAIR</a>
                </div>
            </div>
            <div class="metric-strip">
        ''', unsafe_allow_html=True)
        
        c_strip = st.columns([0.5, 1.5, 1.5, 1.5, 2.5, 0.5])
        with c_strip[0]: 
            with st.popover("🔔"): st.info("Sem avisos.")
        with c_strip[1]: st.markdown(f'<div class="metric-box"><div class="metric-label">SUA COLOCAÇÃO</div><div class="metric-value">🏆 {pos}</div></div>', unsafe_allow_html=True)
        with c_strip[2]: st.markdown(f'<div class="metric-box"><div class="metric-label">PERÍODO</div><div class="metric-value">JANEIRO / 2026</div></div>', unsafe_allow_html=True)
        with c_strip[3]: st.markdown(f'<div class="metric-box"><div class="metric-label">STATUS</div><div class="metric-value">🟢 ONLINE</div></div>', unsafe_allow_html=True)
        with c_strip[4]: st.markdown(f'<div class="metric-box"><div class="metric-label">UNIDADE</div><div class="metric-value">CALL CENTER PDF</div></div>', unsafe_allow_html=True)
        with c_strip[5]: st.toggle("🌙", value=st.session_state.dark_mode, on_change=toggle_theme, key="dark_tgl")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        # 5. GRÁFICO ALINHADO (01-31 e 0-100%)
        col_rank, col_chart = st.columns(2)
        with col_rank:
            st.markdown("### 🏆 Ranking da Equipe")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=400)
            
        with col_chart:
            st.markdown(f"### 📈 Evolução da Meta - {p_match.title()}")
            if not u_meta.empty:
                # Transposição e limpeza para 0-100%
                y_vals = [clean_p(v) * 100 for v in u_meta.iloc[0, 2:].values]
                chart_df = pd.DataFrame({"Dia": [f"{i:02d}" for i in range(1, 32)], "Meta %": y_vals}).set_index("Dia")
                
                # Gráfico com Eixos Corrigidos
                st.line_chart(chart_df, color=colors['accent'], y_label="Meta (%)")
            else:
                st.warning("Histórico não localizado para este operador em A27:AG211.")

        # 6. PERFORMANCE INDIVIDUAL COM COROA
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cols_cards = st.columns(8)
        for idx, row in rk.iterrows():
            val, color_c = row['Meta_Num'], ("#10B981" if row['Meta_Num'] >= 80 else "#EF4444")
            crown = '<div class="crown">👑</div>' if val >= 80 else ''
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            with cols_cards[idx % 8]:
                st.markdown(f'''<div class="card">{crown}<div class="av">{ini}</div><div style="font-size:10px;font-weight:700;height:35px;">{" ".join(str(row["Nome"]).split()[:2])}</div><div style="font-size:22px;font-weight:800;color:{color_c};">{row["Meta_Str"]}</div></div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
