# Regra de rollback do piloto

**Regra (definida pela responsável do projeto):** se o piloto retornar ao erro duas vezes, volta-se à primeira
implementação que funcionou de ponta a ponta.

## Baseline
- Commit: `8fa07e3` ("Fix model auto-selection block placement"), na branch `claude/lucid-goodall-6gcsed`.
- Build na plataforma: `46ea4a3` (hash do `git subtree split` desse commit).
- Evidência: execução do piloto Construtora Colmeia, 18/18 tarefas, estado SUCCESS (2026-10-01).
- O que esse baseline NÃO tem: portões humanos reais (HITL), base de conhecimento de clientes, divisão dos portões
  em pedido + aplicação, guardrails, memória desligada, carga automática do cliente. Voltar a ele perde esses ganhos.

## Contagem
- Conta como erro: execução de piloto que termina com estado FAILED, ou que a plataforma aborta/descarta, no build
  atual. Não conta: parecer reprovado, qualidade fraca de conteúdo, pausa em portão humano.
- Duas ocorrências seguidas no mesmo build acionam o rollback. O contador zera após uma execução que conclui.

## Procedimento
1. `git subtree split --prefix=integrations/crewai/marketing-operations 8fa07e3` (resulta em `46ea4a3`).
2. Enviar esse hash por force push para a branch `crewai-marketing-ops`.
3. Responsável faz o redeploy; confirmar que o Build ID mostra `46ea4a3`.
4. Disparar o piloto com o payload sem portões humanos (`CREW_HUMAN_GATES` desligado).
5. Registrar o motivo do rollback e o erro observado antes de tentar de novo a versão nova.
