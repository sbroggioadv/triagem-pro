# Apresentação — Triagem Pro

Material auxiliar de venda e onboarding do **Triagem Pro**.

Mesmo padrão estrutural do `apresentacao/` do Plugin IA Combativa-Adv-OS (paleta IA Combativa, fonts Bebas Neue/Inter/JetBrains Mono).

---

## Conteúdo

### 1. Quick-Start de instalação

- **`quick-start.md`** (1 página A4 portrait)
- Audiência: comprador novo fazendo a primeira instalação
- Conteúdo: 3 passos numerados (marketplace → install → `/configurar`) + URL canônica
- Use: anexar no e-mail de boas-vindas da Kirvano

### 2. Termo de Uso e Política de Privacidade (LGPD)

- **`termo-de-uso-e-privacidade.md`** (template — placeholders em ALL CAPS pra preencher)
- Audiência: compradores do plugin + proteção jurídica do titular
- Conteúdo: definições, aceitação, licença, responsabilidades do usuário (OAB, sigilo, validação),
  limitação de responsabilidade, política LGPD, direitos do titular dos dados, foro
- **⚠ Documento template** — contém placeholders que devem ser preenchidos antes da publicação
- Use: anexar no rodapé da página de venda Kirvano + linkar no MANUAL.pdf

### 3. Manual completo do produto

- **Localização:** `~/Dev/Manual-Triagem-Pro/build/manual.pdf` (após `python3 build.py`)
- **Cópia final:** `~/Desktop/Triagem-Pro-MANUAL.pdf` (1.0 MB)
- **Audiência:** comprador final do produto
- **Conteúdo:** 24 capítulos cobrindo o produto inteiro (instalação, setup `/configurar`, uso diário, guardrail OAB, segurança/LGPD, FAQ, cheat-sheet, licença)
- **Distribuição:** dentro do ZIP entregue pela Kirvano (`Kirvano-Triagem-Pro-PACOTE-FINAL.zip`)

### 4. Capa quadrada Kirvano

- **Localização:** `~/Desktop/Kirvano-Triagem-Pro-QUADRADA.png` (90 KB) e `.jpg` (74 KB)
- **Dimensão:** 1000×1000 px
- **Uso:** imagem do produto na Kirvano + bônus pro comprador reutilizar

---

## Pacote final pra Kirvano

```
~/Desktop/Kirvano-Triagem-Pro-PACOTE-FINAL.zip  (706 KB)
├── Triagem-Pro-MANUAL.pdf  (1.0 MB original, compactado 40%)
└── 0-CAPA-QUADRADA.png     (90 KB)
```

**Upload na Kirvano:**

| Campo | Valor |
|---|---|
| Nome do produto | `Triagem Pro — Plugin Claude` |
| Imagem do produto | `~/Desktop/Kirvano-Triagem-Pro-QUADRADA.png` |
| Descrição curta | "Agente de triagem de WhatsApp para escritórios de advocacia. Plugin Claude Code + Cowork com triagem por urgência, redator com voz própria da advogada, guardrail OAB (5 travas), 4 comandos de supervisão e wizard de instalação 100% pelo chat." |
| Descrição longa | Copiar do README do `triagem-pro` (raiz deste repo) |
| Categoria | Produtos digitais / Software / IA |
| Tipo de entrega | Download automático após pagamento |
| Entregável | `~/Desktop/Kirvano-Triagem-Pro-PACOTE-FINAL.zip` |
| E-mail pós-compra | Anexar `quick-start.md` desta pasta + link de suporte |

---

## URLs canônicas

| | |
|---|---|
| Marketplace (instalação) | https://github.com/sbroggioadv/triagem-pro-marketplace |
| Plugin source | https://github.com/sbroggioadv/triagem-pro |
| Releases | https://github.com/sbroggioadv/triagem-pro/releases |
| Issues / suporte | https://github.com/sbroggioadv/triagem-pro/issues |
| Página de venda Kirvano | (preencher após criar o produto na Kirvano) |

---

## Identidade visual

Paleta IA Combativa oficial (mesma do ecossistema Bravy):

| Cor | Hex | Uso |
|---|---|---|
| Kinetic Lime | `#CCFF00` | Accent principal |
| Obsidian Black | `#101010` | Fundo premium |
| Cool Gray | `#D6D6D6` | Texto secundário |
| Nearly White | `#F4F4F4` | Texto principal |

Fonts: Bebas Neue (display), Inter (body), JetBrains Mono (mono).
