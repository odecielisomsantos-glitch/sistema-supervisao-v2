import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata
import plotly.graph_objects as go
import numpy as np

# 1. SETUP DE ELITE E ESTADO DO TEMA
st.set_page_config(page_title="Atlas Gestão", page_icon="👔", layout="wide", initial_sidebar_state="collapsed")

# Inicialização do Tema (Padrão: Escuro)
if 'dark_mode' not in st.session_state: st.session_state.dark_mode = True
if 'mural' not in st.session_state: st.session_state.mural = "Foco total na operação!"
if 'auth' not in st.session_state: st.session_state.auth = False

def logout(): st.session_state.clear(); st.rerun()

# 2. DESIGN SYSTEM DINÂMICO (Contraste Inteligente)
is_dark = st.session_state.dark_mode
c = {
    "bg": "#0E1117" if is_dark else "#F0F2F6", 
    "card": "#1F2937" if is_dark else "#FFFFFF",
    "tx": "#FFFFFF" if is_dark else "#111827", 
    "tx_sec": "#9CA3AF" if is_dark else "#4B5563",
    "brd": "#30363D" if is_dark else "#D1D5DB"
}

st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: {c['bg']}; color: {c['tx']}; font-family: 'Inter', sans-serif; transition: 0.3s; }}
    
    /* Navbar e Texto */
    .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: {c['bg']}; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid {c['brd']}; }}
    .stMarkdown, p, h1, h2, h3, h4, span, label {{ color: {c['tx']} !important; }}
    
    /* Métricas e Cards */
    .m-strip {{ margin-top: 55px; padding: 12px 40px; background: {c['card']}; border-bottom: 1px solid {c['brd']}; display: flex; align-items: center; justify-content: space-between; }}
    .m-box {{ text-align: center; flex: 1; border-right: 1px solid {c['brd']}; padding: 5px; }}
    .m-lab {{ font-size: 11px; color: {c['tx_sec']}; font-weight: 800; text-transform: uppercase; }}
    .m-val {{ font-size: 22px; font-weight: 900; color: #F97316; }}
    
    .card {{ position: relative; background: {c['card']}; padding: 15px; border-radius: 12px; border: 1px solid {c['brd']}; text-align: center; height: 175px; color: {c['tx']}; }}
    .av {{ width: 45px; height: 45px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; font-weight: 800; }}
    .main-content {{ margin-top: 70px; padding: 0 40px; }}
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

def format_audit_cell(v):
    if pd.isna(v) or str(v).strip() in ["", "0", "0%"]: return "0%"
    f = to_f(v)
    return f"{f:g}%".replace('.', ',')

# --- LOGIN ---
if not st.session_state.auth:
    _, cent, _ = st.columns([1, 1.2, 1])
    with cent.container():
        st.markdown(f'<div style="background:{c["card"]}; padding:40px; border-radius:15px; border:1px solid {c["brd"]}; text-align:center; margin-top:100px;">', unsafe_allow_html=True)
        st.subheader("Atlas - Acesso ao Portal")
        with st.form("login"):
            u_in = st.text_input("Usuário").lower().strip()
            p_in = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA", use_container_width=True):
                df_u = get_data("Usuarios").iloc[1:]; df_u.columns = ['U','P','N','F']
                match = df_u[(df_u['U'].astype(str) == u_in) & (df_u['P'].astype(str) == p_in)]
                if not match.empty:
                    st.session_state.auth, st.session_state.user = True, match.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Incorreto")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    u = st.session_state.user
    role, p_nome = str(u['F']).upper().strip(), u['N'].upper().split()[0]
    
    # Navbar Superior
    st.markdown(f'<div class="nav"><b style="color:#F97316; font-size:20px">ATLAS {"GESTÃO" if role != "OPERADOR" else ""}</b><div style="font-size:11px">{u["N"]} | {role}</div></div>', unsafe_allow_html=True)
    
    with st.sidebar: 
        st.button("🚪 Sair", on_click=logout, use_container_width=True)
        # CHAVE SELETORA DE MODO DE COR
        st.toggle("🌙 Modo Noturno", value=st.session_state.dark_mode, key="theme_toggle", on_change=lambda: st.session_state.update(dark_mode=not st.session_state.dark_mode))

    df_raw = get_data("DADOS-DIA")
    rk = df_raw.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "M_Str"]; rk['N'] = rk['M_Str'].apply(to_f)

    # VISÃO GESTOR
    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.header(f"💼 Painel de Gestão Atlas")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média Equipe", f"{rk['N'].mean():.1f}%".replace('.',','))
        c2.metric("Coroas (80%+)", f"{len(rk[rk['N']>=80])} 👑")
        c3.metric("Foco Crítico (<70%)", len(rk[rk['N']<70]))
        c4.metric("Ativos", len(rk))
        
        tab_v, tab_m, tab_a = st.tabs(["🎯 Radar", "📢 Mural", "🔍 Auditoria"])
        
        with tab_v: st.dataframe(rk.sort_values("N", ascending=False)[["Nome", "M_Str"]], use_container_width=True, hide_index=True)
        with tab_m:
            st.session_state.mural = st.text_area("Aviso no Sininho:", value=st.session_state.mural)
            if st.button("Disparar"): st.success("Atualizado!")
            
        with tab_a:
            st.subheader("Auditoria por Operador")
            op_sel = st.selectbox("Selecione o Operador:", rk["Nome"].unique())
            if op_sel:
                df_h = df_raw.iloc[26:211, 0:33].copy()
                days = [f"D{i:02d}" for i in range(1, 32)]
                df_h.columns = ["Nome", "Métrica"] + days
                df_h['Métrica'] = df_h['Métrica'].replace({"LIGAÇÃO": "INTERAÇÃO"})
                
                audit_filt = df_h[df_h['Nome'].apply(norm).str.contains(norm(op_sel.split()[0]), na=False)].copy()
                table_disp = audit_filt.copy()
                for col in days: table_disp[col] = table_disp[col].apply(format_audit_cell)
                st.dataframe(table_disp, use_container_width=True, hide_index=True)
                
                # Analytics com Tendência Técnica
                st.markdown("---")
                st.subheader(f"📈 Analytics: {op_sel}")
                col_s, col_t = st.columns([3, 1])
                with col_s:
                    m_opts = audit_filt['Métrica'].unique().tolist()
                    sel_m = st.multiselect("Visualizar:", m_opts, default=m_opts)
                with col_t:
                    st.write(""); show_t = st.toggle("📊 Exibir Tendência", value=False)
                
                fig = go.Figure()
                for m_name in sel_m:
                    row = audit_filt[audit_filt['Métrica'] == m_name].iloc[0]
                    x_r = np.array([int(d.replace("D","")) for d in days])
                    y_r = np.array([to_f(row[d]) for d in days])
                    mask = y_r > 0 
                    if any(mask):
                        fig.add_trace(go.Scatter(x=x_r[mask], y=y_r[mask], name=m_name, mode='lines+markers'))
                        if show_t and len(y_r[mask]) > 1:
                            z = np.polyfit(x_r[mask], y_r[mask], 1)
                            p = np.poly1d(z)
                            fig.add_trace(go.Scatter(x=x_r[mask], y=p(x_r[mask]), name=f"Tendência {m_name}", line=dict(dash='dash', width=2), opacity=0.5))
                
                fig.update_layout(template="plotly_dark" if is_dark else "plotly_white", yaxis_range=[0, 105], margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # VISÃO OPERADOR (ESTÁVEL)
    else:
        st.markdown('<div class="main-content">Módulo Operador Ativo</div>', unsafe_allow_html=True)
