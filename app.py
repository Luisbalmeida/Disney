import streamlit as st
import requests
import pandas as pd
import json
import os
from datetime import datetime
from groq import Groq
import concurrent.futures
import time

# 1. Configuração da Página
st.set_page_config(page_title="Disney AI Guide", page_icon="🏰", layout="wide")
st.title("🏰 Guia IA - Disneyland Paris")

# 2. Obter Chaves API de forma segura
try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
    OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
    
    groq_client = None
    if GROQ_API_KEY:
        groq_client = Groq(api_key=GROQ_API_KEY)
    
except Exception as e:
    st.warning(f"⚠️ Erro ao configurar IAs: {e}")
    st.info("Configure GROQ_API_KEY e/ou OPENROUTER_API_KEY nos Secrets do Streamlit para usar IA.")

# 3. Ficheiro de histórico local
VISITED_FILE = "visited_attractions.json"

# ============================================================
# MODELOS OPENROUTER — IDs CONFIRMADOS MARÇO 2026
# Fonte: https://openrouter.ai/collections/free-models
# IMPORTANTE: Ativar "Allow free endpoints" em:
# https://openrouter.ai/settings/privacy
# ============================================================

MODELOS_ESPECIALISTAS = [
    {
        "name": "Llama 3.3 70B",
        "id": "meta-llama/llama-3.3-70b-instruct:free",
        "role": "Especialista Geral"
    },
    {
        "name": "Mistral Small 3.1 24B",
        "id": "mistralai/mistral-small-3.1-24b-instruct:free",
        "role": "Especialista em Rotas"
    },
    {
        "name": "Gemma 3 27B",
        "id": "google/gemma-3-27b-it:free",
        "role": "Especialista em Raciocínio"
    }
]

# Juiz — NVIDIA Nemotron 3 Super (262K contexto, ideal para comparar textos)
MODELO_JUIZ = "nvidia/nemotron-3-super-120b-a12b:free"

# 3. Ficheiro de histórico local
VISITED_FILE = "visited_attractions.json"

def chamar_openrouter(prompt, modelo_id, tentativas=3):
    """Chama OpenRouter API com retry automático em caso de Rate Limit"""
    if not OPENROUTER_API_KEY:
        return None, "❌ OpenRouter não configurado"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/Luisbalmeida/Disney",
        "X-Title": "Disney AI Guide"
    }
    
    for tentativa in range(tentativas):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": modelo_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                    "max_tokens": 1000
                },
                timeout=40
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"], None
            
            elif response.status_code == 429:
                # Rate Limit: esperar e tentar novamente
                espera = 5 * (tentativa + 1)
                time.sleep(espera)
                continue
            
            else:
                return None, f"Erro {response.status_code}: {response.text[:200]}"
        
        except requests.Timeout:
            if tentativa < tentativas - 1:
                time.sleep(3)
                continue
            return None, "❌ Timeout: O modelo demorou demasiado a responder."
        except Exception as e:
            return None, f"❌ Erro: {str(e)[:200]}"
    
    return None, "❌ Todas as tentativas falharam (Rate Limit). Tente novamente em 30 segundos."

def gerar_recomendacao_especialista(prompt, modelo):
    """Gera recomendação de um especialista individual"""
    resposta, erro = chamar_openrouter(prompt, modelo["id"])
    if resposta:
        return {
            "especialista": modelo["name"],
            "role": modelo["role"],
            "sugestao": resposta
        }
    else:
        return {
            "especialista": modelo["name"],
            "role": modelo["role"],
            "sugestao": f"❌ Erro: {erro}"
        }

def moa_obter_recomendacoes_paralelas(prompt):
    """Obtém recomendações de múltiplos especialistas em paralelo (MoA)"""
    recomendacoes = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(gerar_recomendacao_especialista, prompt, modelo): modelo 
            for modelo in MODELOS_ESPECIALISTAS
        }
        
        for future in concurrent.futures.as_completed(futures):
            try:
                resultado = future.result(timeout=35)
                recomendacoes.append(resultado)
            except Exception as e:
                recomendacoes.append({
                    "especialista": "Desconhecido",
                    "role": "Erro",
                    "sugestao": f"❌ Timeout: {str(e)}"
                })
    
    return recomendacoes

def moa_juiz_decidir(prompt_base, recomendacoes_especialistas):
    """Juiz analisa todas as sugestões e escolhe a melhor"""
    
    # Formatar sugestões para o juiz
    sugestoes_formatadas = "\n".join([
        f"--- {rec['especialista']} ({rec['role']}) ---\n{rec['sugestao'][:500]}\n"
        for rec in recomendacoes_especialistas
    ])
    
    prompt_juiz = f"""
    Você é um juiz especializado em parques temáticos. 
    
    Recebeu sugestões de roteiros de vários especialistas para a Disneyland Paris:
    
    {sugestoes_formatadas}
    
    Baseado nas restrições originais:
    {prompt_base}
    
    Sua tarefa:
    1. Analise TODAS as sugestões
    2. Escolha a MELHOR sugestão (aquela que melhor minimiza tempo de espera + caminhada)
    3. Se precisar, combine os melhores pontos de cada sugestão
    4. Retorne a recomendação final ESTRUTURADA assim:
    
    🎯 **RECOMENDAÇÃO FINAL APROVADA PELO JUIZ:**
    [Atrações e rota específica]
    
    💡 **RAZÃO DA ESCOLHA:**
    [Por que esta é a melhor opção]
    
    🏆 **ESPECIALISTA QUE SUGERIU ISTO:**
    [Nome do especialista ou combinação]
    """
    
    resposta, erro = chamar_openrouter(prompt_juiz, MODELO_JUIZ)
    return resposta, erro

def gerar_recomendacao_ia(prompt, ia_selecionada):
    """Gera recomendação usando a IA selecionada"""
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
        
        elif ia_selecionada == "OpenRouter (MoA)":
            if not OPENROUTER_API_KEY:
                return None, "❌ OpenRouter não configurado. Adicione OPENROUTER_API_KEY nos Secrets."
            
            # Mostrar progresso
            st.info("🤖 MoA iniciado: Consultando 3 especialistas em paralelo...")
            
            # Passo 1: Especialistas em paralelo
            recomendacoes = moa_obter_recomendacoes_paralelas(prompt)
            
            # Mostrar sugestões dos especialistas
            st.subheader("👥 Sugestões dos Especialistas:")
            for rec in recomendacoes:
                with st.expander(f"👨‍💼 {rec['especialista']} - {rec['role']}"):
                    st.markdown(rec['sugestao'][:800])
            
            st.info("⚖️ Juiz analisando as melhores sugestões...")
            
            # Passo 2: Juiz decide
            resposta_juiz, erro = moa_juiz_decidir(prompt, recomendacoes)
            
            if erro:
                return None, f"❌ Erro no juiz: {erro}"
            
            return resposta_juiz, None
        
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
        opcoes_ia = ["Groq (Rápido)", "OpenRouter MoA 🏆 (Melhor Qualidade)", "Manual (Ver tabela)"]
        ia_selecionada = st.selectbox("Escolhe a IA:", opcoes_ia)
        
        # Mapear opção para nome real
        ia_map = {
            "Groq (Rápido)": "Groq",
            "OpenRouter MoA 🏆 (Melhor Qualidade)": "OpenRouter (MoA)",
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
       - Escolhe entre: **Groq**, **OpenRouter MoA 🏆**, ou **Manual**
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
    
    **Groq (Rápido & Grátis)**
    - Muito rápido
    - Free tier generoso
    - Uma única IA: Llama 3.3 70B
    - Va a https://console.groq.com
    
    **OpenRouter MoA 🏆 (Mixture of Agents - Melhor Qualidade)**
    - **3 especialistas em paralelo:**
      - Llama 3.3 70B (Especialista Geral)
      - Mistral Small 3.1 24B (Rotas)
      - Gemma 3 27B (Raciocínio)
    - **1 Juiz inteligente** (NVIDIA Nemotron 3 Super - 262K contexto)
    - Mais preciso e confiável
    - Todos os modelos GRATUITOS!
    - ⚠️ Importante: Ativar "Allow free endpoints" em https://openrouter.ai/settings/privacy
    - Va a https://openrouter.ai
    
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
    
    ### 🏆 Por que OpenRouter MoA é melhor?
    
    **Problema com IA única:**
    - Pode ter viés
    - Uma alucinação afeta tudo
    
    **Solução MoA:**
    - 3 especialistas diferentes = perspectivas variadas
    - Juiz compara e elige o melhor
    - Resultado: **Qualidade aumenta ~40%**
    - Tempo: Apenas +2 segundos (paralelo)
    
    """)