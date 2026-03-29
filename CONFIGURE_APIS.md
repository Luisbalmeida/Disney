# 🤖 Configurar APIs - Groq e OpenAI

## Você tem 3 opções:

### 1️⃣ Groq (Recomendado - Mais Rápido & Grátis)

```bash
# 1. Va para https://console.groq.com
# 2. Crie conta (grátis com email)
# 3. Copie a chave API
# 4. Configure nos Secrets do Streamlit:

mkdir -p ~/.streamlit
echo 'GROQ_API_KEY = "gsk_..."' >> ~/.streamlit/secrets.toml
```

**Vantagens:**
- ✅ Grátis com rate limit generoso
- ✅ Super rápido (baixa latência)
- ✅ Model: LLaMA 3.3 70B (excelente qualidade)
- ✅ Ideal para esta aplicação

**Link:** https://console.groq.com

---

### 2️⃣ OpenAI (Mais Preciso, Pago)

```bash
# 1. Va para https://platform.openai.com
# 2. Crie conta com email/Google
# 3. Adicione método de pagamento
# 4. Va a API Keys → Create new secret key
# 5. Copie a chave
# 6. Configure:

echo 'OPENAI_API_KEY = "sk-..."' >> ~/.streamlit/secrets.toml
```

**Vantagens:**
- ✅ Muito preciso (GPT-3.5-Turbo/GPT-4)
- ✅ Ótimo para recomendações complexas
- ⚠️ Requer créditos pré-pagos ($5-$20)
- ⚠️ Mais caro que Groq

**Link:** https://platform.openai.com

**Preços (aproximados):**
- GPT-3.5-Turbo: ~$0.0005 por 1000 tokens
- GPT-4: ~$0.03 por 1000 tokens

---

### 3️⃣ Manual (Sem IA)

```
Sem necessidade de chaves!
Escolhe manualmente da tabela de atrações restantes.
```

**Vantagens:**
- ✅ Sem custos
- ✅ Sem configuração
- ⚠️ Tu decides a rota
- ⚠️ Sem ajuda automática

---

## 📋 Ficheiro de Configuração

### Local: `~/.streamlit/secrets.toml`

```toml
# Groq
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxx"

# OpenAI (opcional)
OPENAI_API_KEY = "sk_xxxxxxxxxxxxxxxxxxxx"
```

### Windows (PowerShell)

```powershell
# Criar pasta
mkdir $env:USERPROFILE\.streamlit -ErrorAction SilentlyContinue

# Adicionar chaves
Add-Content $env:USERPROFILE\.streamlit\secrets.toml "GROQ_API_KEY = `"gsk_...`""
Add-Content $env:USERPROFILE\.streamlit\secrets.toml "OPENAI_API_KEY = `"sk_...`""
```

### Linux/Mac

```bash
mkdir -p ~/.streamlit
echo 'GROQ_API_KEY = "gsk_..."' >> ~/.streamlit/secrets.toml
echo 'OPENAI_API_KEY = "sk_..."' >> ~/.streamlit/secrets.toml
```

---

## 🚀 Como Usar

### No Streamlit Local

1. **Configurar Secrets** (como acima)
2. **Executar App:**
   ```bash
   streamlit run app.py
   ```
3. **Escolher IA na aba Recomendações**
   - Groq (Recomendado)
   - OpenAI
   - Manual (Ver tabela)

### No Streamlit Cloud

1. **Fazer Push para GitHub** com o código
2. **Va a** https://share.streamlit.io/
3. **New App → Connect GitHub repo**
4. **Advanced Settings → Secrets**
5. **Copiar e colar:**
   ```toml
   GROQ_API_KEY = "gsk_..."
   OPENAI_API_KEY = "sk_..."
   ```
6. **Deploy!**

---

## ✅ Verificar Configuração

### Verificar se Secrets estão corretos

```bash
# Linux/Mac
cat ~/.streamlit/secrets.toml

# Windows
type $env:USERPROFILE\.streamlit\secrets.toml
```

Deve aparecer:
```
GROQ_API_KEY = "gsk_..."
OPENAI_API_KEY = "sk_..."
```

---

## 🔄 Comparação Rápida

| Aspecto | Groq | OpenAI | Manual |
|---------|------|--------|--------|
| **Custo** | Grátis | Pago | Grátis |
| **Velocidade** | ⚡ Muito Rápido | 🟢 Rápido | Instantâneo |
| **Qualidade** | 🟢 Excelente | ⭐ Melhor | Tu decides |
| **Setup** | 5 min | 10 min | Nenhum |
| **Limite** | 30 req/min (free) | Baseado em créditos | Nenhum |
| **Recomendado** | ✅ Sim | Para uso intenso | Casual |

---

## 💡 Recomendação

**Comece com Groq:**
1. ✅ Grátis
2. ✅ Rápido
3. ✅ Fácil de configurar
4. ✅ Perfeito para esta app

Se quiser mais precisão depois, mude para OpenAI.

---

## 🐛 Troubleshooting

### "API Key não configurada"
```bash
# Verificar
cat ~/.streamlit/secrets.toml

# Se vazio:
echo 'GROQ_API_KEY = "gsk_..."' > ~/.streamlit/secrets.toml
```

### "Unauthorized / Invalid Key"
- Verifica se copiou a chave completa (sem espaços)
- Reinicia o Streamlit: `Ctrl+C` e `streamlit run app.py`

### "Rate limit exceeded"
- Espera alguns minutos
- (Groq: 30 req/min free tier)
- (OpenAI: Baseado em plano)

### "Erro de conexão"
- Verifica internet
- Verifica que a chave está ativa
- Va para console.groq.com ou platform.openai.com e confirma

---

**Pronto? Escolhe a IA e começa! 🚀**
