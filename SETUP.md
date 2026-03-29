# ⚙️ Configuração Completa - Disney AI Guide

## 🎯 Objetivo

Guardar um histórico **persistente e sincronizado em GitHub** de todas as atrações que visitou na Disneyland Paris, com uma tabela visual de tempos de espera por zona.

---

## 📋 O que foi implementado

### 1. ✅ Sistema de Histórico em JSON
**Ficheiro:** `visited_attractions.json`
- Guarda automaticamente atrações visitadas
- Formato: JSON simples e legível
- Persiste entre sessões
- Fácil de sincronizar no GitHub

### 2. ✅ Tabela Visual com Filtro por Zona
**Aba:** "📊 Histórico"
- Mostra todas as atrações visitadas
- **Filtro automático pela sua zona atual**
- Tempos de espera gravados
- Data da visita
- Estatísticas (total, médio, economizado)

### 3. ✅ Sincronização GitHub
- Ficheiro fica versionado no Git
- Simples `git push` para backup
- Script Python automático para sync

### 4. ✅ Recomendações de IA (mantido)
- Continua a sugerir próximas atrações
- Baseado no histórico e localização

---

## 🚀 Setup Passo a Passo

### Passo 1: Chave API do Groq (Grátis)

```bash
# 1. Va para https://console.groq.com
# 2. Crie uma conta (grátis com email)
# 3. Copie a chave API
# 4. Configure em seu PC:

mkdir -p ~/.streamlit
echo 'GROQ_API_KEY = "sk-..." >> ~/.streamlit/secrets.toml
```

**Windows (PowerShell):**
```powershell
mkdir $env:USERPROFILE\.streamlit -ErrorAction SilentlyContinue
Add-Content $env:USERPROFILE\.streamlit\secrets.toml "GROQ_API_KEY = `"sk-...`""
```

### Passo 2: Instalar Dependências

```bash
pip install streamlit requests pandas groq
# ou
pip install -r requirements.txt
```

### Passo 3: Executar a App

```bash
streamlit run app.py
```

A app abrirá em `http://localhost:8501`

---

## 📱 Como Usar a App

### Fluxo Principal

1. **🎯 Aba "Recomendações"**
   - Escolha onde está agora (zona)
   - Selecione atrações que já visitou
   - Clique "✨ Pedir Sugestão Mágica"
   - A IA vai recomendar a próxima melhor atração
   - ✅ **Histórico é salvo automaticamente**

2. **📊 Aba "Histórico"**
   - Vê todas as atrações visitadas
   - Filtrado por sua zona atual
   - Tempos de espera economizados
   - Opções: Exportar CSV, Limpar

3. **❓ Aba "Ajuda"**
   - Documentação e exemplos

---

## 💾 Sincronizar com GitHub

### Opção A: Manual (recomendado)

```bash
# Ver o histórico
cat visited_attractions.json

# Fazer backup/sync
git add visited_attractions.json
git commit -m "Atualizar histórico de atrações"
git push origin main
```

### Opção B: Automático (Script Python)

```bash
python sync_to_github.py
```

Este script:
- ✅ Verifica se ficheiro existe
- ✅ Faz add/commit/push automático
- ✅ Mostra estatísticas
- ✅ Trata erros

### Opção C: Automático Contínuo (GitHub Actions)

Se quiser sincronização diária automática:

**1. Criar ficheiro** `.github/workflows/sync-attractions.yml`:

```yaml
name: Sync Attractions Daily

on:
  workflow_dispatch:
  schedule:
    - cron: '0 2 * * *'  # 02:00 todo dia UTC

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Commit and Push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add visited_attractions.json || echo "No changes"
          git commit -m "Auto-sync attractions [$(date)]" || echo "Nothing to commit"
          git push || echo "Nothing to push"
```

---

## 📊 Estrutura dos Dados

### Ficheiro: `visited_attractions.json`

```json
{
  "zona": "Fantasyland",
  "visitadas": {
    "It's a Small World": {
      "zona": "Fantasyland",
      "data": "2026-03-29T15:30:45.123456",
      "tempo_espera": 35
    },
    "Peter Pan's Flight": {
      "zona": "Fantasyland",
      "data": "2026-03-29T16:15:22.654321",
      "tempo_espera": 45
    }
  },
  "ultima_atualizacao": "2026-03-29T16:15:22.654321"
}
```

### Campos

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `zona` | Sua zona atual | `"Fantasyland"` |
| `visitadas` | Dictionary de atrações | `{...}` |
| `data` | ISO timestamp | `"2026-03-29T15:30"` |
| `tempo_espera` | Minutos de fila | `35` |
| `ultima_atualizacao` | Último update | `"2026-03-29T16:15"` |

---

## 🗺️ Mapa de Atrações por Zona

(Automático - app detecta mapeamento)

| Zona | Atrações Exemplo |
|------|-----------------|
| **Fantasyland** | It's a Small World, Peter Pan's Flight, Dumbo |
| **Adventureland** | Jungle Cruise, Pirates of the Caribbean |
| **Frontierland** | Big Thunder Mountain, Phantom Manor |
| **Discoveryland** | Space Mountain, Star Tours, Buzz Lightyear |
| **Main Street** | Railroad, Shops |

---

## 🐛 Troubleshooting

### Problema: "API Key não encontrada"
```bash
# Verificar
cat ~/.streamlit/secrets.toml

# Se vazio, adicionar:
echo 'GROQ_API_KEY = "sk-..."' >> ~/.streamlit/secrets.toml
```

### Problema: "Git não reconhece repositório"
```bash
# Reinicializar git
git init
git remote add origin https://github.com/Luisbalmeida/Disney.git
git pull origin main
```

### Problema: "visited_attractions.json desapareceu"
```bash
# Recuperar do GitHub
git pull origin main

# Ou criar novo
git show HEAD:visited_attractions.json > visited_attractions.json
```

### Problema: Conflito de merge
```bash
# Usar versão online
git checkout --theirs visited_attractions.json
git add visited_attractions.json
git commit -m "Resolver conflito - use versão online"
git push
```

---

## 📚 Ficheiros e Sua Função

```
Disney/
├── app.py                          # 🚀 Aplicação principal (MODIFICADA)
├── requirements.txt                # 📦 Dependências
├── README.md                       # 📖 Documentação completa
├── QUICKSTART.md                   # ⚡ Guia rápido
├── SETUP.md                        # ⚙️ Este ficheiro
├── sync_to_github.py              # 🔄 Script de sincronização
├── visited_attractions.json        # 💾 Histórico (CRIADO ao usar app)
├── visited_attractions.example.json # 📄 Exemplo
├── .gitignore                      # 🚫 Ignorar ficheiros
└── .github/workflows/              # 📅 (Opcional) Automação
    └── sync-attractions.yml
```

---

## ✨ Recursos Principais

### Na App Streamlit

```
🏰 Guia IA - Disneyland Paris
│
├── 🎯 Recomendações
│   ├── 📍 Escolher zona
│   ├── 🎢 Selecionar atrações visitadas
│   └── ✨ Receber recomendação IA
│
├── 📊 Histórico
│   ├── 📋 Tabela de atrações visitadas
│   ├── 📍 Filtro por zona
│   ├── 📊 Estatísticas
│   ├── 📥 Exportar CSV
│   └── 🔄 Limpar histórico
│
└── ❓ Ajuda
    └── 📖 Documentação
```

---

## 🎓 Conceitos-Chave

### 1. Persistência Local
- Dados ficam em `visited_attractions.json` no seu PC
- Persiste entre reiniços da app
- Carregado automaticamente

### 2. Versionamento GitHub
- Ficheiro fica no repositório Git
- Histórico de versões
- Recuperação de backups antigos

### 3. Sincronização Multi-dispositivo
```
PC/Laptop → git push → GitHub
              ↓
        visited_attractions.json
              ↓
Tablet/Phone ← git pull ← GitHub
```

### 4. IA em Tempo Real
- LLaMA 3.3 70B via Groq
- Lê histórico atual
- Recomenda melhor rota

---

## 📱 Deploy Grátis (Streamlit Cloud)

Se quiser a app **online 24/7**:

1. **Push para GitHub**
   ```bash
   git push origin main
   ```

2. **Va a** https://share.streamlit.io/

3. **Conecte repo** Luisbalmeida/Disney

4. **Configure Secrets** (copie GROQ_API_KEY)

5. **App fica online!** 🚀

---

## 🎯 Próximos Passos

1. ✅ Copiar chave Groq
2. ✅ Configurar `~/.streamlit/secrets.toml`
3. ✅ Instalar dependências
4. ✅ Executar `streamlit run app.py`
5. ✅ Usar a app normalmente
6. ✅ Dados sincronizam automaticamente!
7. ✅ (Opcional) fazer `python sync_to_github.py` ou `git push`

---

**Pronto? Vá para o QUICKSTART.md para começar! 🚀**
