import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata
import plotly.graph_objects as go
import numpy as np

# 1. SETUP DE ELITE - TEMA BRANCO INTEGRAL
st.set_page_config(page_title="Atlas Gestão", page_icon="👔", layout="wide", initial_sidebar_state="collapsed")

if 'mural' not in st.session_state: st.session_state.mural = "Foco total na operação!"
if 'auth' not in st.session_state: st.session_state.auth = False

def logout(): st.session_state.clear(); st.rerun()

# 2. DESIGN SYSTEM - ALTA NITIDEZ E PÓDIO MINIMALISTA
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #FFFFFF; color: #111827; font-family: 'Inter', sans-serif; }
    .nav { position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: #FFFFFF; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid #E5E7EB; }
    .stMarkdown, p, h1, h2, h3, h4, span, label, li { color: #111827 !important; font-weight: 500; }
    .m-strip { margin-top: 55px; padding: 12px 40px; background: #F9FAFB; border-bottom: 1px solid #E5E7EB; display: flex; align-items: center; justify-content: space-between; }
    
    /* Estilo do Pódio Profissional */
    .podium-card { background: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); transition: 0.3s; }
    .podium-gold { border-top: 5px solid #FACC15; }
    .podium-silver { border-top: 5px solid #94A3B8; }
    .podium-bronze { border-top: 5px solid #D97706; }
    .podium-critical { border-top: 5px solid #EF4444; }
    
    .podium-name { font-size: 14px; font-weight: 800; margin-bottom: 10px; color: #111827; text-transform: uppercase; }
    .podium-metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 15px; border-top: 1px solid #F3F4F6; padding-top: 10px; }
    .podium-item { text-align: left; }
    .podium-label { font-size: 9px; color: #6B7280; font-weight: 700; text-transform: uppercase; }
    .podium-val { font-size: 12px; color: #111827; font-weight: 800; }
    
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

    # =================================================================
    # ÁREA DO GESTOR
    # =================================================================
    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.header("📊 Painel de Gestão Atlas")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média Equipe", f"{rk['N'].mean():.1f}%".replace('.',','))
        c2.metric("Coroas (80%+)", f"{len(rk[rk['N']>=80])} 👑")
        c3.metric("Foco Crítico", len(rk[rk['N']<70])); c4.metric("Ativos", len(rk))
        
        tab_v, tab_m, tab_a, tab_gb = st.tabs(["🎯 Radar da Equipe", "📢 Mural", "🔍 Auditoria", "📈 GB"])
        
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
            df_h = df_raw.iloc[26:211, 0:33].copy()
            days_cols = [f"D{i:02d}" for i in range(1, 32)]
            df_h.columns = ["Nome", "Métrica"] + days_cols
            
            perf_list = []
            for op_n in rk['Nome'].unique():
                op_d = df_h[df_h['Nome'].apply(norm).str.contains(norm(op_n.split()[0]), na=False)]
                row_p = {"Operador": op_n}
                map_m = {"META": "Sparkline (Meta)", "CSAT": "Csat", "TPC": "Tpc", "LIGAÇÃO": "Interação", "IR": "Ir", "PONTUALIDADE": "Pontualidade"}
                for s_n, d_n in map_m.items():
                    met_r = op_d[op_d['Métrica'].apply(norm) == norm(s_n)]
                    if not met_r.empty:
                        vals = [to_f(v) for v in met_r.iloc[0, 2:].values]
                        if s_n == "META":
                            last_i = max([i for i, v in enumerate(vals) if v > 0] + [0])
                            row_p["Sparkline (Meta)"] = vals[:last_i+1]
                            hist = [v for v in vals if v > 0]
                            if len(hist) >= 2:
                                arrow = " 🟢 ▲" if hist[-1] > hist[-2] else (" 🔴 ▼" if hist[-1] < hist[-2] else "")
                                row_p["Meta Atual"] = f"{hist[-1]:g}%{arrow}".replace('.',',')
                            else: row_p["Meta Atual"] = f"{hist[-1]:g}%".replace('.',',') if hist else "0%"
                            row_p["_RawMeta"] = hist[-1] if hist else 0
                        else:
                            curr = [v for v in vals if v > 0]
                            row_p[d_n] = f"{curr[-1]:g}%".replace('.',',') if curr else "0%"
                    else: row_p[d_n] = "0%"
                perf_list.append(row_p)
            
            df_perf_final = pd.DataFrame(perf_list)
            st.dataframe(df_perf_final.drop(columns=["_RawMeta"]), column_config={"Operador": st.column_config.TextColumn("Nome", width="medium"), "Sparkline (Meta)": st.column_config.LineChartColumn("Evolução Meta", y_min=0, y_max=100)}, hide_index=True, use_container_width=True)

            # =================================================================
            # NOVO: PÓDIO DOS 3 MELHORES E 3 PIORES
            # =================================================================
            st.markdown("---")
            
            # Dados para o Pódio
            sorted_perf = df_perf_final.sort_values("_RawMeta", ascending=False).reset_index(drop=True)
            top_3 = sorted_perf.head(3)
            bottom_3 = sorted_perf.tail(3).iloc[::-1] # Inverte para mostrar o pior primeiro

            def render_podium_card(row, rank_type, medal_icon):
                style_class = f"podium-{rank_type}"
                return f"""
                <div class="podium-card {style_class}">
                    <div style="font-size:30px">{medal_icon}</div>
                    <div class="podium-name">{row['Operador'][:22]}</div>
                    <b style="color:#F97316; font-size:18px">{row['Meta Atual']}</b>
                    <div class="podium-metric-grid">
                        <div class="podium-item"><div class="podium-label">CSAT</div><div class="podium-val">{row['Csat']}</div></div>
                        <div class="podium-item"><div class="podium-label">TPC</div><div class="podium-val">{row['Tpc']}</div></div>
                        <div class="podium-item"><div class="podium-label">INT.</div><div class="podium-val">{row['Interação']}</div></div>
                        <div class="podium-item"><div class="podium-label">IR</div><div class="podium-val">{row['Ir']}</div></div>
                    </div>
                </div>
                """

            st.subheader("🥇 Pódio de Elite (Top 3 Performance)")
            c_gold = st.columns(3)
            icons = ["🥇", "🥈", "🥉"]
            types = ["gold", "silver", "bronze"]
            for i in range(3):
                if i < len(top_3):
                    with c_gold[i]: st.markdown(render_podium_card(top_3.iloc[i], types[i], icons[i]), unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("🔻 Foco Necessário (Base da Equipe)")
            c_low = st.columns(3)
            for i in range(3):
                if i < len(bottom_3):
                    with c_low[i]: st.markdown(render_podium_card(bottom_3.iloc[i], "critical", "📉"), unsafe_allow_html=True)

        with tab_m:
            st.session_state.mural = st.text_area("Aviso:", value=st.session_state.mural)
            if st.button("Disparar"): st.success("Atualizado!")
        
        with tab_a:
            st.subheader("Auditoria por Operador")
            op_sel = st.selectbox("Selecione:", rk["Nome"].unique())
            if op_sel:
                aud = df_h[df_h['Nome'].apply(norm).str.contains(norm(op_sel.split()[0]), na=False)].copy()
                s_met = st.multiselect("Métricas:", aud['Métrica'].unique().tolist(), default=audit['Métrica'].unique().tolist())
                fig = go.Figure()
                for m_n in s_met:
                    row = aud[aud['Métrica'] == m_n].iloc[0]
                    xr, yr = np.array([int(d.replace("D","")) for d in days_cols]), np.array([to_f(row[d]) for d in days_cols])
                    fig.add_trace(go.Scatter(x=xr, y=yr, name=m_n, mode='lines+markers+text', text=[f"{v:g}%".replace('.',',') if v > 0 else "" for v in yr], textposition="top center", textfont=dict(size=9)))
                fig.update_layout(template="plotly_white", yaxis_range=[-5, 115], xaxis=dict(tickmode='linear', dtick=1, range=[0.5, 31.5]), margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
        
        with tab_gb:
            st.subheader("📊 Visualização de Dados Analíticos - GB")
            st.info("Página GB pronta para vinculação.")
        st.markdown('</div>', unsafe_allow_html=True)

    # =================================================================
    # ÁREA DO OPERADOR (PRESERVADA)
    # =================================================================
    else:
        df_h = df_raw.iloc[26:211, 0:33].copy()
        m_map, m_data = {"INTERAÇÃO": "LIGAÇÃO"}, {}
        u_block = df_h[df_h.iloc[:, 0].apply(norm).str.contains(p_nome, na=False)]
        for m in ["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]:
            row = u_block[u_block.iloc[:, 1].apply(norm) == norm(m_map.get(m, m))]
            if not row.empty:
                v_l = [v for v in row.iloc[0, 2:].tolist() if pd.notna(v) and str(v).strip() not in ["", "0", "0%"]]
                curr = v_l[-1] if v_l else "0%"; prev = v_l[-2] if len(v_l) > 1 else curr
                m_data[m] = {"val": format_cell(curr), "arr": '▲' if to_f(curr) > to_f(prev) else ('▼' if to_f(curr) < to_f(prev) else ""), "col": get_style(m, curr)}
            else: m_data[m] = {"val": "0%", "arr": "", "col": "#F97316"}
        st.markdown('<div class="m-strip">', unsafe_allow_html=True)
        cols_m = st.columns([0.4, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 0.4])
        for i, mk in enumerate(["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]):
            with cols_m[i+1]: st.markdown(f'<div class="m-box"><div class="m-lab">{mk}</div><div class="m-val" style="color:{m_data[mk]["col"]}">{m_data[mk]["val"]} {m_data[mk]["arr"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div><div style="padding:20px 40px">', unsafe_allow_html=True)
        cl, cr = st.columns(2)
        with cl: st.markdown("### 🏆 Ranking"); st.dataframe(rk.sort_values("N", ascending=False)[["Nome", "M_Str"]], use_container_width=True, hide_index=True, height=380)
        with cr:
            st.markdown(f"### 📈 Evolução Meta")
            u_meta = u_block[u_block.iloc[:, 1].apply(norm) == "META"]
            if not u_meta.empty: 
                y_meta = [to_f(v) for v in u_meta.iloc[0, 2:].values]
                st.line_chart(pd.DataFrame({"Dia": [f"{i:02d}" for i in range(1, 32)], "Meta": y_meta}).set_index("Dia"), color="#F97316")
        st.markdown('</div>', unsafe_allow_html=True)
