import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Team Brisa", page_icon="🌊", layout="wide")

# CSS Otimizado: Navbar, Animação e Cards
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFF; font-family: 'Inter', sans-serif; }
    .navbar { position: fixed; top: 0; left: 0; width: 100%; height: 60px; background: #F9FAFB; border-bottom: 1px solid #E5E7EB; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; z-index: 1000; }
    @keyframes float { 0%, 100% { transform: translateY(0) rotate(0); } 50% { transform: translateY(-5px) rotate(5deg); } }
    .card { position: relative; background: #FFF; padding: 15px; border-radius: 15px; border: 1px solid #F3F4F6; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; margin-bottom: 30px; height: 190px; }
    .crown { position: absolute; top: -20px; left: 40%; font-size: 25px; animation: float 3s infinite; }
    .av { width: 50px; height: 50px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet=aba, ttl=0, header=None)
    return df if aba != "Usuarios" else df.iloc[1:].copy()

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    with st.form("login"):
        u_in = st.text_input("Usuário").lower().strip()
        p_in = st.text_input("Senha", type="password").strip()
        if st.form_submit_button("ENTRAR"):
            df_u = get_data("Usuarios")
            m = df_u[(df_u[0].astype(str).str.lower() == u_in) & (df_u[1].astype(str) == p_in)]
            if not m.empty:
                st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                st.rerun()
else:
    u = st.session_state.user
    st.markdown(f'<div class="navbar"><b>🌊 Team Brisa</b><div style="font-size:13px"><span style="color:#F97316">●</span> {u[2]} | 2026</div></div>', unsafe_allow_html=True)
    
    st.write("<br><br>", unsafe_allow_html=True)
    df = get_data("DADOS-DIA")
    if df is not None:
        rk = df.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]
        rk['Meta_Num'] = rk['Meta_Str'].str.replace('%','').str.replace(',','.').astype(float)
        rk = rk.sort_values(by='Meta_Num', ascending=False)

        st.subheader("🏆 Ranking Geral")
        st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True)

        st.subheader("📊 Performance Individual")
        cols = st.columns(8) # Mais colunas = cards menores
        for idx, row in rk.reset_index(drop=True).iterrows():
            val = row['Meta_Num']
            color = "#10B981" if val >= 80 else "#EF4444" # Lógica de cores simplificada
            crown = '<div class="crown">👑</div>' if val >= 80 else ''
            ini = "".join([n[0] for n in row['Nome'].split()[:2]]).upper()
            
            with cols[idx % 8]:
                st.markdown(f"""
                <div class="card">
                    {crown}
                    <div class="av">{ini}</div>
                    <div style="font-size:10px; font-weight:bold; height:30px;">{row['Nome']}</div>
                    <div style="font-size:22px; font-weight:800; color:{color};">{row['Meta_Str']}</div>
                </div>
                """, unsafe_allow_html=True)
