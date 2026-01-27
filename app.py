import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata
import plotly.express as px

# 1. SETUP DE ELITE - TEMA BRANCO OBRIGATÓRIO
st.set_page_config(page_title="Atlas Gestão", page_icon="👔", layout="wide", initial_sidebar_state="collapsed")

if 'mural' not in st.session_state: st.session_state.mural = "Foco total na operação!"
if 'auth' not in st.session_state: st.session_state.auth = False

def logout(): st.session_state.clear(); st.rerun()

# 2. DESIGN SYSTEM - ALTA NITIDEZ (Fundo Branco / Texto Preto)
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #FFFFFF; color: #111827; font-family: 'Inter', sans-serif; }}
    
    /* Navbar e Texto */
    .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: #FFFFFF; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid #E5E7EB; }}
    .stMarkdown, p, h1, h2, h3, h4, span, label, li {{ color: #111827 !important; font-weight: 500; }}
    
    /* Faixa de Métricas e Cards */
    .m-strip {{ margin-top: 55px; padding: 12px 40px; background: #F9FAFB; border-bottom: 1px solid #E5E7EB; display: flex; align-items: center; justify-content: space-between; }}
    .m-box {{ text-align: center; flex: 1; border-right: 1px solid #E5E7EB; padding: 5px; }}
    .m-lab {{ font-size: 11px; color: #4B5563; font-weight: 800; text-transform: uppercase; }}
    .m-val {{ font-size: 22px; font-weight: 900; color: #F97316; }}
    
    .card {{ position: relative; background: #FFFFFF; padding: 15px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; height: 175px; color: #111827; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    .av {{ width: 45px; height: 45px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; font-weight: 800; }}
    
    /* Ajustes Gerais */
    .main-content {{ margin-top: 70px; padding: 0 40px; }}
    [data-testid="stMetricValue"] {{ color: #F97316 !important; font-weight: 900 !important; }}
    [data-testid="stMetricLabel"] {{ color: #4B5563 !important; }}
    .stTabs [data-baseweb="tab"] {{ color: #111827 !important; font-weight: 700 !important; }}
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

# --- LOGIN ---
if not st.session_state.auth:
    _, cent, _ = st.columns([1, 1.2, 1])
    with cent.container():
        st.markdown(f'<div style="background:#F9FAFB; padding:40px; border-radius:15px; border:1px solid #E5E7EB; text-align:center; margin-top:100px;">', unsafe_allow_html=True)
        st.subheader("Atlas - Acesso ao Portal")
        with st.form("login"):
            u_in = st.text_input("Usuário").lower().strip()
            p_in = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA", use_container_width=True):
                df_u = get_data("Usuarios").iloc[1:]; df_u.columns = ['U','P','N','F']
                match = df_u[(df_u['U'].astype(str) == u_in) & (df_u['P'].astype(str) == p_in)]
                if not match.empty:
                    st.session_state.auth, st.session_state.user = True, match.iloc[0].to_dict(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- DASHBOARDS ---
else:
    u, role = st.session_state.user, str(st.session_state.user['F']).upper().strip()
    p_nome = u['N'].upper().split()[0]
    
    st.markdown(f'<div class="nav"><b style="color:#F97316; font-size:20px">ATLAS {"GESTÃO" if role != "OPERADOR" else ""}</b><div style="font-size:11px; color:#111827">{u["N"]} | {role}</div></div>', unsafe_allow_html=True)
    with st.sidebar: st.button("🚪 Sair do Sistema", on_click=logout, use_container_width=True)

    df_raw = get_data("DADOS-DIA")
    rk = df_raw.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "M_Str"]; rk['N'] = rk['M_Str'].apply(to_f)

    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.header(f"📊 Painel de Gestão")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média Equipe", f"{rk['N'].mean():.1f}%".replace('.',','))
        c2.metric("Coroas (80%+)", f"{len(rk[rk['N']>=80])} 👑")
        c3.metric("Foco Crítico", len(rk[rk['N']<70]))
        c4.metric("Operadores Ativos", len(rk))
        
        tab_v, tab_m, tab_a = st.tabs(["🎯 Radar da Equipe", "📢 Mural de Avisos", "🔍 Auditoria por Operador"])
        
        with tab_v: st.dataframe(rk.sort_values("N", ascending=False)[["Nome", "M_Str"]], use_container_width=True, hide_index=True)
        with tab_m:
            st.session_state.mural = st.text_area("Aviso no Sininho:", value=st.session_state.mural)
            if st.button("Disparar Mural"): st.success("Atualizado!")
            
        with tab_a:
            st.subheader("Auditoria Detalhada")
            op_sel = st.selectbox("Selecione o Operador:", rk["Nome"].unique())
            if op_sel:
                df_h = df_raw.iloc[26:211, 0:33].copy()
                days = [f"D{i:02d}" for i in range(1, 32)]
                df_h.columns = ["Nome", "Métrica"] + days
                df_h['Métrica'] = df_h['Métrica'].replace({"LIGAÇÃO": "INTERAÇÃO"})
                audit_filt = df_h[df_h['Nome'].apply(norm).str.contains(norm(op_sel.split()[0]), na=False)].copy()
                
                table_disp = audit_filt.copy()
                for col in days: table_disp[col] = table_disp[col].apply(format_cell)
                st.dataframe(table_disp, use_container_width=True, hide_index=True)
                
                st.markdown("---")
                st.subheader(f"📈 Analytics Clean: {op_sel}")
                metrics_av = audit_filt['Métrica'].unique().tolist()
                sel_met = st.multiselect("Visualizar métricas:", metrics_av, default=metrics_av)
                
                chart_data = []
                for _, row in audit_filt[audit_filt['Métrica'].isin(sel_met)].iterrows():
                    m_name = row['Métrica']
                    for d in days:
                        v = to_f(row[d])
                        chart_data.append({"Dia": d.replace("D",""), "Métrica": m_name, "Valor": v})
                
                if chart_data:
                    df_px = pd.DataFrame(chart_data)
                    fig = px.line(df_px, x="Dia", y="Valor", color="Métrica", markers=True, template="plotly_white")
                    fig.update_layout(yaxis_range=[0, 105], margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        # VISÃO OPERADOR (CONGELADA NO PADRÃO LIMPO)
        df_h = df_raw.iloc[26:211, 0:33].copy()
        m_map, m_data = {"INTERAÇÃO": "LIGAÇÃO"}, {}
        u_block = df_h[df_h.iloc[:, 0].apply(norm).str.contains(p_nome, na=False)]
        for m in ["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]:
            row = u_block[u_block.iloc[:, 1].apply(norm) == norm(m_map.get(m, m))]
            if not row.empty:
                v_list = [v for v in row.iloc[0, 2:].tolist() if pd.notna(v) and str(v).strip() not in ["", "0", "0%"]]
                curr = v_list[-1] if v_list else "0%"; prev = v_list[-2] if len(v_list) > 1 else curr
                arr = '▲' if to_f(curr) > to_f(prev) else ('▼' if to_f(curr) < to_f(prev) else "")
                m_data[m] = {"val": format_cell(curr), "arr": arr, "col": get_style(m, curr)}
            else: m_data[m] = {"val": "0%", "arr": "", "col": "#F97316"}

        st.markdown('<div class="m-strip">', unsafe_allow_html=True)
        cols_m = st.columns([0.4, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 0.4])
        with cols_m[0]: 
            with st.popover("🔔"): st.info(st.session_state.mural)
        for i, mk in enumerate(["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]):
            d = m_data[mk]
            with cols_m[i+1]: st.markdown(f'<div class="m-box"><div class="m-lab">{mk}</div><div class="m-val" style="color:{d["col"]}">{d["val"]} {d["arr"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="padding:20px 40px">', unsafe_allow_html=True)
        cl, cr = st.columns(2)
        with cl: st.markdown("### 🏆 Ranking"); st.dataframe(rk.sort_values("N", ascending=False)[["Nome", "M_Str"]], use_container_width=True, hide_index=True, height=380)
        with cr:
            st.markdown(f"### 📈 Evolução Meta")
            u_meta = u_block[u_block.iloc[:, 1].apply(norm) == "META"]
            if not u_meta.empty: st.line_chart(pd.DataFrame({"Dia": [f"{i:02d}" for i in range(1, 32)], "Meta": [to_f(v) for v in u_meta.iloc[0, 2:].values]}).set_index("Dia"), color="#F97316")
        
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cc = st.columns(8); rk_cards = rk.sort_values("N", ascending=False).reset_index(drop=True)
        for i, row in rk_cards.iterrows():
            crown = '👑' if row['N'] >= 80 else ''
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            with cc[i % 8]: st.markdown(f'<div class="card"><div style="font-size:20px; position:absolute; top:-10px; left:40%">{crown}</div><div class="av">{ini}</div><div style="font-size:10px;font-weight:700">{row["Nome"][:13]}</div><b style="color:{"#10B981" if row["N"] >= 80 else "#EF4444"}; font-size:18px">{row["M_Str"]}</b></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
