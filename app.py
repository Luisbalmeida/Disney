import streamlit as st
import requests
import pandas as pd
import json
import os
from datetime import datetime
from groq import Groq
from mistralai import Mistral
import time

# 1. Configuração da Página
st.set_page_config(page_title="Disney AI Guide", page_icon="🏰", layout="wide")
st.title("🏰 Guia IA - Disneyland Paris")

# 2. Obter Chaves API de forma segura
try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    MISTRAL_API_KEY = st.secrets.get("MISTRAL_API_KEY", "")
    
    groq_client = None
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
    
except Exception as e:
    st.warning(f"⚠️ Erro ao configurar IAs: {e}")
    st.info("Configure GROQ_API_KEY e/ou MISTRAL_API_KEY nos Secrets do Streamlit para usar IA.")

# 3. Ficheiro de histórico local
VISITED_FILE = "visited_attractions.json"

# Inicializar cliente Mistral
mistral_client = None
if MISTRAL_API_KEY:
    mistral_client = Mistral(api_key=MISTRAL_API_KEY)

# 3. Ficheiro de histórico local
VISITED_FILE = "visited_attractions.json"

def carregar_historico():
    """Carrega o histórico de atrações visitadas do ficheiro JSON"""
    if os.path.exists(VISITED_FILE):
        try:
            with open(VISITED_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"zona": "", "visitadas": {}, "ultima_atualizacao": ""}
    return {"zona": "", "visitadas": {}, "ultima_atualizacao": ""}

def guardar_historico(historico):
    """Guarda o histórico de atrações visitadas em JSON"""
    historico["ultima_atualizacao"] = datetime.now().isoformat()
    with open(VISITED_FILE, 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

# 4. Buscar Dados (Usa cache de 2 minutos para não bloquear a API da Disney)
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

# Mapeamento de atrações para zonas
ZONA_POR_ATRACAO = {
    "Frontierland": ["Big Thunder Mountain", "Phantom Manor", "Lucky Luke Saloon", "Tom Sawyer Island Rafts"],
    "Fantasyland": ["Cinderella Castle", "It's a Small World", "Sleeping Beauty Castle Walkthrough", "Pinocchio's Fantastic Journey", "Snow White and the Seven Dwarfs", "Peter Pan's Flight", "Dumbo the Flying Elephant", "The Mad Teacups", "Alice's Curious Labyrinth"],
    "Adventureland": ["Jungle Cruise", "Adventure Isle", "Aladdin's Enchanted Carpet", "The Magic Carpets of Aladdin", "Pirates of the Caribbean"],
    "Discoveryland": ["Space Mountain", "Star Tours", "Buzz Lightyear of the Galaxy", "Autopia"],
    "Main Street, U.S.A.": ["Disneyland Railroad", "The Walt Disney Studios Park Railroad"]
}

def obter_zona_atracao(nome_atracao):
    """Retorna a zona de uma atração"""
    for zona, atracoes in ZONA_POR_ATRACAO.items():
        for atracao in atracoes:
            if atracao.lower() in nome_atracao.lower():
                return zona
    return "Desconhecida"

def gerar_recomendacao_ia(prompt, ia_selecionada):
    """Gera recomendação usando a IA selecionada (Groq ou Mistral)"""
    try:
        if ia_selecionada == "Groq":
            if not groq_client:
                return None, "❌ Groq não configurado. Adicione GROQ_API_KEY nos Secrets."
            response = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile", 
                temperature=0.4
            )
            return response.choices[0].message.content, None
        
        elif ia_selecionada == "Mistral":
            if not mistral_client:
                return None, "❌ Mistral não configurado. Adicione MISTRAL_API_KEY nos Secrets."
            response = mistral_client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4
            )
            return response.choices[0].message.content, None
        
        elif ia_selecionada == "Manual":
            return "📝 Ver tabela de atrações na aba 'Histórico' (restantes) para escolher manualmente", None
    
    except Exception as e:
        return None, f"❌ Erro ao contactar IA: {str(e)}"

# Carregar histórico existente
historico = carregar_historico()

with st.spinner("A carregar tempos de espera reais da Disney..."):
    df_attractions = buscar_tempos_espera()

st.write("Bem-vindo! Escolhe onde estás e o que já visitaste para obteres a melhor rota.")

# 5. Tabs para navegação
tab1, tab2, tab3 = st.tabs(["🎯 Recomendações", "📊 Histórico", "❓ Ajuda"])

with tab1:
    # 6. Interface da App - Recomendações
    with st.form("disney_form"):
        st.subheader("📍 Onde estás agora?")
        zonas = ['Main Street, U.S.A.', 'Fantasyland', 'Adventureland', 'Frontierland', 'Discoveryland', 'Não sei ao certo']
        localizacao_atual = st.selectbox("Escolhe a tua zona:", zonas)

        st.subheader("🎢 O que já visitaste hoje?")
        nomes_atracoes = sorted(df_attractions['Nome'].unique())
        visitadas = st.multiselect("Seleciona as atrações:", nomes_atracoes)

        st.subheader("🤖 Qual IA usar?")
        opcoes_ia = ["Groq (Rápido)", "Mistral (Qualidade)", "Manual (Ver tabela)"]
        ia_selecionada = st.selectbox("Escolhe a IA:", opcoes_ia)
        
        # Mapear opção para nome real
        ia_map = {
            "Groq (Rápido)": "Groq",
            "Mistral (Qualidade)": "Mistral",
            "Manual (Ver tabela)": "Manual"
        }
        ia_nome = ia_map[ia_selecionada]

        # Botão principal
        submit_button = st.form_submit_button("✨ Pedir Sugestão ✨")

    # 7. Processamento e Ligação à IA
    if submit_button:
        # Guardar visita no histórico
        for atracao in visitadas:
            if atracao not in historico["visitadas"]:
                zona = obter_zona_atracao(atracao)
                historico["visitadas"][atracao] = {
                    "zona": zona,
                    "data": datetime.now().isoformat(),
                    "tempo_espera": int(df_attractions[df_attractions['Nome'] == atracao]['Espera (min)'].values[0] if len(df_attractions[df_attractions['Nome'] == atracao]) > 0 else 0)
                }
        
        historico["zona"] = localizacao_atual
        guardar_historico(historico)
        st.success("✅ Atrações guardadas no histórico!")
        
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

        st.divider()
        
        if ia_nome == "Manual":
            st.info("📝 **Modo Manual:** Ver tabela de atrações que faltam visitar na aba '📊 Histórico'")
        else:
            with st.spinner(f"A consultar {ia_nome} para calcular a tua rota..."):
                resposta, erro = gerar_recomendacao_ia(prompt, ia_nome)
                if erro:
                    st.error(erro)
                else:
                    st.success(f"✨ Recomendação de {ia_nome}:")
                    st.markdown(resposta)

with tab2:
    st.subheader("📊 Histórico e Tempos de Espera")
    
    # Separar visitadas e não visitadas
    visitadas_nomes = set(historico.get("visitadas", {}).keys())
    nao_visitadas_df = df_attractions[~df_attractions['Nome'].isin(visitadas_nomes)].copy()
    
    # Section 1: Atrações NÃO visitadas (NOVO)
    st.markdown("### 🎢 Atrações que Faltam Visitar")
    
    if len(nao_visitadas_df) > 0:
        # Adicionar zona a cada atração não visitada
        nao_visitadas_df['Zona'] = nao_visitadas_df['Nome'].apply(obter_zona_atracao)
        
        # Filtro por zona
        zonas_nao_visitadas = ['Todas'] + sorted(nao_visitadas_df['Zona'].unique().tolist())
        zona_filtro = st.selectbox("Filtrar por zona:", zonas_nao_visitadas, key="zona_nao_visitadas")
        
        if zona_filtro == "Todas":
            df_nao_visitadas_filtro = nao_visitadas_df
        else:
            df_nao_visitadas_filtro = nao_visitadas_df[nao_visitadas_df['Zona'] == zona_filtro]
        
        # Reordenar colunas
        df_nao_visitadas_display = df_nao_visitadas_filtro[['Nome', 'Zona', 'Espera (min)']].sort_values('Espera (min)')
        
        st.dataframe(df_nao_visitadas_display, use_container_width=True, hide_index=True)
        
        st.metric("Atrações para visitar", len(df_nao_visitadas_filtro))
    else:
        st.success("🎉 Parabéns! Visitaste todas as atrações!")
    
    st.divider()
    
    # Section 2: Atrações já visitadas
    st.markdown("### ✅ Atrações Já Visitadas")
    
    if historico["visitadas"]:
        # Construir DataFrame do histórico
        dados_historico = []
        for atracao, info in historico["visitadas"].items():
            dados_historico.append({
                "Atração": atracao,
                "Zona": info.get("zona", "Desconhecida"),
                "Tempo de Espera (min)": info.get("tempo_espera", 0),
                "Data Visitada": info.get("data", "").split("T")[0]
            })
        
        df_historico = pd.DataFrame(dados_historico).sort_values("Zona")
        
        # Tabela de atrações visitadas na zona
        if historico["zona"]:
            st.info(f"📍 Sua zona atual: **{historico['zona']}**")
            df_zona = df_historico[df_historico["Zona"] == historico["zona"]]
            
            if len(df_zona) > 0:
                st.subheader(f"🎢 Atrações visitadas em {historico['zona']}")
                st.dataframe(df_zona, use_container_width=True, hide_index=True)
            else:
                st.write(f"Ainda não visitaste atrações em {historico['zona']}")
        
        # Tabela geral
        st.subheader("📋 Todas as Atrações Visitadas")
        st.dataframe(df_historico, use_container_width=True, hide_index=True)
        
        # Estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Visitadas", len(historico["visitadas"]))
        with col2:
            tempo_medio = df_historico["Tempo de Espera (min)"].mean()
            st.metric("Tempo Médio de Espera", f"{tempo_medio:.0f} min")
        with col3:
            tempo_total = df_historico["Tempo de Espera (min)"].sum()
            st.metric("Tempo Total Economizado", f"{tempo_total} min")
        
        # Botão para exportar/limpar
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 Exportar Histórico como CSV"):
                csv = df_historico.to_csv(index=False)
                st.download_button(
                    label="Descarregar CSV",
                    data=csv,
                    file_name=f"disney_visited_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        with col2:
            if st.button("📤 Exportar Restantes como CSV"):
                csv = df_nao_visitadas_display.to_csv(index=False)
                st.download_button(
                    label="Descarregar CSV",
                    data=csv,
                    file_name=f"disney_remaining_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        with col3:
            if st.button("🔄 Limpar Histórico"):
                historico["visitadas"] = {}
                guardar_historico(historico)
                st.success("✅ Histórico limpo!")
                st.rerun()
    else:
        st.info("📭 Ainda não visitaste nenhuma atração. Começa a adicionar!")

with tab3:
    st.subheader("❓ Como funciona?")
    st.markdown("""
    ### 📱 Funcionalidades Principais:
    
    1. **🎯 Recomendações** 
       - Recebe sugestões de IA sobre qual é a próxima melhor atração
       - Escolhe entre: **Groq**, **Mistral**, ou **Manual**
       - Baseado na tua localização e histórico
    
    2. **📊 Histórico e Tempos de Espera**
       - Vê todas as atrações que já visitaste
       - **Vê todas as atrações que FALTAM visitar** com os tempos de espera
       - Filtro por zona
       - Exportar em CSV
    
    3. **☁️ Sincronização**
       - Os dados ficam guardados em `visited_attractions.json`
       - Backup automático no GitHub
    
    ### 🤖 Escolher IA:
    
    **Groq (Rápido)**
    - Muito rápido
    - Excelente qualidade
    - Modelo: Llama 3.3 70B
    - Va a https://console.groq.com
    
    **Mistral (Qualidade)**
    - Resposta detalhada
    - Modelo: Mistral Large
    - Ótimo para análise de rotas
    - Va a https://console.mistral.ai
    
    **Manual**
    - Ver tabela de atrações restantes
    - Escolher tu próprio
    - Sem necessidade de API
    
    ### 💾 Guardar Dados:
    - Os dados ficam em `visited_attractions.json` (local)
    - Sincronizar com GitHub:
      ```bash
      git add visited_attractions.json
      git commit -m "Atualizar histórico"
      git push origin main
      ```
    
    ### 📊 Dados Guardados:
    - Nome da atração
    - Zona onde fica
    - Tempo de espera quando visitaste
    - Data da visita
    
    ### 🏆 Por que comparar Groq e Mistral?
    
    **Groq:**
    - Mais rápido
    - Ótimo para respostas imediatas
    - Llama 3.3 é excelente em lógica
    
    **Mistral:**
    - Mais detalhado
    - Ótimo para análise profunda
    - Excelente em português
    
    Teste ambas e veja qual prefere! 🚀
    
    """)