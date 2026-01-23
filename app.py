import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Team Brisa v2", page_icon="🌊")

st.title("🌊 Sistema Team Brisa - Conexão v2")

try:
    # Criando a conexão
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Lendo a aba Usuarios
    df = conn.read(worksheet="Usuarios", ttl=0)
    
    st.success("✅ Conexão estabelecida com sucesso!")
    st.write("Dados encontrados na planilha:")
    st.dataframe(df)
    
except Exception as e:
    st.error("❌ Falha na conexão")
    st.code(f"Erro detalhado: {e}")

if st.button("Verificar Sessão"):
    st.balloons()
