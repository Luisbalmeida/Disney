# 🏰 Disney AI Guide - Disneyland Paris

Uma aplicação **Streamlit + IA (Groq)** que te ajuda a otimizar a tua visita à Disneyland Paris, recomendando as melhores atrações para visitar a cada momento.

## ✨ Funcionalidades

### 🎯 Recomendações Inteligentes
- Recebe sugestões de IA baseadas na tua localização atual e atrações já visitadas
- Considera os tempos de espera em tempo real
- Minimiza o tempo de deslocação entre zonas

### 📊 Histórico de Atrações
- **Guarda automaticamente** todas as atrações que visitaste
- Armazena em ficheiro JSON (`visited_attractions.json`)
- Mostra tabela com tempos de espera por zona
- Estatísticas de atrações visitadas

### ☁️ Sincronização com GitHub
- Os dados ficam em `visited_attractions.json` (versionado no Git)
- Fácil de fazer backup e sincronizar entre dispositivos
- Histórico persistente em cloud

## 🚀 Instalação

### Pré-requisitos
- Python 3.8+
- Chave API do Groq (gratuita em https://console.groq.com)

### Setup

```bash
# 1. Clonar repositório
git clone https://github.com/Luisbalmeida/Disney.git
cd Disney

# 2. Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar Streamlit Secrets
mkdir -p ~/.streamlit
echo 'GROQ_API_KEY = "sua_chave_aqui"' >> ~/.streamlit/secrets.toml
```

## 💻 Como Usar

### Local
```bash
streamlit run app.py
```

### Deploy no Streamlit Cloud
1. Faz push do código para GitHub
2. Va para https://share.streamlit.io/
3. Conecta o repositório GitHub
4. Adiciona a chave GROQ_API_KEY nos "Secrets"

## 📂 Estrutura

```
visited_attractions.json    # Histórico de atrações visitadas (LOCAL + GITHUB)
app.py                     # Aplicação principal
requirements.txt           # Dependências Python
README.md                  # Este ficheiro
```

## 💾 Sincronizar Histórico no GitHub

Os dados do histórico ficam automaticamente em `visited_attractions.json`:

```bash
# Fazer backup/sincronizar
git add visited_attractions.json
git commit -m "Atualizar histórico de atrações visitadas"
git push origin main
```

### Estrutura do Ficheiro JSON
```json
{
  "zona": "Fantasyland",
  "visitadas": {
    "It's a Small World": {
      "zona": "Fantasyland",
      "data": "2026-03-29T15:30:45.123456",
      "tempo_espera": 35
    },
    "Cinderella Castle": {
      "zona": "Fantasyland",
      "data": "2026-03-29T14:45:12.123456",
      "tempo_espera": 0
    }
  },
  "ultima_atualizacao": "2026-03-29T15:30:45.123456"
}
```

## 📊 Tabela de Tempos de Espera

A aba **"Histórico"** mostra:
- ✅ Todas as atrações que visitaste
- 🕐 Tempos de espera quando visitaste
- 📍 Zona de cada atração
- 📅 Data da visita

Plus:
- **CSV Export** - Exporta os dados para Excel
- **Estatísticas** - Total de atrações, tempo médio, tempo economizado
- **Filtro por Zona** - Vê apenas as atrações da tua zona atual

## 🤖 IA - Como Funciona

A aplicação usa **LLaMA 3.3 70B** (via Groq) para:
1. Analisar a tua localização atual
2. Ver o histórico de atrações visitadas
3. Considerar tempos de espera em tempo real
4. Minimizar tempo de deslocação
5. Recomendar a melhor atração para agora

### Regras de Caminhada (Disneyland Paris)
- **Mesma zona**: 1-3 min
- **Zonas adjacentes**: 4-6 min
- **Zonas opostas**: 8-12 min

## 🔐 Segurança

- Chave API guardada em `~/.streamlit/secrets.toml` (não commitida)
- Dados do histórico em `visited_attractions.json` (commitido no GitHub)
- Sem dados pessoais armazenados

## 🛠️ Troubleshooting

### "Chave GROQ_API_KEY não configurada"
```bash
# Verificar se exists:
cat ~/.streamlit/secrets.toml

# Se não existe, criar:
mkdir -p ~/.streamlit
echo 'GROQ_API_KEY = "sk-..."' > ~/.streamlit/secrets.toml
```

### Dados do Histórico Desapareceram
- Verifica se `visited_attractions.json` existe
- Se não, cria com `git pull` (se estava no GitHub)
- Ou adiciona novamente as atrações

## 📝 API Utilizada

- **Theme Parks Wiki API** - Tempos de espera da Disneyland Paris (free)
- **Groq API** - Recomendações de IA (free tier disponível)

## 🎨 Zonas da Disneyland Paris

- 🏛️ Main Street, U.S.A.
- 🏰 Fantasyland
- 🌴 Adventureland
- 🤠 Frontierland
- 🚀 Discoveryland

## 🤝 Contribuições

Feel free para fazer fork e submeter pull requests!

## 📄 Licença

MIT

---

**Desenvolvido com ❤️ para otimizar a tua visita à Disneyland Paris**