# Instalar o Triagem Pro

Você não precisa ser desenvolvedora. Vou guiar você passo a passo. Reserve 15 minutos.

## O que você vai precisar

- Computador com **Mac** ou **Windows**
- Seu **celular** (para conectar o WhatsApp)
- Conta gratuita em **Zappfy** (cria na hora — link no Passo 2)
- **Claude Code** instalado (veja Passo 1)

---

## Passo 1 — Instalar o Claude Code

O Claude Code é o "motor" onde o Triagem Pro roda. É gratuito pra começar.

1. Acesse **[claude.com/claude-code](https://claude.com/claude-code)** e clique em **Get started**
2. Faça login com sua conta Anthropic (ou crie uma)
3. Siga a instalação do app pra seu sistema (Mac ou Windows)
4. Abra o Claude Code uma vez pra confirmar que funciona

Pronto. Não precisa configurar mais nada aqui — o resto é dentro do próprio Claude.

---

## Passo 2 — Instalar o Triagem Pro

Dentro do Claude Code, digite (copiando exatamente):

```
/plugin install triagem-pro
```

Aperte Enter. Aguarde a instalação confirmar.

> Se a sua instalação for por download direto (sem marketplace), você vai ter recebido um link pra clonar este repositório. Nesse caso, siga as instruções que você recebeu junto com o link.

---

## Passo 3 — Conectar seu WhatsApp

Dentro do Claude Code, digite:

```
/configurar
```

O Triagem Pro vai te guiar conversando, **uma pergunta por vez**. Ele vai:

1. **Verificar Python** no seu computador (instala se faltar; ele te ensina como).
2. **Pedir o token da Zappfy** — você vai abrir [dash.zappfy.io](https://dash.zappfy.io), criar conta gratuita, criar uma instância, escanear o QR Code com seu WhatsApp, e copiar o token. Ele cola pra você.
3. **Configurar seu escritório** — nome, sua identificação no WhatsApp, equipe (se tiver), grupos internos a ignorar, palavras de urgência, horários de atraso.
4. **Aprender sua voz** — vai ler suas últimas mensagens enviadas (privadamente, na sua máquina) e gerar um perfil do seu estilo de escrita. Te mostra um resumo pra você confirmar.
5. **Primeira triagem demonstrativa** — pra você ver funcionando.

Em 10 minutos, tá tudo configurado.

---

## Passo 4 — Usar no dia a dia

A partir de agora, sempre que quiser verificar seu WhatsApp, é só dizer dentro do Claude Code:

| O que você diz | O que acontece |
|----------------|----------------|
| `verifica meu zap` | Tabela com pendências classificadas por urgência |
| `redige uma resposta pro [cliente]` | Triagem invoca o redator → você vê 1–3 opções → aprova qual sai |
| `manda a 1` (após ver opções) | Envia a opção 1 pela Zappfy |
| `/sem-resposta` | Quem está aguardando sua resposta há mais tempo |
| `/tempo-resposta` | Seu KPI de tempo médio de resposta |
| `/resumo-dia` | Resumo das últimas 24h |
| `/grupos-inativos` | Grupos de cliente sem atividade |
| `/aprender-voz` | Re-aprende seu estilo (re-rode periodicamente) |

---

## O que NÃO acontece (segurança)

- ❌ Nenhuma mensagem é enviada sem sua aprovação explícita
- ❌ Nenhum dado seu sai da sua máquina pra servidor nosso
- ❌ Nenhuma telemetria, nenhum analytics, nenhum tracking
- ❌ O redator não pode enviar mensagem — só você manda. Trava arquitetural.

## Atualizar o guardrail OAB pro seu escritório

O Triagem Pro vem com 5 travas éticas padrão (`compliance.md`). Se quiser ajustar pra realidade do seu escritório (ex.: liberar 1 emoji específico em mensagem cliente):

1. Crie um arquivo chamado **`compliance.local.md`** dentro de `skills/whatsapp/`
2. Cole o conteúdo do `compliance.md` original e edite à vontade
3. O Triagem Pro automaticamente usa a sua versão local em vez do padrão

Sua versão local **fica só na sua máquina** (coberta pelo `.gitignore`).

---

## Algo deu errado?

| Sintoma | O que fazer |
|---------|-------------|
| `command not found: python3` no Mac | Instale Python em [python.org/downloads](https://python.org/downloads) |
| `command not found: python3` no Windows | Instale Python e **marque o checkbox "Add Python to PATH"** durante a instalação |
| Triagem volta vazia | Não é erro — significa que você está em dia |
| `ZAPPFY_TOKEN nao configurado` | Refaça o `/configurar` ou cole o token correto |
| Outra coisa | Abra issue no repositório com o print do que apareceu no chat |

---

Bem-vinda ao Triagem Pro.
