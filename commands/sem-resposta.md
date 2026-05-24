---
description: Relatório de clientes que estão aguardando sua resposta há mais tempo (gap configurável, default 24h).
---

Gere o relatório "Sem Resposta" — pendências mais antigas do seu lado.

## Roteiro

1. Pergunte ao operador qual janela usar — defaults sugeridos: 24h, 48h, 7 dias. Se ele já disse no input do comando (`/sem-resposta 48`), use o valor.

2. Rode a triagem com a janela escolhida:

```bash
python3 skills/whatsapp/scripts/whatsapp.py --json triagem <janela_em_horas>
```

3. Do JSON retornado, use **apenas** o array `items_pendentes` (esses já são os que aguardam o operador — `items_respondidos` é o oposto). Em seguida, filtre por:
   - `urgencia in ["URGENTE", "ATRASADA", "IMPORTANTE"]` (descarta `NORMAL` e `RECENTE`), e
   - `gap_hours >= <janela>` (acima do threshold).

4. Ordene por `gap_hours` decrescente.

5. Renderize como tabela no chat, agrupada por urgência (URGENTE primeiro):

```
=== Sem Resposta — últimas <janela>h ===

🔴 URGENTE (N)
- [name] | sender: [last_sender] | gap: [gap_hours]h | "[last_text 100 chars]" | sugestão: responder hoje
- ...

🟡 ATRASADA (N)
- ...

Total pendentes: N
```

6. **NUNCA invoque o redator nesse comando.** Esse é um comando de supervisão — só reporta. Se o operador quiser redigir resposta pra um item específico depois, ele pede explicitamente "redige resposta pra [item]" e aí o `triagem` invoca o redator no fluxo padrão.

7. Ao final, ofereça: "Quer que eu prepare resposta pra algum desses?" — só essa pergunta, sem auto-acionar nada.
