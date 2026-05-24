---
description: Aprende ou atualiza o perfil de voz da compradora (gera/atualiza $CONFIG_DIR/voz.md).
---

Execute o protocolo da skill `voz`.

Se `$CONFIG_DIR/voz.md` já existir, pergunte primeiro: "Já tem um perfil de voz aprendido aqui. Você quer (a) atualizar com mensagens mais recentes, (b) começar do zero, ou (c) só revisar o atual?" — e siga conforme a resposta.

Conduza tudo em linguagem leiga. A compradora **só responde**; você puxa, analisa e grava. Nunca exiba o `voz.md` inteiro no chat — mostre o resumo de 5–6 traços e aponte o arquivo.

---

## Bootstrap de Sessao (v0.2.3 — se invocado fora do fluxo do triagem)

Se voce esta sendo invocado e `$CONFIG_DIR` nao esta setado no shell, rode este comando UMA vez no inicio:

```bash
export CONFIG_DIR="$(python3 skills/whatsapp/scripts/whatsapp.py config-dir)"
```

Esse subcomando faz multi-path discovery automatica e retorna o path absoluto. Depois disso todos os `"$CONFIG_DIR/X"` resolvem corretamente. Normalmente o agente `triagem` ja exportou antes de invocar voce — mas a redundancia nao machuca.

---

