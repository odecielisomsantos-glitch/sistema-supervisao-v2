import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Team Brisa", page_icon="🌊", layout="wide")

# CSS: Navbar, Cards e Animação da Coroa
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFF; font-family: 'Inter', sans-serif; }
    .nav { position: fixed; top: 0; left: 0; width: 100%; height: 50px; background: #F9FAFB; border-bottom: 1px solid #EEE; display: flex; align-items: center; justify-content: space-between; padding: 0 30px; z-index: 1000; font-size: 13px; }
    @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
    .card { position: relative; background: #FFF; padding: 10px; border-radius: 12px; border: 1px solid #F3F4F6; text-align: center; margin-bottom: 20px; height: 160px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .crown { position: absolute; top: -15px; left: 35%; font-size: 20px; animation: float 3s infinite; }
    .av { width: 40px; height: 40px; background: #22D3EE; color: #083344; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 5px; font-weight: bold; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet=aba, ttl=0, header=None)
    return df if aba != "Usuarios" else df.iloc[1:].copy()

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    with st.form("login"):
        u_in, p_in = st.text_input("Usuário").lower().strip(), st.text_input("Senha", type="password").strip()
        if st.form_submit_button("ENTRAR"):
            df_u = get_data("Usuarios")
            # Correção do erro: Usamos nomes de colunas claros
            df_u.columns = ['User', 'Pass', 'Nome', 'Func']
            m = df_u[(df_u['User'].astype(str).str.lower() == u_in) & (df_u['Pass'].astype(str) == p_in)]
            if not m.empty:
                st.session_state.auth, st.session_state.user = True, m.iloc[0].to_dict()
                st.rerun()
            else: st.error("Incorreto")
else:
    u = st.session_state.user
    # Navbar com o nome corrigido
    st.markdown(f'<div class="nav"><b>🌊 Team Brisa</b><div><span style="color:#F97316">●</span> {u["Nome"]} | 2026</div></div>', unsafe_allow_html=True)
    st.write("<br><br>", unsafe_allow_html=True)
    
    df = get_data("DADOS-DIA")
    if df is not None:
        rk = df.iloc[1:24, [0, 1]].dropna()
        rk.columns = ["Nome", "Meta_Str"]
        rk['Meta_Num'] = rk['Meta_Str'].str.replace('%','').str.replace(',','.').astype(float)
        rk = rk.sort_values(by='Meta_Num', ascending=False)

        st.subheader("🏆 Ranking Geral")
        st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True)

        st.subheader("📊 Performance")
        cols = st.columns(8) # 8 colunas para cards pequenos
        for idx, row in rk.reset_index(drop=True).iterrows():
            val = row['Meta_Num']
            # Verde >= 80, Vermelho < 80
            color = "#10B981" if val >= 80 else "#EF4444"
            crown = '<div class="crown">👑</div>' if val >= 80 else ''
            ini = "".join([n[0] for n in row['Nome'].split()[:2]]).upper()
            
            with cols[idx % 8]:
                st.markdown(f"""
                <div class="card">
                    {crown}<div class="av">{ini}</div>
                    <div style="font-size:9px; font-weight:bold; height:25px; overflow:hidden;">{row['Nome']}</div>
                    <div style="font-size:18px; font-weight:800; color:{color};">{row['Meta_Str']}</div>
                </div>
                """, unsafe_allow_html=True)
