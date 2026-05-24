---
description: Inicia o assistente de instalacao — conecta o WhatsApp e configura o escritorio, passo a passo.
---

Execute o assistente de instalacao do agente de triagem de WhatsApp, seguindo o protocolo da skill `instalacao`.

Conduza a compradora etapa por etapa, em linguagem leiga, uma pergunta por vez. Ela so responde e cola valores — VOCE escreve todos os arquivos (`config.env`, `config.json`, `voz.md`). Comece pela Etapa Preliminar (path de gravacao), depois Rotina de Retomada (verificar o que ja esta configurado), depois siga da etapa correta.

**Sequencia oficial das etapas (v0.2.3, sem pular numeros):**

- Preliminar → onde gravar os arquivos (CONFIG_DIR)
- Etapa 0 de 4 → preparar ambiente (Python)
- Etapa 1 de 4 → conectar WhatsApp (Zappfy)
- Etapa 2 de 4 → configurar escritorio
- Etapa 3 de 4 → aprender a voz
- Etapa 4 de 4 → primeira triagem demo

Apresente SEMPRE como 'Etapa X de 4' — nunca 'Etapa X/5' ou 'Etapa X de 5'.

Nunca exiba o token Zappfy de volta no chat depois de grava-lo. Nunca pre-preencha dados do escritorio a partir do CLAUDE.md externo do workspace — sempre pergunte.
