import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata
import plotly.graph_objects as go
import numpy as np
import re

# 1. SETUP DE ELITE - TEMA BRANCO INTEGRAL E ESTABILIDADE
st.set_page_config(page_title="Atlas Gestão", page_icon="👔", layout="wide", initial_sidebar_state="collapsed")

if 'mural' not in st.session_state: st.session_state.mural = "Foco total na operação!"
if 'auth' not in st.session_state: st.session_state.auth = False

def logout(): st.session_state.clear(); st.rerun()

# 2. DESIGN SYSTEM - ALTA NITIDEZ E INTERATIVIDADE 3D
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #FFFFFF; color: #111827; font-family: 'Inter', sans-serif; }
    .nav { position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: #FFFFFF; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid #E5E7EB; }
    .stMarkdown, p, h1, h2, h3, h4, span, label, li { color: #111827 !important; font-weight: 500; }
    .m-strip { margin-top: 55px; padding: 12px 40px; background: #F9FAFB; border-bottom: 1px solid #E5E7EB; display: flex; align-items: center; justify-content: space-between; }
    .m-box { text-align: center; flex: 1; border-right: 1px solid #E5E7EB; padding: 5px; }
    .m-lab { font-size: 11px; color: #4B5563; font-weight: 800; text-transform: uppercase; }
    .m-val { font-size: 22px; font-weight: 900; color: #F97316; }
    
    /* PÓDIO 3D INTERATIVO */
    .podium-card { 
        background: #FFFFFF; padding: 15px; border-radius: 12px; border: 1px solid #E5E7EB; 
        text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); cursor: default; margin-bottom: 10px;
    }
    .podium-card:hover { transform: translateY(-8px); box-shadow: 0 15px 20px -5px rgba(0,0,0,0.1); border-color: #F97316; }
    .podium-gold { border-top: 5px solid #FACC15; }
    .podium-silver { border-top: 5px solid #94A3B8; }
    .podium-bronze { border-top: 5px solid #D97706; }
    .podium-critical { border-top: 5px solid #EF4444; }
    .podium-name { font-size: 13px; font-weight: 900; margin-bottom: 8px; color: #111827; text-transform: uppercase; }
    .podium-metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; border-top: 1px solid #F3F4F6; padding-top: 10px; }
    .podium-label { font-size: 9px; color: #6B7280; font-weight: 800; text-transform: uppercase; }
    .podium-val { font-size: 12px; color: #111827; font-weight: 900; }
    
    /* CARDS OPERAÇÃO */
    .card { position: relative; background: #FFFFFF; padding: 15px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; height: 175px; color: #111827; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .av { width: 45px; height: 45px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; font-weight: 800; }
    
    .main-content { margin-top: 70px; padding: 0 40px; }
    [data-testid="stMetricValue"] { color: #F97316 !important; font-weight: 900 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. MOTOR DE DADOS E CONVERSORES ANALÍTICOS
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

def parse_val_gb(v, is_time=False):
    if pd.isna(v) or str(v).strip() in ["", "0", "0%", "0s"]: return 0.0
    s = str(v).lower().replace(',', '.').strip()
    if is_time:
        m_match = re.search(r'(\d+)\s*m', s)
        s_match = re.search(r'(\d+)\s*s', s)
        minutos = int(m_match.group(1)) if m_match else 0
        segundos = int(s_match.group(1)) if s_match else 0
        return minutos + (segundos / 60.0)
    try: return float(s.replace('%', ''))
    except: return 0.0

def render_podium_card(row, rank_type, medal_icon, main_color="#10B981"):
    return f"""
    <div class="podium-card podium-{rank_type}">
        <div style="font-size:30px">{medal_icon}</div>
        <div class="podium-name">{row['Operador'][:22]}</div>
        <b style="color:{main_color}; font-size:20px">{row['Meta Atual']}</b>
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

    # Processamento de Dados (Geral)
    df_h = df_raw.iloc[26:211, 0:33].copy()
    days_cols = [f"D{i:02d}" for i in range(1, 32)]
    df_h.columns = ["Nome", "Métrica"] + days_cols
    perf_list = []
    for op_n in rk['Nome'].unique():
        op_d = df_h[df_h['Nome'].apply(norm).str.contains(norm(op_n.split()[0]), na=False)]
        row_p = {"Operador": op_n}
        mapping = {"META": "Sparkline", "CSAT": "Csat", "TPC": "Tpc", "LIGAÇÃO": "Interação", "IR": "Ir"}
        for s_n, d_n in mapping.items():
            met_row = op_d[op_d['Métrica'].apply(norm) == norm(s_n)]
            if not met_row.empty:
                vals = [to_f(v) for v in met_row.iloc[0, 2:].values]
                if s_n == "META":
                    last_idx = max([i for i, v in enumerate(vals) if v > 0] + [0])
                    row_p["Sparkline (Meta)"] = vals[:last_idx+1]
                    hist = [v for v in vals if v > 0]
                    if len(hist) >= 2:
                        arrow = " 🟢 ▲" if hist[-1] > hist[-2] else (" 🔴 ▼" if hist[-1] < hist[-2] else "")
                        row_p["Meta Atual"] = f"{hist[-1]:g}%{arrow}".replace('.',',')
                    else: row_p["Meta Atual"] = f"{hist[-1]:g}%".replace('.',',') if hist else "0%"
                    row_p["_RawMeta"] = hist[-1] if hist else 0
                else: row_p[d_n] = f"{[v for v in vals if v > 0][-1]:g}%".replace('.',',') if any(v > 0 for v in vals) else "0%"
            else: row_p[d_n] = "0%"
        perf_list.append(row_p)
    df_perf_podium = pd.DataFrame(perf_list).sort_values("_RawMeta", ascending=False).reset_index(drop=True)

    # =================================================================
    # ÁREA DO GESTOR
    # =================================================================
    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.header("📊 Painel de Gestão Atlas")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média Equipe", f"{rk['N'].mean():.1f}%".replace('.',','))
        c2.metric("Coroas", f"{len(rk[rk['N']>=80])} 👑"); c3.metric("Foco", len(rk[rk['N']<70])); c4.metric("Ativos", len(rk))
        
        tab_v, tab_m, tab_a, tab_gb = st.tabs(["🎯 Radar", "📢 Mural", "🔍 Auditoria", "📈 GB"])
        
        with tab_v:
            col_rk, col_pie = st.columns([1, 1])
            with col_rk:
                st.subheader("Ranking Geral")
                st.dataframe(rk.sort_values("N", ascending=False)[["Nome", "M_Str"]], use_container_width=True, hide_index=True, height=350)
            with col_pie:
                st.subheader("Distribuição de Performance")
                v_h, v_m, v_l = len(rk[rk['N']>=80]), len(rk[(rk['N']>=70)&(rk['N']<80)]), len(rk[rk['N']<70])
                fig_p = go.Figure(data=[go.Pie(labels=['80%+', '70-79%', '<70%'], values=[v_h, v_m, v_l], hole=.45, marker_colors=['#10B981', '#FACC15', '#EF4444'], textinfo='value+percent', textfont=dict(size=16))])
                fig_p.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=350, showlegend=True, legend=dict(orientation="h", y=-0.15))
                st.plotly_chart(fig_p, use_container_width=True)
            
            st.markdown("---")
            st.subheader("📈 Matriz de Performance Individual")
            st.dataframe(df_perf_podium.drop(columns=["_RawMeta"]), column_config={"Sparkline (Meta)": st.column_config.LineChartColumn("Evolução Meta", y_min=0, y_max=100)}, hide_index=True, use_container_width=True)

            st.markdown("---")
            st.subheader("🥇 Pódio de Elite")
            c_g = st.columns(3)
            icons, types = ["🥇","🥈","🥉"], ["gold","silver","bronze"]
            for i in range(3):
                if i < len(df_perf_podium):
                    with c_g[i]: st.markdown(render_podium_card(df_perf_podium.iloc[i], types[i], icons[i]), unsafe_allow_html=True)
            
            st.markdown("<br>🔻 Foco Necessário", unsafe_allow_html=True)
            bot_3 = df_perf_podium.tail(3).iloc[::-1]
            c_b = st.columns(3)
            for i in range(3):
                if i < len(bot_3):
                    with c_b[i]: st.markdown(render_podium_card(bot_3.iloc[i], "critical", "📉", "#EF4444"), unsafe_allow_html=True)

        with tab_m:
            st.session_state.mural = st.text_area("Aviso:", value=st.session_state.mural)
            if st.button("Disparar Mural"): st.success("Atualizado!")
            
        with tab_a:
            st.subheader("Auditoria por Operador")
            op_sel = st.selectbox("Selecione Colaborador:", rk["Nome"].unique())
            if op_sel:
                aud_data = df_h[df_h['Nome'].apply(norm).str.contains(norm(op_sel.split()[0]), na=False)].copy()
                l_met_aud = aud_data['Métrica'].unique().tolist()
                s_met_aud = st.multiselect("Métricas:", l_met_aud, default=l_met_aud)
                fig_aud = go.Figure()
                for m_n in s_met_aud:
                    row = aud_data[aud_data['Métrica'] == m_n].iloc[0]
                    xr, yr = np.array([int(d.replace("D","")) for d in days_cols]), np.array([to_f(row[d]) for d in days_cols])
                    fig_aud.add_trace(go.Scatter(x=xr, y=yr, name=m_n, mode='lines+markers+text', text=[f"{v:g}%".replace('.',',') if v > 0 else "" for v in yr], textposition="top center", textfont=dict(size=9)))
                fig_aud.update_layout(template="plotly_white", yaxis_range=[-5, 115], xaxis=dict(tickmode='linear', dtick=1, range=[0.5, 31.5]), margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_aud, use_container_width=True)
        
        with tab_gb:
            st.subheader("📊 Dashboard Analítico GB")
            df_gb_raw = get_data("RELATÓRIO")
            if df_gb_raw is not None:
                df_gb = df_gb_raw.iloc[24:177, 2:35].copy(); df_gb.columns = ["Nome", "Métrica"] + days_cols
                op_gb_sel = st.selectbox("Selecione o Operador para Visualização Analítica:", df_gb["Nome"].unique())
                
                if op_gb_sel:
                    rows_gb = df_gb[df_gb["Nome"] == op_gb_sel]
                    fig_gb = go.Figure()
                    
                    # 📈 GRÁFICO REFORMULADO: LINHAS DIÁRIAS (1-31)
                    t_m = {"Conversação média": "#F97316", "Tratamento médio": "#FB923C", "Espera média": "#FDBA74"}
                    for m, c in t_m.items():
                        r = rows_gb[rows_gb["Métrica"].str.contains(m, na=False, case=False)]
                        if not r.empty:
                            y = [parse_val_gb(r[d].values[0], True) for d in days_cols]
                            fig_gb.add_trace(go.Scatter(x=days_cols, y=y, name=m, mode='lines+markers', line=dict(color=c, width=2), marker=dict(size=6)))
                    
                    q_m = {"Conformidade": "#10B981", "Aderência": "#3B82F6"}
                    for m, c in q_m.items():
                        r = rows_gb[rows_gb["Métrica"].str.contains(m, na=False, case=False)]
                        if not r.empty:
                            y = [parse_val_gb(r[d].values[0]) for d in days_cols]
                            fig_gb.add_trace(go.Scatter(x=days_cols, y=y, name=m, yaxis="y2", mode='lines+markers', line=dict(color=c, width=3, dash='dot'), marker=dict(size=8)))

                    fig_gb.update_layout(template="plotly_white", hovermode="x unified",
                                      yaxis=dict(title="Tempo (Minutos)", range=[0, 15]),
                                      yaxis2=dict(title="Porcentagem (%)", overlaying="y", side="right", range=[0, 110], showgrid=False),
                                      xaxis=dict(title="Dias do Mês", tickmode='linear', dtick=1),
                                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    st.plotly_chart(fig_gb, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # =================================================================
    # ÁREA DO OPERADOR (RESTAURADA INTEGRALMENTE)
    # =================================================================
    else:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.subheader("🥇 Hall da Fama - Elite Atlas")
        c_pod_op = st.columns(3)
        icons, types = ["🥇","🥈","🥉"], ["gold","silver","bronze"]
        for i in range(3):
            if i < len(df_perf_podium):
                with c_pod_op[i]: st.markdown(render_podium_card(df_perf_podium.iloc[i], types[i], icons[i]), unsafe_allow_html=True)
        
        st.markdown("---")
        u_block = df_h[df_h.iloc[:, 0].apply(norm).str.contains(p_nome, na=False)]
        m_map, m_data = {"INTERAÇÃO": "LIGAÇÃO"}, {}
        for m in ["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]:
            row = u_block[u_block.iloc[:, 1].apply(norm) == norm(m_map.get(m, m))]
            if not row.empty:
                v_l = [v for v in row.iloc[0, 2:].tolist() if pd.notna(v) and str(v).strip() not in ["", "0", "0%"]]
                curr = v_l[-1] if v_l else "0%"; prev = v_l[-2] if len(v_l) > 1 else curr
                f_val = f"{to_f(curr):g}%".replace('.', ',')
                m_data[m] = {"val": f_val, "arr": '▲' if to_f(curr) > to_f(prev) else ('▼' if to_f(curr) < to_f(prev) else ""), "col": get_style(m, curr)}
            else: m_data[m] = {"val": "0%", "arr": "", "col": "#F97316"}

        st.markdown('<div class="m-strip" style="margin-top:0px">', unsafe_allow_html=True)
        cols_m = st.columns([0.4, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 0.4])
        with cols_m[0]: 
            with st.popover("🔔"): st.info(st.session_state.mural)
        for i, mk in enumerate(["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]):
            d = m_data[mk]
            with cols_m[i+1]: st.markdown(f'<div class="m-box"><div class="m-lab">{mk}</div><div class="m-val" style="color:{d["col"]}">{d["val"]} {d["arr"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div><div style="padding:20px 40px">', unsafe_allow_html=True)
        
        cl, cr = st.columns(2)
        with cl: st.markdown("### 🏆 Ranking"); st.dataframe(rk.sort_values("N", ascending=False)[["Nome", "M_Str"]], use_container_width=True, hide_index=True, height=380)
        with cr:
            st.markdown(f"### 📈 Evolução Meta")
            u_meta_op = u_block[u_block.iloc[:, 1].apply(norm) == "META"]
            if not u_meta_op.empty:
                y_m = [to_f(v) for v in u_meta_op.iloc[0, 2:].values]
                st.line_chart(pd.DataFrame({"Dia": [f"{i:02d}" for i in range(1, 32)], "Meta": y_m}).set_index("Dia"), color="#F97316")
        
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cc = st.columns(8); rk_grid = rk.sort_values("N", ascending=False).reset_index(drop=True)
        for i, row in rk_grid.iterrows():
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            with cc[i % 8]: st.markdown(f'<div class="card"><div style="font-size:20px; position:absolute; top:-10px; left:40%">{"👑" if row["N"] >= 80 else ""}</div><div class="av">{ini}</div><div style="font-size:10px;font-weight:700">{row["Nome"][:13]}</div><b style="color:{"#10B981" if row["N"] >= 80 else "#EF4444"}; font-size:18px">{row["M_Str"]}</b></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
