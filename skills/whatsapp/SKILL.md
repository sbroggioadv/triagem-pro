---
name: whatsapp
description: "CLI completo para WhatsApp via API Zappfy. Para triagem de mensagens SEMPRE use o comando `triagem` (nao `unread`). 45+ comandos: triagem, mensagens, grupos, CRM/leads, contatos. Dual output (human + --json)."
---

# WhatsApp Skill

CLI completo para operar WhatsApp via API Zappfy.

## ⚠️ PROTOCOLO OBRIGATORIO — Verificacao de mensagens

Quando o usuario pedir "verifica meu zap", "tem msg?", "o que tem no zap", "o que eu tenho pendente", "quem ta me devendo", ou QUALQUER variacao sobre ver mensagens/pendencias:

**SEMPRE use `triagem`. NUNCA use `unread`.**

### Por que NAO usar `unread`

O comando `unread` usa o contador `wa_unreadCount` da API Zappfy, que tem DOIS problemas estruturais que o tornam inutil:

1. **Device-scoped (desincroniza com o celular):** a Zappfy/uazapi e um dispositivo companheiro do WhatsApp. O contador dela e totalmente independente do contador do celular do usuario. Msgs ja lidas no celular continuam aparecendo como "unread" na Zappfy — historicamente acumulam ate milhares de fantasmas.

2. **Conta as proprias mensagens do usuario como "nao lidas":** quando o usuario envia msgs pelo celular, a Zappfy recebe como evento novo e tambem incrementa o contador — mesmo essa msg sendo `from_me: true`. Resultado: o comando `unread` devolve conversas onde a ultima mensagem foi ENVIADA pelo proprio usuario, contadas erroneamente como "nao lidas".

### Comando correto: `triagem`

```bash
python3 skills/whatsapp/scripts/whatsapp.py --json triagem 24
```

Parametro `24` = janela em horas. Use `6` pra urgencias, `48` pra panorama amplo, `168` pra semana toda.

O `triagem` resolve os 2 problemas acima:

- **Filtra `from_me: true`** — msgs do proprio usuario vao pra categoria `items_respondidos` (nao pra pendencias)
- **Usa gap temporal** (horas sem resposta) em vez do contador sujo
- **Detecta sender** identificado no grupo (separa equipe interna de cliente)
- **Palavras-chave de urgencia** disparam URGENTE — configuradas em `config.json` → `urgent_keywords`
- **Silencia ruido** (grupos nao-clientes, servicos SaaS) — configurado em `config.json` → `silence_keywords`

### Categorias do output `triagem`

| Categoria | Significado |
|---|---|
| `URGENTE` | palavra-chave critica no texto (definida em `config.json`) |
| `ATRASADA` | ultima msg deles, gap > threshold configurado (default 24h) |
| `IMPORTANTE` | ultima msg deles, gap dentro da faixa configurada (default 4-24h) |
| `NORMAL` | ultima msg deles, gap dentro da faixa configurada (default 1-4h) |
| `RECENTE` | ultima msg deles, gap abaixo do minimo configurado (default < 1h) |
| `EQUIPE_CUIDANDO` | ultima msg no grupo e de um membro da equipe interna (definida em `config.json` → `team`). NAO e pendencia do operador — apenas acompanhar. |
| `items_respondidos` | ultima msg e sua (bola esta com o outro lado) |

Thresholds e equipe sao configurados em `config.json`. Ver `config.json.example` para referencia.

### Protocolo completo apos rodar `triagem`

1. Rodar `triagem` com a janela apropriada (padrao 24h)
2. Carregar `skills/whatsapp/memory/_index.md` pra lookup de contatos, SE o arquivo existir (populado pelo assistente de instalacao no Sprint 2)
3. A equipe interna vem do `config.json` (campo `team`), ja aplicada pelo CLI na triagem — NAO ha arquivo `team.md` separado
4. Para cada item em `items_pendentes`:
   - Casar `last_sender` com `team` do `config.json` → se for membro da equipe, deduzir area do caso
   - Se a memoria ja foi populada (Sprint 2): casar `name` com arquivos em `memory/contacts/` e `memory/groups/` e carregar o card pra ter contexto
5. Apresentar agrupado por categoria (URGENTE/ATRASADA/IMPORTANTE/NORMAL/RECENTE), com:
   - Nome do chat + cluster se aplicavel
   - Sender (se e equipe, qual membro/area)
   - Resumo 1 linha da ultima msg
   - Gap temporal
   - Sugestao de acao (responder / delegar pra equipe / formular msg / ignorar)
6. No fim, mencionar `items_respondidos` como "voce ja respondeu X conversas (bola com o outro lado), sem acao necessaria"

### REGRAS ABSOLUTAS

- NUNCA rode `unread` pra triagem — use `triagem`
- NUNCA categorize por "Pessoais / Grupos / Juridico" — use as 6 categorias oficiais do triagem
- NUNCA liste msgs `from_me: true` em categorias de pendencia (vao pra `items_respondidos`)
- NUNCA liste msgs com sender na equipe interna como pendencia do operador — vao pra `EQUIPE_CUIDANDO`
- NUNCA apresente numeros sem contexto tipo "50 conversas nao lidas" — o contador e lixo
- **SEMPRE mostre o campo `last_text`** na apresentacao, pra o operador saber o contexto sem precisar abrir o grupo
- **SEMPRE mostre o campo `last_sender`** (nome de quem enviou a ultima msg) junto com o nome do chat
- **SEMPRE destaque visualmente `EQUIPE_CUIDANDO`** como "a equipe esta tocando" — operador so acompanha, nao precisa agir

---

## Setup

Antes de qualquer comando, garantir que `config.env` esta preenchido com o token Zappfy:

```bash
# Copiar e preencher
cp skills/whatsapp/config.env.example skills/whatsapp/config.env
# editar config.env com seu ZAPPFY_TOKEN
```

Script principal:

```bash
python3 skills/whatsapp/scripts/whatsapp.py [--json] <comando> [args...]
```

- Sem flag: output formatado para humanos
- Com `--json`: output estruturado para parsing por agentes AI

## Resolucao de Identificadores

Todos os comandos que aceitam `<numero|nome>` fazem smart resolution:
- Numero direto: `5511999999999`
- ChatID completo: `5511999999999@s.whatsapp.net` ou `GROUPID@g.us`
- Nome do contato: `"Fulano"` (fuzzy match contra lista de chats)

Se multiplos resultados, retorna lista para desambiguacao.

## Comandos

### Status

| Comando | Descricao |
|---------|-----------|
| `status` | Status da conexao |
| `presence <available\|unavailable>` | Define presenca online/offline |

### Leitura

| Comando | Descricao |
|---------|-----------|
| `unread [limite]` | Conversas com msgs nao lidas (padrao: 50) — ver aviso acima |
| `chats [limite]` | Ultimas conversas (padrao: 20) |
| `messages <numero\|nome> [limite]` | Mensagens de um contato (padrao: 20) |
| `search-chat <termo>` | Busca conversas por nome |
| `search-msg <termo> [numero\|nome]` | Busca mensagens por conteudo |
| `contact-info <numero\|nome>` | Info detalhada de contato + dados de lead |

### Envio

| Comando | Descricao |
|---------|-----------|
| `send <numero\|nome> <texto>` | Envia texto |
| `reply <numero\|nome> <msgid> <texto>` | Responde mensagem especifica |
| `send-media <numero\|nome> <url> [tipo] [legenda]` | Envia midia (image/video/audio/document) |
| `send-contact <numero\|nome> <nome_contato> <numero_contato>` | Envia cartao de contato |
| `send-location <numero\|nome> <lat> <lon> [nome] [endereco]` | Envia localizacao |
| `send-menu <numero\|nome> <json>` | Envia menu interativo (JSON inline ou arquivo) |

### LID Cache (resolve sender vazio)

A API Zappfy as vezes retorna `senderName=''` em mensagens enviadas por WhatsApp Web (vem so o LID — Linked Identifier). O CLI mantem cache persistente em `memory/lid_cache.json` que aprende LID → nome automaticamente.

| Comando | Descricao |
|---------|-----------|
| `lid-bootstrap [chats] [msgs_por_chat]` | Scan inicial pra popular cache (default: 200 chats × 30 msgs). Rodar uma vez ao instalar |
| `lid-stats` | Mostra total de LIDs cacheados e amostra |

O cache e atualizado **automaticamente** sempre que rodar `messages`, `search-msg`, `triagem` ou `group-recap`. Quanto mais uso, mais completo o cache.

### Acoes em Mensagens

| Comando | Descricao |
|---------|-----------|
| `markread <numero\|nome>` | Marca conversa como lida |
| `react <numero\|nome> <msgid> <emoji>` | Reage com emoji |
| `delete <numero\|nome> <msgid> [everyone]` | Deleta mensagem |
| `edit <numero\|nome> <msgid> <novo_texto>` | Edita mensagem enviada |
| `typing <numero\|nome> [duracao]` | Envia indicador de digitando |

### Gerenciamento de Chat

| Comando | Descricao |
|---------|-----------|
| `pin <numero\|nome>` | Fixa/desfixa conversa |
| `archive <numero\|nome>` | Arquiva/desarquiva |
| `mute <numero\|nome> [horas]` | Silencia conversa |
| `labels <numero\|nome> [list\|add\|remove] [label]` | Gerencia labels |
| `block <numero\|nome>` | Bloqueia contato |
| `unblock <numero\|nome>` | Desbloqueia contato |

### CRM / Leads

| Comando | Descricao |
|---------|-----------|
| `lead-info <numero\|nome>` | Info completa do lead |
| `lead-update <numero\|nome> <json_campos>` | Atualiza campos (JSON) |
| `lead-tag <numero\|nome> <add\|remove> <tag>` | Gerencia tags |
| `lead-assign <numero\|nome> <attendant_id>` | Atribui a atendente |
| `lead-ticket <numero\|nome> <open\|close>` | Abre/fecha ticket |
| `lead-status <numero\|nome> <status>` | Atualiza status do lead |

### Grupos

| Comando | Descricao |
|---------|-----------|
| `groups [limite]` | Lista grupos |
| `group-info <nome\|id>` | Info detalhada com participantes |
| `group-recap <nome> [horas]` | Recap de mensagens (padrao: 48h) |
| `group-create <nome> <num1> [num2...]` | Cria grupo |
| `group-participants <nome\|id> <add\|remove\|promote\|demote> <num...>` | Gerencia participantes |
| `group-update <nome\|id> <name\|description\|image> <valor>` | Atualiza grupo |
| `group-invite <nome\|id>` | Gera link de convite |
| `group-admin-only <nome\|id> <on\|off>` | Modo somente admins |

### Contatos

| Comando | Descricao |
|---------|-----------|
| `contacts [limite] [pagina]` | Lista contatos com paginacao |
| `contact-add <numero> <nome>` | Adiciona contato |
| `contact-remove <numero>` | Remove contato |

### Raw

| Comando | Descricao |
|---------|-----------|
| `raw <GET\|POST> <endpoint> [json_body]` | Chamada direta a API |

Para endpoints nao cobertos pelos comandos acima, consultar:
`skills/whatsapp/references/api-reference.md`

## Sistema de Memoria

O agente mantem memoria persistente em `skills/whatsapp/memory/` (populada pelo assistente de instalacao — ver Sprint 2):

| Arquivo | Proposito |
|---------|-----------|
| `_index.md` | Tabela de lookup rapido: nome, numero, empresa, categoria |
| `_pending.md` | Follow-ups prometidos, esperando resposta, alertas |
| `_patterns.md` | Padroes de comunicacao (horarios, comportamentos) |
| `contacts/<numero>.md` | Contact card individual com perfil e contexto |
| `groups/<groupid>.md` | Group card com regras, tipo e contexto |

### Protocolo de memoria:

**ANTES de qualquer acao:**
1. Ler `_index.md` para identificar quem esta envolvido
2. Ler contact/group card relevante se existir
3. Ler `_pending.md` para cruzar com pendencias

**APOS interacao significativa:**
1. Atualizar contact card se info nova relevante
2. Adicionar/remover itens de `_pending.md`
3. Atualizar `_index.md` se contato novo

**NAO atualizar para:** mensagens triviais (ok, obrigado), info ja registrada.

## Regras

1. **NUNCA enviar mensagem sem aprovacao explicita do usuario** — mostrar mensagem exata e esperar "manda", "pode enviar", "vai"
2. **SEMPRE carregar contexto antes de agir** — memoria + contexto do cliente se aplicavel
3. Delay padrao de 1500ms em envios para simular digitacao natural
4. readchat: true em envios para marcar como lido automaticamente
5. Para operacoes avancadas nao cobertas, usar `raw` com referencia ao api-reference.md
