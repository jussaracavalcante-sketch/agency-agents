# Aviso de Privacidade: Portal de Aprovação e Equipe de Operação de Marketing

**Versão:** 0.1 (minuta para validação do jurídico e do encarregado)
**Vigência:** a partir da liberação do piloto
**Público:** colaboradores da Vanguarda Martech que usam o portal (revisores, aprovadores e administradores)

> **Como ler esta minuta.** Os campos entre colchetes e marcados com **[PREENCHER]** dependem de dados da empresa. Os campos marcados com **[CONFIRMAR]** dependem de verificação com o fornecedor. Os prazos e as bases legais são propostas técnicas e precisam da validação do jurídico antes da publicação.

## 1. Quem somos e quem responde pelos seus dados

A **[RAZÃO SOCIAL] [PREENCHER]**, CNPJ **[PREENCHER]**, com sede em **[ENDEREÇO] [PREENCHER]**, é a controladora dos dados pessoais descritos neste aviso.

**Encarregado pelo tratamento de dados pessoais:** **[NOME] [PREENCHER]**
**Canal do titular:** **[E-MAIL DO ENCARREGADO] [PREENCHER]**

## 2. O que é o portal e por que ele existe

O portal de aprovação é a ferramenta em que a equipe acompanha as campanhas produzidas pela Equipe de Operação de Marketing, um conjunto de agentes de inteligência artificial. A produção passa por três portões de decisão humana (G1, G2 e G3). Cada portão é decidido por uma pessoa designada. **Nenhuma peça é publicada pelo sistema.**

## 3. Quais dados pessoais tratamos

| Dado | De onde vem | Para que usamos |
|---|---|---|
| Nome, e-mail corporativo, cargo | Cadastro de convite feito pela administração | Identificar você e liberar o acesso |
| Papel e portões sob sua responsabilidade | Definidos pela administração | Controlar o que você pode ver e decidir |
| Identificador da sessão, data e hora de cada ação | Gerados pelo portal | Registrar quem fez o quê, para segurança e responsabilização |
| Suas decisões (aprovar, devolver, reprovar) e o texto de feedback que você escrever | Digitados por você | Registrar a decisão e repassar o feedback aos agentes |
| Alterações que você fizer em configurações, base de conhecimento e ajustes dos agentes | Digitadas por você | Manter o histórico do que mudou |
| Dados técnicos de acesso, como endereço IP e navegador | Registrados pelos provedores de autenticação e hospedagem **[CONFIRMAR]** | Segurança e prevenção a fraude |

**Não tratamos** dados sensíveis seus (saúde, biometria, filiação, convicções). Se você escrever um dado desse tipo num campo de texto, ele será gravado como qualquer outro texto. Por isso, **não escreva dados pessoais no portal** além do necessário. O termo de conduta traz as regras.

## 4. Para que finalidades e com qual base legal

| Finalidade | Base legal proposta (LGPD, art. 7º) **[VALIDAR COM O JURÍDICO]** |
|---|---|
| Dar acesso ao portal e controlar permissões | Execução do contrato de trabalho ou de prestação de serviços (inciso V) |
| Registrar decisões e ações (trilha de auditoria) | Legítimo interesse da empresa em responsabilização e segurança (inciso IX); cumprimento de obrigação legal ou regulatória, quando houver (inciso II) |
| Proteger o sistema contra acesso indevido e fraude | Legítimo interesse (inciso IX) |
| Apurar incidentes de segurança | Legítimo interesse (inciso IX) |

Não usamos seus dados para marketing, perfilamento comercial nem decisões automatizadas sobre você. A avaliação de desempenho individual **não** é finalidade do portal. Os registros existem para segurança e responsabilização das decisões.

## 5. Com quem compartilhamos

O tratamento envolve prestadores que operam a infraestrutura em nosso nome:

| Prestador | Função | Local do armazenamento |
|---|---|---|
| Supabase | Banco de dados, autenticação e atualização em tempo real | São Paulo, Brasil |
| Vercel | Hospedagem do portal | **[CONFIRMAR região das funções]** |
| CrewAI AMP | Execução dos agentes de IA. Recebe o texto das campanhas, não o seu cadastro | **[CONFIRMAR]** |
| Provedor do modelo de linguagem | Geração de texto pelos agentes. Recebe o texto das campanhas, não o seu cadastro | **[CONFIRMAR]** |

Seus dados de cadastro e as suas ações ficam no banco de dados. O texto das campanhas segue para a plataforma de agentes. Se algum prestador tratar dados fora do Brasil, a transferência seguirá os mecanismos dos arts. 33 a 36 da LGPD **[CONFIRMAR mecanismo adotado]**.

Também podemos compartilhar dados quando houver ordem judicial, exigência de autoridade competente ou necessidade de defesa em processo.

## 6. Por quanto tempo guardamos

Os prazos abaixo são propostas, sujeitas à aprovação do encarregado.

| Dado | Prazo proposto |
|---|---|
| Cadastro e perfil de acesso | Enquanto durar o seu vínculo e a necessidade de acesso. Removido após o desligamento do acesso, salvo obrigação de guarda |
| Trilha de auditoria (ações, sessão, data e hora, o que mudou) | 5 anos, somente de acréscimo |
| Decisões e disparos de campanha | 5 anos |
| Texto integral produzido pelos agentes (eventos da plataforma) | 180 dias |

Depois do prazo, os dados são eliminados ou anonimizados, salvo se a lei exigir guarda maior.

## 7. Como protegemos

- Acesso apenas por convite e por e-mail corporativo, com autenticação em dois fatores para administradores e aprovadores **[CONFIRMAR ativação]**.
- Permissões por papel e por portão; cada decisão só é aceita de quem é designado para aquele portão.
- Chaves de serviço guardadas somente no servidor.
- Registro de auditoria que não pode ser alterado nem apagado pelo caminho normal do sistema.
- Cabeçalhos de segurança no portal e bloqueio de dados pessoais no briefing das campanhas.
- Banco de dados no Brasil.

Nenhum sistema é totalmente imune a incidentes. Se houver um incidente com risco relevante aos titulares, a empresa o avaliará e comunicará a ANPD e os titulares nos termos da regulamentação vigente.

## 8. Seus direitos

Nos termos do art. 18 da LGPD, você pode pedir, a qualquer momento:

1. confirmação de que tratamos seus dados;
2. acesso aos dados;
3. correção de dados incompletos, inexatos ou desatualizados;
4. anonimização, bloqueio ou eliminação de dados desnecessários ou tratados em desconformidade;
5. portabilidade, nos termos da regulamentação;
6. informação sobre com quem compartilhamos seus dados;
7. informação sobre a possibilidade de não fornecer consentimento e suas consequências, quando o tratamento se basear nele;
8. revisão de decisões tomadas unicamente de forma automatizada que afetem seus interesses.

Observação: a trilha de auditoria tem finalidade de segurança e responsabilização. Pedidos de eliminação dela serão analisados caso a caso pelo encarregado, porque a eliminação pode comprometer essa finalidade ou uma obrigação legal.

**Como pedir:** escreva para **[E-MAIL DO ENCARREGADO] [PREENCHER]**. Responderemos no prazo previsto na regulamentação **[CONFIRMAR prazo]**. Você também pode peticionar à Autoridade Nacional de Proteção de Dados (ANPD).

## 9. Inteligência artificial neste processo

Os agentes de IA produzem **rascunhos**. Eles podem errar. Toda peça passa por revisão humana antes de ser usada, e o sistema não publica nada. A decisão sobre aprovar, devolver ou reprovar é sempre de uma pessoa. A IA não toma nenhuma decisão a seu respeito.

## 10. Alterações deste aviso

Podemos atualizar este aviso. A versão vigente fica disponível no portal, com a data da última alteração.

**Última atualização:** **[DATA] [PREENCHER]**
