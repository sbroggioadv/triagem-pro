---
description: Calcula tempo médio de resposta do operador (e da equipe) nos últimos N dias. Default 7 dias.
---

Calcule e apresente o tempo médio de resposta do operador nas conversas do WhatsApp.

## Roteiro

1. Pergunte ao operador qual período usar — default 7 dias. Se já disse no input (`/tempo-resposta 14`), use o valor.

2. Liste os chats com atividade no período:

```bash
python3 skills/whatsapp/scripts/whatsapp.py --json chats 50
```

3. Para cada chat com atividade no período, puxe as mensagens:

```bash
python3 skills/whatsapp/scripts/whatsapp.py --json messages "<chatid>" 50
```

4. Para cada par (mensagem do cliente → resposta do operador `fromMe=true`), calcule o gap em horas.

5. Considere apenas pares onde:
   - A mensagem do cliente é seguida por uma resposta `fromMe=true` no mesmo chat.
   - Ignorar pares onde o gap > 14 dias (provável conversa pausada, não atraso real).

6. Calcule:
   - **Mediana** do tempo de resposta (mais representativa que média porque outliers distorcem).
   - **P75** (75% dos casos respondidos em até X horas).
   - **Mais lento** (chat onde o gap foi maior, com nome do contato).
   - **Mais rápido** (chat com gap menor).

7. Renderize:

```
=== Tempo de Resposta — últimos <N> dias ===

Mediana: [X]h
P75: [Y]h (75% dos contatos respondidos em até [Y]h)
Mais lento: [Nome] — [Zh]h
Mais rápido: [Nome] — [Wh] minutos

Conversas analisadas: [total]
Pares (msg → resposta) considerados: [pares]

Observação: [comentário curto contextual — ex: "P75 abaixo de 4h é excelente", ou "P75 alto indica que vale priorizar".]
```

8. **Nunca invoque o redator nesse comando.**
