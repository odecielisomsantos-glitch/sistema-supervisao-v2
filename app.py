import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração de Performance e Estilo
st.set_page_config(page_title="Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

if 'dark_mode' not in st.session_state: st.session_state.dark_mode = False
if 'msg_global' not in st.session_state: st.session_state.msg_global = "Sem novos avisos."

def toggle_theme(): st.session_state.dark_mode = not st.session_state.dark_mode
def logout(): st.session_state.clear(); st.rerun()

is_dark = st.session_state.dark_mode
c = {"bg": "#0E1117" if is_dark else "#FFF", "txt": "#F9FAFB" if is_dark else "#111", "brd": "#30363D" if is_dark else "#E5E7EB", "bar": "#1F2937" if is_dark else "#F9FAFB"}

st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {c['bg']}; color: {c['txt']}; font-family: 'Inter', sans-serif; }}
    .nav-top {{ position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: {c['bg']}; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid {c['brd']}; }}
    .metric-strip {{ margin-top: 55px; padding: 10px 40px; background: {c['bar']}; border-bottom: 1px solid {c['brd']}; }}
    .metric-card {{ text-align: center; padding: 10px; border-right: 1px solid {c['brd']}; }}
    .metric-label {{ font-size: 10px; opacity: 0.7; font-weight: 800; text-transform: uppercase; }}
    .metric-value {{ font-size: 14px; font-weight: 700; color: #F97316; }}
    .card {{ position: relative; background: {c['bar']}; padding: 15px; border-radius: 12px; border: 1px solid {c['brd']}; text-align: center; height: 180px; }}
    .crown {{ position: absolute; top: -15px; left: 35%; font-size: 22px; animation: float 3s infinite; }}
    @keyframes float {{ 50% {{ transform: translateY(-5px); }} }}
    .av-icon {{ width: 45px; height: 45px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data(aba):
    try: return st.connection("gsheets", type=GSheetsConnection).read(worksheet=aba, ttl=0, header=None)
    except: return None

def clean_v(v):
    if pd.isna(v) or v == "" or str(v).strip() == "0%": return 0.0
    val = str(v).replace('%','').replace(',','.').strip()
    try: return float(val) if float(val) <= 1 else float(val)/100
    except: return 0.0

# --- Lógica de Captura das Métricas Atuais (Última preenchida) ---
def get_current_metrics(df_block, p_match):
    metrics = ["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]
    results = {}
    u_block = df_block[df_block.iloc[:, 0].astype(str).str.upper().str.contains(p_match, na=False)]
    for m in metrics:
        row = u_block[u_block.iloc[:, 1].astype(str).str.upper() == m]
        if not row.empty:
            # Pega o último valor não nulo das colunas C em diante
            vals = row.iloc[0, 2:].replace("", pd.NA).dropna()
            results[m] = vals.iloc[-1] if not vals.empty else "0%"
        else: results[m] = "0%"
    return results

# --- AUTH & DASHBOARD ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.2, 1])
    with center.form("login"):
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR PORTAL"):
            df_u = get_data("Usuarios")
            if df_u is not None:
                df_u = df_u.iloc[1:]; df_u.columns = ['User', 'Pass', 'Nome', 'Func']
                match = df_u[(df_u['User'].astype(str) == u_in) & (df_u['Pass'].astype(str) == p_in)]
                if not match.empty:
                    st.session_state.auth, st.session_state.user = True, match.iloc[0].to_dict()
                    st.rerun()
else:
    u, role, p_nome = st.session_state.user, str(st.session_state.user['Func']).upper().strip(), st.session_state.user['Nome'].upper().split()[0]
    
    st.markdown(f'<div class="nav-top"><b style="color:#F97316; font-size:22px">ATLAS</b><div style="font-size:12px">{u["Nome"]} | {role}</div></div>', unsafe_allow_html=True)
    with st.sidebar: st.button("SAIR", on_click=logout, use_container_width=True)

    df_raw = get_data("DADOS-DIA")

    # --- VISÃO GESTOR ---
    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<br><br><br>', unsafe_allow_html=True)
        st.header(f"Painel Gestão")
        if st.button("Publicar Aviso"): st.session_state.msg_global = st.text_area("Aviso:")
        st.dataframe(df_raw.iloc[1:24, [0, 1]], use_container_width=True, hide_index=True)

    # --- VISÃO OPERADOR ---
    else:
        # Processamento Base
        rk = df_raw.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]; rk['N'] = rk['Meta_Str'].apply(clean_v) * 100
        rk = rk.sort_values(by='N', ascending=False).reset_index(drop=True)
        
        # Captura de Métricas do Bloco A27:AG211
        df_hist = df_raw.iloc[26:211, 0:33].copy()
        current_metrics = get_current_metrics(df_hist, p_nome)
        
        # Barra de Métricas (Métricas de CSAT a Meta)
        st.markdown('<div class="metric-strip">', unsafe_allow_html=True)
        cols = st.columns([0.4, 1, 1, 1, 1, 1, 1, 0.4])
        with cols[0]: 
            with st.popover("🔔"): st.info(st.session_state.msg_global)
        # Exibição das 6 métricas dinâmicas
        metrics_to_show = ["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]
        for i, m_name in enumerate(metrics_to_show):
            with cols[i+1]:
                st.markdown(f'<div class="metric-card"><div class="metric-label">{m_name}</div><div class="metric-value">{current_metrics[m_name]}</div></div>', unsafe_allow_html=True)
        with cols[7]: st.toggle("🌙", value=st.session_state.dark_mode, on_change=toggle_theme, key="tgl")
        st.markdown('</div>', unsafe_allow_html=True)

        # Layout Principal
        st.markdown('<div style="padding: 20px 40px;">', unsafe_allow_html=True)
        l, r = st.columns(2)
        with l:
            st.markdown("### 🏆 Ranking")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=400)
        with r:
            st.markdown(f"### 📈 Evolução Meta - {p_nome}")
            u_data = df_hist[(df_hist.iloc[:, 0].astype(str).str.upper().str.contains(p_nome)) & (df_hist.iloc[:, 1].astype(str).str.upper() == "META")]
            if not u_data.empty:
                y = [clean_v(v) * 100 for v in u_data.iloc[0, 2:].values]
                df_chart = pd.DataFrame({"Dia": [f"{i:02d}" for i in range(1, 32)], "Meta %": y}).set_index("Dia")
                st.line_chart(df_chart, color="#F97316")

        # Cards
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cards = st.columns(8)
        for i, row in rk.iterrows():
            crown = '<div class="crown">👑</div>' if row['N'] >= 80 else ''
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            with cards[i % 8]:
                st.markdown(f'''<div class="card">{crown}<div class="av-icon">{ini}</div><div style="font-size:10px;font-weight:700;">{row["Nome"][:12]}</div><b style="color:{"#10B981" if row["N"] >= 80 else "#EF4444"}">{row["Meta_Str"]}</b></div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
