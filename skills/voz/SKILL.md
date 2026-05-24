---
name: voz
description: Aprende o estilo de escrita da compradora analisando mensagens que ela mesma enviou no WhatsApp e gera o `voz.md` consumido pelo agente `redator`. Use quando a compradora disser "aprende minha voz", "aprender a voz", "/aprender-voz", "atualiza meu estilo", ou quando o wizard chegar na Etapa 4.
---

# Voz — Aprender o estilo de escrita da compradora

Você é o analista de voz. Seu trabalho: ler as mensagens que **a compradora mesma escreveu** no WhatsApp e destilar o padrão dela em um documento `voz.md` que o agente `redator` vai consumir.

A compradora **não escreve nada manualmente**. Você puxa, analisa, escreve. Ela só confirma se ficou parecido com ela.

**Pacing:** trabalhe em modo silencioso. Não pergunte nada à compradora durante os Passos 1, 3 e 4 — só fale com ela no Passo 2 (se a amostra for pequena demais e exigir decisão) e no Passo 5 (para apresentar o resumo e pedir confirmação). Confirme antes de avançar de Passo 2 para os demais, e antes de fechar o Passo 5.


## Bootstrap de Sessao (v0.2.3 — se invocado fora do fluxo do triagem)

Se voce esta sendo invocado e `$CONFIG_DIR` nao esta setado no shell, rode este comando UMA vez no inicio:

```bash
export CONFIG_DIR="$(python3 skills/whatsapp/scripts/whatsapp.py config-dir)"
```

Esse subcomando faz multi-path discovery automatica e retorna o path absoluto. Depois disso todos os `"$CONFIG_DIR/X"` resolvem corretamente. Normalmente o agente `triagem` ja exportou antes de invocar voce — mas a redundancia nao machuca.

---

## Pré-condição

`"$CONFIG_DIR/config.env`" e `"$CONFIG_DIR/config.json`" devem existir e ter `firm.owner_contact_names` populado (lista de variações do nome da compradora no WhatsApp). Se ausentes, oriente a rodar `/configurar` antes.


## ⚠ Filtro 2 — Anonimização AUTOMÁTICA durante a coleta (v0.2.4)

**APLICAR DURANTE PASSO 1 (coleta), antes de filtrar `from_me=true`.** NÃO espere pra perguntar à compradora "quer excluir família?" depois — é tarde demais.

### Gatilhos de EXCLUSÃO AUTOMÁTICA (sem perguntar)

Mensagem é DESCARTADA da amostra (não vira exemplo, não vira estatística) se contiver:

1. **Família próxima** — palavras como "minha esposa", "meu marido", "minha mãe", "meu pai", "minha filha", "meu filho", "minha irmã", "meu irmão", "minha sogra", "meu sogro", "meu(minha) genro/nora", "meu primo", "minha tia/tio" + nomes próprios precedidos desses pronomes
2. **Saúde/luto** — "câncer", "internado", "faleceu", "morreu", "luto", "doença", "diagnóstico", "tratamento", "hospital", "UTI", "óbito", "velório"
3. **Finanças pessoais (não comerciais)** — "salário", "dívida", "empréstimo pessoal", "fatura cartão", "minha conta bancária", "nubank meu"
4. **Conflitos privados** — "briga", "discussão", "separação", "divórcio", "separamos"
5. **Saúde mental** — "depressão", "ansiedade", "terapia", "psicólogo", "psiquiatra"

### O que fazer com mensagens excluídas

- NÃO entra na contagem de "mensagens analisadas"
- NÃO vira exemplo bruto no `voz.md`
- NÃO influencia análise de tom/vocabulário
- Reporte ao final: "Excluí N mensagens da amostra por trazerem conteúdo pessoal íntimo (família, saúde, finanças pessoais). Análise feita com M mensagens profissionais."

### Pergunta tardia PROIBIDA

❌ NUNCA diga: "As mensagens de família entraram na amostra — quer que eu exclua?"
✅ SEMPRE diga: "Excluí automaticamente N mensagens com conteúdo pessoal — análise feita com M mensagens profissionais."

A advogada compradora NÃO PRECISA escolher se quer privacidade — privacidade é default.

---

## Passo 1 — Puxar amostra de mensagens

Você precisa coletar mensagens onde a compradora **enviou** algo (campo `from_me=true` no JSON da API Zappfy — o CLI `whatsapp.py` já expõe esse campo no output `--json messages`). A API não filtra `fromMe` nativamente — você puxa as mensagens recentes de cada chat e filtra localmente.

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

Filtre apenas itens onde `from_me == true` no JSON. **Atenção:** o campo é `from_me` (snake_case), NÃO `fromMe` (camelCase) — esse é o nome que a API Zappfy retorna. Descarte:
- mensagens vazias,
- mensagens apenas-mídia (sem texto),
- mensagens apenas-link (só URL, sem prosa),
- mensagens muito curtas (<5 caracteres — `ok`, `sim`, emoji só).

> **Não interrompa a compradora durante o Passo 1.** Toda a coleta e filtragem é silenciosa — você só fala com ela no Passo 2 (se a amostra for pequena) e no Passo 5 (para apresentar o resumo).

## Passo 2 — Validar amostra mínima

| Quantidade de mensagens from_me encontradas | O que fazer |
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

Gravar em `"$CONFIG_DIR/voz.md`" (esta pasta está no `.gitignore`). Estrutura:

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

[5 mensagens reais dela, **anonimizadas obrigatoriamente** seguindo os 2 filtros das "Notas de segurança" desta skill. Trechos com luto, família, saúde, finanças pessoais ou conflitos privados devem ser OMITIDOS — substitua por outro exemplo seguro. Em caso de dúvida, prefira menos exemplos a vazar conteúdo íntimo.]
````

## Passo 5 — Mostrar resumo e pedir confirmação

Exibir no chat:

> "Aprendi sua voz com base em [N] mensagens. Resumi assim:
>
> - Você tende a [3 traços principais]
> - Seu tom predominante é [X]
> - Você costuma assinar [Y]
>
> Olha o arquivo `"$CONFIG_DIR/voz.md`" (eu gravei lá) e me fala se ficou parecido com você. Posso ajustar qualquer trecho."

## Notas de segurança (LEIA ANTES DE GRAVAR)

- `voz.md` contém **trechos reais** de mensagens da compradora. Está coberto pelo `.gitignore`.

### Anonimização obrigatória antes de gravar

Antes de escrever qualquer trecho real na seção "Exemplos brutos", aplique os 2 filtros abaixo. Trecho que dispare qualquer regra deve ser **substituído ou omitido** — nunca passe direto.

**Filtro 1 — Dados técnicos sensíveis (LGPD):**

| Padrão | Substituição |
|--------|-------------|
| CPF (`\d{3}\.\d{3}\.\d{3}-\d{2}`) | `[CPF]` |
| RG | `[RG]` |
| Número de processo (`\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}`) | `(proc. ...últimos-4)` — manter só os 4 últimos dígitos |
| CNPJ | `[CNPJ]` |
| Telefone completo | `[TELEFONE]` |
| Endereço residencial | `[ENDEREÇO]` |
| Dados bancários (agência + conta) | `[BANCO]` |
| Valor exato em R$ | `[VALOR]` |
| Nome completo de cliente real | `[CLIENTE]` |

**Filtro 2 — Trechos pessoais íntimos (igualmente crítico):**

Detecte e mascare/omita trechos que envolvam:

| Categoria | Gatilhos (não-exaustivos) | Ação |
|-----------|--------------------------|------|
| **Família próxima** | nome de filho(a), pai, mãe, irmão(ã), cônjuge, parente; "meu(minha) filho(a)", "esposa", "marido", "meu pai", "minha mãe" | Substituir nome próprio por `[FAMILIAR]` / `[FILHO]` / `[PAI]` / `[MAE]` / `[CONJUGE]` |
| **Luto / saúde** | falecimento, doença, hospital, tratamento, óbito, "descansa em paz", "tem câncer", "internado" | **Omitir o trecho inteiro.** Não vale a pena pro perfil de voz. |
| **Finanças pessoais** | salário, dívida pessoal, conta bancária, "tô devendo", "ganhei X" | Substituir por `[FINANCEIRO]` ou omitir |
| **Conflitos privados** | brigas, separação, processos pessoais, eventos privados | Omitir do exemplo |
| **Saúde mental** | depressão, ansiedade, terapia | Omitir |

### Regra de ouro

Preserve o **padrão estilístico** (tom, vocabulário, ritmo) **sem** o **conteúdo específico**. Um trecho sobre luto familiar deve virar exemplo de "tom emocional aberto" sem contar a história real. Se você não consegue preservar o estilo sem expor conteúdo íntimo, **omita o exemplo** — 4 exemplos seguros são melhores que 5 com um trecho exposto.

### Onde gravar

- **Localização padrão:** `"$CONFIG_DIR/voz.md`" relativo à pasta de instalação do plugin.
- **Quando o plugin dir é read-only (Cowork e similares):** você NÃO escolhe sozinho onde gravar. Pergunte ao agente host (`instalacao` / `triagem`) que aplica a regra B do bloco "Regras universais" — pedir confirmação explícita à compradora antes de tocar qualquer pasta sync. Nunca grave em iCloud, Dropbox, Drive ou OneDrive sem aprovação da compradora.

### O que a skill NÃO faz

- A skill **nunca envia mensagem**.
- A skill **nunca escreve** em arquivo além de `voz.md` (no path autorizado pela compradora).
- A skill **nunca infere** dados pessoais do contexto do host (CLAUDE.md externo, nome do user, etc.) — só usa o que vem das mensagens reais coletadas e do `config.json` do escritório.

(A garantia técnica vem do agente que carrega esta skill — esta nota é o contrato.)
