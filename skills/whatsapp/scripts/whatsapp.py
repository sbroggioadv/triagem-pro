#!/usr/bin/env python3
"""
whatsapp.py — CLI completo para WhatsApp via API Zappfy
Uso: python3 ~/.claude/skills/whatsapp/scripts/whatsapp.py [--json] <comando> [args...]

Flag --json: output estruturado para consumo por agentes AI
Sem flag: output formatado para humanos
"""

import sys
import os
import json
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# Windows UTF-8 fix: Python 3.13 no Windows usa cp1252 por default, que nao
# suporta emojis e varios caracteres acentuados das mensagens WhatsApp.
# Forcar UTF-8 no stdout/stderr resolve o UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ============================================================
# CONFIGURACAO — MULTI-PATH DISCOVERY (v0.2.3)
# ============================================================
#
# A v0.2.3 introduziu descoberta automatica de CONFIG_DIR pra resolver
# o problema do plugin ser read-only no Cowork. A compradora escolhe
# onde gravar seus arquivos (config.env, config.json, voz.md) via wizard,
# e este script localiza esse path automaticamente em runtime.
#
# Ordem de prioridade (primeiro que tem config.env vence):
#   1. $TRIAGEM_CONFIG_DIR (env var — override avancado/dev)
#   2. ~/Library/Mobile Documents/com~apple~CloudDocs/Cowork OS/Triagem Pro/  (Mac iCloud — default v0.2.3)
#   3. ~/OneDrive/Cowork OS/Triagem Pro/  (Windows OneDrive — default v0.2.3)
#   4. ~/Documents/triagem-pro/  (path da v0.2.x — retrocompat)
#   5. ~/Library/Mobile Documents/com~apple~CloudDocs/Cowork OS/skills/whatsapp/  (path da v0.1.0 — retrocompat)
#   6. SKILL_DIR  (fallback dev — plugin instalado direto, modo working tree)
#
# Se NENHUM path tem config.env, retorna o default v0.2.3 (item 2 ou 3 conforme SO).
# load_config() vai falhar com mensagem clara orientando rodar /configurar.

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
HOME = Path.home()


def _candidate_config_dirs():
    """Retorna lista ordenada de paths candidatos pro CONFIG_DIR."""
    candidates = []
    env_override = os.environ.get("TRIAGEM_CONFIG_DIR", "").strip()
    if env_override:
        candidates.append(Path(env_override).expanduser())
    icloud_root = HOME / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
    candidates.extend([
        icloud_root / "Cowork OS" / "Triagem Pro",
        HOME / "OneDrive" / "Cowork OS" / "Triagem Pro",
        HOME / "Documents" / "triagem-pro",
        icloud_root / "Cowork OS" / "skills" / "whatsapp",
        SKILL_DIR,
    ])
    return candidates


def discover_config_dir():
    """Retorna o CONFIG_DIR ativo:
    1. Se TRIAGEM_CONFIG_DIR env var setada, SEMPRE prevalece (mesmo sem config.env ainda — pra wizard gravar la).
    2. Senao, retorna primeiro candidato com config.env existente.
    3. Senao, retorna default v0.2.3 conforme SO (pra wizard gravar la na primeira instalacao).
    """
    env_override = os.environ.get("TRIAGEM_CONFIG_DIR", "").strip()
    if env_override:
        return Path(env_override).expanduser()
    for c in _candidate_config_dirs():
        if (c / "config.env").exists():
            return c
    # Nenhum tem config.env — retorna default v0.2.3 conforme SO
    if sys.platform == "win32":
        return HOME / "OneDrive" / "Cowork OS" / "Triagem Pro"
    if sys.platform.startswith("linux"):
        # Em Linux (raro mas possivel — Cowork sandbox server-side),
        # iCloud nao existe. Retorna ~/Documents/ que tem maior chance.
        return HOME / "Documents" / "triagem-pro"
    return HOME / "Library" / "Mobile Documents" / "com~apple~CloudDocs" / "Cowork OS" / "Triagem Pro"


def cmd_config_dir():
    """Subcomando: imprime CONFIG_DIR ativo. Util pra agents e bash:
        export CONFIG_DIR=$(python3 .../whatsapp.py config-dir)
    """
    print(str(CONFIG_DIR))


CONFIG_DIR = discover_config_dir()
CONFIG_FILE = CONFIG_DIR / "config.env"
CONFIG_JSON_PATH = CONFIG_DIR / "config.json"
VOZ_PATH = CONFIG_DIR / "voz.md"

JSON_MODE = False


def load_config():
    if not CONFIG_FILE.exists():
        print(f"Arquivo de credenciais nao encontrado: {CONFIG_FILE}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Triagem Pro nao esta configurado neste ambiente.", file=sys.stderr)
        print("Rode /configurar no chat do Claude para configurar.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Paths verificados (em ordem):", file=sys.stderr)
        for c in _candidate_config_dirs():
            mark = "OK" if (c / "config.env").exists() else "  "
            print(f"  [{mark}] {c}", file=sys.stderr)
        sys.exit(1)
    config = {}
    with open(CONFIG_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                config[key.strip()] = value.strip()
    token = config.get("ZAPPFY_TOKEN", "")
    if not token:
        print("ZAPPFY_TOKEN nao configurado em config.env", file=sys.stderr)
        sys.exit(1)
    base_url = config.get("ZAPPFY_BASE_URL", "https://zappfy-v2.uazapi.com").rstrip("/")
    # Exporta configuracoes do whisper (se presentes) pra os.environ,
    # pra que _load_whisper_model() consiga le-las sem depender de shell export.
    for key, value in config.items():
        if key.startswith("WHISPER_") and value:
            os.environ.setdefault(key, value)
    return token, base_url


# Subcomando especial "config-dir" não precisa de credenciais — retorna sem load_config()
# para nao falhar quando agente roda no inicio de sessao pra descobrir CONFIG_DIR.
if len(sys.argv) >= 2 and sys.argv[1] in ("config-dir", "--config-dir"):
    print(str(CONFIG_DIR))
    sys.exit(0)

TOKEN, ZAPPFY_BASE_URL = load_config()


# ============================================================
# FIRM CONFIG — carregador de config.json do escritorio
# ============================================================

URGENT_KEYWORDS_DEFAULT = [
    "urgente", "problema", "cancelar", "rescisao", "rescisão",
    "audiencia", "audiência", "intimacao", "intimação",
    "sentenca", "sentença", "liminar", "penhora",
    "bloqueio", "pericia", "perícia", "prazo",
]
SILENCE_KEYWORDS_DEFAULT = [
    "jusbrasil", "asaas", "fireflies", "pagbank",
    "nomad", "porto seguro", "sem parar", "escavador",
]

def load_firm_config(path=None):
    """Carrega config.json do escritorio aplicando defaults. Nunca lanca excecao:
    arquivo ausente ou JSON invalido -> defaults completos.

    Campos retornados para consumo pelo CLI: team_names, urgent_keywords,
    silence_keywords, thresholds, max_chats, max_process.
    Campos owner_contact_names, internal_groups e client_group_prefixes sao
    expostos para consumo direto pelo agente (que le config.json diretamente)
    — nao sao usados pelo CLI, mas nao sao dead code."""
    if path is None:
        # v0.2.3: usa CONFIG_DIR descoberto, nao SKILL_DIR hardcoded
        path = str(CONFIG_JSON_PATH)
    raw = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (FileNotFoundError, ValueError, OSError):
        raw = {}

    team_names = []
    for member in raw.get("team", []):
        for name in member.get("names", []):
            norm = name.strip().lower()
            if norm and norm not in team_names:
                team_names.append(norm)

    triagem = raw.get("triagem", {})
    thr = triagem.get("thresholds", {})

    return {
        "firm_name": raw.get("firm", {}).get("name", ""),
        "owner_contact_names": [n.strip().lower() for n in raw.get("firm", {}).get("owner_contact_names", [])],
        "team_names": team_names,
        "internal_groups": raw.get("internal_groups", []),
        "client_group_prefixes": raw.get("client_group_prefixes", []),
        "urgent_keywords": raw.get("urgent_keywords", list(URGENT_KEYWORDS_DEFAULT)),
        "silence_keywords": raw.get("silence_keywords", list(SILENCE_KEYWORDS_DEFAULT)),
        "thresholds": {
            "atrasada_hours": thr.get("atrasada_hours", 24),
            "importante_hours": thr.get("importante_hours", 4),
            "normal_hours": thr.get("normal_hours", 1),
        },
        "max_chats": triagem.get("max_chats", 100),
        "max_process": triagem.get("max_process", 30),
    }


# ============================================================
# LID CACHE — resolve sender names from cached LID -> name mapping
# ============================================================
#
# WhatsApp Business retorna `sender` como LID (Linked Identifier — ex:
# "192827019538614@lid") em vez de numero. Quando senderName/pushName vem
# vazio, perdemos a info de quem mandou.
#
# Solucao: cache persistente em memory/lid_cache.json que aprende LID -> nome
# a partir de qualquer mensagem onde senderName veio populado. Funciona
# cross-chat e cross-sessao.

LID_CACHE_PATH = CONFIG_DIR / "memory" / "lid_cache.json"
_LID_CACHE = None


def _load_lid_cache():
    global _LID_CACHE
    if _LID_CACHE is None:
        if LID_CACHE_PATH.exists():
            try:
                _LID_CACHE = json.loads(LID_CACHE_PATH.read_text(encoding="utf-8"))
            except Exception:
                _LID_CACHE = {}
        else:
            _LID_CACHE = {}
    return _LID_CACHE


def _save_lid_cache():
    if _LID_CACHE is None:
        return
    try:
        LID_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        LID_CACHE_PATH.write_text(
            json.dumps(_LID_CACHE, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass


def _update_lid_cache_from_messages(messages):
    """Atualiza cache com pares LID -> nome encontrados nas mensagens.
    Retorna numero de novos LIDs cacheados."""
    if not messages:
        return 0
    cache = _load_lid_cache()
    new_count = 0
    for m in messages:
        if not isinstance(m, dict):
            continue
        sid = m.get("sender") or ""
        sname = m.get("senderName") or m.get("pushName") or ""
        if sid and sname and sid not in cache:
            cache[sid] = sname
            new_count += 1
    if new_count > 0:
        _save_lid_cache()
    return new_count


def resolve_sender(msg):
    """Resolve nome do sender usando senderName/pushName + cache LID como fallback.

    Retorna string vazia se nao conseguir resolver.
    Funciona como drop-in replacement de `msg.get("senderName") or msg.get("pushName") or ""`."""
    if not isinstance(msg, dict):
        return ""
    name = msg.get("senderName") or msg.get("pushName") or ""
    if name:
        return name
    sid = msg.get("sender") or ""
    if not sid:
        return ""
    cache = _load_lid_cache()
    return cache.get(sid, "")


# ============================================================
# API CLIENT
# ============================================================


def api_request(method, endpoint, body=None):
    url = f"{ZAPPFY_BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json", "token": TOKEN}
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        if JSON_MODE:
            output({"error": True, "code": e.code, "message": error_body})
        else:
            print(f"Erro {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        if JSON_MODE:
            output({"error": True, "message": str(e.reason)})
        else:
            print(f"Erro de conexao: {e.reason}", file=sys.stderr)
        sys.exit(1)


def api_get(endpoint):
    return api_request("GET", endpoint)


def api_post(endpoint, body=None):
    return api_request("POST", endpoint, body or {})


# ============================================================
# OUTPUT HELPERS
# ============================================================


def output(data):
    """Output JSON ou human-readable"""
    if JSON_MODE:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        if isinstance(data, dict):
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(data)


def human(text):
    """Print somente em modo human"""
    if not JSON_MODE:
        print(text)


def format_ts(ts):
    try:
        ts = int(ts)
        if ts > 9999999999:
            ts = ts // 1000
        if ts > 0:
            return datetime.fromtimestamp(ts).strftime("%d/%m %H:%M")
    except (ValueError, TypeError, OSError):
        pass
    return "-"


def truncate(text, max_len=80):
    text = str(text or "")
    return text[:max_len] + "..." if len(text) > max_len else text


def resolve_chatid(identifier):
    """Resolve identificador para chatid. Aceita numero, chatid, ou nome."""
    if "@" in identifier:
        return identifier
    if identifier.replace("+", "").isdigit():
        num = identifier.replace("+", "")
        return f"{num}@s.whatsapp.net"
    # Busca por nome
    result = api_post("/chat/find", {
        "wa_contactName": f"~{identifier}",
        "sort": "-wa_lastMsgTimestamp",
        "limit": 5,
    })
    chats = result.get("chats", [])
    if not chats:
        # Tenta por wa_name (grupos)
        result = api_post("/chat/find", {
            "wa_name": f"~{identifier}",
            "sort": "-wa_lastMsgTimestamp",
            "limit": 5,
        })
        chats = result.get("chats", [])
    if not chats:
        human(f"Nenhum contato encontrado para '{identifier}'")
        if JSON_MODE:
            output({"error": True, "message": f"Contato nao encontrado: {identifier}"})
        sys.exit(1)
    if len(chats) > 1 and JSON_MODE:
        matches = []
        for c in chats:
            matches.append({
                "name": c.get("wa_contactName") or c.get("wa_name") or c.get("name", "?"),
                "chatid": c.get("wa_chatid", ""),
                "phone": c.get("phone", ""),
                "is_group": c.get("wa_isGroup", False),
            })
        output({"error": True, "message": "Multiplos contatos encontrados", "matches": matches})
        sys.exit(1)
    if len(chats) > 1 and not JSON_MODE:
        print(f"Multiplos resultados para '{identifier}':")
        for i, c in enumerate(chats, 1):
            name = c.get("wa_contactName") or c.get("wa_name") or c.get("name", "?")
            chatid = c.get("wa_chatid", "")
            print(f"  {i}. {name} | {chatid}")
        print(f"\nUsando o primeiro: {chats[0].get('wa_chatid', '')}")
    return chats[0].get("wa_chatid", "")


def resolve_number(identifier):
    """Resolve para numero (sem @suffix). Para envio de mensagens."""
    if "@" in identifier:
        return identifier.split("@")[0]
    if identifier.replace("+", "").isdigit():
        return identifier.replace("+", "")
    chatid = resolve_chatid(identifier)
    return chatid.split("@")[0]


def chat_name(chat):
    return (
        chat.get("wa_contactName")
        or chat.get("wa_name")
        or chat.get("name")
        or chat.get("phone")
        or chat.get("wa_chatid", "?")
    )


def parse_msg_ts(msg):
    ts = msg.get("messageTimestamp") or msg.get("timestamp") or msg.get("created") or 0
    if isinstance(ts, str):
        try:
            ts = int(ts)
        except ValueError:
            return 0
    ts = int(ts) if ts else 0
    if ts > 9999999999:
        ts = ts // 1000
    return ts


# ============================================================
# COMANDOS: STATUS
# ============================================================


def cmd_status():
    """Verifica status da conexao"""
    result = api_get("/instance/status")
    if JSON_MODE:
        output(result)
    else:
        status = result.get("status", "desconhecido")
        print(f"Status: {status}")


def cmd_presence(state):
    """Define presenca: available | unavailable"""
    result = api_post("/instance/presence", {"presence": state})
    if JSON_MODE:
        output(result)
    else:
        print(f"Presenca alterada para: {state}")


# ============================================================
# COMANDOS: LEITURA
# ============================================================


def cmd_unread(limit="50"):
    """Lista conversas com mensagens nao lidas"""
    limit = int(limit)
    result = api_post("/chat/find", {
        "sort": "-wa_lastMsgTimestamp",
        "limit": limit,
        "wa_unreadCount": ">0",
    })
    chats = result.get("chats", [])
    if JSON_MODE:
        items = []
        for c in chats:
            items.append({
                "name": chat_name(c),
                "chatid": c.get("wa_chatid", ""),
                "phone": c.get("phone", ""),
                "unread_count": c.get("wa_unreadCount", 0),
                "last_message": c.get("wa_lastMessageTextVote", ""),
                "is_group": c.get("wa_isGroup", False),
                "last_timestamp": c.get("wa_lastMsgTimestamp", 0),
            })
        output({"total": len(items), "chats": items})
    else:
        if not chats:
            print("Nenhuma mensagem nao lida.")
            return
        print(f"Conversas com mensagens nao lidas ({len(chats)}):\n")
        for c in chats:
            icon = "G" if c.get("wa_isGroup") else " "
            name = chat_name(c)
            unread = c.get("wa_unreadCount", 0)
            last = truncate(c.get("wa_lastMessageTextVote", "-"), 60)
            ts = format_ts(c.get("wa_lastMsgTimestamp", 0))
            print(f"  [{icon}] {name} | {unread} nao lida(s) | {ts} | {last}")


def cmd_chats(limit="20"):
    """Lista ultimas conversas"""
    limit = int(limit)
    result = api_post("/chat/find", {
        "sort": "-wa_lastMsgTimestamp",
        "limit": limit,
    })
    chats = result.get("chats", [])
    if JSON_MODE:
        items = []
        for c in chats:
            items.append({
                "name": chat_name(c),
                "chatid": c.get("wa_chatid", ""),
                "phone": c.get("phone", ""),
                "unread_count": c.get("wa_unreadCount", 0),
                "last_message": c.get("wa_lastMessageTextVote", ""),
                "is_group": c.get("wa_isGroup", False),
                "last_timestamp": c.get("wa_lastMsgTimestamp", 0),
            })
        output({"total": len(items), "chats": items})
    else:
        print(f"Ultimas {limit} conversas:\n")
        for c in chats:
            icon = "G" if c.get("wa_isGroup") else " "
            name = chat_name(c)
            unread = c.get("wa_unreadCount", 0)
            last = truncate(c.get("wa_lastMessageTextVote", "-"), 50)
            print(f"  [{icon}] {name} | Nao lidas: {unread} | {last}")


def cmd_messages(identifier, limit="20"):
    """Busca mensagens de um contato ou grupo"""
    limit = int(limit)
    chatid = resolve_chatid(identifier)
    result = api_post("/message/find", {"chatid": chatid, "limit": limit})
    messages = result.get("messages", [])
    _update_lid_cache_from_messages(messages)
    if JSON_MODE:
        items = []
        for msg in messages:
            items.append({
                "id": msg.get("id", ""),
                "from_me": msg.get("fromMe", False),
                "sender": resolve_sender(msg),
                "text": msg.get("text") or "",
                "type": msg.get("messageType", ""),
                "timestamp": parse_msg_ts(msg),
                "quoted_text": msg.get("quotedText", ""),
            })
        output({"chatid": chatid, "total": len(items), "messages": items})
    else:
        if not messages:
            print("Nenhuma mensagem encontrada.")
            return
        print(f"Ultimas {limit} mensagens de {chatid}:\n")
        for msg in messages:
            direction = "EU" if msg.get("fromMe") else (resolve_sender(msg) or "?")
            text = truncate(msg.get("text") or msg.get("messageType", "-"), 100)
            ts = format_ts(parse_msg_ts(msg))
            print(f"  [{ts}] {direction}: {text}")


def cmd_search_chat(term):
    """Busca conversas por nome"""
    result = api_post("/chat/find", {
        "wa_contactName": f"~{term}",
        "sort": "-wa_lastMsgTimestamp",
        "limit": 20,
    })
    chats = result.get("chats", [])
    # Tambem busca por nome de grupo
    result2 = api_post("/chat/find", {
        "wa_name": f"~{term}",
        "wa_isGroup": True,
        "sort": "-wa_lastMsgTimestamp",
        "limit": 10,
    })
    group_chats = result2.get("chats", [])
    # Merge sem duplicatas
    seen = set()
    all_chats = []
    for c in chats + group_chats:
        cid = c.get("wa_chatid", "")
        if cid not in seen:
            seen.add(cid)
            all_chats.append(c)

    if JSON_MODE:
        items = []
        for c in all_chats:
            items.append({
                "name": chat_name(c),
                "chatid": c.get("wa_chatid", ""),
                "phone": c.get("phone", ""),
                "is_group": c.get("wa_isGroup", False),
                "unread_count": c.get("wa_unreadCount", 0),
            })
        output({"query": term, "total": len(items), "results": items})
    else:
        if not all_chats:
            print(f"Nenhuma conversa encontrada para '{term}'.")
            return
        print(f"Resultados para '{term}' ({len(all_chats)}):\n")
        for c in all_chats:
            icon = "G" if c.get("wa_isGroup") else " "
            name = chat_name(c)
            chatid = c.get("wa_chatid", "")
            print(f"  [{icon}] {name} | {chatid}")


def cmd_search_msg(term, identifier=None):
    """Busca mensagens por conteudo (em um chat especifico ou global)"""
    # A API nao suporta busca full-text diretamente
    # Workaround: buscar mensagens recentes e filtrar local
    if identifier:
        chatid = resolve_chatid(identifier)
        result = api_post("/message/find", {"chatid": chatid, "limit": 200})
    else:
        # Sem chat especifico, buscamos nos chats recentes
        chats_result = api_post("/chat/find", {"sort": "-wa_lastMsgTimestamp", "limit": 10})
        all_msgs = []
        for c in chats_result.get("chats", []):
            cid = c.get("wa_chatid", "")
            r = api_post("/message/find", {"chatid": cid, "limit": 50})
            for msg in r.get("messages", []):
                msg["_chat_name"] = chat_name(c)
                all_msgs.append(msg)
        result = {"messages": all_msgs}

    _update_lid_cache_from_messages(result.get("messages", []))
    term_lower = term.lower()
    matches = [m for m in result.get("messages", []) if term_lower in (m.get("text") or "").lower()]

    if JSON_MODE:
        items = []
        for msg in matches[:50]:
            items.append({
                "chat": msg.get("_chat_name", ""),
                "chatid": msg.get("chatid", ""),
                "id": msg.get("id", ""),
                "from_me": msg.get("fromMe", False),
                "sender": resolve_sender(msg),
                "text": msg.get("text", ""),
                "timestamp": parse_msg_ts(msg),
            })
        output({"query": term, "total": len(items), "results": items})
    else:
        if not matches:
            print(f"Nenhuma mensagem encontrada com '{term}'.")
            return
        print(f"Mensagens com '{term}' ({len(matches)}):\n")
        for msg in matches[:30]:
            sender = "EU" if msg.get("fromMe") else (resolve_sender(msg) or "?")
            text = truncate(msg.get("text", ""), 100)
            ts = format_ts(parse_msg_ts(msg))
            chat = msg.get("_chat_name", "")
            prefix = f"[{chat}] " if chat else ""
            print(f"  {prefix}[{ts}] {sender}: {text}")


def cmd_contact_info(identifier):
    """Info detalhada de um contato/lead"""
    chatid = resolve_chatid(identifier)
    # Buscar dados do chat
    result = api_post("/chat/find", {"wa_chatid": chatid, "limit": 1})
    chats = result.get("chats", [])
    if not chats:
        human(f"Chat nao encontrado: {chatid}")
        if JSON_MODE:
            output({"error": True, "message": "Chat nao encontrado"})
        sys.exit(1)
    chat = chats[0]
    if JSON_MODE:
        output({
            "name": chat_name(chat),
            "chatid": chat.get("wa_chatid", ""),
            "phone": chat.get("phone", ""),
            "is_group": chat.get("wa_isGroup", False),
            "unread_count": chat.get("wa_unreadCount", 0),
            "is_pinned": chat.get("wa_isPinned", False),
            "is_archived": chat.get("wa_archived", False),
            "is_blocked": chat.get("wa_isBlocked", False),
            "labels": chat.get("wa_label", ""),
            "lead_name": chat.get("lead_name", ""),
            "lead_fullName": chat.get("lead_fullName", ""),
            "lead_email": chat.get("lead_email", ""),
            "lead_status": chat.get("lead_status", ""),
            "lead_tags": chat.get("lead_tags", []),
            "lead_notes": chat.get("lead_notes", ""),
            "lead_isTicketOpen": chat.get("lead_isTicketOpen", False),
            "lead_assignedAttendant_id": chat.get("lead_assignedAttendant_id", ""),
        })
    else:
        name = chat_name(chat)
        print(f"Contato: {name}")
        print(f"  ChatID: {chat.get('wa_chatid', '')}")
        print(f"  Telefone: {chat.get('phone', '-')}")
        print(f"  Grupo: {'Sim' if chat.get('wa_isGroup') else 'Nao'}")
        print(f"  Nao lidas: {chat.get('wa_unreadCount', 0)}")
        print(f"  Fixado: {'Sim' if chat.get('wa_isPinned') else 'Nao'}")
        print(f"  Arquivado: {'Sim' if chat.get('wa_archived') else 'Nao'}")
        print(f"  Bloqueado: {'Sim' if chat.get('wa_isBlocked') else 'Nao'}")
        print(f"  Labels: {chat.get('wa_label', '-')}")
        lead_name = chat.get("lead_name") or chat.get("lead_fullName")
        if lead_name:
            print(f"\n  Lead:")
            print(f"    Nome: {chat.get('lead_fullName', '-')}")
            print(f"    Email: {chat.get('lead_email', '-')}")
            print(f"    Status: {chat.get('lead_status', '-')}")
            print(f"    Tags: {chat.get('lead_tags', [])}")
            print(f"    Notas: {chat.get('lead_notes', '-')}")
            print(f"    Ticket aberto: {'Sim' if chat.get('lead_isTicketOpen') else 'Nao'}")


# ============================================================
# COMANDOS: ENVIO
# ============================================================


def cmd_send(identifier, *text_parts):
    """Envia mensagem de texto"""
    text = " ".join(text_parts)
    if not text:
        print("Uso: send <numero|nome> <texto>", file=sys.stderr)
        sys.exit(1)
    number = resolve_number(identifier)
    result = api_post("/send/text", {
        "number": number,
        "text": text,
        "delay": 1500,
        "readchat": True,
    })
    if JSON_MODE:
        output({"sent": True, "to": number, "text": text, "result": result})
    else:
        print(f"Enviado para {number}: \"{truncate(text, 60)}\"")


def cmd_reply(identifier, msgid, *text_parts):
    """Responde a uma mensagem especifica"""
    text = " ".join(text_parts)
    if not text:
        print("Uso: reply <numero|nome> <msgid> <texto>", file=sys.stderr)
        sys.exit(1)
    number = resolve_number(identifier)
    result = api_post("/send/text", {
        "number": number,
        "text": text,
        "delay": 1500,
        "readchat": True,
        "replyid": msgid,
    })
    if JSON_MODE:
        output({"sent": True, "to": number, "reply_to": msgid, "text": text, "result": result})
    else:
        print(f"Respondido para {number} (ref: {msgid[:20]}...)")


def cmd_send_media(identifier, media_url, media_type="image", caption=""):
    """Envia midia"""
    number = resolve_number(identifier)
    body = {
        "number": number,
        "media": media_url,
        "type": media_type,
        "delay": 1500,
    }
    if caption:
        body["caption"] = caption
    result = api_post("/send/media", body)
    if JSON_MODE:
        output({"sent": True, "to": number, "type": media_type, "result": result})
    else:
        print(f"Midia ({media_type}) enviada para {number}")


# ============================================================
# COMANDOS: DOWNLOAD / READ MEDIA
# ============================================================

MEDIA_CACHE_DIR = CONFIG_DIR / "cache" / "media"


def _ensure_cache_dir():
    MEDIA_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _mimetype_to_kind(mimetype):
    if not mimetype:
        return "unknown"
    if mimetype.startswith("image/"):
        return "image"
    if mimetype.startswith("audio/"):
        return "audio"
    if mimetype.startswith("video/"):
        return "video"
    if mimetype.startswith("application/"):
        return "document"
    return "other"


def download_media_by_msgid(msgid):
    """Baixa midia de uma mensagem via /message/download.

    Retorna dict: {msgid, kind, mimetype, file_url, local_path, cached: bool}
    Usa filename do fileURL (hash SHA256 do Zappfy) como chave de cache —
    content-addressable, dedupe automatico.
    """
    _ensure_cache_dir()
    meta = api_post("/message/download", {"id": msgid})
    file_url = meta.get("fileURL", "")
    mimetype = meta.get("mimetype", "")
    if not file_url:
        raise RuntimeError(f"API nao retornou fileURL: {meta}")
    filename = file_url.rsplit("/", 1)[-1]
    local_path = MEDIA_CACHE_DIR / filename
    cached = local_path.exists() and local_path.stat().st_size > 0
    if not cached:
        req = urllib.request.Request(file_url, headers={"User-Agent": "whatsapp-cli/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(local_path, "wb") as f:
                f.write(resp.read())
    return {
        "msgid": msgid,
        "kind": _mimetype_to_kind(mimetype),
        "mimetype": mimetype,
        "file_url": file_url,
        "local_path": str(local_path),
        "cached": cached,
    }


def cmd_download_media(identifier_or_msgid, msgid=None):
    """Baixa midia de uma mensagem e salva em cache.

    Uso: download-media <msgid>
         download-media <numero|nome> <msgid>  (identifier e ignorado, so pra symmetry)
    """
    real_msgid = msgid if msgid else identifier_or_msgid
    info = download_media_by_msgid(real_msgid)
    if JSON_MODE:
        output(info)
    else:
        status = "cache hit" if info["cached"] else "baixado"
        print(f"[{status}] {info['kind']} ({info['mimetype']})")
        print(f"  Path: {info['local_path']}")
        print(f"  URL:  {info['file_url']}")


TRANSCRIPT_CACHE_DIR = CONFIG_DIR / "cache" / "transcripts"
_WHISPER_MODEL = None


def _load_whisper_model(model_size="large-v3"):
    """Lazy-load faster-whisper model. Singleton por processo.

    Retorna None (sem excecao) se faster-whisper nao estiver instalado —
    o chamador deve checar e tratar o fallback.

    Device/compute auto-detect (override com env WHISPER_DEVICE, WHISPER_COMPUTE_TYPE,
    WHISPER_MODEL_SIZE). CUDA usa float16 + large-v3.
    Fallback CPU cai pra int8 — use WHISPER_MODEL_SIZE=medium ou small
    pra latencia aceitavel.
    """
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            return None
        model_size = os.environ.get("WHISPER_MODEL_SIZE", model_size)
        device = os.environ.get("WHISPER_DEVICE", "auto")
        compute_type = os.environ.get("WHISPER_COMPUTE_TYPE")

        if device == "auto":
            try:
                _WHISPER_MODEL = WhisperModel(
                    model_size, device="cuda",
                    compute_type=compute_type or "float16",
                )
                return _WHISPER_MODEL
            except Exception:
                device = "cpu"

        _WHISPER_MODEL = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type or ("float16" if device == "cuda" else "int8"),
        )
    return _WHISPER_MODEL


def cmd_transcribe_audio(msgid, language="pt"):
    """Transcreve audio local via faster-whisper (usa GPU CUDA se disponivel, senao CPU).

    Requer pacote faster-whisper instalado (pip install faster-whisper).

    Uso: transcribe-audio <msgid> [language]
         language: pt (default), en, es, auto

    Cache: transcript salvo em cache/transcripts/<hash>.txt — re-runs instant.
    """
    TRANSCRIPT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    info = download_media_by_msgid(msgid)
    if info["kind"] != "audio":
        msg = f"Msg nao e audio (kind={info['kind']}, mime={info['mimetype']})"
        if JSON_MODE:
            output({"error": True, "message": msg})
        else:
            print(msg, file=sys.stderr)
        sys.exit(1)

    audio_path = Path(info["local_path"])
    transcript_path = TRANSCRIPT_CACHE_DIR / (audio_path.stem + ".txt")
    cached = transcript_path.exists() and transcript_path.stat().st_size > 0

    if cached:
        text = transcript_path.read_text(encoding="utf-8")
        result = {
            "msgid": msgid,
            "language": language,
            "cached": True,
            "local_path": str(audio_path),
            "transcript_path": str(transcript_path),
            "text": text,
        }
    else:
        model = _load_whisper_model("large-v3")
        if model is None:
            msg = "faster-whisper nao esta instalado. Instale com: pip install faster-whisper"
            if JSON_MODE:
                output({"error": True, "message": msg})
            else:
                print(msg, file=sys.stderr)
            sys.exit(1)
        lang_arg = None if language == "auto" else language
        segments, meta = model.transcribe(
            str(audio_path),
            language=lang_arg,
            beam_size=5,
            vad_filter=True,
        )
        parts = []
        for seg in segments:
            parts.append(seg.text.strip())
        text = " ".join(parts).strip()
        transcript_path.write_text(text, encoding="utf-8")
        result = {
            "msgid": msgid,
            "language": meta.language,
            "language_probability": round(meta.language_probability, 3),
            "duration": round(meta.duration, 2),
            "cached": False,
            "local_path": str(audio_path),
            "transcript_path": str(transcript_path),
            "text": text,
        }

    if JSON_MODE:
        output(result)
    else:
        header = f"[cache] " if result.get("cached") else f"[whisper large-v3] "
        if not result.get("cached"):
            header += f"{result['duration']}s | lang={result['language']} ({result['language_probability']})"
        print(header)
        print("---")
        print(result["text"])
        print("---")


def cmd_read_media(identifier, msgid=None):
    """Le midia da ultima mensagem (ou de uma msg especifica) do chat.

    Uso: read-media <numero|nome>           → le ultima midia do chat
         read-media <numero|nome> <msgid>   → le msg especifica

    Para IMAGEM: retorna o path local — o agente usa Read tool nativa (vision)
    Para AUDIO:  retorna path + aviso (transcricao via cmd separado)
    """
    chatid = resolve_chatid(identifier)
    if msgid is None:
        msgs = api_post("/message/find", {
            "chatid": chatid,
            "sort": "-messageTimestamp",
            "limit": 20,
        }).get("messages", [])
        media_types = {"ImageMessage", "AudioMessage", "PttMessage", "VideoMessage", "DocumentMessage"}
        target = next((m for m in msgs if m.get("type") in media_types), None)
        if not target:
            msg = f"Nenhuma midia encontrada nas ultimas 20 msgs de {identifier}"
            if JSON_MODE:
                output({"error": True, "message": msg})
            else:
                print(msg, file=sys.stderr)
            sys.exit(1)
        msgid = target.get("id")

    info = download_media_by_msgid(msgid)
    info["chatid"] = chatid
    if info["kind"] == "image":
        info["instruction"] = "Claude pode ler via Read tool nativa (vision)"
    elif info["kind"] == "audio":
        info["instruction"] = "Use transcribe-audio <msgid> pra converter em texto"
    if JSON_MODE:
        output(info)
    else:
        print(f"[{info['kind']}] {info['mimetype']}")
        print(f"  Path: {info['local_path']}")
        if "instruction" in info:
            print(f"  -> {info['instruction']}")


def cmd_send_contact(identifier, contact_name, contact_number):
    """Envia cartao de contato"""
    number = resolve_number(identifier)
    result = api_post("/send/contact", {
        "number": number,
        "contact_name": contact_name,
        "contact_number": contact_number,
    })
    if JSON_MODE:
        output({"sent": True, "to": number, "contact": contact_name, "result": result})
    else:
        print(f"Contato {contact_name} enviado para {number}")


def cmd_send_location(identifier, lat, lon, name="", address=""):
    """Envia localizacao"""
    number = resolve_number(identifier)
    body = {
        "number": number,
        "latitude": lat,
        "longitude": lon,
    }
    if name:
        body["name"] = name
    if address:
        body["address"] = address
    result = api_post("/send/location", body)
    if JSON_MODE:
        output({"sent": True, "to": number, "lat": lat, "lon": lon, "result": result})
    else:
        print(f"Localizacao enviada para {number}")


def cmd_send_menu(identifier, menu_json):
    """Envia menu interativo"""
    number = resolve_number(identifier)
    try:
        menu = json.loads(menu_json)
    except json.JSONDecodeError:
        # Tenta ler como arquivo
        if os.path.exists(menu_json):
            with open(menu_json) as f:
                menu = json.load(f)
        else:
            print("JSON invalido e arquivo nao encontrado", file=sys.stderr)
            sys.exit(1)
    menu["number"] = number
    result = api_post("/send/menu", menu)
    if JSON_MODE:
        output({"sent": True, "to": number, "type": "menu", "result": result})
    else:
        print(f"Menu enviado para {number}")


# ============================================================
# COMANDOS: ACOES EM MENSAGENS
# ============================================================


def cmd_markread(identifier):
    """Marca conversa como lida. A API uazapi espera `number` (sem @suffix),
    nao `chatid`. Retorna string enganosa 'marked as unread successfully' mas
    efetivamente marca como LIDA."""
    number = resolve_number(identifier)
    result = api_post("/chat/read", {"number": number})
    if JSON_MODE:
        output({"marked_read": True, "number": number, "result": result})
    else:
        print(f"Conversa marcada como lida: {number}")


def cmd_markread_all(*args):
    """Marca todas as conversas com unread>0 como lidas em lote.

    Uso:
        markread-all              # dry-run, apenas lista o que seria feito
        markread-all --confirm    # executa o reset de verdade

    Util para limpar o contador historico da Zappfy (device scoped), que
    acumula mensagens nao-lidas desde o pairing mesmo quando ja lidas no celular.
    """
    import time
    confirm = "--confirm" in args

    all_unread = []
    offset = 0
    batch_size = 100
    while True:
        result = api_post("/chat/find", {
            "wa_unreadCount": ">0",
            "sort": "-wa_lastMsgTimestamp",
            "limit": batch_size,
            "offset": offset,
        })
        chats = result.get("chats", [])
        if not chats:
            break
        all_unread.extend(chats)
        if len(chats) < batch_size:
            break
        offset += batch_size

    total_unread_msgs = sum(c.get("wa_unreadCount", 0) for c in all_unread)

    if not confirm:
        print(f"DRY-RUN | {len(all_unread)} conversas com {total_unread_msgs} mensagens nao-lidas")
        print("Top 30 por volume:")
        print()
        for c in sorted(all_unread, key=lambda x: -x.get("wa_unreadCount", 0))[:30]:
            name = chat_name(c)
            unread = c.get("wa_unreadCount", 0)
            icon = "G" if c.get("wa_isGroup") else " "
            print(f"  [{icon}] {unread:>5} | {name}")
        if len(all_unread) > 30:
            print(f"  ... (+{len(all_unread) - 30} conversas adicionais)")
        print()
        print("Para executar o reset de verdade: markread-all --confirm")
        return

    print(f"Executando markread em {len(all_unread)} conversas ({total_unread_msgs} mensagens)")
    print()
    marked = 0
    errors = 0
    for i, c in enumerate(all_unread, 1):
        chatid = c.get("wa_chatid", "")
        name = chat_name(c)
        if not chatid:
            continue
        number = chatid.split("@")[0]
        try:
            url = f"{ZAPPFY_BASE_URL}/chat/read"
            headers = {"Content-Type": "application/json", "token": TOKEN}
            data = json.dumps({"number": number}).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                resp.read()
            marked += 1
        except Exception as e:
            errors += 1
            print(f"  ERRO em '{name}': {e}", file=sys.stderr)
        if i % 20 == 0 or i == len(all_unread):
            print(f"  Progresso: {i}/{len(all_unread)} ({marked} OK, {errors} erros)")
        time.sleep(0.1)

    print()
    print(f"Concluido: {marked} conversas marcadas como lidas, {errors} erros")


def cmd_triagem(*args):
    """Triagem inteligente baseada em fromMe + gap temporal (nao unread_count).

    Uso:
        triagem              # janela padrao de 24h, audios auto-transcritos
        triagem 6            # janela de 6h
        triagem 48 --no-audio      # janela de 48h, sem transcrever audios
        triagem 24 --read-images   # tambem le conteudo das imagens via vision

    Default: audios dos pendentes sao TRANSCRITOS automaticamente;
             imagens sao SINALIZADAS (label claro) mas nao lidas.

    Flags:
      --no-audio      Nao transcreve audios (so sinaliza como [audio])
      --read-images   Le conteudo das imagens via vision nativa (mais lento)

    Separa em:
      URGENTE    - palavras-chave criticas definidas em config.json -> urgent_keywords
      ATRASADA   - ultima msg deles, gap acima do limite atrasada_hours (default: 24h; configuravel em config.json)
      IMPORTANTE - ultima msg deles, gap entre importante_hours e atrasada_hours (defaults: 4-24h)
      NORMAL     - ultima msg deles, gap entre normal_hours e importante_hours (defaults: 1-4h)
      RECENTE    - ultima msg deles, gap abaixo de normal_hours (default: < 1h)
      RESPONDIDO - ultima msg e sua (bola esta com o outro lado)
    """
    firm = load_firm_config()

    horas = 24
    transcribe_audio = True
    read_images = False
    for a in args:
        if a.isdigit():
            horas = int(a)
        elif a == "--no-audio":
            transcribe_audio = False
        elif a == "--read-images":
            read_images = True

    cutoff = datetime.now().timestamp() - (horas * 3600)

    # Equipe interna do escritorio — definida em config.json -> team
    TEAM_NAMES_NORM = firm["team_names"]

    def is_equipe(sender):
        if not sender:
            return False
        # Lowercase + strip acentos comuns (TEAM_NAMES_NORM esta em ASCII)
        s = str(sender).lower().strip()
        for a, b in (("á","a"),("à","a"),("ã","a"),("â","a"),
                     ("é","e"),("ê","e"),("í","i"),
                     ("ó","o"),("õ","o"),("ô","o"),
                     ("ú","u"),("ç","c")):
            s = s.replace(a, b)
        return any(tn == s or tn in s or s in tn for tn in TEAM_NAMES_NORM)

    SILENCIAR_KEYWORDS = firm["silence_keywords"]

    URGENT_KEYWORDS = firm["urgent_keywords"]

    def is_silenciado(name):
        n = (name or "").lower()
        return any(kw in n for kw in SILENCIAR_KEYWORDS)

    # 1. Buscar chats recentes
    result = api_post("/chat/find", {
        "sort": "-wa_lastMsgTimestamp",
        "limit": firm["max_chats"],
    })
    all_chats = result.get("chats", [])

    # 2. Filtrar por janela + silenciados
    relevantes = []
    for c in all_chats:
        ts = c.get("wa_lastMsgTimestamp", 0)
        if ts > 9999999999:
            ts = ts // 1000
        if ts < cutoff:
            continue
        if is_silenciado(chat_name(c)):
            continue
        relevantes.append(c)

    # 3. Buscar ultima mensagem de cada relevante pra saber fromMe
    triaged = []
    for c in relevantes[:firm["max_process"]]:
        chatid = c.get("wa_chatid", "")
        if not chatid:
            continue
        try:
            msg_result = api_post("/message/find", {"chatid": chatid, "limit": 1})
            msgs = msg_result.get("messages", [])
            if not msgs:
                continue
            last_msg = msgs[0]
            _update_lid_cache_from_messages(msgs)
        except Exception:
            continue

        ts = parse_msg_ts(last_msg)
        gap_hours = (datetime.now().timestamp() - ts) / 3600 if ts else 9999

        from_me = last_msg.get("fromMe", False)
        text = last_msg.get("text") or ""
        msg_type = last_msg.get("messageType", "")
        if not text:
            type_labels = {
                "ImageMessage": "[imagem]", "VideoMessage": "[video]",
                "AudioMessage": "[audio]", "PttMessage": "[audio]",
                "DocumentMessage": "[documento]", "StickerMessage": "[figurinha]",
                "LocationMessage": "[localizacao]", "ContactMessage": "[contato]",
                "ReactionMessage": "[reacao]", "PollCreationMessage": "[enquete]",
            }
            text = type_labels.get(msg_type, f"[{msg_type}]" if msg_type else "[sem texto]")
        sender = resolve_sender(last_msg)

        triaged.append({
            "chat": c,
            "from_me": from_me,
            "gap_hours": gap_hours,
            "text": text,
            "sender": sender,
            "name": chat_name(c),
            "is_group": c.get("wa_isGroup", False),
            "chatid": chatid,
            "msg_id": last_msg.get("id", ""),
            "msg_type": msg_type,
            "media_kind": None,
            "media_processed": False,
        })

    # 4. Separar pendentes (bola comigo) vs respondidos (bola com o outro)
    pendentes = [t for t in triaged if not t["from_me"]]
    respondidos = [t for t in triaged if t["from_me"]]

    # 5. Classificar urgencia dos pendentes
    def classificar(item):
        gap = item["gap_hours"]
        text_lower = (item["text"] or "").lower()
        # Se a ultima msg no grupo e de uma advogada da equipe interna, nao e
        # pendencia do Doc — a equipe esta cuidando, basta acompanhar
        if item["is_group"] and is_equipe(item["sender"]):
            return ("EQUIPE_CUIDANDO", 5)
        if any(kw in text_lower for kw in URGENT_KEYWORDS):
            return ("URGENTE", 0)
        if gap > firm["thresholds"]["atrasada_hours"]:
            return ("ATRASADA", 1)
        elif gap > firm["thresholds"]["importante_hours"]:
            return ("IMPORTANTE", 2)
        elif gap > firm["thresholds"]["normal_hours"]:
            return ("NORMAL", 3)
        else:
            return ("RECENTE", 4)

    for item in pendentes:
        item["urgencia"], item["prio"] = classificar(item)

    pendentes.sort(key=lambda x: (x["prio"], -x["gap_hours"]))

    # 5.5 Processar midia dos pendentes (audios transcritos, imagens sinalizadas)
    AUDIO_TYPES = {"AudioMessage", "PttMessage"}
    IMAGE_TYPES = {"ImageMessage"}
    DOC_TYPES = {"DocumentMessage"}
    VIDEO_TYPES = {"VideoMessage"}

    media_stats = {"audios_transcritos": 0, "imagens_sinalizadas": 0, "imagens_lidas": 0, "erros": 0}

    for item in pendentes:
        mtype = item.get("msg_type") or ""
        msgid = item.get("msg_id") or ""
        if not msgid:
            continue

        try:
            if mtype in AUDIO_TYPES and transcribe_audio:
                info = download_media_by_msgid(msgid)
                if info["kind"] == "audio":
                    TRANSCRIPT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
                    audio_path = Path(info["local_path"])
                    transcript_path = TRANSCRIPT_CACHE_DIR / (audio_path.stem + ".txt")
                    if transcript_path.exists() and transcript_path.stat().st_size > 0:
                        transcript = transcript_path.read_text(encoding="utf-8")
                        item["text"] = f"[audio transcrito] {transcript}"
                    else:
                        model = _load_whisper_model("large-v3")
                        if model is None:
                            item["text"] = "[audio — transcricao indisponivel (instale faster-whisper para ativar)]"
                            item["media_kind"] = "audio"
                            media_stats["audios_transcritos"] += 0
                            continue
                        segments, _meta = model.transcribe(
                            str(audio_path), language="pt",
                            beam_size=5, vad_filter=True,
                        )
                        transcript = " ".join(s.text.strip() for s in segments).strip()
                        transcript_path.write_text(transcript, encoding="utf-8")
                        item["text"] = f"[audio transcrito] {transcript}"
                    item["media_kind"] = "audio"
                    item["media_processed"] = True
                    media_stats["audios_transcritos"] += 1

            elif mtype in IMAGE_TYPES:
                if read_images:
                    info = download_media_by_msgid(msgid)
                    item["text"] = f"[imagem enviada — path: {info['local_path']}]"
                    item["media_kind"] = "image"
                    item["media_processed"] = True
                    item["media_path"] = info["local_path"]
                    media_stats["imagens_lidas"] += 1
                else:
                    item["text"] = "[imagem enviada — abrir no celular ou usar --read-images]"
                    item["media_kind"] = "image"
                    media_stats["imagens_sinalizadas"] += 1

            elif mtype in DOC_TYPES:
                item["text"] = "[documento/arquivo enviado — abrir no celular]"
                item["media_kind"] = "document"

            elif mtype in VIDEO_TYPES:
                item["text"] = "[video enviado — abrir no celular]"
                item["media_kind"] = "video"
        except Exception as e:
            item["text"] = f"{item['text']} (erro ao processar midia: {type(e).__name__})"
            media_stats["erros"] += 1

    # 6. Output
    if JSON_MODE:
        output({
            "horas_janela": horas,
            "total_janela": len(relevantes),
            "total_analisados": len(triaged),
            "pendentes": len(pendentes),
            "respondidos": len(respondidos),
            "media_stats": media_stats,
            "flags": {"transcribe_audio": transcribe_audio, "read_images": read_images},
            "items_pendentes": [{
                "name": t["name"],
                "chatid": t["chatid"],
                "is_group": t["is_group"],
                "urgencia": t["urgencia"],
                "gap_hours": round(t["gap_hours"], 1),
                "last_sender": t["sender"],
                "last_text": (t["text"] or "")[:2000],
                "media_kind": t.get("media_kind"),
                "msg_id": t.get("msg_id", ""),
            } for t in pendentes],
            "items_respondidos": [{
                "name": t["name"],
                "chatid": t["chatid"],
                "is_group": t["is_group"],
                "gap_hours": round(t["gap_hours"], 1),
                "last_text": (t["text"] or "")[:120],
            } for t in respondidos],
        })
        return

    # Human output
    print(f"TRIAGEM ({horas}h) | {len(relevantes)} chats na janela | {len(triaged)} analisados")
    print(f"Pendentes: {len(pendentes)} | Voce ja respondeu: {len(respondidos)}")
    ms = media_stats
    if ms["audios_transcritos"] or ms["imagens_sinalizadas"] or ms["imagens_lidas"] or ms["erros"]:
        parts = []
        if ms["audios_transcritos"]:
            parts.append(f"{ms['audios_transcritos']} audios transcritos")
        if ms["imagens_sinalizadas"]:
            parts.append(f"{ms['imagens_sinalizadas']} imagens sinalizadas")
        if ms["imagens_lidas"]:
            parts.append(f"{ms['imagens_lidas']} imagens lidas")
        if ms["erros"]:
            parts.append(f"{ms['erros']} erros")
        print(f"Midia: {' | '.join(parts)}")
    print()

    categorias_ordenadas = ["URGENTE", "ATRASADA", "IMPORTANTE", "NORMAL", "RECENTE", "EQUIPE_CUIDANDO"]
    for cat in categorias_ordenadas:
        items = [p for p in pendentes if p["urgencia"] == cat]
        if not items:
            continue
        print(f"=== {cat} ({len(items)}) ===")
        for item in items:
            icon = "G" if item["is_group"] else " "
            gap = f"{item['gap_hours']:.1f}h"
            text = truncate(item["text"], 180)
            sender_prefix = f"[{item['sender']}] " if item["is_group"] and item["sender"] else ""
            print(f"  [{icon}] {item['name']} | ha {gap}")
            print(f"      {sender_prefix}{text}")
        print()

    if respondidos:
        print(f"=== VOCE JA RESPONDEU ({len(respondidos)}) ===")
        for item in respondidos[:10]:
            icon = "G" if item["is_group"] else " "
            gap = f"{item['gap_hours']:.1f}h"
            print(f"  [{icon}] {item['name']} | ha {gap}")
        if len(respondidos) > 10:
            print(f"  ... +{len(respondidos) - 10}")


def cmd_react(identifier, msgid, emoji):
    """Reage a uma mensagem"""
    chatid = resolve_chatid(identifier)
    result = api_post("/message/react", {
        "chatid": chatid,
        "messageid": msgid,
        "reaction": emoji,
    })
    if JSON_MODE:
        output({"reacted": True, "chatid": chatid, "messageid": msgid, "emoji": emoji, "result": result})
    else:
        print(f"Reagido com {emoji}")


def cmd_delete(identifier, msgid, everyone="false"):
    """Deleta mensagem"""
    chatid = resolve_chatid(identifier)
    result = api_post("/message/delete", {
        "chatid": chatid,
        "messageid": msgid,
        "everyone": everyone.lower() in ("true", "1", "yes", "sim"),
    })
    if JSON_MODE:
        output({"deleted": True, "chatid": chatid, "messageid": msgid, "result": result})
    else:
        print(f"Mensagem deletada")


def cmd_edit(identifier, msgid, *text_parts):
    """Edita mensagem enviada"""
    text = " ".join(text_parts)
    if not text:
        print("Uso: edit <numero|nome> <msgid> <novo_texto>", file=sys.stderr)
        sys.exit(1)
    chatid = resolve_chatid(identifier)
    result = api_post("/message/edit", {
        "chatid": chatid,
        "messageid": msgid,
        "text": text,
    })
    if JSON_MODE:
        output({"edited": True, "chatid": chatid, "messageid": msgid, "text": text, "result": result})
    else:
        print(f"Mensagem editada")


def cmd_typing(identifier, duration="5"):
    """Envia indicador de digitando"""
    number = resolve_number(identifier)
    api_post("/message/presence", {
        "number": number,
        "presence": "composing",
    })
    if JSON_MODE:
        output({"typing": True, "to": number, "duration": int(duration)})
    else:
        print(f"Digitando para {number}...")


# ============================================================
# COMANDOS: GERENCIAMENTO DE CHAT
# ============================================================


def cmd_pin(identifier):
    """Fixa/desfixa conversa"""
    chatid = resolve_chatid(identifier)
    result = api_post("/chat/pin", {"chatid": chatid})
    if JSON_MODE:
        output({"pinned": True, "chatid": chatid, "result": result})
    else:
        print(f"Conversa fixada/desfixada: {chatid}")


def cmd_archive(identifier):
    """Arquiva/desarquiva conversa"""
    chatid = resolve_chatid(identifier)
    result = api_post("/chat/archive", {"chatid": chatid})
    if JSON_MODE:
        output({"archived": True, "chatid": chatid, "result": result})
    else:
        print(f"Conversa arquivada/desarquivada: {chatid}")


def cmd_mute(identifier, duration="8"):
    """Silencia conversa (horas)"""
    chatid = resolve_chatid(identifier)
    result = api_post("/chat/mute", {"chatid": chatid})
    if JSON_MODE:
        output({"muted": True, "chatid": chatid, "result": result})
    else:
        print(f"Conversa silenciada: {chatid}")


def cmd_labels(identifier, action="list", label=""):
    """Gerencia labels: labels <contato> [list|add|remove] [label]"""
    chatid = resolve_chatid(identifier)
    if action == "list":
        result = api_post("/chat/find", {"wa_chatid": chatid, "limit": 1})
        chats = result.get("chats", [])
        labels = chats[0].get("wa_label", "") if chats else ""
        if JSON_MODE:
            output({"chatid": chatid, "labels": labels})
        else:
            print(f"Labels: {labels or '(nenhuma)'}")
    else:
        result = api_post("/chat/labels", {
            "chatid": chatid,
            "action": action,
            "label": label,
        })
        if JSON_MODE:
            output({"chatid": chatid, "action": action, "label": label, "result": result})
        else:
            print(f"Label '{label}' {action}: {chatid}")


def cmd_block(identifier):
    """Bloqueia contato"""
    chatid = resolve_chatid(identifier)
    result = api_post("/chat/block", {"chatid": chatid})
    if JSON_MODE:
        output({"blocked": True, "chatid": chatid, "result": result})
    else:
        print(f"Bloqueado: {chatid}")


def cmd_unblock(identifier):
    """Desbloqueia contato"""
    chatid = resolve_chatid(identifier)
    result = api_post("/chat/block", {"chatid": chatid, "action": "unblock"})
    if JSON_MODE:
        output({"unblocked": True, "chatid": chatid, "result": result})
    else:
        print(f"Desbloqueado: {chatid}")


# ============================================================
# COMANDOS: CRM / LEADS
# ============================================================


def cmd_lead_info(identifier):
    """Info de lead"""
    chatid = resolve_chatid(identifier)
    result = api_post("/chat/find", {"wa_chatid": chatid, "limit": 1})
    chats = result.get("chats", [])
    if not chats:
        human("Chat nao encontrado")
        if JSON_MODE:
            output({"error": True, "message": "Chat nao encontrado"})
        sys.exit(1)
    chat = chats[0]
    lead_data = {
        "chatid": chatid,
        "name": chat.get("lead_name", ""),
        "fullName": chat.get("lead_fullName", ""),
        "email": chat.get("lead_email", ""),
        "personalid": chat.get("lead_personalid", ""),
        "status": chat.get("lead_status", ""),
        "tags": chat.get("lead_tags", []),
        "notes": chat.get("lead_notes", ""),
        "isTicketOpen": chat.get("lead_isTicketOpen", False),
        "assignedAttendant": chat.get("lead_assignedAttendant_id", ""),
        "field01": chat.get("lead_field01", ""),
    }
    if JSON_MODE:
        output(lead_data)
    else:
        print(f"Lead: {lead_data['fullName'] or lead_data['name'] or chatid}")
        print(f"  Email: {lead_data['email'] or '-'}")
        print(f"  Status: {lead_data['status'] or '-'}")
        print(f"  Tags: {lead_data['tags'] or '-'}")
        print(f"  Notas: {lead_data['notes'] or '-'}")
        print(f"  Ticket: {'Aberto' if lead_data['isTicketOpen'] else 'Fechado'}")


def cmd_lead_update(identifier, fields_json):
    """Atualiza campos do lead"""
    chatid = resolve_chatid(identifier)
    try:
        fields = json.loads(fields_json)
    except json.JSONDecodeError:
        print("JSON invalido para campos", file=sys.stderr)
        sys.exit(1)
    fields["id"] = chatid
    result = api_post("/chat/editLead", fields)
    if JSON_MODE:
        output({"updated": True, "chatid": chatid, "fields": fields, "result": result})
    else:
        print(f"Lead atualizado: {chatid}")


def cmd_lead_tag(identifier, action, tag):
    """Gerencia tags do lead: lead-tag <contato> add|remove <tag>"""
    chatid = resolve_chatid(identifier)
    # Buscar tags atuais
    result = api_post("/chat/find", {"wa_chatid": chatid, "limit": 1})
    chats = result.get("chats", [])
    current_tags = chats[0].get("lead_tags", []) if chats else []
    if not isinstance(current_tags, list):
        current_tags = []

    if action == "add" and tag not in current_tags:
        current_tags.append(tag)
    elif action == "remove" and tag in current_tags:
        current_tags.remove(tag)

    result = api_post("/chat/editLead", {"id": chatid, "lead_tags": current_tags})
    if JSON_MODE:
        output({"chatid": chatid, "action": action, "tag": tag, "tags": current_tags, "result": result})
    else:
        print(f"Tag '{tag}' {action}: {current_tags}")


def cmd_lead_assign(identifier, attendant_id):
    """Atribui lead a um atendente"""
    chatid = resolve_chatid(identifier)
    result = api_post("/chat/editLead", {
        "id": chatid,
        "lead_assignedAttendant_id": attendant_id,
    })
    if JSON_MODE:
        output({"chatid": chatid, "assigned": attendant_id, "result": result})
    else:
        print(f"Lead atribuido a: {attendant_id}")


def cmd_lead_ticket(identifier, action):
    """Abre/fecha ticket: lead-ticket <contato> open|close"""
    chatid = resolve_chatid(identifier)
    is_open = action.lower() in ("open", "abrir", "true", "1")
    result = api_post("/chat/editLead", {
        "id": chatid,
        "lead_isTicketOpen": is_open,
    })
    if JSON_MODE:
        output({"chatid": chatid, "ticket_open": is_open, "result": result})
    else:
        print(f"Ticket {'aberto' if is_open else 'fechado'}: {chatid}")


def cmd_lead_status(identifier, status):
    """Atualiza status do lead"""
    chatid = resolve_chatid(identifier)
    result = api_post("/chat/editLead", {
        "id": chatid,
        "lead_status": status,
    })
    if JSON_MODE:
        output({"chatid": chatid, "status": status, "result": result})
    else:
        print(f"Status do lead: {status}")


# ============================================================
# COMANDOS: GRUPOS
# ============================================================


def cmd_groups(limit="50"):
    """Lista grupos"""
    limit = int(limit)
    result = api_post("/chat/find", {
        "wa_isGroup": True,
        "sort": "-wa_lastMsgTimestamp",
        "limit": limit,
    })
    chats = result.get("chats", [])
    if JSON_MODE:
        items = []
        for c in chats:
            items.append({
                "name": c.get("wa_name") or c.get("name", "?"),
                "chatid": c.get("wa_chatid", ""),
                "unread_count": c.get("wa_unreadCount", 0),
                "is_admin": c.get("wa_isGroup_admin", False),
                "member_count": c.get("wa_isGroup_member", 0),
                "last_timestamp": c.get("wa_lastMsgTimestamp", 0),
            })
        output({"total": len(items), "groups": items})
    else:
        if not chats:
            print("Nenhum grupo encontrado.")
            return
        print(f"Grupos ({len(chats)}):\n")
        for c in chats:
            name = c.get("wa_name") or c.get("name", "?")
            admin = " [ADMIN]" if c.get("wa_isGroup_admin") else ""
            unread = c.get("wa_unreadCount", 0)
            print(f"  {name}{admin} | Nao lidas: {unread}")


def cmd_group_info(identifier):
    """Info detalhada de grupo"""
    chatid = resolve_chatid(identifier)
    if not chatid.endswith("@g.us"):
        chatid = f"{chatid}@g.us"
    result = api_post("/group/info", {"groupid": chatid})
    if JSON_MODE:
        output(result)
    else:
        print(f"Grupo: {result.get('subject', result.get('name', '?'))}")
        print(f"  ID: {chatid}")
        print(f"  Descricao: {result.get('desc', '-')}")
        participants = result.get("participants", [])
        print(f"  Participantes: {len(participants)}")
        for p in participants[:20]:
            role = " [ADMIN]" if p.get("admin") else ""
            print(f"    {p.get('id', '?')}{role}")
        if len(participants) > 20:
            print(f"    ... e mais {len(participants) - 20}")


def cmd_group_recap(group_name, hours="48"):
    """Recap de mensagens do grupo nas ultimas N horas"""
    hours = int(hours)
    cutoff = datetime.now().timestamp() - (hours * 3600)

    # Encontrar grupo
    result = api_post("/chat/find", {
        "wa_isGroup": True,
        "wa_name": f"~{group_name}",
        "sort": "-wa_lastMsgTimestamp",
        "limit": 10,
    })
    chats = result.get("chats", [])
    if not chats:
        human(f"Nenhum grupo encontrado com '{group_name}'")
        if JSON_MODE:
            output({"error": True, "message": f"Grupo nao encontrado: {group_name}"})
        sys.exit(1)

    group = chats[0]
    chatid = group.get("wa_chatid", "")
    name = group.get("wa_name") or group.get("name", "?")

    # Buscar mensagens com paginacao
    all_messages = []
    offset = 0
    batch_size = 100
    reached_cutoff = False

    while not reached_cutoff:
        result = api_post("/message/find", {
            "chatid": chatid,
            "limit": batch_size,
            "offset": offset,
        })
        messages = result.get("messages", [])
        if not messages:
            break
        _update_lid_cache_from_messages(messages)
        for msg in messages:
            ts = parse_msg_ts(msg)
            if ts > 0 and ts < cutoff:
                reached_cutoff = True
                break
            all_messages.append(msg)
        if not reached_cutoff and result.get("hasMore"):
            offset = result.get("nextOffset", offset + batch_size)
        else:
            break

    # Filtrar reacoes
    content_msgs = []
    reaction_count = 0
    for msg in all_messages:
        if msg.get("messageType") == "ReactionMessage":
            reaction_count += 1
        else:
            content_msgs.append(msg)

    if JSON_MODE:
        items = []
        for msg in reversed(content_msgs):
            items.append({
                "sender": "EU" if msg.get("fromMe") else (resolve_sender(msg) or "?"),
                "from_me": msg.get("fromMe", False),
                "text": msg.get("text") or "",
                "type": msg.get("messageType", ""),
                "timestamp": parse_msg_ts(msg),
            })
        output({
            "group": name,
            "chatid": chatid,
            "hours": hours,
            "total_messages": len(content_msgs),
            "total_reactions": reaction_count,
            "messages": items,
        })
    else:
        print(f"Grupo: {name}")
        print(f"Periodo: ultimas {hours}h")
        print(f"Mensagens: {len(content_msgs)} + {reaction_count} reacoes")
        print("=" * 60)

        if not content_msgs:
            print("\nNenhuma mensagem neste periodo.")
            return

        current_day = ""
        for msg in reversed(content_msgs):
            sender = resolve_sender(msg) or "?"
            if msg.get("fromMe"):
                sender = "EU"
            text = msg.get("text") or ""
            msg_type = msg.get("messageType", "")
            if not text:
                type_labels = {
                    "ImageMessage": "[imagem]", "VideoMessage": "[video]",
                    "AudioMessage": "[audio]", "PttMessage": "[audio]",
                    "DocumentMessage": "[documento]", "StickerMessage": "[figurinha]",
                    "LocationMessage": "[localizacao]", "ContactMessage": "[contato]",
                    "RevokedMessage": "[apagada]", "PollCreationMessage": "[enquete]",
                }
                text = type_labels.get(msg_type, f"[{msg_type}]")
            ts = parse_msg_ts(msg)
            if ts > 0:
                day = datetime.fromtimestamp(ts).strftime("%d/%m/%Y")
                if day != current_day:
                    current_day = day
                    print(f"\n--- {day} ---\n")
            ts_str = format_ts(ts)
            print(f"  [{ts_str}] {sender}: {text}")

        print(f"\n{'=' * 60}")
        print(f"Total: {len(content_msgs)} msgs + {reaction_count} reacoes | {name}")


def cmd_group_create(name, *numbers):
    """Cria grupo"""
    if not numbers:
        print("Uso: group-create <nome> <numero1> [numero2] ...", file=sys.stderr)
        sys.exit(1)
    participants = [n.replace("+", "") for n in numbers]
    result = api_post("/group/create", {"name": name, "participants": participants})
    if JSON_MODE:
        output({"created": True, "name": name, "participants": participants, "result": result})
    else:
        print(f"Grupo '{name}' criado com {len(participants)} participante(s)")


def cmd_group_participants(identifier, action, *numbers):
    """Gerencia participantes: add|remove|promote|demote"""
    chatid = resolve_chatid(identifier)
    if not chatid.endswith("@g.us"):
        chatid = f"{chatid}@g.us"
    if action not in ("add", "remove", "promote", "demote"):
        print(f"Acao invalida: {action}. Use: add, remove, promote, demote", file=sys.stderr)
        sys.exit(1)
    participants = [n.replace("+", "") for n in numbers]
    result = api_post("/group/updateParticipants", {
        "groupid": chatid,
        "participants": participants,
        "action": action,
    })
    if JSON_MODE:
        output({"chatid": chatid, "action": action, "participants": participants, "result": result})
    else:
        print(f"{action}: {participants} em {chatid}")


def cmd_group_update(identifier, field, value):
    """Atualiza grupo: name|description|image"""
    chatid = resolve_chatid(identifier)
    if not chatid.endswith("@g.us"):
        chatid = f"{chatid}@g.us"
    endpoint_map = {
        "name": "/group/updateName",
        "description": "/group/updateDescription",
        "image": "/group/updateImage",
    }
    if field not in endpoint_map:
        print(f"Campo invalido: {field}. Use: name, description, image", file=sys.stderr)
        sys.exit(1)
    body = {"groupid": chatid}
    if field == "name":
        body["name"] = value
    elif field == "description":
        body["description"] = value
    elif field == "image":
        body["image"] = value
    result = api_post(endpoint_map[field], body)
    if JSON_MODE:
        output({"chatid": chatid, "field": field, "value": value, "result": result})
    else:
        print(f"Grupo atualizado ({field}): {value}")


def cmd_group_invite(identifier):
    """Gera link de convite do grupo"""
    chatid = resolve_chatid(identifier)
    if not chatid.endswith("@g.us"):
        chatid = f"{chatid}@g.us"
    result = api_post("/group/inviteInfo", {"groupid": chatid})
    if JSON_MODE:
        output(result)
    else:
        code = result.get("code") or result.get("inviteCode", "?")
        print(f"Link de convite: https://chat.whatsapp.com/{code}")


def cmd_group_admin_only(identifier, state):
    """Ativa/desativa modo somente admins: on|off"""
    chatid = resolve_chatid(identifier)
    if not chatid.endswith("@g.us"):
        chatid = f"{chatid}@g.us"
    announce = state.lower() in ("on", "true", "1", "sim")
    result = api_post("/group/updateAnnounce", {
        "groupid": chatid,
        "announce": announce,
    })
    if JSON_MODE:
        output({"chatid": chatid, "admin_only": announce, "result": result})
    else:
        print(f"Modo admin-only: {'ativado' if announce else 'desativado'}")


# ============================================================
# COMANDOS: CONTATOS
# ============================================================


def cmd_contacts(limit="50", page="1"):
    """Lista contatos com paginacao"""
    limit = int(limit)
    page = int(page)
    result = api_post("/contacts/list", {"page": page, "pageSize": limit})
    contacts = result.get("contacts", [])
    pagination = result.get("pagination", {})
    if JSON_MODE:
        output({
            "contacts": [{"name": c.get("contact_name") or c.get("contactName", ""), "jid": c.get("jid", "")} for c in contacts],
            "pagination": pagination,
        })
    else:
        print(f"Contatos (pagina {page}):\n")
        for c in contacts:
            name = c.get("contact_name") or c.get("contactName") or "Sem nome"
            jid = c.get("jid", "")
            print(f"  {name} | {jid}")
        total = pagination.get("totalRecords", "?")
        print(f"\nTotal: {total} contatos | Pagina {page}/{pagination.get('totalPages', '?')}")


def cmd_contact_add(number, name):
    """Adiciona contato"""
    result = api_post("/contact/add", {"number": number, "name": name})
    if JSON_MODE:
        output({"added": True, "number": number, "name": name, "result": result})
    else:
        print(f"Contato adicionado: {name} ({number})")


def cmd_contact_remove(number):
    """Remove contato"""
    result = api_post("/contact/remove", {"number": number})
    if JSON_MODE:
        output({"removed": True, "number": number, "result": result})
    else:
        print(f"Contato removido: {number}")


# ============================================================
# COMANDOS: RAW
# ============================================================


def cmd_raw(method, endpoint, body_json=None):
    """Chamada raw a API"""
    if method.upper() == "GET":
        result = api_get(endpoint)
    else:
        body = json.loads(body_json) if body_json else {}
        result = api_post(endpoint, body)
    output(result)

# COMANDOS: LID CACHE
# ============================================================


def cmd_lid_bootstrap(limit_chats="200", msgs_per_chat="30"):
    """Faz scan de mensagens em varios chats pra popular cache LID->nome.

    Util pra resolver senders vazios em mensagens onde a API Zappfy retorna
    senderName=''. O cache fica persistido em memory/lid_cache.json e e
    atualizado automaticamente sempre que cmd_messages, cmd_search_msg,
    cmd_triagem ou cmd_group_recap rodam.

    Args:
        limit_chats: quantos chats scanear (default 200)
        msgs_per_chat: quantas msgs por chat (default 30)
    """
    limit_chats = int(limit_chats)
    msgs_per_chat = int(msgs_per_chat)
    cache = _load_lid_cache()
    initial = len(cache)

    chats_result = api_post("/chat/find", {
        "sort": "-wa_lastMsgTimestamp",
        "limit": limit_chats,
    })
    chats = chats_result.get("chats", [])
    if not chats:
        if JSON_MODE:
            output({"error": True, "message": "Nenhum chat encontrado"})
        else:
            print("Nenhum chat encontrado.")
        return

    scanned = 0
    failed = 0
    for i, c in enumerate(chats):
        cid = c.get("wa_chatid") or c.get("chatid") or ""
        if not cid:
            continue
        try:
            r = api_post("/message/find", {"chatid": cid, "limit": msgs_per_chat})
            _update_lid_cache_from_messages(r.get("messages", []))
            scanned += 1
        except Exception:
            failed += 1
        if not JSON_MODE and (i + 1) % 20 == 0:
            print(f"  Progresso: {i+1}/{len(chats)} chats | LIDs cacheados: {len(cache)}", file=sys.stderr)

    final = len(cache)
    new = final - initial

    if JSON_MODE:
        output({
            "chats_scanned": scanned,
            "chats_failed": failed,
            "lids_before": initial,
            "lids_after": final,
            "new_lids": new,
            "cache_path": str(LID_CACHE_PATH),
        })
    else:
        print()
        print("LID bootstrap concluido.")
        print(f"  Chats scaneados: {scanned} (falhas: {failed})")
        print(f"  LIDs antes: {initial}")
        print(f"  LIDs depois: {final}")
        print(f"  Novos LIDs cacheados: {new}")
        print(f"  Cache em: {LID_CACHE_PATH}")


def cmd_lid_stats():
    """Mostra estatisticas do cache de LIDs."""
    cache = _load_lid_cache()
    if JSON_MODE:
        output({
            "total_lids": len(cache),
            "cache_path": str(LID_CACHE_PATH),
            "exists": LID_CACHE_PATH.exists(),
            "sample": dict(list(cache.items())[:10]),
        })
    else:
        print(f"LID Cache — {len(cache)} entradas")
        print(f"Arquivo: {LID_CACHE_PATH}")
        if cache:
            print("\nAmostra (primeiras 10 entradas):")
            for sid, name in list(cache.items())[:10]:
                print(f"  {sid:35s} -> {name}")


# ============================================================
# COMANDOS: HELP
# ============================================================


def cmd_help():
    """Mostra ajuda"""
    print("""whatsapp.py — CLI WhatsApp via API Zappfy
Uso: whatsapp.py [--json] <comando> [args...]

STATUS
  status                                    Status da conexao
  presence <available|unavailable>          Define presenca

LEITURA
  unread [limite]                           Conversas nao lidas (padrao: 50)
  chats [limite]                            Ultimas conversas (padrao: 20)
  messages <numero|nome> [limite]           Mensagens de um contato (padrao: 20)
  search-chat <termo>                       Busca conversas por nome
  search-msg <termo> [numero|nome]          Busca mensagens por conteudo
  contact-info <numero|nome>                Info detalhada de contato/lead

ENVIO
  send <numero|nome> <texto>                Envia texto
  reply <numero|nome> <msgid> <texto>       Responde mensagem especifica
  send-media <numero|nome> <url> [tipo] [legenda]  Envia midia
  send-contact <numero|nome> <nome_contato> <numero_contato>  Envia cartao
  send-location <numero|nome> <lat> <lon> [nome] [endereco]  Envia localizacao
  send-menu <numero|nome> <json>            Envia menu interativo

LEITURA DE MIDIA
  download-media <msgid>                    Baixa midia pro cache local
  read-media <numero|nome> [msgid]          Baixa ultima (ou especifica) midia do chat
                                            Imagem: abrir local_path via Read (vision nativa)
                                            Audio: usar transcribe-audio
  transcribe-audio <msgid> [lang]           Transcreve audio via faster-whisper large-v3
                                            (usa GPU CUDA se disponivel, senao CPU; cache automatico)
                                            lang: pt (default), en, es, auto

ACOES EM MENSAGENS
  markread <numero|nome>                    Marca conversa como lida
  markread-all [--confirm]                  Marca TODAS as conversas unread>0 como lidas (reset Zappfy)
  triagem [horas]                           Triagem inteligente por fromMe+gap temporal (padrao: 24h)
  react <numero|nome> <msgid> <emoji>       Reage com emoji
  delete <numero|nome> <msgid> [everyone]   Deleta mensagem
  edit <numero|nome> <msgid> <novo_texto>   Edita mensagem enviada
  typing <numero|nome> [duracao_seg]        Envia indicador de digitando

GERENCIAMENTO DE CHAT
  pin <numero|nome>                         Fixa/desfixa conversa
  archive <numero|nome>                     Arquiva/desarquiva
  mute <numero|nome> [horas]               Silencia conversa
  labels <numero|nome> [list|add|remove] [label]  Gerencia labels
  block <numero|nome>                       Bloqueia contato
  unblock <numero|nome>                     Desbloqueia contato

CRM / LEADS
  lead-info <numero|nome>                   Info do lead
  lead-update <numero|nome> <json_campos>   Atualiza campos do lead
  lead-tag <numero|nome> <add|remove> <tag> Gerencia tags
  lead-assign <numero|nome> <attendant_id>  Atribui a atendente
  lead-ticket <numero|nome> <open|close>    Abre/fecha ticket
  lead-status <numero|nome> <status>        Atualiza status

GRUPOS
  groups [limite]                           Lista grupos
  group-info <nome|id>                      Info detalhada
  group-recap <nome> [horas]               Recap de mensagens (padrao: 48h)
  group-create <nome> <num1> [num2] ...    Cria grupo
  group-participants <nome|id> <add|remove|promote|demote> <num...>
  group-update <nome|id> <name|description|image> <valor>
  group-invite <nome|id>                    Gera link de convite
  group-admin-only <nome|id> <on|off>       Modo somente admins

CONTATOS
  contacts [limite] [pagina]               Lista contatos
  contact-add <numero> <nome>              Adiciona contato
  contact-remove <numero>                  Remove contato

RAW
  raw <GET|POST> <endpoint> [json_body]    Chamada direta a API

Flag --json no inicio ativa output estruturado para agentes AI.""")


# ============================================================
# ROUTER
# ============================================================


COMMANDS = {
    # Bootstrap (sem credenciais)
    "config-dir": (cmd_config_dir, 0, 0),
    # Status
    "status": (cmd_status, 0, 0),
    "presence": (cmd_presence, 1, 1),
    # Leitura
    "unread": (cmd_unread, 0, 1),
    "chats": (cmd_chats, 0, 1),
    "messages": (cmd_messages, 1, 2),
    "search-chat": (cmd_search_chat, 1, 1),
    "search-msg": (cmd_search_msg, 1, 2),
    "contact-info": (cmd_contact_info, 1, 1),
    # Envio
    "send": (cmd_send, 2, 99),
    "reply": (cmd_reply, 3, 99),
    "send-media": (cmd_send_media, 2, 4),
    "download-media": (cmd_download_media, 1, 2),
    "read-media": (cmd_read_media, 1, 2),
    "transcribe-audio": (cmd_transcribe_audio, 1, 2),
    "send-contact": (cmd_send_contact, 3, 3),
    "send-location": (cmd_send_location, 3, 5),
    "send-menu": (cmd_send_menu, 2, 2),
    # Acoes
    "markread": (cmd_markread, 1, 1),
    "markread-all": (cmd_markread_all, 0, 1),
    "triagem": (cmd_triagem, 0, 3),
    "lid-bootstrap": (cmd_lid_bootstrap, 0, 2),
    "lid-stats": (cmd_lid_stats, 0, 0),
    "react": (cmd_react, 3, 3),
    "delete": (cmd_delete, 2, 3),
    "edit": (cmd_edit, 3, 99),
    "typing": (cmd_typing, 1, 2),
    # Chat
    "pin": (cmd_pin, 1, 1),
    "archive": (cmd_archive, 1, 1),
    "mute": (cmd_mute, 1, 2),
    "labels": (cmd_labels, 1, 3),
    "block": (cmd_block, 1, 1),
    "unblock": (cmd_unblock, 1, 1),
    # CRM/Leads
    "lead-info": (cmd_lead_info, 1, 1),
    "lead-update": (cmd_lead_update, 2, 2),
    "lead-tag": (cmd_lead_tag, 3, 3),
    "lead-assign": (cmd_lead_assign, 2, 2),
    "lead-ticket": (cmd_lead_ticket, 2, 2),
    "lead-status": (cmd_lead_status, 2, 2),
    # Grupos
    "groups": (cmd_groups, 0, 1),
    "group-info": (cmd_group_info, 1, 1),
    "group-recap": (cmd_group_recap, 1, 2),
    "group-create": (cmd_group_create, 2, 99),
    "group-participants": (cmd_group_participants, 3, 99),
    "group-update": (cmd_group_update, 3, 3),
    "group-invite": (cmd_group_invite, 1, 1),
    "group-admin-only": (cmd_group_admin_only, 2, 2),
    # Contatos
    "contacts": (cmd_contacts, 0, 2),
    "contact-add": (cmd_contact_add, 2, 2),
    "contact-remove": (cmd_contact_remove, 1, 1),
    # Raw
    "raw": (cmd_raw, 2, 3),
    # Help
    "help": (cmd_help, 0, 0),
    "--help": (cmd_help, 0, 0),
    "-h": (cmd_help, 0, 0),
}


def main():
    global JSON_MODE

    args = sys.argv[1:]

    # Parse --json flag
    if args and args[0] == "--json":
        JSON_MODE = True
        args = args[1:]

    if not args:
        cmd_help()
        return

    command = args[0]
    cmd_args = args[1:]

    if command not in COMMANDS:
        print(f"Comando desconhecido: {command}", file=sys.stderr)
        if not JSON_MODE:
            print()
            cmd_help()
        else:
            output({"error": True, "message": f"Comando desconhecido: {command}"})
        sys.exit(1)

    func, min_args, max_args = COMMANDS[command]

    if len(cmd_args) < min_args:
        msg = f"'{command}' precisa de pelo menos {min_args} argumento(s)"
        if JSON_MODE:
            output({"error": True, "message": msg})
        else:
            print(msg, file=sys.stderr)
        sys.exit(1)

    if max_args < 99 and len(cmd_args) > max_args:
        cmd_args = cmd_args[:max_args]

    func(*cmd_args)


if __name__ == "__main__":
    main()
