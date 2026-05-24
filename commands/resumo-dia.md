---
description: Resumo do que aconteceu no WhatsApp nas últimas 24h — quantos chats, urgência, categorias.
---

Gere um resumo diário das interações de WhatsApp das últimas 24 horas.

## Roteiro

1. Rode a triagem com janela de 24h:

```bash
python3 skills/whatsapp/scripts/whatsapp.py --json triagem 24
```

2. Do JSON retornado, agrupe e conte:

```
=== Resumo do dia — últimas 24h ===

📊 Atividade
- Chats com mensagens novas: [total]
- Mensagens recebidas: [N]
- Mensagens enviadas (suas): [M]

🚨 Urgência
- 🔴 URGENTE: [N] (palavra-chave crítica detectada)
- 🟠 ATRASADA: [N] (mais de [atrasada_hours]h sem resposta)
- 🟡 IMPORTANTE: [N]
- ⚪ NORMAL/RECENTE: [N]

🎯 Estado das conversas
- AGUARDANDO VOCÊ: [N] (a bola está com você)
- EQUIPE CUIDANDO: [N] (equipe interna respondeu)
- VOCÊ JÁ RESPONDEU: [N] (bola com o cliente)

🔝 Top 5 mais urgentes
1. [Nome do chat] — [gap]h — "[trecho 80 chars]"
2. ...

🎉 Conquistas do dia
- [conversas respondidas hoje, baseado em fromMe nas últimas 24h]
```

3. Use leitura via `config.json` pra puxar `atrasada_hours`/`importante_hours` reais (não hardcoded).

4. Ao final, ofereça ações:

> "Quer que eu detalhe alguma categoria, ou prepare resposta pra algum item específico?"

5. **Nunca invoque o redator nesse comando** — só relate.
