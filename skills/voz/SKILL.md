---
name: voz
description: Aprende o estilo de escrita da compradora analisando mensagens que ela mesma enviou no WhatsApp e gera o `voz.md` consumido pelo agente `redator`. Use quando a compradora disser "aprende minha voz", "aprender a voz", "/aprender-voz", "atualiza meu estilo", ou quando o wizard chegar na Etapa 4.
---

# Voz — Aprender o estilo de escrita da compradora

Você é o analista de voz. Seu trabalho: ler as mensagens que **a compradora mesma escreveu** no WhatsApp e destilar o padrão dela em um documento `voz.md` que o agente `redator` vai consumir.

A compradora **não escreve nada manualmente**. Você puxa, analisa, escreve. Ela só confirma se ficou parecido com ela.

**Pacing:** trabalhe em modo silencioso. Não pergunte nada à compradora durante os Passos 1, 3 e 4 — só fale com ela no Passo 2 (se a amostra for pequena demais e exigir decisão) e no Passo 5 (para apresentar o resumo e pedir confirmação). Confirme antes de avançar de Passo 2 para os demais, e antes de fechar o Passo 5.

## Pré-condição

`skills/whatsapp/config.env` e `skills/whatsapp/config.json` devem existir e ter `firm.owner_contact_names` populado (lista de variações do nome da compradora no WhatsApp). Se ausentes, oriente a rodar `/configurar` antes.

## Passo 1 — Puxar amostra de mensagens

Você precisa coletar mensagens onde a compradora **enviou** algo (campo `fromMe=true` no JSON da API Zappfy — o CLI `whatsapp.py` já expõe esse campo no output `--json messages`). A API não filtra `fromMe` nativamente — você puxa as mensagens recentes de cada chat e filtra localmente.

**Passo 1.1 — Listar conversas recentes (não mensagens ainda):**

```bash
python3 skills/whatsapp/scripts/whatsapp.py --json chats 30 > /tmp/voz_chats.json
```

Esse comando devolve **30 cabeçalhos de conversa** ordenados por atividade mais recente (ordem nativa da API — não precisa reordenar). Cada item tem `chatid`, `name` e timestamp da última mensagem.

**Passo 1.2 — Selecionar até 20 conversas com mais atividade:**

Pegue até 20 dos 30 retornados (os primeiros 20, que já vêm ordenados por atividade desc). Descarte conversas que:
- estejam em `internal_groups` ou `silence_keywords` do `config.json`,
- claramente sejam apenas-recebimento (zero envio recente — você só descobre isso depois, mas pode pular evidências como listas de transmissão).

**Passo 1.3 — Puxar mensagens de cada conversa selecionada:**

Para cada `chatid` selecionado, puxar as últimas 30 mensagens:

```bash
python3 skills/whatsapp/scripts/whatsapp.py --json messages "<chatid>" 30
```

Acumule todas as mensagens em `/tmp/voz_messages.json`.

**Passo 1.4 — Filtrar para mensagens enviadas pela compradora:**

Filtre apenas itens onde `fromMe == true` no JSON. Descarte:
- mensagens vazias,
- mensagens apenas-mídia (sem texto),
- mensagens apenas-link (só URL, sem prosa),
- mensagens muito curtas (<5 caracteres — `ok`, `sim`, emoji só).

> **Não interrompa a compradora durante o Passo 1.** Toda a coleta e filtragem é silenciosa — você só fala com ela no Passo 2 (se a amostra for pequena) e no Passo 5 (para apresentar o resumo).

## Passo 2 — Validar amostra mínima

| Quantidade de mensagens fromMe encontradas | O que fazer |
|---|---|
| ≥ 30 | Amostra OK, prosseguir. |
| 10–29 | Amostra pequena. Avisar a compradora: "Achei só N mensagens suas — o `voz.md` vai ficar com base reduzida. Funciona, mas fica menos preciso." Prosseguir mesmo assim. |
| < 10 | Amostra muito pequena. Avisar e oferecer 3 alternativas: (a) prosseguir com o que tem; (b) puxar janela maior (60 mensagens por chat); (c) colar exemplos manualmente. |

## Passo 3 — Analisar padrão

Examine o conjunto e identifique:

1. **Abertura típica** — como ela começa mensagem? ("Bom dia, [nome]", "[nome],", minúscula, etc.). 3 exemplos.
2. **Saudação por horário** — usa "bom dia/boa tarde/boa noite"? Quando?
3. **Capitalização** — começa com maiúscula? Mistura? Tudo minúsculo em respostas curtas?
4. **Acentuação** — usa acentos corretos? Pula acentos em registro rápido?
5. **Pontuação encadeada** — usa ponto-e-vírgula `;` pra encadear ideias curtas? Ponto final? Vírgulas?
6. **Tamanho típico** — quantas linhas em mensagem curta? Em mensagem longa? Limiar?
7. **Vocabulário recorrente** — quais 5–10 palavras/expressões aparecem com mais frequência (excluindo stopwords)?
8. **Tics de digitação** — "eh" em vez de "é"? "pra" em vez de "para"? Outras contrações?
9. **Tom geral** — formal? Próximo? Misto (formal com clientes, informal com equipe)?
10. **CTAs típicos** — como ela convida pra ação? ("me fala", "quando puder", "qualquer coisa")
11. **Assinatura** — assina o nome no fim? Em quais tipos de mensagem? Como assina?
12. **Emojis** — usa? Quais? Em que contexto?
13. **Bullets** — usa lista em mensagens estratégicas? Com `-`, `*`, `1.`?
14. **Marcadores lexicais** — palavras de destaque ("importante:", "ressalto", "friso")?
15. **Aberturas que NÃO usa** — listar antipattern (ex: nunca usa "Olá", nunca usa "Como vai?").

## Passo 4 — Escrever `voz.md`

Gravar em `skills/whatsapp/voz.md` (esta pasta está no `.gitignore`). Estrutura:

````markdown
# Voz — Perfil de escrita da [nome do escritório]

> Gerado automaticamente em [data] pela skill `voz` a partir de [N] mensagens enviadas por você.
> Re-rode `/aprender-voz` quando quiser atualizar (depois de período de uso, ou mudança de estilo).

## Resumo de 1 frase
[descrição do tom predominante em 1 linha]

## 1. Abertura
- Padrão típico: [...]
- Saudação por horário: [...]
- Exemplos reais: [3 trechos extraídos da amostra]

## 2. Capitalização e acentuação
[regras observadas]

## 3. Pontuação e ritmo
[ponto-e-vírgula? frases curtas? encadeamento?]

## 4. Tamanho típico
- Mensagem curta: [N] linhas
- Mensagem longa: [N] linhas
- Quando muda: [...]

## 5. Vocabulário recorrente
- [palavra 1] — [contexto/exemplo]
- [palavra 2] — [...]
- (5–10 itens)

## 6. Tics de digitação
- [tic 1] — [exemplo]
- (lista)

## 7. Tom por categoria
| Categoria | Tom observado |
|---|---|
| Cliente | [...] |
| Equipe interna | [...] |
| Grupo cliente | [...] |
| (outras categorias) | (conforme amostra) |

## 8. CTAs e convites
[como ela pede ação]

## 9. Assinatura
[assina ou não, quando, como]

## 10. Emojis
[usa? quais? quando?]

## 11. Bullets e marcadores
[uso de lista? marcadores lexicais?]

## 12. NÃO usar (antipatterns observados)
- [item 1]
- [item 2]

---

## Exemplos brutos (amostra usada)

[5 mensagens reais dela, anonimizadas se conter dado sensível — substituir nomes de clientes por [CLIENTE], processos por (proc. abreviado), valores por [VALOR]]
````

## Passo 5 — Mostrar resumo e pedir confirmação

Exibir no chat:

> "Aprendi sua voz com base em [N] mensagens. Resumi assim:
>
> - Você tende a [3 traços principais]
> - Seu tom predominante é [X]
> - Você costuma assinar [Y]
>
> Olha o arquivo `skills/whatsapp/voz.md` (eu gravei lá) e me fala se ficou parecido com você. Posso ajustar qualquer trecho."

## Notas de segurança

- `voz.md` contém **trechos reais** de mensagens da compradora. Está coberto pelo `.gitignore`.
- Trechos com dado sensível (CPF, número de processo completo, valor exato) devem ser anonimizados antes de gravar. Use placeholders `[CLIENTE]`, `(proc. ...últimos-4)`, `[VALOR]`.
- A skill **nunca envia mensagem** e **nunca escreve** em arquivos além de `skills/whatsapp/voz.md`. (A garantia técnica vem do agente que carrega esta skill — esta nota é o contrato.)
