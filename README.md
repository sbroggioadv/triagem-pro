# Triagem Pro

Agente de triagem de WhatsApp para escritórios de advocacia, distribuído como **plugin Claude Code**.

A advogada conecta o WhatsApp dela à Zappfy, o plugin lê tudo, classifica por urgência usando regras configuráveis do escritório, mantém um quadro vivo de pendências, aprende a voz dela a partir das mensagens que ela mesma enviou, e redige respostas no estilo dela aplicando guardrail OAB antes de devolver — sempre pedindo aprovação antes de enviar.

**Instalação e configuração 100% pelo chat.** A advogada não precisa ser desenvolvedora.

---

## Como instalar

Tudo está no [INSTALAR.md](./INSTALAR.md) — passo a passo, com prints, sem código. Leva 15 minutos.

## O que vem na caixa

| Componente | O que faz |
|------------|-----------|
| **Triagem** | "Verifica meu zap" → tabela com pendências classificadas por urgência (URGENTE / ATRASADA / IMPORTANTE / NORMAL / RECENTE). |
| **Redator** | Leitor da sua voz + aplicador do guardrail OAB. Devolve 1–3 opções de mensagem; você aprova qual sai. |
| **Guardrail OAB** | 5 travas éticas aplicadas em toda mensagem (promessa de resultado, dados sensíveis, aconselhamento a lead, captação, emoji em comunicação profissional). Configurável por escritório. |
| **Aprende sua voz** | `/aprender-voz` lê suas mensagens enviadas, destila estilo, gera `voz.md`. Re-rode quando quiser atualizar. |
| **Quadro de pendências** | Cruza com seu CRM (in-chat) e alerta vencimentos. |
| **Comandos de supervisão** | `/sem-resposta`, `/tempo-resposta`, `/resumo-dia`, `/grupos-inativos` — só relatam, nunca redigem ou enviam automaticamente. |

## Segurança em 1 frase

Tudo roda na **sua máquina**. Nenhum dado passa por servidor nosso. Nenhuma telemetria. Sigilo profissional inviolável.

## Suporte

Encontrou bug? Sugestão? Abra issue neste repositório.

---

Triagem Pro · uso e distribuição sob autorização.
