# 🚀 Guia Rápido - Disney AI Guide

## 📱 O que foi criado?

Uma solução **completa** para guardar e rastrear as atrações da Disneyland Paris que já visitaram:

### ✅ 1. Sistema de Histórico Automático (`visited_attractions.json`)
- Guarda automaticamente cada atração visitada
- Armazena: nome, zona, tempo de espera, data
- Ficheiro fica **commitido no GitHub** para sincronização em cloud

### ✅ 2. Tabela Visual das Atrações por Zona
- Aba "📊 Histórico" mostra:
  - Todas as atrações visitadas
  - **Filtrado por sua zona atual**
  - Tempos de espera economizados (estatísticas)
  - Opção de exportar em CSV

### ✅ 3. Integração com GitHub
- Dados sincronizam automaticamente entre dispositivos
- Basta fazer `git push` para fazer backup

---

## 💾 Como Usar

### Local (seu PC/Tablet)

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar API Groq (grátis):
# - Va para https://console.groq.com
# - Crie uma conta (grátis)
# - Copie a chave e cole em ~/.streamlit/secrets.toml:
mkdir -p ~/.streamlit
echo 'GROQ_API_KEY = "sk-sua-chave-aqui"' >> ~/.streamlit/secrets.toml

# 3. Executar
streamlit run app.py
```

### Sincronizar no GitHub

```bash
# Ver o histórico
cat visited_attractions.json

# Fazer backup/sync
git add visited_attractions.json
git commit -m "Atualizar histórico - visitei mais atrações"
git push origin main
```

---

## 📊 O que você verá

### Aba 1: 🎯 Recomendações
1. Escolhe onde estás agora (zona)
2. Seleciona atrações que já visitaste
3. IA aconselha a próxima melhor atração

### Aba 2: 📊 Histórico
- **Tabela bonita** com todas as atrações visitadas na sua zona
- Tempos de espera guardados
- Estatísticas (total de atrações, tempo médio, economizado)
- Botões para exportar CSV ou limpar histórico

### Aba 3: ❓ Ajuda
- Documentação completa da app

---

## 🗂️ Ficheiros Criados/Modificados

```
✅ app.py                                (MODIFICADO - nova funcionalidade)
✅ README.md                             (ATUALIZADO - documentação completa)
✅ .gitignore                            (CRIADO - para ignorar ficheiros desnecessários)
✅ visited_attractions.json              (AUTO - gerado quando usar a app)
✅ visited_attractions.example.json      (EXEMPLO - mostra o formato)
✅ QUICKSTART.md                         (ESTE ficheiro)
```

---

## 🎯 Fluxo de Uso

```
┌─────────────────────────────────────┐
│ App Streamlit (local ou cloud)      │
├─────────────────────────────────────┤
│ 1. Escolhe zona + atrações visitadas │
│ 2. App guarda em visited_...json     │
│ 3. Tabela mostra histórico por zona  │
│ 4. Faz git push → GitHub             │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│ visited_attractions.json (GitHub)   │
│ ☁️ Sincronizado em cloud             │
│ 📲 Acesso de qualquer dispositivo    │
└─────────────────────────────────────┘
```

---

## 🆚 Comparação: Local vs Cloud

| Aspecto | Local | + GitHub |
|---------|-------|----------|
| **Guarda dados** | ✅ Sim | ✅ Sim |
| **Persiste entre sessões** | ✅ Sim | ✅ Sim |
| **Acesso de outro PC** | ❌ Não | ✅ Sim |
| **Backup em cloud** | ❌ Não | ✅ Sim |
| **Sincronizar entre dispositivos** | ❌ Não | ✅ Sim |

---

## 💡 Dicas Profissionais

### 1. Sincronizar do Tablet/Telemóvel
```bash
# No seu computador, push os dados
git push

# No tablet/telemóvel, pull
git pull

# visited_attractions.json fica atualizado!
```

### 2. Backup Automático
- Cria um GitHub Actions workflow para fazer pull diário
- Ou simplesmente usa a app e faz push manual

### 3. Exportar Dados
- Clique em "📥 Exportar como CSV" na aba Histórico
- Abre em Excel para análises adicionais

### 4. Limpar Histórico
- Botão "🔄 Limpar Histórico" remove tudo
- Depois: `git add visited_attractions.json && git commit -m "Limpar histórico" && git push`

---

## 🐛 Problemas Comuns

### "Chave API não configurada"
```bash
# Verificar:
cat ~/.streamlit/secrets.toml

# Se não aparecer GROQ_API_KEY:
# 1. Va a https://console.groq.com
# 2. Crie conta (grátis)
# 3. Copie a chave
# 4. Cola em ~/.streamlit/secrets.toml
```

### "visited_attractions.json não aparece"
- Arquivo é criado **quando você usar a app** (primeira vez que marcar uma atração)
- Se desaparecer: `git pull` para recuperar do GitHub

### "Dados não sincronizam entre dispositivos"
- Faz `git push` no PC
- Faz `git pull` no tablet
- O ficheiro visited_attractions.json fica sincronizado

---

## 🎓 Estrutura dos Dados

Cada entrada no histórico tem:
```json
{
  "atração": "It's a Small World",
  "zona": "Fantasyland",
  "tempo_espera": 35,        // minutos quando visitou
  "data": "2026-03-29T15:30"  // hora exata
}
```

---

## 📱 Deploy Grátis (Opcional)

Se quiser usar a app **online** (sem PC ligado):

1. **Streamlit Cloud** (grátis)
   - Push para GitHub
   - Va a https://share.streamlit.io/
   - Conecta repositório
   - App fica online!

2. **GitHub Pages** (para os dados)
   - Já está setado - dados em cloud automáticamente

---

## ✨ Funcionalidades Futuras (Ideias)

- [ ] Integrar mapa interativo da Disneyland
- [ ] Notificações de tempos de espera muito baixos
- [ ] Análise de melhor altura para visitar cada atração
- [ ] Modo colaborativo (múltiplos utilizadores)
- [ ] Comparação com versitas anteriores

---

**Pronto para começar? 🚀**

Próximo passo: Instalar dependências e criar secrets da API!
