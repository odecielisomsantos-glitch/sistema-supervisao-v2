import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import unicodedata

# 1. SETUP DE ELITE
st.set_page_config(page_title="Atlas - Centro de Comando", page_icon="👔", layout="wide", initial_sidebar_state="collapsed")

if 'dark' not in st.session_state: st.session_state.dark = True
if 'mural' not in st.session_state: st.session_state.mural = "Foco total na operação!"

def toggle(): st.session_state.dark = not st.session_state.dark
def logout(): st.session_state.clear(); st.rerun()

# 2. DESIGN SYSTEM (Scannability & Clarity)
c = {"bg": "#0E1117" if st.session_state.dark else "#FFF", "tx": "#F9FAFB" if st.session_state.dark else "#111", "brd": "#30363D" if st.session_state.dark else "#E5E7EB", "bar": "#1F2937" if st.session_state.dark else "#F9FAFB"}

st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: {c['bg']}; color: {c['tx']}; font-family: 'Inter', sans-serif; }}
    .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: 55px; background: {c['bg']}; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1001; border-bottom: 1px solid {c['brd']}; }}
    .m-strip {{ margin-top: 55px; padding: 12px 40px; background: {c['bar']}; border-bottom: 1px solid {c['brd']}; }}
    .m-box {{ text-align: center; flex: 1; border-right: 1px solid {c['brd']}; padding: 5px; }}
    .m-lab {{ font-size: 11px; opacity: 0.8; font-weight: 800; text-transform: uppercase; }}
    .m-val {{ font-size: 22px; font-weight: 900; display: flex; align-items: center; justify-content: center; gap: 4px; }}
    .card {{ position: relative; background: {c['bar']}; padding: 15px; border-radius: 12px; border: 1px solid {c['brd']}; text-align: center; height: 175px; }}
    .crown {{ position: absolute; top: -15px; left: 35%; font-size: 22px; animation: float 3s infinite; }}
    @keyframes float {{ 50% {{ transform: translateY(-6px); }} }}
    .av {{ width: 45px; height: 45px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 8px; font-weight: 800; }}
    .main-g {{ margin-top: 70px; padding: 0 40px; }}
    </style>
""", unsafe_allow_html=True)

# 3. MOTOR DE DADOS
@st.cache_data(ttl=60)
def get_data(aba): return st.connection("gsheets", type=GSheetsConnection).read(worksheet=aba, ttl=0, header=None)

def norm(t): return "".join(ch for ch in unicodedata.normalize('NFD', str(t)) if unicodedata.category(ch) != 'Mn').upper().strip()

def to_f(v):
    try:
        val = float(str(v).replace('%','').replace(',','.'))
        return val * 100 if val <= 1.05 else val
    except: return 0.0

def get_style(metric, val_str):
    v, m = to_f(val_str), norm(metric)
    if m in ["CSAT", "IR", "INTERACAO", "META"]: return "#10B981" if v >= 80 else ("#FACC15" if v >= 70 else "#F97316")
    if m == "TPC": return "#10B981" if v >= 95 else ("#FACC15" if v >= 90 else "#F97316")
    if m == "PONTUALIDADE": return "#10B981" if v >= 90 else ("#FACC15" if v >= 85 else "#F97316")
    return "#F97316"

# --- LOGIN ---
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, cent, _ = st.columns([1, 1, 1])
    with cent.form("login"):
        st.subheader("Atlas - Acesso")
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password")
        if st.form_submit_button("ACESSAR"):
            df_u = get_data("Usuarios").iloc[1:]; df_u.columns = ['U','P','N','F']
            match = df_u[(df_u['U'].astype(str) == u_in) & (df_u['P'].astype(str) == p_in)]
            if not match.empty: st.session_state.auth, st.session_state.user = True, match.iloc[0].to_dict(); st.rerun()
            else: st.error("Incorreto")
else:
    u = st.session_state.user
    role, p_nome = str(u['F']).upper().strip(), u['N'].upper().split()[0]
    
    # Navbar Global
    st.markdown(f'<div class="nav"><b style="color:#F97316; font-size:20px">ATLAS {"GESTÃO" if role != "OPERADOR" else ""}</b><div style="font-size:11px">{u["N"]} | {role}</div></div>', unsafe_allow_html=True)
    with st.sidebar: 
        st.button("Sair", on_click=logout, use_container_width=True)
        st.toggle("🌙 Noturno", value=st.session_state.dark, on_change=toggle)

    df_raw = get_data("DADOS-DIA")
    rk = df_raw.iloc[1:24, [0, 1]].dropna()
    rk.columns = ["Nome", "M_Str"]; rk['N'] = rk['M_Str'].apply(to_f)

    # =================================================================
    # ÁREA DO GESTOR (PROFISSIONAL & INTERATIVA)
    # =================================================================
    if role in ["GESTOR", "GESTÃO"]:
        st.markdown('<div class="main-g">', unsafe_allow_html=True)
        st.header(f"📊 Painel Gestão Strategica")
        
        # KPIs Macro de Encantamento
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média Equipe", f"{rk['N'].mean():.1f}%".replace('.',','), delta=f"{rk['N'].mean()-80:.1f}% vs Meta")
        c2.metric("Coroas (80%+)", f"{len(rk[rk['N']>=80])} 👑")
        c3.metric("Foco Crítico", len(rk[rk['N']<70]))
        c4.metric("Total Operadores", len(rk))
        
        t_radar, t_mural, t_audit = st.tabs(["🎯 Radar da Equipe", "📢 Mural de Avisos", "🔍 Auditoria por Operador"])
        
        with t_radar:
            st.subheader("Ranking Detalhado")
            st.dataframe(rk.sort_values("N", ascending=False), use_container_width=True, hide_index=True)
            
        with t_mural:
            st.subheader("Comunicado para o Time")
            st.session_state.mural = st.text_area("Aviso no Sininho:", value=st.session_state.mural)
            if st.button("Disparar Mural"): st.success("Aviso atualizado!")
            
        with t_audit:
            st.subheader("Histórico A27:AG211")
            op = st.selectbox("Selecione Operador:", rk["Nome"].unique())
            df_h = df_raw.iloc[26:211, 0:33].copy()
            df_h.columns = ["Nome", "Métrica"] + [f"D{i:02d}" for i in range(1, 32)]
            df_h['Métrica'] = df_h['Métrica'].replace({"LIGAÇÃO": "INTERAÇÃO"})
            st.dataframe(df_h[df_h['Nome'].apply(norm).str.contains(op.upper().split()[0], na=False)], use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # =================================================================
    # ÁREA DO OPERADOR (CONGELADA & ESTÁVEL)
    # =================================================================
    else:
        df_h = df_raw.iloc[26:211, 0:33].copy()
        m_map = {"INTERAÇÃO": "LIGAÇÃO"}
        m_data = {}
        u_block = df_h[df_h.iloc[:, 0].apply(norm).str.contains(p_nome, na=False)]
        
        # Busca dinâmica das métricas [Ligação -> Interação]
        for m in ["CSAT", "TPC", "INTERAÇÃO", "IR", "PONTUALIDADE", "META"]:
            row = u_block[u_block.iloc[:, 1].apply(norm) == norm(m_map.get(m, m))]
            if not row.empty:
                vals = [v for v in row.iloc[0, 2:].tolist() if pd.notna(v) and str(v).strip() not in ["", "0", "0%"]]
                curr = vals[-1] if vals else "0%"
                prev = vals[-2] if len(vals) > 1 else curr
                arr = '<span style="color:#10B981;font-size:14px">▲</span>' if to_f(curr) > to_f(prev) else ('<span style="color:#EF4444;font-size:14px">▼</span>' if to_f(curr) < to_f(prev) else "")
                m_data[m] = {"val": f"{to_f(curr):g}%".replace('.',','), "arr": arr, "col": get_style(m, curr)}
            else: m_data[m] = {"val": "0%", "arr": "", "col": "#F97316"}

        # Barra de Métricas
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
            st.dataframe(rk[["Nome", "M_Str"]].sort_values("N", ascending=False), use_container_width=True, hide_index=True, height=380)
        with cr:
            st.markdown(f"### 📈 Evolução Meta - {p_nome.title()}")
            u_meta = u_block[u_block.iloc[:, 1].apply(norm) == "META"]
            if not u_meta.empty:
                st.line_chart(pd.DataFrame({"Dia": [f"{i:02d}" for i in range(1, 32)], "Meta": [to_f(v) for v in u_meta.iloc[0, 2:].values]}).set_index("Dia"), color="#F97316")
        
        # Cards Individuais
        st.markdown("<br>### 📊 Performance Individual", unsafe_allow_html=True)
        cc = st.columns(8)
        for i, row in rk.sort_values("N", ascending=False).reset_index(drop=True).iterrows():
            crown = '<div class="crown">👑</div>' if row['N'] >= 80 else ''
            ini = "".join([n[0] for n in str(row['Nome']).split()[:2]]).upper()
            with cc[i % 8]: st.markdown(f'<div class="card">{crown}<div class="av">{ini}</div><div style="font-size:10px;font-weight:700">{row["Nome"][:13]}</div><b style="color:{"#10B981" if row["N"] >= 80 else "#EF4444"}; font-size:18px">{row["M_Str"]}</b></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
