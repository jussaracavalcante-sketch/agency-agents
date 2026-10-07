# Base de conhecimento ligada à Nekt: VJOB > clientes > setup

## O que está conectado

O módulo de IA do VJOB guarda, por cliente, um **setup** autorado pela casa: bíblia da marca, instruções de comunicação, tom de voz, elementos visuais, fatos verificados, regras inegociáveis, palavras a evitar e observações. A Nekt publica esse setup em `vanguardamartech_trusted.trs_vjob__ia_cliente_config` (uma linha por cliente, chave `id_cliente`).

O portal lê esse setup e o entrega aos agentes junto com o guia de identidade visual. No portal ele aparece em **Conhecimento > cliente** como o documento **Setup de IA no VJOB (Nekt)**, marcado como somente leitura. Quem edita é o VJOB.

| Peça | Onde fica |
|---|---|
| Fonte | Nekt, tabela `trs_vjob__ia_cliente_config` (Trusted, classificação L3 confidencial) |
| Cópia no portal | Supabase, tabela `portal_vjob_setup` (sem acesso do navegador; só o servidor lê) |
| Uso | `contexto_cliente` do disparo, depois do guia de identidade visual |
| Teto de texto | 10.000 caracteres do guia e dos documentos do portal, mais o tamanho inteiro do setup do VJOB, para ele nunca cortar o guia |

## Estado em 07/10/2026

| Cliente no VJOB | Situação | Cliente no portal |
|---|---|---|
| MOVE RENTAL CARS (336) | Setup com 8.976 caracteres, 5 de 7 campos | `move`. **Sincronizado** |
| PRESTEX ENCOMENDAS (136) | Configuração aberta e vazia | `prestex`. Registrado como **vazio**, não entra nos agentes |
| THEREZINHA RUIZ (339) | Setup com 6 de 7 campos | **Não existe no portal.** Cadastrar o cliente em `portal_clientes` para sincronizar |

O VJOB tem 315 clientes cadastrados e só 3 com setup. A adoção é pequena. Não derive indicador dela.

## Como as regras negativas são tratadas

As seções "Regras inegociáveis" e "Evitar" citam termos justamente para proibi-los ("a melhor locadora da Flórida", "garantia total"). O título dessas seções leva a marca `[LISTA NEGATIVA ...]`, e a crew as **retira do texto permitido** (`_sem_secoes_negativas`). Sem isso, a trava de claims leria o termo no contexto e o liberaria.

## Como sincronizar (procedimento repetível)

Não há conexão automática da Nekt com o portal: o portal na Vercel não tem credencial da Nekt. A sincronização é feita pela Head de IA, ou por uma sessão do Claude com acesso às duas ferramentas.

1. **Montar o documento na Nekt**, em uma linha (o conector quebra textos com várias linhas). Troque o `id_cliente` pelo cliente desejado:

```sql
WITH c AS (
  SELECT id_cliente, cliente_nome, atualizado_em, qtd_campos_preenchidos,
    REPLACE(TRIM(IFNULL(biblia_resumo,'')), '\r', '') AS biblia,
    REPLACE(TRIM(IFNULL(instrucoes,'')), '\r', '') AS instr,
    REPLACE(TRIM(IFNULL(tom_voz,'')), '\r', '') AS tom,
    REPLACE(TRIM(IFNULL(elementos_visuais,'')), '\r', '') AS vis,
    REPLACE(TRIM(IFNULL(fatos_verificados,'')), '\r', '') AS fatos,
    REPLACE(TRIM(IFNULL(regras_inegociaveis,'')), '\r', '') AS regras,
    REPLACE(TRIM(IFNULL(palavras_evitar,'')), '\r', '') AS evitar,
    REPLACE(TRIM(IFNULL(observacoes,'')), '\r', '') AS obs
  FROM `vanguardamartech_trusted.trs_vjob__ia_cliente_config`
  WHERE id_cliente = <ID> AND is_ativo AND NOT flag_config_vazia
), m AS (
  SELECT *, CONCAT(
    '# Setup de IA do cliente no VJOB: ', cliente_nome, '\n\n',
    'Fonte: Nekt > VJOB > clientes > setup (trs_vjob__ia_cliente_config). Documento sincronizado, somente leitura no portal: edite no VJOB. ',
    'Se algo aqui conflitar com o Guia de identidade visual, não escolha um dos lados: marque [VALIDAR] e aponte o conflito.\n',
    IF(biblia != '', CONCAT('\n## Bíblia da marca\n\n', biblia, '\n'), ''),
    IF(instr != '', CONCAT('\n## Instruções de comunicação do cliente\n\n', instr, '\n'), ''),
    IF(tom != '', CONCAT('\n## Tom de voz\n\n', tom, '\n'), ''),
    IF(vis != '', CONCAT('\n## Elementos visuais\n\n', vis, '\n'), ''),
    IF(fatos != '', CONCAT('\n## Fatos verificados\n\n', fatos, '\n'), ''),
    IF(regras != '', CONCAT('\n## Regras inegociáveis [LISTA NEGATIVA: não autoriza nenhum termo citado]\n\n', regras, '\n'), ''),
    IF(evitar != '', CONCAT('\n## Evitar [LISTA NEGATIVA: não autoriza nenhum termo citado]\n\n', evitar, '\n'), ''),
    IF(obs != '', CONCAT('\n## Observações\n\n', obs, '\n'), '')
  ) AS md FROM c
)
SELECT id_cliente, cliente_nome, CAST(atualizado_em AS STRING) AS vjob_atualizado_em, qtd_campos_preenchidos,
       LENGTH(md) AS chars, TO_HEX(SHA256(md)) AS sha, TO_JSON_STRING(md) AS md_json
FROM m
```

2. **Conferir dado pessoal** no texto: CPF, telefone e e-mail pessoais, nome de paciente. Se houver, **não sincronize**: peça a limpeza no VJOB. (Em 24/09/2026 a Nekt mediu zero ocorrência, mas o texto é livre e digitado por pessoa.)
3. **Gravar no Supabase** em `portal_vjob_setup`: `cliente_slug`, `id_cliente_vjob`, `nome_vjob`, `status = 'ok'`, `conteudo` (o JSON decodificado com `::jsonb #>> '{}'`), `sha256`, `chars`, `campos_preenchidos`, `vjob_atualizado_em`, com `on conflict (cliente_slug) do update`.
4. **Conferir a cópia:** `encode(sha256(convert_to(conteudo,'UTF8')),'hex')` deve ser igual ao `sha` da Nekt.
5. Setup vazio no VJOB: gravar `status = 'vazio'` e `conteudo` vazio. Ele não vai para os agentes.

## Regras de governança

- **Nunca commitar o conteúdo do setup no repositório.** O repositório é público e o setup é estratégia de cliente (L3 confidencial). O conteúdo vive só no Supabase.
- O setup segue para a plataforma de agentes e para o provedor do modelo de linguagem, como já acontece com o guia de marca. Isso depende da validação dos fornecedores descrita no dossiê de compliance.
- O portal não edita o setup. Para corrigir, altere no VJOB e sincronize de novo.
- Reexecute a sincronização quando o `atualizado_em` do VJOB for maior que o `vjob_atualizado_em` do portal. A tela Conhecimento mostra a data da última sincronização.

## Próximos passos possíveis

- **Sincronização automática:** exige uma credencial da Nekt no servidor do portal ou uma rotina agendada. É decisão da Head de IA, porque envolve segredo.
- **Documentos anexados ao cliente** (`trs_vjob__ia_documento`): hoje 21 documentos, 17 com texto, a maioria transcrita de imagem. A Nekt orienta tratar como transcrição, não como fonte. Ficaram fora desta conexão.
