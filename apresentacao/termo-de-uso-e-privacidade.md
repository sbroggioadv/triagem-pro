# Termo de Uso e Política de Privacidade — Triagem Pro

> **⚠ DOCUMENTO TEMPLATE.** Antes de publicar, substitua os placeholders em MAIÚSCULA pelos valores reais. Recomenda-se revisão por advogado especialista em LGPD/direito digital antes da publicação definitiva.

**Última atualização:** [DATA DA PUBLICAÇÃO]
**Titular do produto:** [NOME COMPLETO DO TITULAR / RAZÃO SOCIAL]
**OAB:** [OAB/UF Nº]
**Cidade/UF:** [CIDADE/UF]
**Foro:** [CIDADE/UF DO FORO]
**Contato:** [E-MAIL DE CONTATO]
**DPO (Encarregado LGPD):** [NOME E E-MAIL DO DPO]

---

## 1. Definições

- **Software:** Plugin **Triagem Pro** (v0.2.0 ou superior) e documentação que o acompanha, distribuído via marketplace público GitHub.
- **Licenciado:** pessoa física advogada/advogado inscrito na OAB ou pessoa jurídica sociedade de advocacia que adquiriu o licenciamento do Software via Kirvano.
- **Titular dos dados:** pessoas naturais cujos dados pessoais são processados pelo Software durante o uso (clientes do escritório do Licenciado, parceiros, equipe).
- **Plataforma host:** Claude Code, Claude Cowork ou qualquer outro ambiente de execução de plugins Anthropic.

---

## 2. Aceitação

O uso do Software implica aceitação plena e irrestrita destes termos. Se você não concorda com os termos, não utilize o Software e solicite estorno na plataforma de compra dentro do prazo previsto.

---

## 3. Licença

O Software é distribuído sob licença comercial proprietária. O Licenciado obtém o direito de:

- Instalar e usar o Software em sua própria infraestrutura (máquina/sessão Cowork)
- Adaptar a configuração local (`compliance.local.md`, `config.json`) sem restrição
- Receber atualizações via marketplace pelo período de licenciamento

**Não é permitido:**

- Redistribuir, sublicenciar ou revender o Software sem autorização escrita do Titular
- Realizar engenharia reversa de qualquer componente proprietário
- Remover ou ocultar avisos de copyright, autoria ou licenciamento

---

## 4. Responsabilidades do Licenciado

Ao usar o Software, o Licenciado é integralmente responsável por:

### 4.1 Conformidade ética (OAB)

- Cumprir o Estatuto da OAB (Lei 8.906/94), o Código de Ética e Disciplina e demais provimentos
- Validar manualmente cada mensagem antes de enviá-la, mesmo após aprovação do agente
- Adaptar o `compliance.md` (via `compliance.local.md`) às particularidades da sua seccional da OAB
- **Não confiar exclusivamente** no guardrail automático — ele é salvaguarda, não substituto do juízo profissional

### 4.2 Sigilo profissional (art. 7º, II, EAOAB)

- Manter o ambiente onde o Software roda em condições adequadas de segurança
- Não compartilhar tokens de acesso (Zappfy, etc.) com terceiros não autorizados
- Decidir conscientemente onde gravar arquivos do Software (recomendamos pasta local, não sincronizada)
- Comunicar à OAB qualquer incidente de violação de sigilo conforme normas vigentes

### 4.3 LGPD (Lei 13.709/18)

- Atuar como **Controlador** dos dados pessoais dos seus clientes processados pelo Software
- Garantir base legal adequada para cada tratamento (consentimento, execução de contrato, etc.)
- Atender aos direitos dos titulares dos dados conforme art. 18 da LGPD
- Designar Encarregado de Proteção de Dados (DPO) quando exigido
- Adotar medidas técnicas e administrativas de segurança proporcionais ao risco

### 4.4 Veracidade das mensagens

- Toda mensagem enviada pelo WhatsApp através do Software é de responsabilidade exclusiva do Licenciado
- O Software apenas auxilia na redação; o envio final depende de aprovação explícita do Licenciado
- O Titular do Software não responde por danos decorrentes do conteúdo das mensagens enviadas

---

## 5. Operação técnica e privacidade

### 5.1 Arquitetura de dados

O Software opera **inteiramente na infraestrutura do Licenciado**:

- Conversas, contatos, mídia, voz da advogada, token Zappfy e configurações ficam armazenados na máquina ou sessão Cowork do Licenciado
- **Nenhum dado é transmitido aos servidores do Titular do Software**
- A única comunicação externa é entre o Licenciado e a API Zappfy (provedor parceiro do WhatsApp), usando o token do próprio Licenciado
- O Software não realiza telemetria, analytics ou tracking

### 5.2 Garantias técnicas (v0.2.0+)

- Agente proibido por design de inferir dados pessoais do contexto da plataforma host
- Agente proibido por design de gravar em pastas sincronizadas (iCloud, Dropbox, Drive, OneDrive) sem confirmação explícita do Licenciado
- Agente proibido por design de enviar mensagens sem aprovação explícita do Licenciado
- Agente proibido por design de executar comandos embutidos em conteúdo de mensagens triadas (defesa contra prompt-injection)

### 5.3 Compartilhamento de dados

O Titular do Software **não recebe, não armazena, não compartilha** dados pessoais dos clientes do Licenciado nem dados operacionais do Licenciado.

A Zappfy é provedora terceira do Licenciado — relacionamento contratual entre Licenciado e Zappfy é independente deste termo. Consulte a política de privacidade da Zappfy diretamente.

---

## 6. Limitação de responsabilidade

O Software é fornecido **"NO ESTADO EM QUE SE ENCONTRA"**, sem garantia de adequação a qualquer finalidade específica.

Em nenhum caso o Titular do Software será responsável por:

- Decisões processuais, estratégicas ou de negócio do Licenciado baseadas em outputs do Software
- Violações éticas, civis ou disciplinares perante a OAB decorrentes de mensagens enviadas pelo Licenciado
- Danos diretos, indiretos, incidentais ou consequenciais do uso do Software
- Indisponibilidade temporária ou definitiva de serviços terceiros (Anthropic Claude, Zappfy, WhatsApp)
- Perda de dados decorrente de falha em adotar medidas de backup adequadas

A responsabilidade total do Titular do Software, em qualquer hipótese, limita-se ao valor efetivamente pago pelo Licenciado pela aquisição do Software.

---

## 7. Política de Privacidade (LGPD)

### 7.1 Posicionamento

Para os dados processados **pelo Software dentro da infraestrutura do Licenciado**, o **Licenciado é o Controlador**. O Titular do Software não é Operador nem Controlador desses dados.

Para os dados de cadastro do **comprador na Kirvano**, aplica-se a política de privacidade da Kirvano + qualquer formulário adicional preenchido pelo comprador no momento da compra.

### 7.2 Direitos do titular dos dados

Pessoas físicas cujos dados sejam processados pelo Software (clientes, parceiros, equipe do Licenciado) podem exercer direitos do art. 18 da LGPD diretamente perante o Licenciado, que é o Controlador.

### 7.3 Encarregado

DPO designado pelo Titular do Software: **[NOME COMPLETO]**, e-mail: **[DPO@EMAIL.COM]**.

DPO do Licenciado deve ser informado nos termos do art. 41 da LGPD pelo próprio Licenciado, conforme exigência aplicável.

---

## 8. Vigência e rescisão

Este termo vigora pelo período de licenciamento adquirido na Kirvano.

O Titular do Software pode rescindir unilateralmente o licenciamento em caso de:

- Uso indevido do Software (redistribuição, engenharia reversa, violação de copyright)
- Violação grave dos termos por parte do Licenciado
- Decisão judicial ou administrativa que assim determine

O Licenciado pode rescindir a qualquer momento desinstalando o Software, sem direito a estorno após o prazo legal de arrependimento (7 dias da compra, conforme CDC).

---

## 9. Foro

Fica eleito o foro da comarca de **[CIDADE/UF DO FORO]** para dirimir quaisquer controvérsias decorrentes deste termo, com renúncia expressa a qualquer outro, por mais privilegiado que seja.

---

## 10. Alterações destes termos

O Titular pode modificar estes termos a qualquer tempo, publicando a versão atualizada no repositório oficial do Software. Atualizações materiais serão comunicadas aos Licenciados pelo canal de contato registrado na compra.

---

**Triagem Pro v0.2.0**
Copyright © 2026 [NOME COMPLETO DO TITULAR]. Todos os direitos reservados.

**Repositório oficial:** https://github.com/sbroggioadv/triagem-pro
**Marketplace:** https://github.com/sbroggioadv/triagem-pro-marketplace
**Issues / suporte:** https://github.com/sbroggioadv/triagem-pro/issues
