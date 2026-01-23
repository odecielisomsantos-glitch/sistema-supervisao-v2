import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Team Brisa | Operação", page_icon="🌊", layout="wide")

# CSS: Design Premium dos Cards e Navbar
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background: #FFFFFF; font-family: 'Inter', sans-serif; color: #1F2937; }
    
    .navbar {
        position: fixed; top: 0; left: 0; width: 100%; height: 60px;
        background: #F9FAFB; border-bottom: 1px solid #E5E7EB;
        display: flex; align-items: center; justify-content: space-between;
        padding: 0 40px; z-index: 1000;
    }

    .main-content { margin-top: 80px; }

    /* Estilo do Card Circular */
    .card-container {
        background: #FFFFFF; padding: 25px 15px; border-radius: 20px;
        border: 1px solid #F3F4F6; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
        text-align: center; margin-bottom: 25px; transition: 0.3s;
    }
    .card-container:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }

    .avatar-circle {
        width: 80px; height: 80px; background: #22D3EE; color: #083344;
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        margin: 0 auto 15px; font-size: 28px; font-weight: bold;
    }

    .colab-name { font-size: 14px; font-weight: 800; color: #1F2937; margin-bottom: 10px; line-height: 1.2; text-transform: uppercase; }
    .colab-score { font-size: 32px; font-weight: 800; color: #10B981; margin: 10px 0; }
    .hover-hint { font-size: 11px; color: #9CA3AF; display: flex; align-items: center; justify-content: center; gap: 5px; }
    </style>
""", unsafe_allow_html=True)

def get_data(aba):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=aba, ttl=0, header=None)
        return df if aba != "Usuarios" else df.iloc[1:].copy()
    except: return None

def get_initials(name):
    parts = name.split()
    if len(parts) >= 2: return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper()

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div style='margin-top:100px; text-align:center;'><h2>Acesso Team Brisa</h2></div>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário").strip().lower()
            p = st.text_input("Senha", type="password").strip()
            if st.form_submit_button("ENTRAR"):
                df_u = get_data("Usuarios")
                if df_u is not None:
                    m = df_u[(df_u[0].astype(str).str.lower() == u) & (df_u[1].astype(str) == p)]
                    if not m.empty:
                        st.session_state.auth, st.session_state.user = True, {"Nome": m.iloc[0][2], "Funcao": m.iloc[0][3].lower()}
                        st.rerun()
                    else: st.error("Dados incorretos.")
else:
    u = st.session_state.user
    st.markdown(f"""
        <div class="navbar">
            <div style="font-weight:800; font-size:18px;">🌊 Team Brisa</div>
            <div style="font-size:14px;">
                <span style="color:#F97316;">●</span> <b>{u['Nome']}</b> &nbsp;&nbsp;
                <span style="color:#F97316;">📅</span> 2026 &nbsp;&nbsp;
                <span style="cursor:pointer; color:#EF4444; font-weight:bold;" onclick="window.location.reload();">SAIR</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-content'>", unsafe_allow_html=True)
    
    if u['Funcao'] == 'operador':
        df = get_data("DADOS-DIA")
        if df is not None:
            # Captura e tratamento dos dados
            rk = df.iloc[1:24, [0, 1]].dropna()
            rk.columns = ["Nome", "Meta_Str"]
            
            # Converte a meta para número para poder ordenar corretamente
            rk['Meta_Num'] = rk['Meta_Str'].str.replace('%', '').str.replace(',', '.').astype(float)
            rk = rk.sort_values(by='Meta_Num', ascending=False)
            
            st.markdown("### 🏆 Ranking Geral da Equipe")
            st.dataframe(rk[["Nome", "Meta_Str"]], use_container_width=True, hide_index=True)
            
            st.write("---")
            st.markdown("### 📊 Performance Individual")
            
            cols = st.columns(6) # Mais colunas para um grid profissional
            for idx, row in rk.reset_index(drop=True).iterrows():
                initials = get_initials(row['Nome'])
                with cols[idx % 6]:
                    st.markdown(f"""
                        <div class="card-container">
                            <div class="avatar-circle">{initials}</div>
                            <div class="colab-name">{row['Nome']}</div>
                            <div class="colab-score">{row['Meta_Str']}</div>
                            <div class="hover-hint">👆 Passe o mouse</div>
                        </div>
                    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
