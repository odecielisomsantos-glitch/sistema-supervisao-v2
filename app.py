import streamlit as st
from streamlit_gsheets import GSheetsConnection

# 1. TEMA DARK UNIFICADO
st.set_page_config(page_title="Team Brisa | Gestão", page_icon="🌊", layout="wide")

st.markdown("""
    <style>
    /* Remove elementos padrão e linha branca */
    header, footer, #MainMenu {visibility: hidden;}
    
    /* Fundo Total Escuro (App e Sidebar) */
    .stApp, [data-testid="stSidebar"] { 
        background-color: #0b0f19 !important; 
        color: #e6edf3 !important;
    }
    
    /* Estilo dos Inputs e Forms */
    div[data-testid="stForm"] { background: #161b22; padding: 40px; border-radius: 12px; border: 1px solid #30363d; }
    input { background-color: #0d1117 !important; color: white !important; border: 1px solid #30363d !important; }
    
    /* Botão Verde Profissional */
    div.stButton > button { 
        width: 100%; background: #238636 !important; color: white !important; 
        font-weight: bold; border-radius: 6px; border: none; height: 45px;
    }
    
    /* Ajuste de Texto e Sidebar */
    [data-testid="stSidebar"] .stMarkdown p { color: #8b949e; font-size: 14px; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 600 !important; }
    
    /* Estilo para o Card de Destaque */
    .destaque-box {
        background: rgba(35, 134, 54, 0.1);
        padding: 15px; border-radius: 8px;
        border: 1px solid #238636; margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def get_sheet_data(aba):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=aba, ttl=0, header=None)
        if aba == "Usuarios": df = df.iloc[1:].copy()
        return df
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("<h2 style='text-align:center;'>Portal Team Brisa</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u_in = st.text_input("Usuário").strip().lower()
            p_in = st.text_input("Senha", type="password").strip()
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                df_u = get_sheet_data("Usuarios")
                if df_u is not None:
                    match = df_u[(df_u[0].astype(str).str.lower() == u_in) & (df_u[1].astype(str) == p_in)]
                    if not match.empty:
                        st.session_state.auth, st.session_state.user = True, {"Nome": match.iloc[0][2], "Funcao": match.iloc[0][3].lower()}
                        st.rerun()
                    else: st.error("Acesso negado.")
else:
    u = st.session_state.user
    st.sidebar.markdown(f"### 🌊 Team Brisa")
    st.sidebar.write(f"Usuário: **{u['Nome']}**")
    if st.sidebar.button("Encerrar Sessão"):
        st.session_state.auth = False
        st.rerun()

    if u['Funcao'] == 'gestor':
        st.title("🏆 Painel do Gestor")
        st.markdown("### Ranking TAM")
        
        df_equipe = get_sheet_data("DADOS-DIA")
        if df_equipe is not None:
            # Seleciona A2:B24 (índices 1 a 24)
            ranking = df_equipe.iloc[1:24, [0, 1]]
            ranking.columns = ["Colaborador", "TAM %"]
            
            # Exibe a tabela de forma integrada ao tema dark
            st.dataframe(ranking, use_container_width=True, hide_index=True)
            
            # Box de Destaque Personalizado
            top_1 = ranking.iloc[0]
            st.markdown(f"""
                <div class='destaque-box'>
                    🥇 <b>Destaque do Dia:</b> {top_1['Colaborador']} com performance de <b>{top_1['TAM %']}</b>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.title("📝 Operação")
        st.info("Área em desenvolvimento para registros operacionais.")
