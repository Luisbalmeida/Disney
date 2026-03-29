import streamlit as st
import requests
import pandas as pd
import json
import os
from datetime import datetime
from groq import Groq
import time

# 1. Configuração da Página
st.set_page_config(page_title="Disney AI Guide", page_icon="🏰", layout="wide")
st.title("🏰 Guia IA - Disneyland Paris")

# 2. Obter Chaves API de forma segura
try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    MISTRAL_API_KEY = st.secrets.get("MISTRAL_API_KEY", "")
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")  # ✅ NOVO
    
    groq_client = None
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
    
except Exception as e:
    st.warning(f"⚠️ Erro ao configurar IAs: {e}")
    st.info("Configure GROQ_API_KEY, MISTRAL_API_KEY e/ou OPENROUTER_API_KEY nos Secrets.")

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

# Mapeamento de atrações para zonas (validado com API Theme Parks Wiki)
ZONA_POR_ATRACAO = {
    "Frontierland": ["Big Thunder Mountain", "Phantom Manor", "Indiana Jones", "La Cabane des Robinson"],
    "Fantasyland": ["Cinderella Castle", "it's a small world", "Blanche-Neige et les Sept Nains", "Les Voyages de Pinocchio", "Le Carrousel de Lancelot", "Peter Pan's Flight", "Dumbo the Flying Elephant", "Mad Hatter's Tea Cups", "Alice's Curious Labyrinth", "La Tanière du Dragon", "Casey Jr"],
    "Adventureland": ["Jungle Cruise", "Adventure Isle", "Le Passage Enchanté d'Aladdin", "Pirates of the Caribbean", "La Cabane", "Les Mystères du Nautilus"],
    "Discoveryland": ["Star Wars Hyperspace Mountain", "Orbitron", "Buzz Lightyear Laser Blast", "Autopia"],
    "Main Street, U.S.A.": ["Disneyland Railroad", "Main Street Vehicles"]
}

def obter_zona_atracao(nome_atracao):
    """Retorna a zona de uma atração"""
    for zona, atracoes in ZONA_POR_ATRACAO.items():
        for atracao in atracoes:
            if atracao.lower() in nome_atracao.lower():
                return zona
    return "Desconhecida"

def chamar_mistral(prompt):
    """Chama a API da Mistral via HTTP sem SDK"""
    if not MISTRAL_API_KEY:
        return None, "❌ Mistral não configurado. Adicione MISTRAL_API_KEY nos Secrets."

    try:
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistral-large-latest",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4
        }

        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=40
        )

        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"], None

        return None, f"❌ Erro Mistral {response.status_code}: {response.text[:300]}"

    except Exception as e:
        return None, f"❌ Erro ao contactar Mistral: {str(e)}"

def chamar_openrouter_conciliador(prompt, localizacao_atual, lista_visitadas, lista_disponiveis):  # ✅ NOVO - Conciliador
    """OpenRouter analisa recomendações de Groq e Mistral e escolhe a melhor"""
    if not OPENROUTER_API_KEY:
        return None, "❌ OpenRouter não configurado. Adicione OPENROUTER_API_KEY nos Secrets."

    try:
        # 1. Obter recomendação do Groq
        resposta_groq, erro_groq = None, None
        if groq_client:
            try:
                response = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile", 
                    temperature=0.4
                )
                resposta_groq = response.choices[0].message.content
            except Exception as e:
                erro_groq = str(e)
        
        # 2. Obter recomendação do Mistral
        resposta_mistral, erro_mistral = chamar_mistral(prompt)
        
        # Se nenhuma funcionou, informar
        if not resposta_groq and not resposta_mistral:
            return None, f"❌ Nenhuma IA respondeu. Groq: {erro_groq}, Mistral: {erro_mistral}"
        
        # 3. Criar prompt para OpenRouter analisar ambas
        prompt_conciliador = f"""
        Você é um conciliador especializado em rotas na Disneyland Paris.
        
        Duas IAs deram recomendações para a próxima atração. Analise ambas e escolha a MELHOR opção.
        
        CONTEXTO:
        - Localização atual: {localizacao_atual}
        - Já visitadas: {lista_visitadas}
        
        RECOMENDAÇÃO DO GROQ (IA rápida):
        {resposta_groq if resposta_groq else "[Groq não respondeu]"}
        
        RECOMENDAÇÃO DO MISTRAL (IA detalhista):
        {resposta_mistral if resposta_mistral else "[Mistral não respondeu]"}
        
        TAREFA:
        Analise ambas as recomendações e escolha a MELHOR atração para visitar AGORA.
        Considere velocidade de resposta + qualidade da análise.
        
        Retorne:
        1. 🎯 **Decisão Final:** [Nome da atração escolhida]
        2. 🤝 **Análise de Conciliação:** [Por que esta é melhor]
        3. 🥈 **Por que a outra não foi escolhida:** [Breve explicação]
        
        Responda em português de Portugal. Seja conciso mas convincente.
        """
        
        # 4. Chamar OpenRouter para conciliar
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://disney-ai-guide.streamlit.app",
            "X-Title": "Disney AI Guide - Conciliador"
        }

        payload = {
            "model": "google/gemini-2.0-flash-001",
            "messages": [
                {"role": "user", "content": prompt_conciliador}
            ],
            "temperature": 0.3  # Temperatura mais baixa para decisão mais coerente
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=40
        )

        if response.status_code == 200:
            data = response.json()
            resposta = data["choices"][0]["message"]["content"]
            return f"🤝 **Conciliação de IAs:**\n\n{resposta}", None

        return None, f"❌ Erro OpenRouter {response.status_code}: {response.text[:300]}"

    except Exception as e:
        return None, f"❌ Erro ao contactar OpenRouter: {str(e)}"

def gerar_recomendacao_ia(prompt, ia_selecionada, localizacao_atual=None, lista_visitadas=None, lista_disponiveis=None):
    """Gera recomendação usando a IA selecionada (Groq, Mistral ou OpenRouter como conciliador)"""
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
            return chamar_mistral(prompt)
        
        elif ia_selecionada == "OpenRouter":  # ✅ NOVO - Conciliador
            return chamar_openrouter_conciliador(prompt, localizacao_atual, lista_visitadas, lista_disponiveis)
        
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
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Recomendações", "📊 Histórico", "🗺️ Mapa Rápido", "❓ Ajuda"])

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
        opcoes_ia = [
            "Groq (Rápido)",
            "Mistral (Qualidade)",
            "OpenRouter (Versátil)",  # ✅ NOVO
            "Manual (Ver tabela)"
        ]
        ia_selecionada = st.selectbox("Escolhe a IA:", opcoes_ia)
        
        # Mapear opção para nome real
        ia_map = {
            "Groq (Rápido)": "Groq",
            "Mistral (Qualidade)": "Mistral",
            "OpenRouter (Versátil)": "OpenRouter",  # ✅ NOVO
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
                resposta, erro = gerar_recomendacao_ia(prompt, ia_nome, localizacao_atual, lista_visitadas, lista_disponiveis)
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
    st.subheader("🗺️ Explorador de Atrações")
    st.write("Seleciona a atração onde estás agora para ver todas as outras com tempos de espera.")
    
    # Obter todas as atrações
    todas_atracoes = sorted(df_attractions['Nome'].unique())
    
    # Selectbox com atração atual
    atracao_atual = st.selectbox(
        "🎢 Onde estou agora?",
        todas_atracoes,
        key="atracao_atual_mapa"
    )
    
    # Obter zona da atração atual
    zona_atual = obter_zona_atracao(atracao_atual)
    
    # Filtrar outras atrações (excluindo a atual)
    outras_atracoes_df = df_attractions[df_attractions['Nome'] != atracao_atual].copy()
    
    if len(outras_atracoes_df) > 0:
        # Adicionar zona a cada atração
        outras_atracoes_df['Zona'] = outras_atracoes_df['Nome'].apply(obter_zona_atracao)
        
        # Criar coluna de distância (simplicidade)
        def calcular_distancia(zona_destino):
            if zona_destino == zona_atual:
                return "Perto (1-3 min)"
            else:
                return "Longe (4-12 min)"
        
        outras_atracoes_df['Distância'] = outras_atracoes_df['Zona'].apply(calcular_distancia)
        
        # Reordenar e ordenar
        df_display = outras_atracoes_df[['Nome', 'Zona', 'Espera (min)', 'Distância']].sort_values(
            by=['Zona', 'Espera (min)']
        )
        
        # Espaçamento visual
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📍 Estás em: **{atracao_atual}** ({zona_atual})")
        with col2:
            st.metric("Outras atrações abertas", len(df_display))
        
        st.divider()
        
        # Tabela
        st.markdown("### 📊 Todas as Atrações Disponíveis")
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Filtro por zona (opcional)
        st.markdown("### 🎯 Filtrar por Zona")
        zonas_disponiveis = ['Todas'] + sorted(df_display['Zona'].unique().tolist())
        zona_selecionada = st.selectbox(
            "Mostra apenas atrações de:",
            zonas_disponiveis,
            key="zona_filtro_mapa"
        )
        
        if zona_selecionada != "Todas":
            df_filtrado = df_display[df_display['Zona'] == zona_selecionada]
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            st.metric("Atrações nesta zona", len(df_filtrado))
    else:
        st.warning("⚠️ Sem outras atrações disponíveis.")

with tab4:
    st.subheader("❓ Como funciona?")
    st.markdown("""
    ### 📱 Funcionalidades Principais:
    
    1. **🎯 Recomendações** 
       - Recebe sugestões de IA sobre qual é a próxima melhor atração
       - Escolhe entre: **Groq**, **Mistral**, **OpenRouter (Conciliador)**, ou **Manual**
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
    
    **Groq (Rápido) ⚡**
    - Muito rápido
    - Excelente qualidade
    - Modelo: Llama 3.3 70B
    - Ideal para: Respostas imediatas
    - Va a https://console.groq.com
    
    **Mistral (Qualidade) 🎓**
    - Resposta detalhada
    - Modelo: Mistral Large
    - Ideal para: Análise profunda de rotas
    - Va a https://console.mistral.ai
    
    **OpenRouter (Conciliador) 🤝 ← NOVO**
    - **Compara Groq vs Mistral automaticamente**
    - Pede ao OpenRouter para escolher a melhor
    - Modelo: Google Gemini 2.0 Flash
    - Ideal para: Melhor decisão com análise combinada
    - Va a https://openrouter.ai/keys
    
    **Manual 📝**
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
    
    ### 🏆 Como o Conciliador (OpenRouter) Funciona?
    
    1. **Groq** da a sua recomendação (rápida)
    2. **Mistral** da a sua recomendação (detalhada)
    3. **OpenRouter** analisa ambas e escolhe a melhor ✨
    
    Assim gets o melhor dos dois mundos:
    - ⚡ Velocidade do Groq
    - 🎓 Qualidade do Mistral
    - 🤝 Decisão inteligente do OpenRouter
    
    Teste os 3 modos e veja qual prefere! 🚀
    
    """)
