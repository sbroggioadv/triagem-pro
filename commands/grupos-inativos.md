---
description: Lista grupos de cliente sem atividade há mais de N dias (default 14).
---

Identifique grupos de cliente com baixa/zero atividade — sinal de cliente esfriando ou conversa morta.

## Roteiro

1. Pergunte ao operador o threshold de dias — default 14. Se já disse no input (`/grupos-inativos 30`), use o valor.

2. Carregue `config.json` pra ter `client_group_prefixes` e `internal_groups`.

3. Liste todos os grupos:

```bash
python3 skills/whatsapp/scripts/whatsapp.py --json groups 200
```

4. Filtre:
   - Inclua apenas grupos cujo nome **começa com algum prefixo de `client_group_prefixes`** (são grupos de cliente).
   - Exclua qualquer grupo cujo nome esteja em `internal_groups`.

5. Para cada grupo filtrado, puxe a última mensagem:

```bash
python3 skills/whatsapp/scripts/whatsapp.py --json messages "<groupid>" 1
```

6. Calcule o gap em dias entre o timestamp dessa mensagem e agora.

7. Mantenha apenas os grupos onde `gap_dias >= <threshold>`.

8. Ordene por `gap_dias` decrescente.

9. Renderize:

```
=== Grupos Inativos — sem atividade há >= <N> dias ===

🔴 ABANDONADOS (gap > 60 dias)
- [Nome do grupo] | última msg: [data] | há [X] dias | último a falar: [quem]
- ...

🟠 ESFRIANDO (30-60 dias)
- ...

🟡 ATENÇÃO (14-30 dias)
- ...

Total inativos: [N]
```

10. Para cada item nos níveis 🔴/🟠, ofereça:

> "Quer que eu monte uma mensagem de check-in pra algum desses?"

Mas **não invoque o redator automaticamente** — só ofereça. Se o operador disser sim com um nome específico, aí sim o `triagem` invoca o redator no fluxo padrão.
