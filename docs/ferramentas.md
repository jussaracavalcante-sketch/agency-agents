# Ferramentas por Agente

## 1. Princípios

1. **Leitura é liberada; escrita é exceção.** Só o Coordenador de Publicação tem ferramenta de
   escrita, desabilitada por padrão (`CREW_ENABLE_WRITE_TOOLS=false`) e condicionada a G3.
2. **Toda ferramenta declara quando está estimando.** Sem chave de API, as ferramentas
   customizadas devolvem texto marcado `[ESTIMATIVA]`/`[SEM INTEGRAÇÃO]` para que o agente
   marque `[VALIDAR]`.
3. **Menos é mais.** Cada agente recebe só as ferramentas de que precisa; reduz custo e erro.

## 2. Matriz agente × ferramenta

| Agente | SerperDev (web) | Scrape | FileRead | SEO (Semrush) | CRM (leitura) | Ads (leitura) | Analytics (CSV) | Publish (escrita) |
|--------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 01 Gerente | | | | | | | | |
| 02 Estrategista | ✅ | | ✅ | | | | | |
| 03 Pesquisador | ✅ | ✅ | ✅ | ✅ | | | | |
| 04 SEO | ✅ | ✅ | ✅ | ✅ | | | | |
| 05 Redator | ✅ | | ✅ | | | | | |
| 06 Social | ✅ | | ✅ | | | | | |
| 07 E-mail/CRM | | | ✅ | | ✅ | | | |
| 08 Mídia Paga | ✅ | | ✅ | | | ✅ | | |
| 09 Arte | | | ✅ | | | | | |
| 10 Analista | | | ✅ | | | | ✅ | |
| 11 Guardião | ✅ | | ✅ | | | | | |
| 12 Publicação | | | ✅ | | | | | ✅ (pós-G3) |

## 3. Ferramentas nativas (`crewai-tools`)

| Ferramenta | Uso | Requisito |
|------------|-----|-----------|
| `SerperDevTool` | Pesquisa web (Google) | `SERPER_API_KEY` |
| `ScrapeWebsiteTool` | Ler páginas (concorrentes, site do cliente) | — |
| `FileReadTool` | Ler brand book, briefing, artefatos anteriores | — |
| `CodeInterpreterTool` (opcional) | Cálculos do Analista sobre CSV | Docker |
| `DallETool` (opcional) | Geração de imagem pelo Diretor de Arte | `OPENAI_API_KEY` |

## 4. Ferramentas customizadas (`src/marketing_ops/tools/`)

| Classe | Nome exposto | Contrato | Integração-alvo (F4) |
|--------|--------------|----------|----------------------|
| `BrandBookTool` | `brand_book_lookup` | `cliente, secao? → guia de identidade visual do cliente (knowledge/<slug>/*.md)` | Google Drive (guias extraídos; atualização manual ou por script) |
| `SeoKeywordTool` | `seo_keyword_research` | `termo, pais → volume, dificuldade, intenção` | Semrush API (`phrase_this`, `phrase_related`) |
| `CrmReadTool` | `crm_read` | `consulta → segmentos, fluxos, métricas agregadas` | RD Station / HubSpot API (somente GET) |
| `PaidMediaReadTool` | `paid_media_read` | `plataforma, consulta → benchmarks, histórico, termos de busca` | Google Ads (GAQL), Meta Marketing API |
| `AnalyticsReadTool` | `analytics_read` | `caminho, linhas → prévia do CSV/JSON` | GA4 Data API, exportações |
| `PublishTool` | `publish_or_schedule` | `canal, peca_id, agendar_para, aprovacao_g3 → log` | CMS, agendador social, Ads (POST) |

### Regras de implementação (F4)

- Credenciais apenas via variáveis de ambiente; nunca em código ou prompt.
- Respostas normalizadas em JSON com campo `fonte` e `coletado_em`.
- Ferramentas de escrita registram cada chamada em `output/crew_log.json` e exigem
  `aprovacao_g3` não vazio.
- Retentativas com backoff; falha devolve `[ERRO]` legível em vez de exceção.

## 5. Conectores MCP (alternativa)

Se o ambiente oferecer servidores MCP (Semrush, Google Ads, Notion, Gmail), eles podem
substituir as ferramentas customizadas via o adaptador MCP do CrewAI (`crewai-tools[mcp]`).
Mantenha a mesma política: leitura liberada, escrita só pós-G3.
