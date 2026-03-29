# 🚀 Configurar OpenRouter.ai - MoA (Mixture of Agents)

## O que é MoA?

**MoA (Mixture of Agents)** é uma técnica revolucionária onde:
1. **3 especialistas** geram sugestões em paralelo
2. **1 juiz** compara e escolhe a melhor
3. **Resultado:** Qualidade ~40% melhor do que IA única

```
┌─────────────────────────────────────────────┐
│   Seu Problema: Próxima atração?            │
└────────────┬────────────────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌─────────┐
│Llama │ │Qwen  │ │DeepSeek │
│ 70B  │ │ 72B  │ │   R1    │
└──────┘ └──────┘ └─────────┘
(Lógica)(Rotas) (Raciocínio)
    │        │        │
    └────────┼────────┘
             │
             ▼
        ┌─────────┐
        │  JUIZ   │
        │ GPT-4O  │
        │ (Escolhe)
        └─────────┘
```

---

## 📋 Setup (5 minutos)

### 1️⃣ Criar Conta OpenRouter

```bash
# VA PARA: https://openrouter.ai/
# 1. Clique em "Sign Up"
# 2. Use Email ou Google
# 3. Confirme email
```

### 2️⃣ Gerar Chave API

```bash
# VA PARA: https://openrouter.ai/keys
# 1. Clique em "Create new key"
# 2. Nomear: "Disney-MoA"
# 3. Copie a chave
```

### 3️⃣ Configurar nos Secrets

```bash
# Linux/Mac
mkdir -p ~/.streamlit
echo 'OPENROUTER_API_KEY = "sk-or-v1-..."' >> ~/.streamlit/secrets.toml

# Windows (PowerShell)
mkdir $env:USERPROFILE\.streamlit -ErrorAction SilentlyContinue
Add-Content $env:USERPROFILE\.streamlit\secrets.toml "OPENROUTER_API_KEY = `"sk-or-v1-...`""
```

### 4️⃣ Verificar

```bash
cat ~/.streamlit/secrets.toml
# Deve aparecer:
# OPENROUTER_API_KEY = "sk-or-v1-..."
```

---

## ✅ Modelos Utilizados (Todos GRATUITOS)

### Especialistas (Consultados em paralelo)

| Modelo | ID | Especialidade | Por quê |
|--------|----|-----------|----|
| **Meta Llama 3.3 70B** | `meta-llama/llama-3.3-70b-instruct:free` | Lógica Pura | Excelente em estruturas e regras |
| **Qwen 2.5 72B** | `qwen/qwen-2.5-72b-instruct:free` | Geometria & Rotas | Especialista em otimização de caminhos |
| **DeepSeek R1** | `deepseek/deepseek-r1-distill-llama-70b:free` | Raciocínio Profundo | Pensa como humano, evita erros |

### Juiz (Escolhe a melhor sugestão)

| Modelo | ID | Função |
|--------|----|----|
| **GPT-4O Mini** | `openai/gpt-4o-mini:free` | Analisa e compara respostas |

---

## 🎯 Como Funciona na Prática

### Exemplo: Está em Fantasyland, visitou "It's a Small World"

```
1. APP envia dados para 3 especialistas (paralelo)
   ├─ Llama 3.3: "Recomendo Pinocchio (45 min)"
   ├─ Qwen 2.5: "Melhor Peter Pan (38 min, caminhada 2 min)"
   └─ DeepSeek: "Dumbo (30 min, ideal para agora)"

2. JUIZ analisa as 3 sugestões
   - Llama tem boa lógica MAS Pinocchio fica longe
   - Qwen é mais eficiente em rotas
   - DeepSeek tem raciocínio sólido

3. JUIZ DECIDE:
   "Recomendo Peter Pan (Qwen sugeriu, tempo ótimo)"
            ↑
        Resposta final
```

---

## 🔐 Limites & Rate Limits

### Gratuito no OpenRouter

| Limite | Valor | Nota |
|--------|-------|------|
| **Requisições/Dia** | Ilimitado* | Com rate limit suave |
| **Tokens/Minuto** | ~3000 | Ou ~30 req/min |
| **Custo** | $0.00 | Sim, é grátis! |

*Nota: Se exceder muito, pode ser throttled (mais lento), mas não é cobrado.

### Estimativa para Uso Típico

```
Cada consulta MoA:
- 3 especialistas: ~500 tokens cada = 1500 tokens
- 1 juiz: ~300 tokens
- Total: ~1800 tokens / consulta

Usando 24h/dia: ~86k tokens
Limite gratuito: Suporta bem!
```

---

## 💡 Dicas Profissionais

### 1. Salvar Chave de Forma Segura

❌ **NUNCA:**
```
echo 'OPENROUTER_API_KEY = "sk-or-..."' > ~/.streamlit/secrets.toml  # Sobrescreve!
```

✅ **SEMPRE:**
```
echo 'OPENROUTER_API_KEY = "sk-or-..."' >> ~/.streamlit/secrets.toml  # Acrescenta!
```

### 2. Testar Conexão

```bash
# Script de teste
python -c "
import requests
headers = {
    'Authorization': 'Bearer sk-or-...',
    'HTTP-Referer': 'https://github.com/Luisbalmeida/Disney',
}
r = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers=headers,
    json={
        'model': 'meta-llama/llama-3.3-70b-instruct:free',
        'messages': [{'role': 'user', 'content': 'Olá!'}],
        'max_tokens': 10
    }
)
print(f'Status: {r.status_code}')
print(r.json()['choices'][0]['message']['content'] if r.status_code == 200 else r.text)
"
```

### 3. Monitorar Uso

```bash
# Verificar uso no dashboard
# VA PARA: https://openrouter.ai/account/usage
```

---

## 🛠️ Deploy no Streamlit Cloud

1. **Fazer Push para GitHub**
   ```bash
   git push origin main
   ```

2. **VA PARA:** https://share.streamlit.io/

3. **Nova App → Conectar GitHub**

4. **Advanced Settings → Secrets**
   ```toml
   GROQ_API_KEY = "gsk_..."
   OPENROUTER_API_KEY = "sk-or-v1-..."
   ```

5. **Deploy!**

---

## 🐛 Troubleshooting

### "API Key inválida"
```bash
# Verificar:
cat ~/.streamlit/secrets.toml

# Copiar de novo em https://openrouter.ai/keys
```

### "429 - Rate Limit"
- Espera 1-2 minutos
- Gratuito tem limite suave
- Se contínuo, use Groq em vez disso

### "Connection Timeout"
- Verifica internet
- OpenRouter está down? (raro)
- Tenta com `curl`:
```bash
curl https://openrouter.ai/api/v1/models
```

### "Modelo não encontrado"
- Verifica se o modelo está na lista gratuita
- Alguns modelos saem (raros)
- Usa alternativa como Llama 3.3 70B

---

## 📊 Comparação: Groq vs OpenRouter MoA

| Aspecto | Groq | OpenRouter MoA |
|---------|------|--------|
| **Velocidade** | ⚡ Muito Rápido | 🟢 Rápido (+2s) |
| **Qualidade** | 🟢 Excelente | ⭐⭐⭐ Excepcional |
| **Modelos** | 1 único | 4 diferentes |
| **Custo** | $0 | $0 |
| **Setup** | 3 min | 5 min |
| **Recomendado para** | Rápido & Casual | Qualidade Máxima |
| **Melhor em Parque** | ✅ Sim | ✅✅✅ Recomendado! |

---

## 🎓 Como o MoA Melhora Qualidade

**Cenário Real:**

Você está em Fantasyland, visitou 3 atrações. Qual próxima?

### Com IA Única (Groq)
```
Groq: "Vai para Dumbo (10 min de fila)"
❌ Problema: Dumbo fica distante (8 min de caminhada)
Resultado: Tempo total = 18 min (caminhada + fila)
```

### Com MoA (3 especialistas + Juiz)
```
Llama 3.3: "Dumbo (10 min fila)"
Qwen 2.5: "Peter Pan (38 min fila, mas 1 min caminhada)"
DeepSeek: "Cinderella (3 min fila, 2 min caminhada)"

JUIZ: "DeepSeek tem razão! Cinderella agora!"
✅ Resultado: Tempo total = 5 min (ótimo!)
```

---

## 🚀 Próximos Passos

1. ✅ Criar conta em https://openrouter.ai/
2. ✅ Gerar chave API
3. ✅ Adicionar em `~/.streamlit/secrets.toml`
4. ✅ Reiniciar Streamlit
5. ✅ Escolher "OpenRouter MoA 🏆" na app
6. ✅ Aproveita as recomendações perfeitas! 🎉

---

## 📞 Suporte

### Não funciona?
1. Verifica internet
2. Verifica chave (https://openrouter.ai/keys)
3. Verifica secrets.toml
4. Reinicia Streamlit: `Ctrl+C` e `streamlit run app.py`

### Perguntas?
- Docs: https://openrouter.ai/docs
- Status: https://openrouter.ai/status
- Issues: GitHub

---

**Pronto para a melhor experiência na Disneyland? 🏰✨**

Use OpenRouter MoA e receba recomendações perfeitas!
