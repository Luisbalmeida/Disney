import streamlit as st
import requests
import pandas as pd
from groq import Groq

# 1. Configuração da Página
st.set_page_config(page_title="Disney AI Guide", page_icon="🏰", layout="centered")
st.title("🏰 Guia IA - Disneyland Paris")

# 2. Obter Chave API de forma segura
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    groq_client = Groq(api_key=GROQ_API_KEY)
except:
    st.error("⚠️ Chave GROQ_API_KEY não configurada nos Secrets do Streamlit.")
    st.stop()

# 3. Buscar Dados (Usa cache de 2 minutos para não bloquear a API da Disney)
@st.cache_data(ttl=120)
def buscar_tempos_espera():
    API_URL = "https://api.themeparks.wiki/v1/entity/dae968d5-630d-4719-8b06-3d107e944401/live"
    response = requests.get(API_URL)
    data = response.json()
    
    attractions = []
    for item in data.get("liveData", []):
        if item.get("entityType") == "ATTRACTION" and item.get("status") == "OPERATING":
            wait_time = item.get("queue", {}).get("STANDBY", {}).get("waitTime")
            if wait_time is not None:
                attractions.append({
                    "Nome": item.get("name"),
                    "Espera (min)": wait_time
                })
    return pd.DataFrame(attractions).sort_values(by="Espera (min)")

with st.spinner("A carregar tempos de espera reais da Disney..."):
    df_attractions = buscar_tempos_espera()

st.write("Bem-vindo! Escolhe onde estás e o que já visitaste para obteres a melhor rota.")

# 4. Interface da App
with st.form("disney_form"):
    st.subheader("📍 Onde estás agora?")
    zonas = ['Main Street, U.S.A.', 'Fantasyland', 'Adventureland', 'Frontierland', 'Discoveryland', 'Não sei ao certo']
    localizacao_atual = st.selectbox("Escolhe a tua zona:", zonas)

    st.subheader("🎢 O que já visitaste hoje?")
    # O multiselect é perfeito para mobile (podes pesquisar ou escolher da lista com checkboxes)
    nomes_atracoes = sorted(df_attractions['Nome'].unique())
    visitadas = st.multiselect("Seleciona as atrações:", nomes_atracoes)

    # Botão principal
    submit_button = st.form_submit_button("✨ Pedir Sugestão Mágica ✨")

# 5. Processamento e Ligação ao Groq
if submit_button:
    nao_visitadas = df_attractions[~df_attractions['Nome'].isin(visitadas)].copy()
    
    lista_disponiveis = nao_visitadas.to_string(index=False)
    lista_visitadas = ", ".join(visitadas) if visitadas else "Ainda não visitei nenhuma"

    regras_distancia = """
    Regras de caminhada na Disneyland Paris (velocidade normal de adulto):
    - Mudar de atração DENTRO DA MESMA ZONA: 1 a 3 min.
    - Zonas ADJACENTES (ex: Main Street para Fantasyland): 4 a 6 min.
    - Zonas OPOSTAS (ex: Discoveryland para Adventureland): 8 a 12 min.
    """

    prompt = f"""
    És um guia especializado na Disneyland Paris.

    LOCALIZAÇÃO: {localizacao_atual}
    JÁ VISITADAS: {lista_visitadas}

    ATRAÇÕES DISPONÍVEIS E FILAS:
    {lista_disponiveis}

    {regras_distancia}

    Tendo em conta a localização atual, o tempo de fila e minimizando a caminhada, sugere a MELHOR atração para ir AGORA. Exclui as já visitadas.

    ESTRUTURA DA RESPOSTA:
    1. 🎯 **Recomendação Principal:** [Nome]
    2. 🚶 **Tempo de Caminhada:** [Estimativa de {localizacao_atual} até lá]
    3. ⏱️ **Fila Atual:** [X min]
    4. 💡 **Porquê:** [Razão breve]
    5. 🥈 **Plano B e C (Top 3):**
       - [Nome] (Fila: X min | Caminhada: Y min)
       - [Nome] (Fila: X min | Caminhada: Y min)

    Responde em português de Portugal.
    """

    st.divider() # Linha separadora
    with st.spinner("A consultar o Groq (LLaMA 3.3) para calcular a tua rota..."):
        try:
            response_groq = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile", 
                temperature=0.4
            )
            st.success("Tudo pronto! Aqui está o teu plano:")
            st.markdown(response_groq.choices[0].message.content)
        except Exception as e:
            st.error(f"Erro ao contactar o Groq: {e}")