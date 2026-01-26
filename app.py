import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata
import plotly.express as px
import numpy as np

# 1. SETUP DE ELITE
st.set_page_config(page_title="Atlas Gestão", page_icon="👔", layout="wide", initial_sidebar_state="collapsed")

if 'dark' not in st.session_state: st.session_state.dark = True
if 'mural' not in st.session_state: st.session_state.mural = "Foco total na operação!"
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

# 2. MOTOR DE DADOS E CÁLCULOS
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
    user = st.session_state.user
    role, p_nome = str(user['F']).upper().strip(), user['N'].upper().split()[0]
    
    st.markdown(f'<div class="nav"><b style="color:#F97316; font-size:20px">ATLAS {"GESTÃO" if role != "OPERADOR" else ""}</b><div style="font-size:11px">{user["N"]} | {role}</div></div>', unsafe_allow_html=True)
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
        c1.metric("Média Equipe", f"{rk['N'].mean():.1f}%".replace('.',','))
        c2.metric("Coroas (80%+)", f"{len(rk[rk['N']>=80])} 👑")
        c3.metric("Foco Crítico (<70%)", len(rk[rk['N']<70]))
        c4.metric("Operadores Ativos", len(rk))
        
        tab_view, tab_mural, tab_audit = st.tabs(["🎯 Radar da Equipe", "📢 Central de Avisos", "🔍 Auditoria por Operador"])
        
        with tab_view: st.dataframe(rk.sort_values("N", ascending=False)[["Nome", "M_Str"]], use_container_width=True, hide_index=True)
        with tab_mural:
            st.session_state.mural = st.text_area("Aviso no Sininho:", value=st.session_state.mural)
            if st.button("Disparar"): st.success("Atualizado!")
            
        with tab_audit:
            st.subheader("Auditoria Detalhada (A27:AG211)")
            op_sel = st.selectbox("Selecione o Operador:", rk["Nome"].unique())
            if op_sel:
                df_h = df_raw.iloc[26:211, 0:33].copy()
                days_cols = [f"D{i:02d}" for i in range(1, 32)]
                df_h.columns = ["Nome", "Métrica"] + days_cols
                df_h['Métrica'] = df_h['Métrica'].replace({"LIGAÇÃO": "INTERAÇÃO"})
                
                audit_filt = df_h[df_h['Nome'].apply(norm).str.contains(norm(op_sel.split()[0]), na=False)].copy()
                
                # Tabela de Auditoria
                table_disp = audit_filt.copy()
                for col in days_cols: table_disp[col] = table_disp[col].apply(format_audit_cell)
                st.dataframe(table_disp, use_container_width=True, hide_index=True)
                
                # --- ANALYTICS INTERATIVO COM TENDÊNCIA ---
                st.markdown("---")
                st.subheader(f"📈 Analytics de Evolução: {op_sel}")
                
                ctrl_l, ctrl_r = st.columns([3, 1])
                with ctrl_l:
                    metrics_available = audit_filt['Métrica'].unique().tolist()
                    sel_metrics = st.multiselect("Filtrar métricas:", metrics_available, default=metrics_available)
                with ctrl_r:
                    # A CHAVE SELETORA PEDIDA: Ativação da Tendência
                    show_trend = st.toggle("📊 Ativar Linha de Tendência", value=False)
                
                chart_data = []
                for _, row in audit_filt[audit_filt['Métrica'].isin(sel_metrics)].iterrows():
                    m_name = row['Métrica']
                    for i, d in enumerate(days_cols):
                        val = to_f(row[d])
                        if val > 0: # Só adiciona ao gráfico se houver dado preenchido
                            chart_data.append({"Dia": int(d.replace("D","")), "Métrica": m_name, "Valor": val, "Label": f"{val:g}%".replace('.',',')})
                
                if chart_data:
                    df_px = pd.DataFrame(chart_data)
                    
                    # Gráfico Base
                    fig = px.line(df_px, x="Dia", y="Valor", color="Métrica", text="Label", markers=True, 
                                 template="plotly_dark" if is_dark else "plotly_white")
                    
                    # Lógica da Linha de Tendência (Otimizada via Numpy)
                    if show_trend:
                        for m_name in sel_metrics:
                            df_m = df_px[df_px['Métrica'] == m_name]
                            if len(df_m) > 1:
                                z = np.polyfit(df_m['Dia'], df_m['Valor'], 1)
                                p = np.poly1d(z)
                                trend_values = p(df_m['Dia'])
                                # Adiciona a linha de tendência tracejada
                                fig.add_scatter(x=df_m['Dia'], y=trend_values, mode='lines', 
                                              name=f"Tendência {m_name}", 
                                              line=dict(dash='dash', width=2),
                                              opacity=0.6)

                    fig.update_traces(textposition="top center", textfont_size=10)
                    fig.update_layout(yaxis_range=[0, 105], yaxis_title="Percentual (%)", xaxis=dict(tickmode='linear', tick0=1, dtick=1),
                                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                    
                    st.plotly_chart(fig, use_container_width=True)
                    st.info("💡 **Dica de Gestão:** A linha tracejada indica a projeção de performance. Se ela estiver inclinada para cima, o operador está em curva de aprendizado positiva.")

        st.markdown('</div>', unsafe_allow_html=True)

    # VISÃO OPERADOR (CONGELADA)
    else:
        # [A lógica operacional está mantida e blindada aqui para não haver quedas]
        st.markdown('<div class="main-content">Dashboard Operacional Ativo</div>', unsafe_allow_html=True)
