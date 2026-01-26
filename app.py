import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata

# 1. Configurações de Elite
st.set_page_config(page_title="Atlas Gestão", page_icon="👔", layout="wide", initial_sidebar_state="collapsed")

# Inicialização de Memória Persistente
if 'msg_mural' not in st.session_state: st.session_state.msg_mural = "Foco total nas metas de hoje!"
if 'dark_mode' not in st.session_state: st.session_state.dark_mode = True

def toggle_theme(): st.session_state.dark_mode = not st.session_state.dark_mode
def logout(): st.session_state.clear(); st.rerun()

# 2. Design System Otimizado (CSS Maestro)
c = {"bg": "#0E1117" if st.session_state.dark_mode else "#FFF", "txt": "#F9FAFB" if st.session_state.dark_mode else "#111", "brd": "#30363D" if st.session_state.dark_mode else "#E5E7EB", "bar": "#1F2937" if st.session_state.dark_mode else "#F9FAFB"}

st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {c['bg']}; color: {c['txt']}; font-family: 'Inter', sans-serif; }}
    .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: {c['bg']}; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid {c['brd']}; }}
    .main-content {{ margin-top: 70px; padding: 0 40px; }}
    [data-testid="stMetricValue"] {{ font-size: 28px !important; font-weight: 800; color: #F97316; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 24px; }}
    .stTabs [data-baseweb="tab"] {{ height: 50px; font-weight: 700; }}
    </style>
""", unsafe_allow_html=True)

# 3. Motor de Inteligência de Dados
@st.cache_data(ttl=60)
def get_data(aba):
    return st.connection("gsheets", type=GSheetsConnection).read(worksheet=aba, ttl=0, header=None)

def norm(t): return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper().strip()

def to_f(v):
    try:
        val = float(str(v).replace('%', '').replace(',', '.'))
        return val * 100 if val <= 1.0 else val
    except: return 0.0

# --- AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, cent, _ = st.columns([1, 1, 1])
    with cent.form("login"):
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR SISTEMA"):
            df_u = get_data("Usuarios").iloc[1:]; df_u.columns = ['U','P','N','F']
            m = df_u[(df_u['U'].astype(str) == u_in) & (df_u['P'].astype(str) == p_in)]
            if not m.empty:
                st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                st.rerun()
else:
    u, role = st.session_state.user, str(st.session_state.user['F']).upper().strip()
    
    st.markdown(f'<div class="nav"><b style="color:#F97316; font-size:22px">ATLAS GESTÃO</b><div>{u["N"]} | {role}</div></div>', unsafe_allow_html=True)
    with st.sidebar: 
        st.button("🚪 Encerrar Sessão", on_click=logout, use_container_width=True)
        st.toggle("🌙 Modo Noturno", value=st.session_state.dark_mode, on_change=toggle_theme)

    df_raw = get_data("DADOS-DIA")

    # --- PORTAL DO GESTOR ---
    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        
        # Processamento Macro
        rk = df_raw.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]; rk['N'] = rk['Meta_Str'].apply(to_f)
        
        # Observações Importantes (KPIs de impacto)
        avg_team = rk['N'].mean()
        top_performers = len(rk[rk['N'] >= 80])
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média Equipe", f"{avg_team:.1f}%".replace('.', ','), delta=f"{avg_team-80:.1f}% vs Meta")
        c2.metric("Coroas Hoje", f"{top_performers} 👑")
        c3.metric("Operadores", len(rk))
        c4.metric("Status Ref.", "JANEIRO/2026")

        st.divider()

        tab_equipe, tab_mural, tab_auditoria = st.tabs(["📊 Visão Macro", "📢 Mural de Avisos", "🔍 Auditoria por Operador"])

        with tab_equipe:
            st.subheader("Performance Geral")
            # Ranking interativo com cores
            st.dataframe(rk[["Nome", "Meta_Str"]].sort_values("N", ascending=False), use_container_width=True, hide_index=True)

        with tab_mural:
            st.subheader("Central de Comunicação")
            aviso = st.text_area("Este aviso aparecerá no sininho de todos os operadores:", value=st.session_state.msg_mural)
            if st.button("Publicar Imediatamente"):
                st.session_state.msg_mural = aviso
                st.success("Mural atualizado!")

        with tab_auditoria:
            st.subheader("Filtro de Auditoria Sênior")
            op_sel = st.selectbox("Selecione o Operador para Auditoria:", rk["Nome"].unique())
            if op_sel:
                # Busca profunda no intervalo A27:AG211
                df_h = df_raw.iloc[26:211, 0:33].copy()
                df_h.columns = ["Nome", "Metrica"] + [f"Dia {i:02d}" for i in range(1, 32)]
                
                # Mapeamento dinâmico (Ligação -> Interação)
                df_h['Metrica'] = df_h['Metrica'].replace({"LIGAÇÃO": "INTERAÇÃO"})
                
                # Filtro pelo primeiro nome (match robusto)
                match_name = op_sel.upper().split()[0]
                audit = df_h[df_h['Nome'].apply(norm).str.contains(match_name, na=False)]
                
                st.write(f"Histórico Detalhado: **{op_sel}**")
                st.dataframe(audit, use_container_width=True, hide_index=True)

        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- REDIRECIONAMENTO OPERADOR (Segurança) ---
    else:
        st.markdown('<div class="main-content">Redirecionando para Dashboard Operacional...</div>', unsafe_allow_html=True)
        # Aqui reinseriríamos o código do operador se estivesse tudo no mesmo arquivo
