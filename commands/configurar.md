---
description: Inicia o assistente de instalacao — conecta o WhatsApp e configura o escritorio, passo a passo.
---

Execute o assistente de instalacao do agente de triagem de WhatsApp, seguindo o protocolo da skill `instalacao`.

Conduza a compradora etapa por etapa, em linguagem leiga, uma pergunta por vez. Ela so responde e cola valores — VOCE escreve todos os arquivos (`config.env`, `config.json`, `voz.md`). Comece pela Etapa Preliminar (path de gravacao), depois Rotina de Retomada (verificar o que ja esta configurado), depois siga da etapa correta.

**Sequencia oficial das etapas (v0.2.3, sem pular numeros):**

- Preliminar → onde gravar os arquivos (CONFIG_DIR)
- Etapa 0 → preparar ambiente (Python)
- Etapa 1 → conectar WhatsApp (Zappfy)
- Etapa 2 → configurar escritorio
- Etapa 3 → aprender a voz
- Etapa 4 → primeira triagem demo

Nunca exiba o token Zappfy de volta no chat depois de grava-lo. Nunca pre-preencha dados do escritorio a partir do CLAUDE.md externo do workspace — sempre pergunte.
