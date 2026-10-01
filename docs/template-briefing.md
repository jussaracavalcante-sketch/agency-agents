# Template de Briefing — entrada da crew

O briefing é o único insumo obrigatório da crew. Suas chaves viram as variáveis `{…}` de
`config/tasks.yaml` e `config/agents.yaml`. Salve como YAML e rode:

```bash
python -m marketing_ops.main --briefing briefings/<cliente>-<campanha>.yaml
```

## Campos obrigatórios

| Chave | Descrição | Exemplo |
|-------|-----------|---------|
| `briefing_titulo` | Nome da campanha | Lançamento do programa de fidelidade |
| `cliente` | Marca/empresa | Loja Exemplo |
| `segmento` | Setor e recorte | Varejo de moda regional |
| `regiao` | Abrangência geográfica | Manaus e Região Metropolitana |
| `publico_alvo` | Descrição do público | Mulheres 25-45, classes B/C… |
| `objetivo` | Objetivo de negócio, com número e prazo | 2.000 adesões em 8 semanas |
| `orcamento_total` | Teto total (produção + mídia) | R$ 60.000 |
| `orcamento_midia` | Parcela destinada a mídia paga | R$ 35.000 |
| `prazo` | Duração da campanha | 8 semanas |
| `duracao_semanas` | Número (para o calendário) | 8 |
| `plataformas_sociais` | Lista de redes | Instagram, TikTok, Facebook |
| `ferramenta_crm` | CRM/automação em uso | RD Station |
| `ferramenta_analytics` | Analytics/tagging | GA4 + GTM |
| `site_url` | Site ou landing atual (ou "nenhum") | https://… |
| `fuso_horario` | Fuso de publicação (IANA) | America/Manaus |

## Campos recomendados (texto livre, lidos via knowledge/)

Coloque em `knowledge/<cliente>/`:

- `brand_book.md` — tom de voz, vocabulário, termos proibidos, claims permitidos, paleta, tipografia, uso do logo.
- `historico_campanhas.md` — o que já foi feito, resultados, aprendizados.
- `ofertas.md` — produtos/serviços, preços, condições, provas sociais autorizadas.
- `restricoes.md` — regulatórias (setor), jurídicas, concorrentes que não podem ser citados.

## Exemplo completo

```yaml
briefing_titulo: Lançamento do programa de fidelidade
cliente: Loja Exemplo
segmento: Varejo de moda regional
regiao: Manaus e Região Metropolitana
publico_alvo: Mulheres 25-45, classes B/C, compram online e em loja física
objetivo: Gerar 2.000 adesões ao programa em 8 semanas
orcamento_total: R$ 60.000
orcamento_midia: R$ 35.000
prazo: 8 semanas
duracao_semanas: "8"
plataformas_sociais: Instagram, TikTok, Facebook
ferramenta_crm: RD Station
ferramenta_analytics: GA4 + Google Tag Manager
site_url: https://www.exemplo.com.br
fuso_horario: America/Manaus
```

## Critério de completude (validado pelo Gerente)

O gerente devolve o briefing se faltar **objetivo com número**, **público**, **orçamento**,
**prazo** ou **canais**. Sem brand book, a crew roda, mas o Guardião marca risco de tom como
`[VALIDAR]` em todas as peças.
