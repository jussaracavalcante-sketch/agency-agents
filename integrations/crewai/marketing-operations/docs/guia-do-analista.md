# Guia do analista: piloto do Portal de Aprovação

**Versão:** 0.1 (piloto)
**Para quem:** revisores, aprovadores e leitores que usam o portal durante o piloto

## 1. O que é o portal

A Equipe de Operação de Marketing é um conjunto de agentes de inteligência artificial que produz o material de uma campanha: pesquisa, brief, conteúdo, calendário, e-mails, plano de mídia e direção de arte. O portal mostra o que os agentes produziram e é onde **uma pessoa decide** se o trabalho segue. **O sistema não publica nada.** Tudo que sai daqui é rascunho para revisão humana.

## 2. Seu papel

| Papel | O que faz |
|---|---|
| Leitor | Vê as campanhas e as aprovações. Não decide |
| Revisor | Vê tudo e edita a base de conhecimento dos clientes. Não decide portões |
| Aprovador | Decide o portão para o qual foi designado e dispara campanhas |
| Administrador | Cuida de acessos, configuração e ajustes. Só ele vê a Administração |

## 3. O caminho de uma campanha

1. **Disparo.** Um aprovador preenche o briefing e dispara. Só roda uma campanha por vez.
2. **G1: brief estratégico.** Chega ao portal em poucos minutos, já com a revisão e a correção automática feitas.
3. **G2: peças de produção.** Conteúdo, calendário, e-mails, plano de mídia e direção de arte.
4. **G3: pacote de publicação.** O pacote final e o plano de medição.
5. **Fim.** O G3 autoriza a conclusão, mas **nada é publicado**.

Cada portão aparece em **Aprovações**, com o parecer do Guardião de Marca e Compliance.

## 4. Como decidir um portão

Leia o parecer e as peças. Depois escolha uma de três ações:

| Ação | Quando usar | O que acontece |
|---|---|---|
| **Aprovar** | A peça está boa como está | Segue para a próxima etapa. Nada é reescrito. Deixe o campo de texto **vazio** |
| **Devolver com ajustes** | Falta corrigir algo | O autor reescreve com o seu texto e o portão reabre para nova decisão |
| **Reprovar** | Não há como aproveitar | A execução termina. Deixe o campo de texto **vazio** |

**Regras do campo de texto**
- Só escreva texto em **Devolver com ajustes**. Em Aprovar e Reprovar o texto não é enviado, e o portal bloqueia para evitar engano.
- Seja específico: cite o trecho e diga o que trocar. Exemplo: `Trocar "o melhor atendimento" por "atendimento humano e acolhedor".`
- Cada pedido tem teto de 4.000 caracteres.

## 5. O que sua aprovação significa

Você aprova a **qualidade e a adequação da peça ao briefing**. Você **não atesta** a conformidade regulatória (CFM, CDC, CONAR, ANVISA). Essa validação é do responsável técnico do cliente e do jurídico. Por isso:
- Marcadores **[VALIDAR]** e **[VALIDAR MÉDICO]** são pendências para validação humana. Não são erros do sistema.
- Em conteúdo de saúde, **não aprove** superlativos, promessas de resultado, garantias clínicas, comparações com concorrentes nem depoimentos de pacientes, mesmo que o sistema os tenha deixado passar.
- Confira números, fontes e datas. A IA pode inventar.

## 6. Como ler os avisos do sistema

- **ALERTA DE QUALIDADE:** uma trava automática reprovou a saída três vezes e o sistema a aceitou assim mesmo, para não derrubar a execução. Leia a pendência descrita e decida com atenção. Alerta é motivo para olhar mais, não para aprovar no automático.
- **AJUSTES PENDENTES:** a reescrita veio incompleta e foi mantida a versão anterior. Devolva de novo ou reprove.
- **Rubrica e auditoria de mídia no G2:** foram feitas sobre a **versão inicial**, antes da correção. Vale o parecer final do Guardião.
- **Parecer "Reprovado":** é recomendação do Guardião. A decisão é sua.

## 7. Regras de conduta (resumo)

Leia o **Termo de Conduta** completo. Em resumo:
- Não escreva **dado pessoal** (CPF, telefone, e-mail, nome de paciente, prontuário, informação de saúde) no briefing, no feedback ou na base de conhecimento. O portal bloqueia os casos que reconhece.
- Descreva o público de forma agregada.
- Não compartilhe seu acesso. Use o segundo fator quando solicitado.
- Não copie conteúdo do portal para fora dele sem autorização.
- Em caso de dúvida ou incidente, avise a Head de IA e o encarregado na hora.

## 8. Limites do piloto

- Uma campanha por vez.
- Até 10 disparos por pessoa em 24 horas (o administrador pode ajustar).
- Textos de briefing com tamanho máximo por campo.
- Clientes liberados no piloto: **[PREENCHER pela Head de IA]**.

## 9. Se algo der errado

| Situação | O que fazer |
|---|---|
| A tela não carrega ou dá erro | Recarregue. Persistindo, avise a Head de IA com o horário e o que estava fazendo |
| O portão não aparece depois de muito tempo | Aguarde alguns minutos e recarregue. Avise a Head de IA se passar de 15 minutos |
| Decisão enviada por engano | Não tente repetir. Avise a Head de IA com o número da execução |
| Viu dado pessoal em alguma peça | Não copie. Avise a Head de IA e o encarregado |
| Não consegue acessar uma área | É esperado para o seu papel. Peça ao administrador, se precisar |

## 10. Como dar retorno sobre o piloto

Anote o que travou, o que confundiu e o que faltou. Entregue à Head de IA ao fim da semana. O que mais ajuda: o número da execução, o portão, o trecho e o que você esperava ver.

**Contatos:** Head de IA **[PREENCHER]**, encarregado **[PREENCHER]**.
