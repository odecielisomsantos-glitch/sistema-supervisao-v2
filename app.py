import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. SETUP DE ELITE
st.set_page_config(page_title="Atlas Gestão", page_icon="👔", layout="wide", initial_sidebar_state="collapsed")

if 'dark' not in st.session_state: st.session_state.dark = True
if 'mural' not in st.session_state: st.session_state.mural = "Foco total!"
if 'auth' not in st.session_state: st.session_state.auth = False

def toggle(): st.session_state.dark = not st.session_state.dark
def logout(): st.session_state.clear(); st.rerun()

is_dark = st.session_state.dark
c = {"bg": "#0E1117" if is_dark else "#F0F2F6", "card": "#1F2937" if is_dark else "#FFF", "tx": "#F9FAFB" if is_dark else "#111", "brd": "#30363D" if is_dark else "#E5E7EB"}

st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: {c['bg']}; color: {c['tx']}; font-family: 'Inter', sans-serif; }}
    .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: {c['bg']}; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid {c['brd']}; }}
    .login-box {{ background: {c['card']}; padding: 40px; border-radius: 15px; border: 1px solid {c['brd']}; text-align: center; margin-top: 100px; }}
    .m-strip {{ margin-top: 55px; padding: 12px 40px; background: {c['card']}; border-bottom: 1px solid {c['brd']}; }}
    .m-box {{ text-align: center; flex: 1; border-right: 1px solid {c['brd']}; padding: 5px; }}
    .m-lab {{ font-size: 11px; opacity: 0.8; font-weight: 800; text-transform: uppercase; }}
    .m-val {{ font-size: 22px; font-weight: 900; display: flex; align-items: center; justify-content: center; gap: 4px; }}
    .card {{ position: relative; background: {c['card']}; padding: 15px; border-radius: 12px; border: 1px solid {c['brd']}; text-align: center; height: 175px; }}
    .crown {{ position: absolute; top: -15px; left: 35%; font-size: 22px; animation: float 3s infinite; }}
    @keyframes float {{ 50% {{ transform: translateY(-6px); }} }}
    .av {{ width: 45px; height: 45px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; font-weight: 800; }}
    .main-content {{ margin-top: 70px; padding: 0 40px; }}
    </style>
""", unsafe_allow_html=True)

# 2. MOTOR DE DADOS
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

def format_audit_cell(v):
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
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.subheader("Atlas - Acesso")
        with st.form("login"):
            u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA", use_container_width=True):
                df_u = get_data("Usuarios").iloc[1:]; df_u.columns = ['U','P','N','F']
                match = df_u[(df_u['U'].astype(str) == u_in) & (df_u['P'].astype(str) == p_in)]
                if not match.empty:
                    st.session_state.auth, st.session_state.user = True, match.iloc[0].to_dict()
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- DASHBOARDS ---
else:
    u = st.session_state.user
    role, p_nome = str(u['F']).upper().strip(), u['N'].upper().split()[0]
    st.markdown(f'<div class="nav"><b style="color:#F97316; font-size:20px">ATLAS {"GESTÃO" if role != "OPERADOR" else ""}</b><div style="font-size:11px">{u["N"]} | {role}</div></div>', unsafe_allow_html=True)
    with st.sidebar: 
        st.button("Sair", on_click=logout, use_container_width=True)
        st.toggle("🌙 Modo Noturno", value=st.session_state.dark, on_change=toggle)

    df_raw = get_data("DADOS-DIA")
    rk = df_raw.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "M_Str"]; rk['N'] = rk['M_Str'].apply(to_f)

    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.header(f"📊 Painel de Gestão Atlas")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média Equipe", f"{rk['N'].mean():.1f}%".replace('.',','), delta=f"{rk['N'].mean()-80:.1f}%")
        c2.metric("Coroas (80%+)", f"{len(rk[rk['N']>=80])} 👑")
        c3.metric("Foco Crítico", len(rk[rk['N']<70]))
        c4.metric("Ativos", len(rk))
        
        t_view, t_mural, t_audit = st.tabs(["🎯 Radar", "📢 Mural", "🔍 Auditoria"])
        
        with t_view: st.dataframe(rk.sort_values("N", ascending=False)[["Nome", "M_Str"]], use_container_width=True, hide_index=True)
        with t_mural:
            st.session_state.mural = st.text_area("Aviso:", value=st.session_state.mural)
            if st.button("Disparar"): st.success("Atualizado!")
            
        with t_audit:
            st.subheader("Auditoria por Operador")
            op_sel = st.selectbox("Selecione o Operador:", rk["Nome"].unique())
            if op_sel:
                df_h = df_raw.iloc[26:211, 0:33].copy()
                days = [f"D{i:02d}" for i in range(1, 32)]
                df_h.columns = ["Nome", "Métrica"] + days
                df_h['Métrica'] = df_h['Métrica'].replace({"LIGAÇÃO": "INTERAÇÃO"})
                
                # Dados Auditados
                audit_filt = df_h[df_h['Nome'].apply(norm).str.contains(norm(op_sel.split()[0]), na=False)].copy()
                
                # Tabela de Auditoria com Porcentagem Real
                table_disp = audit_filt.copy()
                for col in days: table_disp[col] = table_disp[col].apply(format_audit_cell)
                st.dataframe(table_disp, use_container_width=True, hide_index=True)
                
                # --- ANALYTICS CLEAN COM TENDÊNCIA TÉCNICA ---
                st.markdown("---")
                st.subheader(f"📈 Analytics de Evolução: {op_sel}")
                
                col_ctrl_1, col_ctrl_2 = st.columns([3, 1])
                with col_ctrl_1:
                    m_opts = audit_filt['Métrica'].unique().tolist()
                    sel_m = st.multiselect("Visualizar métricas:", m_opts, default=m_opts)
                with col_ctrl_2:
                    st.write("") # Alinhamento
                    show_t = st.toggle("📊 Exibir Linha de Tendência", value=False)
                
                # Preparação do gráfico (Foco na limpeza visual)
                fig = go.Figure()
                
                for m_name in sel_m:
                    row = audit_filt[audit_filt['Métrica'] == m_name].iloc[0]
                    # Filtra apenas dias com dados para não distorcer a tendência
                    x_raw = np.array([int(d.replace("D","")) for d in days])
                    y_raw = np.array([to_f(row[d]) for d in days])
                    mask = y_raw > 0 
                    
                    if any(mask):
                        # Linha de Performance (Sem labels fixos, apenas no hover)
                        fig.add_trace(go.Scatter(x=x_raw[mask], y=y_raw[mask], name=m_name, mode='lines+markers',
                                                 hovertemplate='%{y:.2f}%<extra></extra>'))
                        
                        # Linha de Tendência (Regressão Linear que corta o gráfico)
                        if show_t and len(y_raw[mask]) > 1:
                            z = np.polyfit(x_raw[mask], y_raw[mask], 1)
                            p = np.poly1d(z)
                            # A linha de tendência corta os pontos existentes
                            fig.add_trace(go.Scatter(x=x_raw[mask], y=p(x_raw[mask]), name=f"Tendência {m_name}",
                                                     line=dict(dash='dash', width=2), opacity=0.5, mode='lines'))

                fig.update_layout(template="plotly_dark" if is_dark else "plotly_white",
                                  yaxis_range=[0, 105], yaxis_title="Percentual (%)", xaxis_title="Dias",
                                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                  margin=dict(l=0, r=0, t=30, b=0))
                
                st.plotly_chart(fig, use_container_width=True)
                st.caption("ℹ️ A Linha de Tendência (tracejada) indica se o operador está em curva de evolução ou regressão.")

        st.markdown('</div>', unsafe_allow_html=True)

    # VISÃO OPERADOR (ESTÁVEL)
    else:
        df_h = df_raw.iloc[26:211, 0:33].copy()
        m_map, m_data = {"INTERAÇÃO": "LIGAÇÃO"}, {}
        u_block = df_h[df_h.iloc[:, 0].apply(norm).str.contains(p_nome, na=False)]
        
        for m in ["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]:
            row = u_block[u_block.iloc[:, 1].apply(norm) == norm(m_map.get(m, m))]
            if not row.empty:
                vals = [v for v in row.iloc[0, 2:].tolist() if pd.notna(v) and str(v).strip() not in ["", "0", "0%"]]
                curr = vals[-1] if vals else "0%"; prev = vals[-2] if len(vals) > 1 else curr
                arr = '▲' if to_f(curr) > to_f(prev) else ('▼' if to_f(curr) < to_f(prev) else "")
                m_data[m] = {"val": f"{to_f(curr):g}%".replace('.',','), "arr": arr, "col": get_style(m, curr)}
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
        with cl:
            st.markdown("### 🏆 Ranking")
            st.dataframe(rk.sort_values("N", ascending=False)[["Nome", "M_Str"]], use_container_width=True, hide_index=True, height=380)
        with cr:
            st.markdown(f"### 📈 Evolução Meta - {p_nome.title()}")
            u_meta = u_block[u_block.iloc[:, 1].apply(norm) == "META"]
            if not u_meta.empty:
                st.line_chart(pd.DataFrame({"Dia": [f"{i:02d}" for i in range(1, 32)], "Meta": [to_f(v) for v in u_meta.iloc[0, 2:].values]}).set_index("Dia"), color="#F97316")
        
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cc = st.columns(8); rk_cards = rk.sort_values("N", ascending=False).reset_index(drop=True)
        for i, row in rk_cards.iterrows():
            crw = '<div class="crown">👑</div>' if row['N'] >= 80 else ''
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            with cc[i % 8]: st.markdown(f'<div class="card">{crw}<div class="av">{ini}</div><div style="font-size:10px;font-weight:700">{row["Nome"][:13]}</div><b style="color:{"#10B981" if row["N"] >= 80 else "#EF4444"}; font-size:18px">{row["M_Str"]}</b></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
