import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata

# 1. Configuração e Estética
st.set_page_config(page_title="Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

if 'dark_mode' not in st.session_state: st.session_state.dark_mode = False
def toggle_theme(): st.session_state.dark_mode = not st.session_state.dark_mode
def logout(): st.session_state.clear(); st.rerun()

is_dark = st.session_state.dark_mode
c = {"bg": "#0E1117" if is_dark else "#FFF", "txt": "#F9FAFB" if is_dark else "#111", "brd": "#30363D" if is_dark else "#E5E7EB", "bar": "#1F2937" if is_dark else "#F9FAFB"}

# CSS de Alta Performance
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {c['bg']}; color: {c['txt']}; font-family: 'Inter', sans-serif; }}
    .nav-top {{ position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: {c['bg']}; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid {c['brd']}; }}
    .m-strip {{ margin-top: 55px; padding: 12px 40px; background: {c['bar']}; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid {c['brd']}; }}
    .m-card {{ text-align: center; flex: 1; border-right: 1px solid {c['brd']}; }}
    .m-label {{ font-size: 9px; opacity: 0.7; font-weight: 800; text-transform: uppercase; }}
    .m-val {{ font-size: 15px; font-weight: 700; color: #F97316; }}
    .card {{ position: relative; background: {c['bar']}; padding: 15px; border-radius: 12px; border: 1px solid {c['brd']}; text-align: center; }}
    .crown {{ position: absolute; top: -15px; left: 35%; font-size: 22px; animation: float 3s infinite; }}
    @keyframes float {{ 50% {{ transform: translateY(-5px); }} }}
    .av {{ width: 45px; height: 45px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data(aba):
    return st.connection("gsheets", type=GSheetsConnection).read(worksheet=aba, ttl=0, header=None)

def normalize(txt):
    return "".join(c for c in unicodedata.normalize('NFD', str(txt)) if unicodedata.category(c) != 'Mn').upper().strip()

def clean_v(v):
    if pd.isna(v) or str(v).strip() in ["", "0", "0%"]: return 0.0
    val = str(v).replace('%','').replace(',','.').strip()
    try:
        f = float(val)
        return f if f <= 1.5 else f/100 # Trata 95.5 ou 0.955
    except: return 0.0

# --- Lógica de Captura Blindada ---
def get_current_metrics(df_block, p_match):
    # Lista exata baseada na sua planilha
    metrics = ["CSAT", "TPC", "INTERACAO", "IR", "PONTUALIDADE", "META"]
    results = {m: "0%" for m in metrics}
    
    # Filtra as linhas do operador
    u_block = df_block[df_block.iloc[:, 0].apply(normalize).str.contains(normalize(p_match), na=False)]
    
    for m in metrics:
        # Busca a linha da métrica ignorando acentos
        row = u_block[u_block.iloc[:, 1].apply(normalize) == m]
        if not row.empty:
            # Pega valores das colunas C(2) até AG(32) e remove os vazios
            vals = row.iloc[0, 2:].replace(["", " ", None], pd.NA).dropna()
            if not vals.empty:
                last_val = vals.iloc[-1]
                # Formata para exibição
                results[m] = f"{last_val}%" if "%" not in str(last_val) else last_val
    return results

# --- AUTH & DASHBOARD ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.2, 1])
    with center.form("login"):
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR"):
            df_u = get_data("Usuarios").iloc[1:]
            df_u.columns = ['User', 'Pass', 'Nome', 'Func']
            match = df_u[(df_u['User'].astype(str) == u_in) & (df_u['Pass'].astype(str) == p_in)]
            if not match.empty:
                st.session_state.auth, st.session_state.user = True, match.iloc[0].to_dict()
                st.rerun()
else:
    u = st.session_state.user
    p_nome = u['Nome'].upper().split()[0] # Ex: MIQUEIAS
    
    # Nav e Logout
    st.markdown(f'<div class="nav-top"><b style="color:#F97316; font-size:22px">ATLAS</b><div style="font-size:12px">{u["Nome"]} | {u["Func"]}</div></div>', unsafe_allow_html=True)
    with st.sidebar: st.button("SAIR", on_click=logout, use_container_width=True)

    df_raw = get_data("DADOS-DIA")

    if u['Func'].upper() in ["GESTOR", "GESTÃO"]:
        st.markdown('<br><br><br>', unsafe_allow_html=True); st.header("Gestão")
        st.dataframe(df_raw.iloc[1:24, [0, 1]], use_container_width=True)
    else:
        # Dados Operador
        rk = df_raw.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]; rk['N'] = rk['Meta_Str'].apply(clean_v) * 100
        rk = rk.sort_values(by='N', ascending=False).reset_index(drop=True)
        
        # Bloco A27:AG211
        df_hist = df_raw.iloc[26:211, 0:33].copy()
        metrics = get_current_metrics(df_hist, p_nome)

        # Barra de Métricas (Refeita para os dados reais)
        st.markdown('<div class="m-strip">', unsafe_allow_html=True)
        cols = st.columns([0.4, 1, 1, 1, 1, 1, 1, 0.4])
        with cols[0]: 
            with st.popover("🔔"): st.info("Sem avisos.")
        
        m_list = ["CSAT", "TPC", "INTERACAO", "IR", "PONTUALIDADE", "META"]
        for i, m_key in enumerate(m_list):
            with cols[i+1]:
                st.markdown(f'<div class="m-card"><div class="m-label">{m_key}</div><div class="m-val">{metrics[m_key]}</div></div>', unsafe_allow_html=True)
        
        with cols[7]: st.toggle("🌙", value=st.session_state.dark_mode, on_change=toggle_theme)
        st.markdown('</div>', unsafe_allow_html=True)

        # Layout Ranking + Gráfico
        st.markdown('<div style="padding: 20px 40px;">', unsafe_allow_html=True)
        l, r = st.columns(2)
        with l:
            st.markdown("### 🏆 Ranking")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=400)
        with r:
            st.markdown(f"### 📈 Evolução Meta - {p_nome.title()}")
            u_data = df_hist[(df_hist.iloc[:, 0].apply(normalize).str.contains(normalize(p_nome))) & (df_hist.iloc[:, 1].apply(normalize) == "META")]
            if not u_data.empty:
                y = [clean_v(v) * 100 for v in u_data.iloc[0, 2:].values]
                chart_df = pd.DataFrame({"Dia": [f"{i:02d}" for i in range(1, 32)], "Meta %": y}).set_index("Dia")
                st.line_chart(chart_df, color="#F97316")

        # Cards com Coroa
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        c_cards = st.columns(8)
        for i, row in rk.iterrows():
            crown = '<div class="crown">👑</div>' if row['N'] >= 80 else ''
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            with c_cards[i % 8]:
                st.markdown(f'<div class="card">{crown}<div class="av">{ini}</div><div style="font-size:10px;font-weight:700;">{row["Nome"][:12]}</div><b style="color:{"#10B981" if row["N"] >= 80 else "#EF4444"}">{row["Meta_Str"]}</b></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
