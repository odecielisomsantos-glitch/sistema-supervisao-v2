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

# 2. DESIGN SYSTEM - ALTA NITIDEZ (Fundo Branco / Texto Preto)
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #FFFFFF; color: #111827; font-family: 'Inter', sans-serif; }
    .nav { position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: #FFFFFF; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid #E5E7EB; }
    .stMarkdown, p, h1, h2, h3, h4, span, label, li { color: #111827 !important; font-weight: 500; }
    .m-strip { margin-top: 55px; padding: 12px 40px; background: #F9FAFB; border-bottom: 1px solid #E5E7EB; display: flex; align-items: center; justify-content: space-between; }
    .m-val { font-size: 22px; font-weight: 900; color: #F97316; }
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

    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.header("📊 Painel de Gestão Atlas")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média Equipe", f"{rk['N'].mean():.1f}%".replace('.',','))
        c2.metric("Coroas (80%+)", f"{len(rk[rk['N']>=80])} 👑")
        c3.metric("Foco Crítico", len(rk[rk['N']<70])); c4.metric("Ativos", len(rk))
        
        tab_v, tab_m, tab_a = st.tabs(["🎯 Radar da Equipe", "📢 Mural", "🔍 Auditoria"])
        
        with tab_v:
            # --- LAYOUT DIVIDIDO: RANKING E PIZZA ---
            col_rk, col_pie = st.columns([1, 1])
            
            with col_rk:
                st.subheader("Ranking Geral")
                st.dataframe(rk.sort_values("N", ascending=False)[["Nome", "M_Str"]], use_container_width=True, hide_index=True)
            
            with col_pie:
                st.subheader("Distribuição de Performance")
                # Lógica de Categorização
                v_high = len(rk[rk['N'] >= 80])
                v_mid = len(rk[(rk['N'] >= 70) & (rk['N'] < 80)])
                v_low = len(rk[rk['N'] < 70])
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['80% ou mais', '70% a 79,99%', 'Abaixo de 70%'],
                    values=[v_high, v_mid, v_low],
                    hole=.4,
                    marker_colors=['#10B981', '#FACC15', '#EF4444'], # Verde, Amarelo e Vermelho
                    textinfo='value+percent'
                )])
                fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.2))
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("---")
            
            # 📈 Matriz de Performance Individual (Ligação -> Interação)
            st.subheader("📈 Matriz de Performance Individual")
            df_h = df_raw.iloc[26:211, 0:33].copy()
            days_cols = [f"D{i:02d}" for i in range(1, 32)]
            df_h.columns = ["Nome", "Métrica"] + days_cols

            performance_list = []
            for op_nome in rk['Nome'].unique():
                op_data = df_h[df_h['Nome'].apply(norm).str.contains(norm(op_nome.split()[0]), na=False)]
                row_perf = {"Operador": op_nome}
                # Mapeamento técnico: Busca 'LIGAÇÃO' mas exibe 'Interação'
                mapping = {"META": "Sparkline (Meta)", "CSAT": "Csat", "TPC": "Tpc", "LIGAÇÃO": "Interação", "IR": "Ir", "PONTUALIDADE": "Pontualidade"}
                
                for sheet_name, display_name in mapping.items():
                    met_row = op_data[op_data['Métrica'].apply(norm) == norm(sheet_name)]
                    if not met_row.empty:
                        vals = [to_f(v) for v in met_row.iloc[0, 2:].values]
                        if sheet_name == "META":
                            last_idx = 0
                            for i, val in enumerate(vals):
                                if val > 0: last_idx = i
                            row_perf["Sparkline (Meta)"] = vals[:last_idx+1] if any(vals) else [0]
                            history = [v for v in vals if v > 0]
                            if len(history) >= 2:
                                curr, prev = history[-1], history[-2]
                                arrow = " 🟢 ▲" if curr > prev else (" 🔴 ▼" if curr < prev else "")
                                row_perf["Meta (Tendência)"] = f"{curr:g}%{arrow}".replace('.',',')
                            else:
                                row_perf["Meta (Tendência)"] = f"{history[-1]:g}%".replace('.',',') if history else "0%"
                        else:
                            curr_list = [v for v in vals if v > 0]
                            row_perf[display_name] = f"{curr_list[-1]:g}%".replace('.',',') if curr_list else "0%"
                    else:
                        if sheet_name == "META": 
                            row_perf["Sparkline (Meta)"] = [0]; row_perf["Meta (Tendência)"] = "0%"
                        row_perf[display_name] = "0%"
                performance_list.append(row_perf)

            st.dataframe(
                pd.DataFrame(performance_list),
                column_config={
                    "Operador": st.column_config.TextColumn("Nome do Operador", width="medium"),
                    "Sparkline (Meta)": st.column_config.LineChartColumn("Tendência Meta", y_min=0, y_max=100),
                    "Meta (Tendência)": st.column_config.TextColumn("Meta Atual"),
                    "Interação": st.column_config.TextColumn("Interação (Ligação)")
                },
                hide_index=True, use_container_width=True
            )

        with tab_m:
            st.session_state.mural = st.text_area("Aviso:", value=st.session_state.mural)
            if st.button("Disparar Mural"): st.success("Atualizado!")
            
        with tab_a:
            st.subheader("Auditoria por Operador")
            op_sel = st.selectbox("Selecione o Operador:", rk["Nome"].unique())
            if op_sel:
                audit = df_h[df_h['Nome'].apply(norm).str.contains(norm(op_sel.split()[0]), na=False)].copy()
                sel_met = st.multiselect("Visualizar métricas:", audit['Métrica'].unique().tolist(), default=audit['Métrica'].unique().tolist())
                
                fig = go.Figure()
                for m_name in sel_met:
                    row = audit[audit['Métrica'] == m_name].iloc[0]
                    xr, yr = np.array([int(d.replace("D","")) for d in days_cols]), np.array([to_f(row[d]) for d in days_cols])
                    fig.add_trace(go.Scatter(x=xr, y=yr, name=m_name, mode='lines+markers+text', 
                                             text=[f"{v:g}%".replace('.', ',') if v > 0 else "" for v in yr],
                                             textposition="top center", textfont=dict(size=9), hovertemplate='Dia %{x}: %{y:.2f}%'))
                fig.update_layout(template="plotly_white", yaxis_range=[-5, 115], xaxis=dict(tickmode='linear', tick0=1, dtick=1, range=[0.5, 31.5]), margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="main-content">Dashboard Operacional Blindado</div>', unsafe_allow_html=True)
