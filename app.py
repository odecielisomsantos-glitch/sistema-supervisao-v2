import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata

# 1. Configuração e Estado
st.set_page_config(page_title="Atlas", page_icon="🌊", layout="wide", initial_sidebar_state="collapsed")

if 'dark_mode' not in st.session_state: st.session_state.dark_mode = False
if 'msg_mural' not in st.session_state: st.session_state.msg_mural = "Sem avisos novos."

def toggle_theme(): st.session_state.dark_mode = not st.session_state.dark_mode
def logout(): st.session_state.clear(); st.rerun()

# 2. CSS Turbinado (Fontes Maiores e Alinhamento)
is_dark = st.session_state.dark_mode
c = {"bg": "#0E1117" if is_dark else "#FFF", "txt": "#F9FAFB" if is_dark else "#111", "brd": "#30363D" if is_dark else "#E5E7EB", "bar": "#1F2937" if is_dark else "#F9FAFB"}

st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {c['bg']}; color: {c['txt']}; font-family: 'Inter', sans-serif; }}
    .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: {c['bg']}; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid {c['brd']}; }}
    .m-strip {{ margin-top: 55px; padding: 15px 40px; background: {c['bar']}; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid {c['brd']}; }}
    
    /* Fontes Aumentadas conforme solicitado */
    .m-box {{ text-align: center; flex: 1; border-right: 1px solid {c['brd']}; padding: 5px; }}
    .m-lab {{ font-size: 13px; opacity: 0.9; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; }}
    .m-val {{ font-size: 24px; font-weight: 900; display: flex; align-items: center; justify-content: center; gap: 5px; }}
    
    .card {{ position: relative; background: {c['bar']}; padding: 18px; border-radius: 15px; border: 1px solid {c['brd']}; text-align: center; height: 180px; }}
    .crown {{ position: absolute; top: -18px; left: 35%; font-size: 24px; animation: float 3s infinite; }}
    @keyframes float {{ 50% {{ transform: translateY(-7px); }} }}
    .av {{ width: 50px; height: 50px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: 800; }}
    </style>
""", unsafe_allow_html=True)

# 3. Lógica de Dados e Formatação Brasileira
@st.cache_data(ttl=60)
def get_data(aba):
    return st.connection("gsheets", type=GSheetsConnection).read(worksheet=aba, ttl=0, header=None)

def norm(t): return "".join(c for c in unicodedata.normalize('NFD', str(t)) if unicodedata.category(c) != 'Mn').upper().strip()

def to_f(v):
    try:
        val = float(str(v).replace('%', '').replace(',', '.'))
        return val * 100 if val <= 1.0 else val
    except: return 0.0

def format_br(v):
    val = to_f(v)
    return f"{val:g}%".replace('.', ',')

# 4. Semáforo de Cores por Métrica
def get_color(metric, val_str):
    v = to_f(val_str)
    m = norm(metric)
    if m in ["CSAT", "IR", "INTERACAO", "META"]:
        if v >= 80: return "#10B981" # Verde
        if v >= 70: return "#FACC15" # Amarelo
    elif m == "TPC":
        if v >= 95: return "#10B981"
        if v >= 90: return "#FACC15"
    elif m == "PONTUALIDADE":
        if v >= 90: return "#10B981"
        if v >= 85: return "#FACC15"
    return "#F97316" # Laranja padrão Atlas para valores baixos

# 5. Busca Comparativa (Atual vs Anterior)
def fetch_metrics_with_trends(df_block, p_match):
    metrics = ["CSAT", "TPC", "INTERACAO", "IR", "PONTUALIDADE", "META"]
    results = {}
    u_data = df_block[df_block.iloc[:, 0].apply(norm).str.contains(norm(p_match), na=False)]
    
    for m in metrics:
        row = u_data[u_data.iloc[:, 1].apply(norm) == m]
        if not row.empty:
            # Pega todos os valores preenchidos da linha
            vals = row.iloc[0, 2:].values.tolist()
            valid_vals = [v for v in vals if pd.notna(v) and str(v).strip() not in ["", "0", "0%"]]
            
            if len(valid_vals) >= 1:
                curr = valid_vals[-1]
                prev = valid_vals[-2] if len(valid_vals) > 1 else curr
                
                # Define a seta baseada na comparação
                diff = to_f(curr) - to_f(prev)
                arrow = ""
                if diff > 0: arrow = '<span style="color:#10B981; font-size:18px;">▲</span>'
                elif diff < 0: arrow = '<span style="color:#EF4444; font-size:18px;">▼</span>'
                
                results[m] = {"val": format_br(curr), "arrow": arrow, "color": get_color(m, curr)}
            else:
                results[m] = {"val": "0%", "arrow": "", "color": "#F97316"}
        else:
            results[m] = {"val": "0%", "arrow": "", "color": "#F97316"}
    return results

# --- AUTH & DASHBOARD ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.1, 1])
    with center.form("login"):
        st.subheader("Atlas - Acesso")
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR"):
            df_u = get_data("Usuarios").iloc[1:]
            df_u.columns = ['U','P','N','F']
            m = df_u[(df_u['U'].astype(str) == u_in) & (df_u['P'].astype(str) == p_in)]
            if not m.empty:
                st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                st.rerun()
else:
    u = st.session_state.user
    role, p_nome = str(u['F']).upper().strip(), u['N'].upper().split()[0]

    st.markdown(f'<div class="nav"><b style="color:#F97316; font-size:22px">ATLAS</b><div style="font-size:12px; font-weight:600;">{u["N"]} | {role}</div></div>', unsafe_allow_html=True)
    with st.sidebar: st.button("🚪 ENCERRAR SESSÃO", on_click=logout, use_container_width=True)

    df_raw = get_data("DADOS-DIA")

    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<br><br><br>', unsafe_allow_html=True)
        st.session_state.msg_mural = st.text_area("📢 Mural de Avisos", value=st.session_state.msg_mural)
        st.dataframe(df_raw.iloc[1:24, [0, 1]], use_container_width=True, hide_index=True)
    else:
        # Ranking e Histórico
        rk = df_raw.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "M_Str"]; rk['N'] = rk['M_Str'].apply(to_f)
        rk = rk.sort_values(by='N', ascending=False).reset_index(drop=True)
        
        df_h = df_raw.iloc[26:211, 0:33].copy()
        metrics_data = fetch_metrics_with_trends(df_h, p_nome)

        # Barra de Métricas com Semáforo e Setas
        st.markdown('<div class="m-strip">', unsafe_allow_html=True)
        cols = st.columns([0.4, 1.1, 1.1, 1.1, 1.1, 1.1, 1.1, 0.4])
        with cols[0]: 
            with st.popover("🔔"): st.info(st.session_state.msg_mural)
        
        m_list = ["CSAT", "TPC", "INTERACAO", "IR", "PONTUALIDADE", "META"]
        for i, m_key in enumerate(m_list):
            m_info = metrics_data[m_key]
            with cols[i+1]:
                st.markdown(f'''
                    <div class="m-box">
                        <div class="m-lab">{m_key}</div>
                        <div class="m-val" style="color:{m_info['color']};">
                            {m_info['val']} {m_info['arrow']}
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
        
        with cols[7]: st.toggle("🌙", value=st.session_state.dark_mode, on_change=toggle_theme)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div style="padding: 20px 40px;">', unsafe_allow_html=True)
        l, r = st.columns(2)
        with l:
            st.markdown("### 🏆 Ranking")
            st.dataframe(rk[["Nome", "M_Str"]], use_container_width=True, hide_index=True, height=400)
        with r:
            st.markdown(f"### 📈 Evolução Meta - {p_nome.title()}")
            u_row = df_h[(df_h.iloc[:, 0].apply(norm).str.contains(norm(p_nome))) & (df_h.iloc[:, 1].apply(norm) == "META")]
            if not u_row.empty:
                y = [to_f(v) for v in u_row.iloc[0, 2:].values]
                st.line_chart(pd.DataFrame({"Dia": [f"{i:02d}" for i in range(1, 32)], "Meta": y}).set_index("Dia"), color="#F97316")

        # Cards com Coroa
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        c_cards = st.columns(8)
        for i, row in rk.iterrows():
            crw = '<div class="crown">👑</div>' if row['N'] >= 80 else ''
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            with c_cards[i % 8]:
                st.markdown(f'''<div class="card">{crw}<div class="av">{ini}</div><div style="font-size:10px;font-weight:700;">{row["Nome"][:12]}</div><b style="color:{"#10B981" if row["N"] >= 80 else "#EF4444"}">{row["M_Str"]}</b></div>''', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
