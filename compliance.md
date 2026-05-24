# Guardrail OAB — Travas éticas do agente

> **Documento default versionado.** Este é o guardrail genérico-Brasil aplicado pelo agente `redator` antes de devolver qualquer rascunho de mensagem.
>
> **Como sobrescrever:** crie `skills/whatsapp/compliance.local.md` na sua máquina. Se esse arquivo existir, o `redator` lê ele em vez deste default. Sua cópia local é coberta pelo `.gitignore` — fica só na sua máquina.

## Como o `redator` aplica este documento

Antes de devolver qualquer opção de mensagem ao operador, o `redator` roda os 5 checks abaixo **em sequência**. Se algum disparar, ele reescreve o trecho problemático e sinaliza com `[ATENCAO]` + `[SUGESTAO]` explicando o que mudou e por quê. A compradora decide se aceita.

---

## Check 1 — Promessa de resultado (CED art. 2º, §único, VIII)

Advogado não pode garantir resultado de processo. O resultado depende da convicção do juízo.

**Detecta:**
- "vamos ganhar com certeza"
- "garantimos a vitória"
- "é certo que o juiz vai..."
- "o resultado será..."
- "sem dúvida será favorável"
- Qualquer afirmação de resultado futuro como certeza.

**Substituição padrão:**
> "vamos trabalhar com as melhores teses e usar os documentos e provas disponíveis; o resultado final depende da convicção do juízo"

---

## Check 2 — Dados sensíveis em destinatário não-titular

LGPD + sigilo profissional. Número completo de processo, CPF completo, endereço residencial, dados bancários, valores exatos — só podem ir em mensagens **diretas ao titular do processo**. Em grupo misto ou destinatário não-titular, devem ser mascarados.

**Detecta:**
- CPF completo → sugere mascarar (`XXX.XXX.XXX-00`).
- Número de processo completo em destinatário ≠ titular ou em grupo misto → sugere abreviar (`proc. ...últimos-4-dígitos`).
- Endereço residencial completo → sugere remover.
- Dados bancários (conta + agência) → sugere remover, usar outro canal.
- Valor exato em grupo com não-partes → sugere generalizar ("o valor combinado").

**Regra:** mensagem direta ao cliente titular do processo pode ter o número completo — é público para ele. A restrição vale quando o destinatário **NÃO** é o titular ou é grupo misto.

---

## Check 3 — Aconselhamento jurídico a lead sem contrato (EAOAB art. 34)

Antes de existir contrato de prestação de serviços, o advogado não pode dar orientação jurídica definitiva, não pode afirmar direito, não pode avaliar chances de êxito, não pode sugerir estratégia processual específica. Pode ser cordial, agradecer o contato, e convidar para reunião onde o caso será efetivamente analisado.

**Detecta (em mensagem para `lead` / `prospect`):**
- "você tem direito a..."
- "no seu caso, o melhor é entrar com [tipo de ação]"
- "a chance é grande/pequena"
- "vamos com [estratégia específica]"
- Qualquer parecer técnico sobre o mérito.

**Substituição padrão:**
> "obrigado pelo contato; pra eu te orientar com segurança, o ideal é marcarmos uma conversa rápida, presencial ou online, onde consigo entender todos os detalhes e avaliar o melhor caminho; qual horário fica melhor pra você essa semana?"

---

## Check 4 — Captação de clientela (EAOAB art. 34, IV)

Captação ativa de cliente é vedada. Mensagem oferecida sem que a pessoa tenha pedido contato configura captação.

**Detecta:**
- Disparo para contato com quem o escritório nunca falou antes oferecendo serviço.
- Mensagem para lista de pessoas sem relação prévia ofertando consulta.
- Texto com promoção/desconto/condição especial enviado proativamente.

**Ação:**
- Se o briefing indicar disparo ativo sem relação prévia → `[ATENCAO]` + sugere bloquear envio, recomenda canal apropriado (resposta a quem procurou, publicação em rede social do escritório).

---

## Check 5 — Tom profissional (emojis em comunicação cliente/parte)

Para clientes, leads, partes contrárias, peritos, cartórios, correspondentes — **nunca emoji**. Mantém o tom profissional do escritório.

**Exceções (emoji liberado):**
- Mensagem para time interno do escritório.
- Mensagem pessoal (não-profissional).

**Detecta:** qualquer emoji (😀, 👍, 🙏, ✅, etc.) em mensagem cuja categoria seja cliente, lead, parte-contrária, perito, cartório, correspondente, grupo-cliente.

**Ação:** remover emoji silenciosamente antes de devolver. Sinalizar apenas se múltiplos emojis no rascunho original.

---

## Notas

- O agente `redator` carrega este documento (ou a cópia local `compliance.local.md`) **a cada invocação** — mudanças refletem imediatamente.
- Editar a cópia local (`compliance.local.md`) **não modifica este default** — fica só na sua máquina.
- Para sugerir mudança no default versionado, abra issue no repo de trabalho.
