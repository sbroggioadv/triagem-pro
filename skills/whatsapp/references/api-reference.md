# Zappfy — Referência Completa da API

> Documentacao de referencia da API Zappfy/uazapi v2.
> Esta referencia complementa o `skills/whatsapp/SKILL.md` (que documenta o CLI Python).
> Use esta doc quando precisar chamar um endpoint que **nao esta coberto** pelos comandos da CLI — neste caso, usar `python3 scripts/whatsapp.py raw <METHOD> <endpoint> [json]`.

**Base URL (padrao):** `https://zappfy-v2.uazapi.com` (configurado em `config.env > ZAPPFY_BASE_URL`)
**Base URL (alternativa Zappfy oficial):** `https://app.zappfy.com.br`
**Autenticacao:** header `token: $ZAPPFY_TOKEN`

---

## Índice

1. [Instância](#1-instância)
2. [Enviar Mensagens](#2-enviar-mensagens)
3. [Ações em Mensagens](#3-ações-em-mensagens)
4. [Chats](#4-chats)
5. [Contatos](#5-contatos)
6. [Grupos](#6-grupos)
7. [CRM / Leads](#7-crm--leads)
8. [Business / Catálogo](#8-business--catálogo)
9. [Webhooks](#9-webhooks)
10. [Agentes e Chatbot](#10-agentes-e-chatbot)
11. [Sender (Disparos em Massa)](#11-sender-disparos-em-massa)
12. [Triggers e Knowledge](#12-triggers-e-knowledge)


---

## 1. Instância

### GET /instance/status
Verifica status da conexão.
Resposta: `{ "status": "connected" | "disconnected" | "connecting" }`

### POST /instance/init
Inicializa/cria uma nova instância.

### POST /instance/connect
Conecta instância (gera QR code ou paircode).

### POST /instance/disconnect
Desconecta instância do WhatsApp.

### POST /instance/updatechatbotsettings
Atualiza configurações do chatbot da instância.
```json
{
  "chatbot_enabled": true,
  "chatbot_ignoreGroups": true,
  "chatbot_stopConversation": "parar",
  "chatbot_stopMinutes": 60
}
```

### POST /instance/presence
Altera presença da instância.
```json
{ "presence": "available" | "unavailable" }
```

### POST /profile/name
Atualiza nome do perfil.
```json
{ "name": "Novo Nome" }
```

### POST /profile/image
Atualiza foto do perfil (URL ou Base64).

---

## 2. Enviar Mensagens

### POST /send/text
Envia mensagem de texto.
```json
{
  "number": "5511999999999",
  "text": "Mensagem aqui",
  "delay": 1500,
  "readchat": true,
  "readmessages": true,
  "replyid": "MSG_ID_PARA_RESPONDER",
  "mentions": "5511999999999,5511888888888",
  "forward": false,
  "linkPreview": true,
  "linkPreviewTitle": "Título customizado",
  "linkPreviewDescription": "Descrição customizada",
  "linkPreviewImage": "https://exemplo.com/img.jpg",
  "linkPreviewLarge": true,
  "track_source": "minha_app",
  "track_id": "msg_123",
  "async": false
}
```
Campos obrigatórios: `number`, `text`
Placeholders suportados: `{{name}}`, `{{company}}`

### POST /send/media
Envia mídia (imagem, vídeo, áudio, documento).
```json
{
  "number": "5511999999999",
  "media": "https://exemplo.com/foto.jpg",
  "type": "image",
  "caption": "Legenda aqui",
  "filename": "arquivo.pdf",
  "delay": 1500
}
```
Tipos: `image`, `video`, `audio`, `document`
Media: URL ou Base64

### POST /send/contact
Envia cartão de contato.
```json
{
  "number": "5511999999999",
  "contact_name": "João Silva",
  "contact_number": "5511888888888"
}
```

### POST /send/location
Envia localização.
```json
{
  "number": "5511999999999",
  "latitude": "-23.5505",
  "longitude": "-46.6333",
  "name": "São Paulo",
  "address": "Av Paulista, 1000"
}
```

### POST /send/status
Publica status/stories.
```json
{
  "type": "text",
  "text": "Texto do status",
  "backgroundColor": "#FF0000",
  "font": 1
}
```

### POST /send/menu
Envia menu de botões/lista.
```json
{
  "number": "5511999999999",
  "title": "Escolha uma opção",
  "description": "Menu de atendimento",
  "footer": "Bravy",
  "sections": [
    {
      "title": "Serviços",
      "rows": [
        { "title": "Suporte", "description": "Falar com suporte", "rowId": "suporte" },
        { "title": "Vendas", "description": "Conhecer produtos", "rowId": "vendas" }
      ]
    }
  ]
}
```

### POST /send/carousel
Envia carrossel de cards.

### POST /send/pix-button
Envia botão de pagamento Pix.

### POST /send/request-payment
Envia solicitação de pagamento.

---

## 3. Ações em Mensagens

### POST /message/find
Busca mensagens com filtros.
```json
{
  "chatid": "5511999999999@s.whatsapp.net",
  "limit": 20,
  "offset": 0,
  "id": "MSG_ID_ESPECIFICO",
  "track_source": "minha_app",
  "track_id": "msg_123"
}
```
Resposta: `{ "returnedMessages": N, "messages": [...], "hasMore": bool, "nextOffset": N }`

### POST /message/markread
Marca mensagens como lidas.
```json
{
  "id": ["MSG_ID_1", "MSG_ID_2"]
}
```

### POST /message/react
Reage a uma mensagem com emoji.
```json
{
  "chatid": "5511999999999@s.whatsapp.net",
  "messageid": "MSG_ID",
  "reaction": "👍"
}
```

### POST /message/delete
Deleta mensagem.
```json
{
  "chatid": "5511999999999@s.whatsapp.net",
  "messageid": "MSG_ID",
  "everyone": true
}
```

### POST /message/edit
Edita mensagem enviada.
```json
{
  "chatid": "5511999999999@s.whatsapp.net",
  "messageid": "MSG_ID",
  "text": "Texto editado"
}
```

### POST /message/download
Baixa mídia de uma mensagem.

### POST /message/presence
Envia indicador de presença (digitando/gravando).
```json
{
  "number": "5511999999999",
  "presence": "composing" | "recording"
}
```

---

## 4. Chats

### POST /chat/find
Busca conversas com filtros avançados.
```json
{
  "operator": "AND",
  "sort": "-wa_lastMsgTimestamp",
  "limit": 20,
  "offset": 0,
  "wa_isGroup": false,
  "wa_unreadCount": ">0",
  "wa_contactName": "~João",
  "wa_isPinned": true,
  "wa_label": "~importante",
  "lead_status": "~novo",
  "lead_isTicketOpen": true,
  "lead_assignedAttendant_id": "ATTENDANT_ID"
}
```

**Operadores de filtro (no valor):**
- `~valor` — LIKE (contém)
- `!~valor` — NOT LIKE (não contém)
- `!=valor` — diferente
- `>=valor` — maior ou igual
- `>valor` — maior que
- `<=valor` — menor ou igual
- `<valor` — menor que
- Sem operador — LIKE (contém)

**Campos filtráveis:** wa_fastid, wa_chatid, wa_archived, wa_contactName, wa_name, name, wa_isBlocked, wa_isGroup, wa_isGroup_admin, wa_isGroup_announce, wa_isGroup_member, wa_isPinned, wa_label, lead_tags, lead_isTicketOpen, lead_assignedAttendant_id, lead_status

**Resposta inclui:** chats[], totalChatsStats, pagination (totalRecords, currentPage, totalPages, hasNextPage)

### POST /chat/block / /chat/blocklist
Bloquear/listar bloqueados.

### POST /chat/labels
Gerenciar labels de um chat.

### POST /chat/delete
Deletar conversa.

### POST /chat/archive
Arquivar/desarquivar conversa.

### POST /chat/read
Marcar conversa como lida.

### POST /chat/mute
Silenciar conversa.

### POST /chat/pin
Fixar conversa.

---

## 5. Contatos

### GET /contacts
Lista todos os contatos (sem paginação).
Resposta: `[{ "jid": "55...@s.whatsapp.net", "contactName": "Nome", "contact_FirstName": "Nome" }]`

### POST /contacts/list
Lista contatos com paginação.
```json
{ "page": 1, "pageSize": 50 }
```

### POST /contact/add
Adiciona contato à agenda.

### POST /contact/remove
Remove contato da agenda.

---

## 6. Grupos

### POST /group/list
Lista grupos. Resposta: array de grupos com metadados.

### POST /group/info
Info detalhada de um grupo.
```json
{ "groupid": "GROUP_ID@g.us" }
```

### POST /group/create
Cria novo grupo.
```json
{
  "name": "Nome do Grupo",
  "participants": ["5511999999999", "5511888888888"]
}
```

### POST /group/updateName
Atualiza nome do grupo.

### POST /group/updateDescription
Atualiza descrição.

### POST /group/updateImage
Atualiza imagem do grupo.

### POST /group/updateParticipants
Adiciona/remove participantes.
```json
{
  "groupid": "GROUP_ID@g.us",
  "participants": ["5511999999999"],
  "action": "add" | "remove" | "promote" | "demote"
}
```

### POST /group/inviteInfo
Obtém info de convite.

### POST /group/join
Entra em grupo via código de convite.

### POST /group/leave
Sai do grupo.

### POST /group/resetInviteCode
Reseta link de convite.

### POST /group/updateAnnounce
Ativa/desativa modo somente admins.

### POST /group/updateLocked
Bloqueia/desbloqueia edição do grupo.

---

## 7. CRM / Leads

### POST /chat/editLead
Atualiza informações de lead de um chat.
```json
{
  "id": "5511999999999@s.whatsapp.net",
  "lead_name": "João Silva",
  "lead_fullName": "João Carlos Silva",
  "lead_email": "joao@email.com",
  "lead_personalid": "123.456.789-00",
  "lead_status": "qualificado",
  "lead_tags": ["cliente", "vip"],
  "lead_notes": "Interessado no plano anual",
  "lead_isTicketOpen": true,
  "lead_assignedAttendant_id": "ATTENDANT_ID",
  "lead_kanbanOrder": 1,
  "lead_field01": "campo customizado",
  "chatbot_disableUntil": 1735686000
}
```

---

## 8. Business / Catálogo

### POST /business/catalog/list
Lista produtos do catálogo.

### POST /business/catalog/create
Cria produto no catálogo.

### POST /business/catalog/edit
Edita produto.

### POST /business/catalog/delete
Deleta produto.

### POST /business/catalog/show / /business/catalog/hide
Mostra/oculta produto.

---

## 9. Webhooks

### POST /webhook
Gerencia webhooks da instância (CRUD).
```json
{
  "enabled": true,
  "url": "https://meu-server.com/webhook",
  "events": ["messages", "connection", "messages_update", "leads"],
  "excludeMessages": ["isGroupYes"]
}
```

Eventos disponíveis: connection, history, messages, messages_update, call, contacts, presence, groups, labels, chats, chat_labels, blocks, leads

### GET /sse
Server-Sent Events para receber eventos em tempo real.

---

## 10. Agentes e Chatbot

### POST /agent/edit
Cria/edita agente de IA (chatbot).

### POST /agent/list
Lista agentes configurados.

---

## 11. Sender (Disparos em Massa)

### POST /sender/simple
Disparo simples para lista de números.

### POST /sender/advanced
Disparo avançado com variáveis e condições.

### POST /sender/edit
Edita campanha de disparo.

### POST /sender/cleardone
Limpa mensagens enviadas.

### POST /sender/clearall
Limpa todas as mensagens.

### POST /sender/listfolders
Lista pastas de disparo.

### POST /sender/listmessages
Lista mensagens de uma campanha.

---

## 12. Triggers e Knowledge

### POST /trigger/edit
Cria/edita trigger automático.

### POST /trigger/list
Lista triggers.

### POST /knowledge/edit
Cria/edita base de conhecimento.

### POST /knowledge/list
Lista bases de conhecimento.

### POST /function/edit
Cria/edita function calling.

### POST /function/list
Lista functions.

---

## Códigos de Resposta Comuns

| Código | Significado |
|---|---|
| 200 | Sucesso |
| 400 | Requisição inválida (payload mal formado) |
| 401 | Token inválido ou expirado |
| 404 | Recurso não encontrado |
| 429 | Limite de requisições excedido |
| 500 | Erro interno do servidor |

