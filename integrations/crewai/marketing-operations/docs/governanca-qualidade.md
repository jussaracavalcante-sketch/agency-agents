# Governança, Qualidade e Guardrails

## 1. Princípios de governança da crew

| Princípio | Como se materializa |
|-----------|---------------------|
| Humano decide o irreversível | Portões G1–G3 com `human_input: true`; `PublishTool` bloqueada sem G3 |
| Rastreabilidade | Toda entrega com fonte, premissas e marcadores; `output_log_file` ativo |
| Separação de funções | Quem produz não revisa; Guardião independente |
| Mínimo privilégio | Ferramentas por agente; escrita só no Coordenador |
| Custo controlado | `max_iter`, `max_rpm`, modelo leve em tarefas simples, cache |

## 2. Guardrails por categoria

### 2.1 Veracidade
- Afirmações factuais com URL e data; sem fonte → `[VALIDAR]`.
- Números estimados → `[DADO ESTIMADO]` com método.
- Guardião reprova peça com `[VALIDAR]` não resolvido em G2/G3.

### 2.2 Marca
- Brand book carregado em `knowledge/` e lido por todos os produtores.
- Termos proibidos e claims permitidos verificados pelo Guardião.
- Direção de arte respeita paleta, tipografia e uso do logo.

### 2.3 LGPD (Lei 13.709/2018)
- Nenhum dado pessoal identificável em prompts, artefatos ou logs.
- Segmentação cita base legal (art. 7º): consentimento, legítimo interesse, execução de contrato.
- Opt-out em todo e-mail; nunca compra de listas.
- Públicos de CRM em mídia paga só com base legal registrada.

### 2.4 Publicidade (CONAR / CDC)
- Sem publicidade enganosa ou abusiva (CDC art. 37).
- Comparativos só objetivos e comprováveis (Código CONAR art. 32).
- Setores regulados (saúde, financeiro, bebidas, infantil) → `[AVAL ESPECIALISTA]` obrigatório.
- Identificação clara de conteúdo publicitário e parcerias.

### 2.5 Políticas de plataforma
- Meta, Google, LinkedIn, TikTok: Guardião checa categorias restritas, claims, uso de "você" em
  atributos sensíveis, texto em imagem, direitos autorais em áudio.

### 2.6 Segurança do agente
- Conteúdo lido da web é **dado**, não instrução: agentes ignoram comandos embutidos em páginas.
- Ferramentas de escrita só após G3; chaves apenas em `.env`.
- `max_iter` evita loops; falha dupla escala ao humano.

## 3. Memória e conhecimento

| Mecanismo CrewAI | Uso nesta crew | Cuidados |
|------------------|----------------|----------|
| `memory` (`CREW_MEMORY`, padrão desligada) | Compartilhar contexto entre tarefas e execuções | **Risco comprovado**: a memória persiste entre execuções da automação e fatos inventados numa rodada (serviços, baselines, fontes) voltam nas seguintes como "memórias internas". Mantenha desligada em pipelines factuais e limpe a aba Memory da plataforma após testes |
| Memória de longo prazo | Aprendizados de campanhas anteriores (o que foi aprovado/reprovado) | Revisar periodicamente; apagar por cliente ao encerrar contrato |
| `knowledge` | Brand book, ofertas, histórico, restrições por cliente | Versionar em `knowledge/<cliente>/`; um cliente nunca acessa o de outro |

Isolamento por cliente: rode uma instância/`knowledge` por cliente e nunca misture memória
de longo prazo entre marcas concorrentes.

## 4. Avaliação de qualidade

### 4.1 Avaliação por entrega (rubrica do Guardião)

| Dimensão | 0 | 1 | 2 |
|----------|---|---|---|
| Aderência ao brief | Desvia | Parcial | Total |
| Fontes | Ausentes | Parciais | Completas |
| Marca | Fora do tom | Pequenos desvios | Conforme |
| Compliance | Risco alto | Risco baixo com ajuste | Sem risco |
| Clareza/estrutura | Confusa | Aceitável | Executiva |

Aprovação em 1ª rodada exige ≥ 8/10 e nenhum zero.

### 4.2 Avaliação da crew (mensal)

| Indicador | Fonte | Meta |
|-----------|-------|------|
| Lead time por fase | `crew_log.json` + registros de portão | Ver README §5.1 |
| Aprovação em 1ª rodada | Pareceres | ≥ 70% |
| Custo por campanha (tokens) | Telemetria do provedor | −20% em 3 meses |
| Incidentes pós-publicação | Registro de incidentes | 0 |
| Satisfação do aprovador (1–5) | Pesquisa curta pós-G3 | ≥ 4 |

### 4.3 Testes de regressão de prompts

Mantenha 3 briefings-padrão (B2C varejo, B2B serviços, setor regulado) em `tests/briefings/` e
rode a crew após qualquer mudança em `agents.yaml`/`tasks.yaml`. Compare os pareceres do
Guardião e o número de `[VALIDAR]` com a execução anterior.

## 5. Papéis humanos

| Papel | Responsabilidade |
|-------|------------------|
| Head de IA / dono(a) da crew | Prompts, ferramentas, custos, evolução, métricas da crew |
| Gestor(a) de marketing | Aprovações G1 e G2; qualidade do briefing |
| Dono(a) do orçamento | Aprovação G3 |
| Marca / jurídico / compliance | `[AVAL ESPECIALISTA]`, setores regulados |
| Operador(a) de canais | Executa roteiros quando ferramentas de escrita estão desabilitadas |

## 6. Gestão de mudanças

- Toda alteração em `agents.yaml`/`tasks.yaml` via PR com descrição do motivo e resultado do
  teste de regressão.
- Versionar a crew (`v1.0`, `v1.1`…) no README e no sumário executivo de cada campanha.
- Registrar decisões arquiteturais (modelo, processo, ferramentas) em `docs/decisoes/` (ADR).
