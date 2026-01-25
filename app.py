import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configuração e Estética (Atlas Design System)
st.set_page_config(page_title="Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

if 'dark_mode' not in st.session_state: st.session_state.dark_mode = False
if 'msg_global' not in st.session_state: st.session_state.msg_global = "Sem novos avisos da gestão."

def toggle_theme(): st.session_state.dark_mode = not st.session_state.dark_mode

def logout():
    st.session_state.clear()
    st.rerun()

# CSS Consolidado (Performance Máxima)
is_dark = st.session_state.dark_mode
c = {"bg": "#0E1117" if is_dark else "#FFF", "txt": "#F9FAFB" if is_dark else "#111", "brd": "#30363D" if is_dark else "#E5E7EB", "bar": "#1F2937" if is_dark else "#F9FAFB"}

st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {c['bg']}; color: {c['txt']}; font-family: 'Inter', sans-serif; transition: 0.2s; }}
    .nav-top {{ position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: {c['bg']}; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid {c['brd']}; }}
    .metric-strip {{ margin-top: 55px; padding: 15px 40px; background: {c['bar']}; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid {c['brd']}; }}
    .card {{ position: relative; background: {c['bar']}; padding: 18px; border-radius: 15px; border: 1px solid {c['brd']}; text-align: center; margin-bottom: 25px; height: 180px; }}
    .crown {{ position: absolute; top: -18px; left: 35%; font-size: 24px; animation: float 3s infinite ease-in-out; }}
    @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
    .av-icon {{ width: 50px; height: 50px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }}
    .btn-sair {{ background: #EF4444; color: white !important; padding: 6px 15px; border-radius: 8px; font-weight: bold; font-size: 11px; border: none; cursor: pointer; }}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def get_data(aba):
    try: return st.connection("gsheets", type=GSheetsConnection).read(worksheet=aba, ttl=0, header=None)
    except: return None

def clean_v(v):
    if pd.isna(v) or v == "" or str(v).strip() == "0%": return 0.0
    val = str(v).replace('%','').replace(',','.').strip()
    try: return float(val) if float(val) <= 1 else float(val)/100
    except: return 0.0

# --- AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.2, 1])
    with center.form("login"):
        st.subheader("Atlas - Acesso")
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR PORTAL"):
            df_u = get_data("Usuarios")
            if df_u is not None:
                df_u = df_u.iloc[1:]; df_u.columns = ['User', 'Pass', 'Nome', 'Func']
                match = df_u[(df_u['User'].astype(str) == u_in) & (df_u['Pass'].astype(str) == p_in)]
                if not match.empty:
                    st.session_state.auth, st.session_state.user = True, match.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Login Inválido")

# --- DASHBOARD ---
else:
    u = st.session_state.user
    role = str(u['Func']).upper().strip()
    p_nome = u['Nome'].upper().split()[0]

    # Navbar Superior Otimizada
    st.markdown(f'''
        <div class="nav-top">
            <b style="color:#F97316; font-size:22px">ATLAS</b>
            <div style="display:flex; align-items:center; gap:20px;">
                <span style="font-size:12px; font-weight:600;">{u["Nome"]} | {role}</span>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    with st.sidebar: st.button("SAIR DO SISTEMA", on_click=logout, use_container_width=True) # Maestro Logout

    df_raw = get_data("DADOS-DIA")

    # --- PÁGINA DO GESTOR ---
    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<br><br><br>', unsafe_allow_html=True)
        st.header(f"💼 Painel de Gestão - {p_nome}")
        msg_input = st.text_area("📢 Publicar Aviso aos Operadores", placeholder="Digite aqui a mensagem para o Sininho...")
        if st.button("Enviar para Equipe"):
            st.session_state.msg_global = msg_input
            st.success("Aviso atualizado com sucesso!")
        
        st.divider()
        st.subheader("Resumo Geral da Equipe")
        rk_full = df_raw.iloc[1:24, [0, 1]].dropna()
        rk_full.columns = ["Operador", "Meta %"]
        st.dataframe(rk_full, use_container_width=True, hide_index=True)

    # --- PÁGINA DO OPERADOR ---
    else:
        # Processamento Meta
        rk = df_raw.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]
        rk['N'] = rk['Meta_Str'].apply(clean_v) * 100
        rk = rk.sort_values(by='N', ascending=False).reset_index(drop=True)
        
        u_rk = rk[rk['Nome'].astype(str).str.upper().str.contains(p_nome)]
        pos = f"{u_rk.index[0] + 1}º" if not u_rk.empty else "N/A"

        # Barra de Métricas Interativa
        st.markdown('<div class="metric-strip">', unsafe_allow_html=True)
        cs = st.columns([0.5, 1.5, 1.5, 1.5, 2.5, 0.5])
        with cs[0]: 
            with st.popover("🔔"): st.info(st.session_state.msg_global) # Recebe aviso do Gestor
        with cs[1]: st.markdown(f'<div style="text-align:center"><small>COLOCAÇÃO</small><br><b>🏆 {pos}</b></div>', unsafe_allow_html=True)
        with cs[2]: st.markdown(f'<div style="text-align:center"><small>STATUS</small><br><b>🟢 ONLINE</b></div>', unsafe_allow_html=True)
        with cs[3]: st.markdown(f'<div style="text-align:center"><small>PERÍODO</small><br><b>JAN / 2026</b></div>', unsafe_allow_html=True)
        with cs[4]: st.markdown(f'<div style="text-align:center"><small>UNIDADE</small><br><b>CALL CENTER PDF</b></div>', unsafe_allow_html=True)
        with cs[5]: st.toggle("🌙", value=st.session_state.dark_mode, on_change=toggle_theme, key="tgl")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div style="padding: 20px 40px;">', unsafe_allow_html=True)
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("### 🏆 Ranking da Equipe")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True, height=400)
        with col_r:
            st.markdown(f"### 📈 Evolução Diária - {p_nome}")
            df_hist = df_raw.iloc[26:211, 0:33].copy()
            df_hist.columns = ["Nome", "M"] + [f"{i:02d}" for i in range(1, 32)]
            u_data = df_hist[(df_hist['Nome'].astype(str).str.upper().str.contains(p_nome)) & (df_hist['M'].astype(str).str.upper() == "META")]
            if not u_data.empty:
                y = [clean_v(v) * 100 for v in u_data.iloc[0, 2:].values]
                df_chart = pd.DataFrame({"Dia": [f"{i:02d}" for i in range(1, 32)], "Meta %": y}).set_index("Dia")
                st.line_chart(df_chart, color="#F97316") # Eixos 01-31 e 0-100% fixados

        # Performance Individual
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cards = st.columns(8)
        for i, row in rk.iterrows():
            crown = '<div class="crown">👑</div>' if row['N'] >= 80 else ''
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            with cards[i % 8]:
                st.markdown(f'''<div class="card">{crown}<div class="av-icon">{ini}</div><div style="font-size:10px;font-weight:700;">{row["Nome"][:15]}</div><b style="font-size:20px;color:{"#10B981" if row["N"] >= 80 else "#EF4444"}">{row["Meta_Str"]}</b></div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
