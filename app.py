import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata
import plotly.graph_objects as go
import numpy as np

# 1. SETUP - TEMA BRANCO INTEGRAL
st.set_page_config(page_title="Atlas Portal", page_icon="👔", layout="wide", initial_sidebar_state="collapsed")

if 'mural' not in st.session_state: st.session_state.mural = "Foco total na operação!"
if 'auth' not in st.session_state: st.session_state.auth = False

def logout(): st.session_state.clear(); st.rerun()

# 2. DESIGN SYSTEM - ALTA NITIDEZ E PÓDIO 3D
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #FFFFFF; color: #111827; font-family: 'Inter', sans-serif; }
    .nav { position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: #FFFFFF; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid #E5E7EB; }
    .stMarkdown, p, h1, h2, h3, h4, span, label, li { color: #111827 !important; font-weight: 500; }
    
    /* PÓDIO 3D INTERATIVO - COMUM PARA TODOS */
    .podium-card { 
        background: #FFFFFF; padding: 25px; border-radius: 16px; border: 1px solid #E5E7EB; 
        text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); cursor: default;
        margin-bottom: 20px;
    }
    .podium-card:hover { 
        transform: translateY(-10px) scale(1.02); 
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
        border-color: #F97316;
    }
    .podium-gold { border-top: 6px solid #FACC15; }
    .podium-silver { border-top: 6px solid #94A3B8; }
    .podium-bronze { border-top: 6px solid #D97706; }
    
    .podium-name { font-size: 16px; font-weight: 900; margin-bottom: 12px; color: #111827; text-transform: uppercase; }
    .podium-metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 15px; border-top: 1px solid #F3F4F6; padding-top: 15px; }
    .podium-label { font-size: 11px; color: #6B7280; font-weight: 800; text-transform: uppercase; }
    .podium-val { font-size: 14px; color: #111827; font-weight: 900; }
    
    .main-content { margin-top: 70px; padding: 0 40px; }
    [data-testid="stMetricValue"] { color: #F97316 !important; font-weight: 900 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. MOTOR DE DADOS
@st.cache_data(ttl=60)
def get_data(aba):
    try: return st.connection("gsheets", type=GSheetsConnection).read(worksheet=aba, ttl=0, header=None)
    except: return None

def norm(t): return "".join(ch for ch in unicodedata.normalize('NFD', str(t)) if unicodedata.category(ch) != 'Mn').upper().strip()

def to_f(v):
    try:
        val = str(v).replace('%','').replace(',','.')
        f = float(val)
        return f * 100 if f <= 1.05 else f
    except: return 0.0

def format_cell(v):
    if pd.isna(v) or str(v).strip() in ["", "0", "0%"]: return "0%"
    f = to_f(v)
    return f"{f:g}%".replace('.', ',')

def get_style(metric, val_str):
    v, m = to_f(val_str), norm(metric)
    if m in ["CSAT", "IR", "INTERACAO", "META"]: return "#10B981" if v >= 80 else ("#FACC15" if v >= 70 else "#F97316")
    if m == "TPC": return "#10B981" if v >= 95 else ("#FACC15" if v >= 90 else "#F97316")
    if m == "PONTUALIDADE": return "#10B981" if v >= 90 else ("#FACC15" if v >= 85 else "#F97316")
    return "#F97316"

# FUNÇÃO COMPARTILHADA DO PÓDIO
def render_podium_card(row, rank_type, medal_icon, main_color="#10B981"):
    return f"""
    <div class="podium-card podium-{rank_type}">
        <div style="font-size:35px">{medal_icon}</div>
        <div class="podium-name">{row['Operador'][:22]}</div>
        <b style="color:{main_color}; font-size:24px">{row['Meta Atual']}</b>
        <div class="podium-metric-grid">
            <div style="text-align:left"><div class="podium-label">CSAT</div><div class="podium-val">{row['Csat']}</div></div>
            <div style="text-align:left"><div class="podium-label">TPC</div><div class="podium-val">{row['Tpc']}</div></div>
            <div style="text-align:left"><div class="podium-label">INT.</div><div class="podium-val">{row['Interação']}</div></div>
            <div style="text-align:left"><div class="podium-label">IR</div><div class="podium-val">{row['Ir']}</div></div>
        </div>
    </div>
    """

# --- LOGIN ---
if not st.session_state.auth:
    _, cent, _ = st.columns([1, 1.2, 1])
    with cent.container():
        st.markdown('<div style="background:#F9FAFB; padding:40px; border-radius:15px; border:1px solid #E5E7EB; text-align:center; margin-top:100px;">', unsafe_allow_html=True)
        st.subheader("Atlas - Acesso ao Portal")
        with st.form("login"):
            u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA", use_container_width=True):
                df_u = get_data("Usuarios").iloc[1:]; df_u.columns = ['U','P','N','F']
                match = df_u[(df_u['U'].astype(str) == u_in) & (df_u['P'].astype(str) == p_in)]
                if not match.empty:
                    st.session_state.auth, st.session_state.user = True, match.iloc[0].to_dict(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    role, p_nome = str(u['F']).upper().strip(), u['N'].upper().split()[0]
    st.markdown(f'<div class="nav"><b style="color:#F97316; font-size:20px">ATLAS GESTÃO</b><div style="font-size:11px; color:#111827">{u["N"]} | {role}</div></div>', unsafe_allow_html=True)
    with st.sidebar: st.button("🚪 Sair", on_click=logout, use_container_width=True)

    df_raw = get_data("DADOS-DIA")
    rk = df_raw.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "M_Str"]; rk['N'] = rk['M_Str'].apply(to_f)

    # PROCESSAMENTO DE PERFORMANCE PARA O PÓDIO
    df_h = df_raw.iloc[26:211, 0:33].copy()
    days_cols = [f"D{i:02d}" for i in range(1, 32)]
    df_h.columns = ["Nome", "Métrica"] + days_cols
    perf_list = []
    for op_n in rk['Nome'].unique():
        op_d = df_h[df_h['Nome'].apply(norm).str.contains(norm(op_n.split()[0]), na=False)]
        row_p = {"Operador": op_n}
        mapping = {"META": "Sparkline (Meta)", "CSAT": "Csat", "TPC": "Tpc", "LIGAÇÃO": "Interação", "IR": "Ir", "PONTUALIDADE": "Pontualidade"}
        for s_n, d_n in mapping.items():
            met_r = op_d[op_d['Métrica'].apply(norm) == norm(s_n)]
            if not met_r.empty:
                vals = [to_f(v) for v in met_r.iloc[0, 2:].values]
                if s_n == "META":
                    history = [v for v in vals if v > 0]
                    if len(history) >= 2:
                        arrow = " 🟢 ▲" if history[-1] > history[-2] else (" 🔴 ▼" if history[-1] < history[-2] else "")
                        row_p["Meta Atual"] = f"{history[-1]:g}%{arrow}".replace('.',',')
                    else: row_p["Meta Atual"] = f"{history[-1]:g}%".replace('.',',') if history else "0%"
                    row_p["_RawMeta"] = history[-1] if history else 0
                else:
                    curr = [v for v in vals if v > 0]
                    row_p[d_n] = f"{curr[-1]:g}%".replace('.',',') if curr else "0%"
            else: row_p[d_n] = "0%"
        perf_list.append(row_p)
    df_perf_podium = pd.DataFrame(perf_list).sort_values("_RawMeta", ascending=False).reset_index(drop=True)

    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.header("📊 Painel de Gestão Atlas")
        # [CÓDIGO DA GESTÃO PRESERVADO...]
        tab_v, tab_m, tab_a, tab_gb = st.tabs(["🎯 Radar", "📢 Mural", "🔍 Auditoria", "📈 GB"])
        with tab_v:
            # (Pódio completo Gold/Silver/Bronze e Critical para Gestor)
            st.subheader("🥇 Pódio de Elite")
            c_g = st.columns(3)
            for i, (t, ic) in enumerate(zip(["gold","silver","bronze"], ["🥇","🥈","🥉"])):
                if i < len(df_perf_podium): with c_g[i]: st.markdown(render_podium_card(df_perf_podium.iloc[i], t, ic), unsafe_allow_html=True)
            st.markdown("<br>🔻 Foco Necessário", unsafe_allow_html=True)
            bot_3 = df_perf_podium.tail(3).iloc[::-1]
            c_b = st.columns(3)
            for i in range(3):
                if i < len(bot_3): with c_b[i]: st.markdown(render_podium_card(bot_3.iloc[i], "critical", "📉", "#EF4444"), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # =================================================================
    # ÁREA DO OPERADOR (INCLUSÃO DO PÓDIO TOP 3!)
    # =================================================================
    else:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        # 🥇 HALL DA FAMA - TOP 3 OPERAÇÃO
        st.subheader("🥇 Hall da Fama - Elite Atlas")
        c_pod = st.columns(3)
        icons, types = ["🥇", "🥈", "🥉"], ["gold", "silver", "bronze"]
        for i in range(3):
            if i < len(df_perf_podium):
                with c_pod[i]: st.markdown(render_podium_card(df_perf_podium.iloc[i], types[i], icons[i]), unsafe_allow_html=True)
        
        st.markdown("---")
        # (O resto da operação continua abaixo...)
        m_map, m_data = {"INTERAÇÃO": "LIGAÇÃO"}, {}
        u_block = df_h[df_h.iloc[:, 0].apply(norm).str.contains(p_nome, na=False)]
        for m in ["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]:
            row = u_block[u_block.iloc[:, 1].apply(norm) == norm(m_map.get(m, m))]
            if not row.empty:
                v_l = [v for v in row.iloc[0, 2:].tolist() if pd.notna(v) and str(v).strip() not in ["", "0", "0%"]]
                curr = v_l[-1] if v_l else "0%"; prev = v_l[-2] if len(v_l) > 1 else curr
                m_data[m] = {"val": format_cell(curr), "arr": '▲' if to_f(curr) > to_f(prev) else ('▼' if to_f(curr) < to_f(prev) else ""), "col": get_style(m, curr)}
            else: m_data[m] = {"val": "0%", "arr": "", "col": "#F97316"}

        st.markdown('<div class="m-strip" style="margin-top:0px">', unsafe_allow_html=True)
        cols_m = st.columns([0.4, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 0.4])
        for i, mk in enumerate(["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]):
            with cols_m[i+1]: st.markdown(f'<div class="m-box"><div class="m-lab">{mk}</div><div class="m-val" style="color:{m_data[mk]["col"]}">{m_data[mk]["val"]} {m_data[mk]["arr"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        cl, cr = st.columns(2)
        with cl: st.markdown("### 🏆 Ranking"); st.dataframe(rk.sort_values("N", ascending=False)[["Nome", "M_Str"]], use_container_width=True, hide_index=True, height=380)
        with cr:
            st.markdown(f"### 📈 Evolução Meta")
            u_meta = u_block[u_block.iloc[:, 1].apply(norm) == "META"]
            if not u_meta.empty: 
                y_meta = [to_f(v) for v in u_meta.iloc[0, 2:].values]
                st.line_chart(pd.DataFrame({"Dia": [f"{i:02d}" for i in range(1, 32)], "Meta": y_meta}).set_index("Dia"), color="#F97316")
        st.markdown('</div>', unsafe_allow_html=True)
