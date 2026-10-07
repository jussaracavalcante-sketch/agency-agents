# Runner no Render: executar a crew sem o limite de execuções da CrewAI AMP

**Versão:** 1.0 · **Status:** código pronto e testado localmente; falta hospedar, configurar e validar com um piloto real.

## 1. Por que existe

A CrewAI AMP cobra por execução (cada retomada de portão conta uma) e bloqueou o piloto com `Monthly execution limit reached`. O runner roda a **mesma crew**, com as mesmas travas e os mesmos portões G1, G2 e G3, em um serviço próprio, usando a chave da OpenAI institucional. O portal, o banco e os eventos continuam iguais.

## 2. Como funciona

| Passo | O que acontece |
|---|---|
| Disparo | O portal chama `POST /kickoff` do runner. Uma campanha por vez (as travas em código dependem disso) |
| Tarefas | Cada tarefa concluída vai ao mesmo webhook (Supabase) no formato da AMP; o portal as lê como antes |
| Portão | A thread da execução publica o pedido (`human_input`) e **espera a decisão sem gastar tokens**, até 72 h (`RUNNER_ESPERA_MAXIMA_HORAS`) |
| Decisão | O portal chama `POST /resume`. "Aprovado." libera; outro texto reexecuta o portão com o feedback e abre um novo pedido (mesmo comportamento da AMP) |
| Reprovação | O portal chama `POST /cancel` e a execução termina |
| Fim | O evento `crew` é enviado ao webhook |

Testes: `tests/test_runner.py` (5 testes do portão, do cancelamento e da trava de uma campanha por vez) e uma execução de ponta a ponta com o executor real do CrewAI e um modelo simulado (pedido, devolução com reescrita, novo pedido, aprovação). Não foi testado com a OpenAI nem no Render.

## 3. Limitação principal

O estado da execução fica **na memória do processo**. Se o serviço reiniciar (deploy, queda, manutenção do Render) com uma campanha parada num portão, **essa campanha se perde**: o `/resume` responde 404, o portal avisa e o administrador a encerra em Administração. A campanha precisa ser disparada de novo.

Regras de operação:
- **Não faça deploy nem altere variáveis do serviço com campanha aberta num portão** (`autoDeploy` está desligado de propósito).
- O plano precisa ser **Starter ou superior** (sempre ligado). O plano gratuito hiberna e perderia a campanha.
- Evolução possível, se isso incomodar: gravar checkpoints em disco persistente e retomar após reinício.

## 4. Passo a passo (você)

### 4.1 Render
1. No Render: **New > Blueprint** (ou **Web Service > Docker**) apontando para o repositório, branch **`crewai-marketing-ops`** (a raiz dessa branch é a pasta da crew). O `render.yaml` já traz o serviço `marketing-ops-runner`.
2. Região: o `render.yaml` usa `oregon` (EUA). Se a política de dados exigir outra região, troque antes de criar. Mesmo assim, o texto das campanhas vai à OpenAI (ver seção 6).
3. Variáveis de ambiente (os valores secretos só no painel do Render, nunca no chat nem no Git):

| Variável | Valor |
|---|---|
| `OPENAI_API_KEY` | chave institucional da OpenAI |
| `MODEL` / `MODEL_LIGHT` | `openai/gpt-4o` e `openai/gpt-4o-mini` (já no blueprint; troque pelo modelo contratado, se for outro) |
| `RUNNER_TOKEN` | segredo longo e aleatório, **novo** (por exemplo 40 caracteres). O mesmo valor vai no portal |
| `WEBHOOK_BASE` | a mesma URL do webhook que o portal já usa |
| `WEBHOOK_KEY` | a mesma chave que o portal já usa |
| `WEBHOOK_AUTOMACAO` | `runner-render` |

4. Crie o serviço e confirme `GET https://<servico>.onrender.com/health` com `{"ok": true, "ocupado": false}`.
5. Na OpenAI, defina **limite de gasto mensal** e alerta de uso.

### 4.2 Portal (Vercel)
Acrescente as variáveis e faça redeploy:

| Variável | Valor |
|---|---|
| `RUNNER_URL` | `https://<servico>.onrender.com` (sem barra no fim) |
| `RUNNER_TOKEN` | o mesmo valor do Render |
| `EXECUTOR` | `runner` (para ativar). Remova ou use `amp` para voltar à AMP |

### 4.3 Reversão
Trocar `EXECUTOR` para `amp` e fazer redeploy do portal devolve o disparo e as decisões à AMP. Campanhas abertas no runner continuam decididas pelo runner somente enquanto `EXECUTOR=runner`; **não alterne com campanha aberta**.

## 5. Validação (piloto limpo, com a Move)

- [ ] `/health` responde e o disparo retorna um id.
- [ ] G1 chega ao portal em poucos minutos, sem erro.
- [ ] Devolver o G1: o pedido reabre com a reescrita; aprovar segue.
- [ ] G2 e G3 funcionam do mesmo modo; reprovar encerra.
- [ ] Reiniciar o serviço **fora de campanha** não deixa lixo; e o aviso de "execução perdida" aparece se forçar o caso com campanha parada.
- [ ] Comparar a qualidade com o piloto de Claude (as travas foram calibradas com outro modelo; defeitos novos são esperados).

## 6. Privacidade e LGPD

- O texto das campanhas é processado pela OpenAI. Complete no Aviso de Privacidade o provedor do modelo, a região e o mecanismo de transferência (arts. 33 a 36 da LGPD), e o Render como novo prestador de hospedagem. Peça validação do jurídico.
- O briefing continua bloqueando dado pessoal no portal.
- O runner não grava o conteúdo das campanhas em disco além do que a crew já grava em `output/` dentro do container, que é descartado a cada deploy.
- O runner só aceita chamadas com `RUNNER_TOKEN` (comparação em tempo constante). Quem tiver o token pode disparar campanhas e gastar tokens: trate-o como segredo.

## 7. Riscos e custos

| Risco | Mitigação |
|---|---|
| Reinício perde campanha parada num portão | `autoDeploy` desligado; regra de não fazer deploy com campanha aberta; evolução futura com checkpoints |
| Mudança de modelo altera a qualidade | Piloto limpo antes de liberar aos analistas |
| Gasto de tokens sem teto | Limite mensal e alertas na OpenAI; limite diário de disparos já existe no portal |
| Serviço fora do ar | Render Starter com health check e reinício automático; o portal mostra o aviso de executor inacessível |
| Custo do Render | Plano Starter (valor a confirmar no painel do Render) |

## 8. Rodar no plano gratuito do Render (sem cartão)

O `render.yaml` usa `plan: free`. Limites e como contorná-los:

| Limite do plano gratuito | Consequência | Contorno |
|---|---|---|
| Hiberna após 15 min sem requisição de fora | Uma campanha parada num portão **se perde** (o processo é encerrado) | Pinger externo gratuito chamando `https://<servico>.onrender.com/health` a cada 5 min (UptimeRobot, cron-job.org ou um workflow agendado do GitHub). Com o ping, o serviço não hiberna |
| 750 horas gratuitas por mês | Um serviço ligado o mês todo cabe (cerca de 744 h) | Não crie outros serviços gratuitos na mesma conta |
| 512 MB de memória | A crew construída ocupa cerca de 250 MB nos meus testes; durante a execução pode subir | Se o serviço reiniciar por falta de memória (o log do Render mostra "out of memory"), é preciso um plano pago |
| Reinícios periódicos pela plataforma | Perdem campanha parada num portão | Não há contorno gratuito. Evite deixar um portão aberto por muitas horas; decida o mais rápido possível |
| Primeira chamada após hibernar leva cerca de 1 min | O disparo pode demorar | O pinger evita isso |

**Conclusão:** o plano gratuito serve para o piloto de teste. Para os analistas, com a garantia de que a operação não para, use o plano pago de entrada: o custo é pequeno perto do gasto de tokens, e o valor atual deve ser conferido no painel do Render.

Alternativas gratuitas para o runner, se o Render não servir: uma máquina virtual always-free (por exemplo, a Oracle Cloud) ou um Space privado no Hugging Face. Ambas pedem outro passo a passo; me avise antes de escolher.
