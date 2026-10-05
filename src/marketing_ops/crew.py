"""
crew.py — Equipe de Operação de Marketing (CrewAI)

Define os 14 agentes e as 23 tarefas do pipeline de campanha (a 24ª, relatório de
performance, roda em uma crew separada pós-campanha). Os textos de role/goal/backstory e
description/expected_output vivem em config/agents.yaml e config/tasks.yaml; este arquivo
só liga agentes, tarefas, ferramentas, dependências (context) e processo.

Processo: pipeline completo em `Process.sequential` com a ordem definida abaixo. O gerente
conduz os portões humanos (human_input=True) como tarefas explícitas.

Variantes (hierárquica e relatório pós-campanha) ficam em crew_variants.py para que a
plataforma CrewAI encontre uma única classe @CrewBase neste arquivo.
"""

from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, ScrapeWebsiteTool, SerperDevTool

from marketing_ops.tools.brand_book import definir_contexto_do_portal
from marketing_ops.tools import (
    AnalyticsReadTool,
    BrandBookTool,
    CrmReadTool,
    PaidMediaReadTool,
    PublishTool,
    SeoKeywordTool,
)



def _modelo_padrao() -> tuple[str, str]:
    """Escolhe o provedor pela chave disponível quando MODEL não é informado."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic/claude-sonnet-5-5", "anthropic/claude-haiku-4-5-20251001"
    if os.getenv("OPENAI_API_KEY"):
        return "openai/gpt-4o", "openai/gpt-4o-mini"
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return "gemini/gemini-2.5-pro", "gemini/gemini-2.5-flash"
    return "openai/gpt-4o", "openai/gpt-4o-mini"


_PADRAO, _PADRAO_LEVE = _modelo_padrao()
MODEL = os.getenv("MODEL", _PADRAO)
OUTPUT_DIR = Path(os.getenv("CREW_OUTPUT_DIR", "output"))
# Log em arquivo é opcional: a plataforma CrewAI já guarda o trace de cada execução.
LOG_FILE = os.getenv("CREW_LOG_FILE", "")


def _resolver_output_dir() -> Path | None:
    """
    Devolve uma pasta GRAVÁVEL para os artefatos (output_file das tarefas e log).
    Tenta OUTPUT_DIR; se o diretório de trabalho for somente leitura (caso de alguns
    containers), cai para a pasta temporária do sistema. Nunca derruba a crew.
    """
    candidatos = [OUTPUT_DIR, Path(tempfile.gettempdir()) / "marketing_ops_output"]
    for pasta in candidatos:
        try:
            pasta.mkdir(parents=True, exist_ok=True)
            sonda = pasta / ".gravavel"
            sonda.touch()
            sonda.unlink()
            return pasta.resolve()
        except OSError:
            continue
    return None


def _cwd_gravavel() -> bool:
    try:
        sonda = Path.cwd() / ".gravavel_cwd"
        sonda.touch()
        sonda.unlink()
        return True
    except OSError:
        return False


def _garantir_output_dir() -> None:
    """
    Garante que exista uma pasta `output/` relativa ao diretório de trabalho, porque o
    runtime da plataforma pode gravar um log relativo (`output/crew_log.json`) por conta
    própria. Se o diretório de trabalho for somente leitura, muda para a pasta temporária,
    onde `output/` pode ser criada. Nunca lança erro.
    """
    try:
        if not _cwd_gravavel():
            os.chdir(tempfile.gettempdir())
        Path("output").mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    _resolver_output_dir()


_REGRA_DE_INSUMOS = (
    "\n\nREGRA DE INSUMOS: as saídas das tarefas anteriores e os dados do briefing já estão no seu CONTEXTO. "
    "Não tente abrir arquivos ou caminhos e nunca responda que não consegue acessar documentos: entregue o "
    "documento pedido com o que está no contexto e marque o que faltar como [VALIDAR]. É PROIBIDO usar conhecimento próprio sobre o cliente: serviços, especialidades, procedimentos e tecnologias do CLIENTE só podem ser citados se constarem do briefing ou da base de conhecimento dele; caso contrário, não cite ou marque [VALIDAR]. Tendências do mercado (por exemplo, cirurgia robótica na saúde) podem ser citadas na pesquisa de mercado e no mapa de palavras-chave, sempre rotuladas como 'tendência setorial', sem atribuí-las ao cliente. NÃO PROPONHA depoimentos, testemunhos, histórias ou casos de pacientes, nem afirmações de liderança, referência ou premiação: nenhum desses itens existe nos insumos. Prefira conteúdo informativo (como escolher, o que esperar, perguntas frequentes). É PROIBIDO inventar pessoas, "
    "pacientes, depoimentos, nomes ou idades de personagens apresentados como reais, números sem fonte (metas, "
    "projeções, percentuais, tamanhos de público) e garantias de resultado; personas só como perfil, sem nome próprio. "
    "Em saúde, superlativos e promessas clínicas sem fonte devem ser evitados ou marcados [VALIDAR MÉDICO]."
)
_REGRA_CONTEXTO_CLIENTE = (
    "\n\nBASE DE CONHECIMENTO DO CLIENTE (leitura obrigatória antes de executar; carregada automaticamente "
    "pelo código a partir da pasta knowledge/ do cliente {cliente}): toda decisão de marca, tom de voz, "
    "termos, paleta e restrições deve vir daqui. O que não estiver aqui deve ser marcado [VALIDAR]; nunca "
    "invente atributos da marca.\n{contexto_cliente}"
)
_LIMITE_CONTEXTO_CLIENTE = 8000


def _injetar_contexto_cliente(inputs):
    """
    before_kickoff: carrega a base de conhecimento do cliente informado em inputs['cliente'] e a expõe como
    inputs['contexto_cliente'], usada por todas as tarefas. Determinístico: não depende de o agente decidir
    consultar a ferramenta.
    """
    inputs = dict(inputs or {})
    if inputs.get("contexto_cliente"):
        definir_contexto_do_portal(str(inputs.get("cliente") or ""), str(inputs["contexto_cliente"]))
        _TEXTO_PERMITIDO["texto"] = " ".join(str(v) for v in inputs.values()).lower()
        _INPUTS_ATUAIS.update(inputs)
        return inputs
    cliente = str(inputs.get("cliente") or "").strip()
    if not cliente:
        inputs["contexto_cliente"] = "[SEM CLIENTE INFORMADO] Marque decisões de marca como [VALIDAR]."
    else:
        texto = BrandBookTool()._run(cliente)
        inputs["contexto_cliente"] = texto[:_LIMITE_CONTEXTO_CLIENTE]
    _TEXTO_PERMITIDO["texto"] = " ".join(str(v) for v in inputs.values()).lower()
    _INPUTS_ATUAIS.update(inputs)
    return inputs


_MODO_COM_HUMANO = (
    "\n\nMODO DO PORTÃO: HUMANO ATIVO. Esta tarefa só executa depois que um aprovador humano liberou o "
    "portão correspondente. Trate a decisão como APROVADA, aplicando os ajustes e o feedback humano "
    "transcritos no pedido do portão e os ajustes obrigatórios do Guardião."
)
_MODO_SEM_HUMANO = (
    "\n\nMODO DO PORTÃO: SEM APROVADOR HUMANO NESTA EXECUÇÃO. A decisão é PENDENTE DE APROVAÇÃO HUMANA. "
    "Aplique apenas os ajustes obrigatórios apontados pelo Guardião, marque o documento como VERSÃO NÃO "
    "APROVADA POR HUMANO e não registre aprovação, aprovador ou data de decisão."
)


_FRASES_DE_FALHA = (
    "erro ao tentar acessar",
    "não consigo acessar",
    "não consegui acessar",
    "não tenho acesso",
    "não poderei completar",
    "forneça acesso",
    "forneça o conteúdo",
    "verifique se os documentos",
    "unable to access",
    "cannot access",
    "i don't have access",
    "please provide the",
)
_MIN_CARACTERES_DOCUMENTO = 700
def _texto_apos_documento(texto):
    """Texto escrito depois do último fechamento de bloco ``` (comentário do agente fora do documento); vazio se não houver."""
    t = _sem_alerta(texto or "")
    if t.count("```") < 2 or t.count("```") % 2:
        return ""
    resto = t[t.rfind("```") + 3:].strip()
    return resto if len(resto) > 20 else ""


_ABERTURA_DE_CONVERSA = re.compile(
    r"^(para (proceder|aplicar|atender|seguir)|vou |vamos|a seguir|abaixo (est[aá]|segue|apresento)|segue |com base n[oa]s?|claro[,!.]|certo[,!.]|entendi|aqui est[aá]|ok[,!.]|"
    r"prezad[oa]s?)\b",
    re.I,
)


def _guardrail_documento(saida):  # sem anotação de retorno: o validador do CrewAI a compara com tipos reais
    """
    Rejeita a saída de uma tarefa de documento quando ela é uma desculpa em vez de entrega: curta demais ou
    dizendo que não conseguiu acessar insumos. Os insumos estão sempre no contexto; a tarefa é refeita.
    """
    texto = (getattr(saida, "raw", None) or str(saida) or "").strip()
    baixo = texto.lower()
    apos = _texto_apos_documento(texto)
    if apos:
        return False, (
            f"A saída traz comentário depois do documento (\"{apos[:70]}\"). O documento termina no fechamento do bloco ou na última seção: "
            "não escreva introdução, resumo, autoavaliação nem frase de conformidade depois dele."
        )
    primeira = next((l.strip() for l in texto.splitlines() if l.strip() and not l.strip().startswith(("```", ">"))), "")
    if _ABERTURA_DE_CONVERSA.match(primeira):
        return False, (
            f"A saída abre com comentário do agente (\"{primeira[:70]}\"). Entregue só o documento, começando pelo título ou pela primeira "
            "seção, sem introdução, sem explicar o que você vai fazer nem o que mudou."
        )
    if len(texto) < _MIN_CARACTERES_DOCUMENTO:
        return False, (
            "Saída curta demais para um documento. Entregue o documento completo usando os insumos que estão no "
            "CONTEXTO desta tarefa; não procure arquivos nem peça acesso."
        )
    for frase in _FRASES_DE_FALHA:
        if frase in baixo[:600]:
            return False, (
                "A saída diz que não foi possível acessar documentos. Isso não procede: todos os insumos estão no "
                "CONTEXTO desta tarefa. Refaça entregando o documento completo; se faltar um dado, marque [VALIDAR]."
            )
    return True, saida


def _normalizar(texto):
    return re.sub(r"[\s*_#>|`\-]+", " ", texto or "").strip().lower()


def _linhas_significativas(texto):
    return [n for n in (_normalizar(l) for l in (texto or "").splitlines()) if len(n) > 25]


def _guardrail_portao_factory(revisao_task, rubrica_task=None, auditoria_task=None):
    """
    Portão humano: o pedido deve copiar o parecer do Guardião (mesmo resultado, pelo menos 70% das linhas) e ter as
    seções obrigatórias. Rejeita paráfrase e a troca de "Reprovado" por outro resultado.
    """

    tentativas = {"n": 0}

    def guardrail(saida):  # sem anotação de retorno (ver _guardrail_documento)
        veredito = _checar_portao(saida)
        if veredito[0] is False:
            veredito = (False, _PREFIXO_AUTO + str(veredito[1]))
            # Após duas rejeições a saída é aceita: o CrewAI derruba a execução inteira quando o guardrail esgota as
            # tentativas, e a plataforma não recupera uma execução pausada que falhou (observado em 02/10).
            tentativas["n"] += 1
            if tentativas["n"] > 2:
                return True, saida
        return veredito

    def _checar_portao(saida):
        texto = (getattr(saida, "raw", None) or str(saida) or "")
        norm = _normalizar(texto)
        for secao in ("histórico de feedbacks", "parecer do guardião", "pedido de decisão"):
            if secao not in norm and secao.replace("pedido de decisão", "decis") not in norm:
                return False, f"Falta a seção obrigatória '{secao}'. Siga o FORMATO OBRIGATÓRIO."
        parecer = getattr(getattr(revisao_task, "output", None), "raw", None)
        if parecer:
            m = re.search(r"resultado[^a-zà-ú]{0,12}[^\n]{0,10}?(reprovado|aprovado com ajustes|aprovado)", _normalizar(parecer))
            if m and m.group(1) not in norm:
                return False, f"O resultado do Guardião é '{m.group(1)}' e precisa aparecer inalterado no pedido."
            linhas = _linhas_significativas(parecer)
            if linhas:
                achadas = sum(1 for l in linhas if l in norm)
                if achadas / len(linhas) < 0.7:
                    return False, (
                        "O parecer do Guardião foi parafraseado ou resumido. Copie o texto do parecer integralmente, "
                        "sem reescrever, na seção 'Parecer do Guardião (cópia literal)'."
                    )
        rubrica = getattr(getattr(rubrica_task, "output", None), "raw", None) if rubrica_task is not None else None
        if rubrica:
            linhas = [_normalizar(l) for l in _linhas_resumo_rubrica(rubrica)]
            if linhas and not all(l in norm for l in linhas):
                return False, (
                    "Falta o quadro da rubrica de qualidade. Na seção 'Quadro da rubrica de qualidade (cópia literal)' copie, sem "
                    "alterar, as quatro linhas que começam com RESUMO | da tarefa de rubrica."
                )
        auditoria = getattr(getattr(auditoria_task, "output", None), "raw", None) if auditoria_task is not None else None
        if auditoria:
            linhas = [_normalizar(l.strip(" *`>-")) for l in _sem_alerta(auditoria).splitlines() if re.match(r"[\s*`>-]*(AUDITORIA|PARECER DO SUPERVISOR)\s*\|", l, re.I)]
            if linhas and not all(l in norm for l in linhas):
                return False, (
                    "Falta a auditoria técnica de mídia. Na seção 'Auditoria técnica de mídia (cópia literal)' copie, sem alterar, as linhas que começam "
                    "com AUDITORIA | e a linha PARECER DO SUPERVISOR | da tarefa de auditoria."
                )
        return True, saida

    return guardrail


_AFIRMACOES_FALSAS = re.compile(
    r"(foram|s[ãa]o|est[ãa]o|contam com|possuem|t[êe]m)\s+[^.\n]{0,60}"
    r"(colhid\w+ com consentimento|reais que consentiram|autoriza[çc][ãa]o para divulga)",
    re.I,
)


_CLAIMS_NOVOS = re.compile(r"garant\w+\s+(a\s+|o\s+)?(seguran[çc]a|precis[ãa]o|resultado|cura|recupera[çc][ãa]o)", re.I)


def _guardrail_aplicacao_g2(saida):
    """Ajuste de veracidade só remove ou marca [VALIDAR]: nunca afirma que depoimento é real ou autorizado."""
    base = _guardrail_documento(saida)
    if base[0] is False:
        return base
    texto = (getattr(saida, "raw", None) or str(saida) or "")
    claims = _claims_proibidos(texto)
    if claims or _placeholders(texto):
        return _guardrail_sem_claims(saida)
    if _CLAIMS_NOVOS.search(texto):
        return False, (
            "A saída introduz garantia de segurança, precisão, resultado ou recuperação sem fonte. Remova a afirmação "
            "ou marque [VALIDAR MÉDICO]; a reemissão não pode acrescentar promessas."
        )
    cal = _trecho_calendario_reemitido(texto)
    if cal:
        erro = _cobertura_calendario(cal)
        if erro:
            return False, "O calendário reemitido está incompleto. " + erro + " Reemita o calendário inteiro, não só as linhas ajustadas."
    if _AFIRMACOES_FALSAS.search(texto):
        return False, (
            "A saída afirma que depoimentos/testemunhos são reais, colhidos com consentimento ou autorizados. Isso não "
            "pode ser afirmado: não há depoimento real nem consentimento. Remova os depoimentos e testemunhos das peças "
            "ou marque [VALIDAR]; nunca declare autorização."
        )
    return True, saida


_TAG_ALERTA = "ALERTA DE QUALIDADE"
_PREFIXO_AUTO = (
    "REVISÃO AUTOMÁTICA DE QUALIDADE (não é feedback humano; não cite, comente nem copie esta mensagem no documento, "
    "entregue só o documento corrigido): "
)


def _sem_alerta(texto):
    """Remove as linhas de alerta que as próprias travas inserem: elas citam o problema e não podem ser varridas como se fossem texto da peça."""
    return "\n".join(l for l in (texto or "").splitlines() if _TAG_ALERTA not in l)


def _com_alerta(saida, motivo):
    """Saída aceita sem correção: devolve o texto com uma linha de alerta no topo, para que o humano veja o que a trava não resolveu."""
    raw = getattr(saida, "raw", None) or str(saida) or ""
    rotulo = getattr(saida, "name", None) or ""
    detalhe = re.sub(r"\s+", " ", str(motivo or "")).strip()[:600]
    linha = f"> ⚠ {_TAG_ALERTA}{' (' + rotulo + ')' if rotulo else ''}: a trava automática reprovou esta saída e ela foi aceita sem correção. Pendência: {detalhe}"
    return linha + "\n\n" + raw


def _com_limite_de_rejeicoes(guardrail, maximo=2):
    """
    Aceita a saída depois de `maximo` rejeições, porque guardrail esgotado derruba a execução inteira na plataforma. A saída aceita
    leva uma linha "ALERTA DE QUALIDADE" no topo com a pendência que a trava não conseguiu corrigir.
    """
    estado = {"n": 0}

    def envelope(saida):  # sem anotação de retorno (ver _guardrail_documento)
        veredito = guardrail(saida)
        if veredito[0] is False:
            estado["n"] += 1
            if estado["n"] > maximo:
                return True, _com_alerta(saida, veredito[1])
            return False, _PREFIXO_AUTO + str(veredito[1])
        return veredito

    return envelope


_TEXTO_PERMITIDO = {"texto": ""}
_TERMOS_SENSIVEIS = re.compile(
    r"cirurgia rob[óo]tica|\brob[óo]tic[ao]s?\b|\bUTI\b|telemedicina|cardiologia|ortopedia|urologia|oncologia|"
    r"neurologia|maternidade|pediatria|pronto[- ]socorro|hemodin[âa]mica|transplante|centro cirúrgico",
    re.I,
)


def _guardrail_producao(saida):
    """
    Peça de produção não pode citar serviço, especialidade ou tecnologia clínica que não conste do briefing nem da base
    de conhecimento do cliente (o modelo costuma "lembrar" serviços reais do cliente que ninguém informou).
    """
    base = _guardrail_documento(saida)
    if base[0] is False:
        return base
    texto = (getattr(saida, "raw", None) or str(saida) or "")
    claims = _claims_proibidos(texto)
    if claims or _placeholders(texto):
        return _guardrail_sem_claims(saida)
    permitido = _TEXTO_PERMITIDO["texto"]
    if not permitido:  # execução retomada sem inputs disponíveis: não há como conferir
        return True, saida
    citados = {m.group(0).lower() for m in _TERMOS_SENSIVEIS.finditer(texto)}
    achados = sorted(t for t in citados if not re.search(rf"\b{re.escape(t)}\b", permitido))
    if achados:
        return False, (
            "A saída cita serviços/especialidades/tecnologias que não constam do briefing nem da base de conhecimento do "
            f"cliente: {', '.join(achados)}. Remova-os ou troque por [VALIDAR]; não use conhecimento próprio sobre o cliente."
        )
    return True, saida


_CLAIMS_PROIBIDOS = re.compile(
    r"depoimento|testemunho|hist[óo]rias? de (pacientes?|recupera[çc][ãa]o|sucesso)|casos? de sucesso|"
    r"paciente real|pacientes? satisfeit|\blidera\b|\bl[íi]der(es)?\b|refer[êe]ncia em|\bpremiad[oa]s?\b|"
    r"o melhor hospital|n[º°o] ?1\b|\bmelhor do (estado|brasil|norte)\b|"
    r"\b(o|a|os|as|ao|do|da|pelo|no|na|nos|nas) melhor(es)?\b|melhor (pra|para) voc[êe]|\bmelhor (atendimento|cuidado|experi[êe]ncia|hospital|cl[íi]nica|estrutura)\b|"
    r"tecnologia de ponta|tecnologias? de ponta|equipamentos? de [úu]ltima gera[çc][ãa]o|[úu]ltima gera[çc][ãa]o|estado da arte|"
    r"diagn[óo]sticos? precis\w+|tratamentos? eficaz\w*|confian[çc]a em cada diagn[óo]stico|seguran[çc]a em cada tratamento|"
    r"\bde ponta\b(?! a ponta)|melhor escolha|escolha preferencial|escolha segura|precis[ãa]o e seguran[çc]a|"
    r"certifica[çc][õo]es? reconhecid\w+|"
    r"garant\w+[^.\n]{0,60}(precis[ãa]o|seguran[çc]a|excel[êe]ncia|qualidade|efici[êe]ncia|resultados?|cura|"
    r"recupera[çc][ãa]o|lgpd|conformidade|ader[êe]ncia|atendimento|cuidado|diagn[óo]stico|tratamento)",
    re.I,
)
_LINHA_NEUTRA = re.compile(r"\[VALIDAR|\bsem (usar )?depoimento|proibid|n[ãa]o (use|usar|incluir|propor|citar)|evitar", re.I)


_PLACEHOLDERS = re.compile(
    r"example\.(com|org|net)|exemplo\.com(\.br)?|lorem ipsum|seu-?site\.com|\[(inserir|link|url)[^\]]*\]|"
    # nota interna do agente que vazou para dentro da peça (texto de retrabalho)
    r"\breformulei\b|\breescrevi\b|ajustei (o|a|os|as) (conte[úu]do|texto|pe[çc]as?)|para evitar os problemas|"
    r"conforme (solicitado|pedido|orienta[çc][ãa]o)|como solicitado|a pedido d[oa]|"
    # autocertificação de conformidade e afirmação de que não há pendência
    r"seguindo rigorosamente|(foi|foram) (criad|elaborad|redigid)\w+ seguindo|em total conformidade|"
    r"todas as (propostas|valida[çc][õo]es|corre[çc][õo]es) foram|n[ãa]o h[áa] ajustes pendentes|todos os feedbacks[^.\n]{0,40}(considerad|inclu[íi]d)",
    re.I,
)


def _placeholders(texto):
    """Link ou texto de exemplo que iria para publicação como se fosse real."""
    texto = _sem_alerta(texto)
    return sorted({m.group(0).lower() for m in _PLACEHOLDERS.finditer(texto or "")})


def _claims_proibidos(texto):
    """Linhas com depoimento/testemunho/superlativo sem [VALIDAR] nem aviso de que o item é proibido."""
    texto = _sem_alerta(texto)
    achados = []
    for linha in (texto or "").splitlines():
        if _CLAIMS_PROIBIDOS.search(linha) and not _LINHA_NEUTRA.search(linha):
            achados.append(_CLAIMS_PROIBIDOS.search(linha).group(0).lower())
    return sorted(set(achados))


def _guardrail_sem_claims(saida):
    base = _guardrail_documento(saida)
    if base[0] is False:
        return base
    texto = getattr(saida, "raw", None) or str(saida) or ""
    achados = _claims_proibidos(texto)
    if achados:
        return False, (
            "A saída propõe itens que não existem nos insumos: " + ", ".join(achados) + ". Não há depoimentos, testemunhos, "
            "histórias ou casos de pacientes, nem prova de liderança ou premiação. Superlativos (\"o melhor\", \"tecnologia de "
            "ponta\", \"última geração\"), garantias (\"garante precisão/excelência/LGPD\") e promessas clínicas (\"diagnósticos "
            "precisos\", \"tratamentos eficazes\") exigem fonte: remova ou marque [VALIDAR MÉDICO] na mesma linha. Reemita o "
            "documento completo."
        )
    ph = _placeholders(texto)
    if ph:
        return False, (
            "A saída contém link/texto de exemplo ou nota interna do agente (" + ", ".join(ph) + "). Peça publicável não pode "
            "ter placeholder nem comentário sobre o próprio retrabalho (\"reformulei\", \"conforme solicitado\"): use [VALIDAR: link] "
            "no lugar e entregue só o documento final, sem notas sobre o que você mudou."
        )
    return True, saida


_INPUTS_ATUAIS = {}


def _cobertura_calendario(texto):
    """Devolve a mensagem de erro se o calendário não cobre todas as semanas da campanha; None se cobre (ou não há como medir)."""
    try:
        semanas = int(str(_INPUTS_ATUAIS.get("duracao_semanas", "")).strip())
    except ValueError:
        return None
    texto = _sem_alerta(texto)
    from datetime import datetime

    datas = []
    for d, mth, a in re.findall(r"\b(\d{2})/(\d{2})/(20\d{2})\b", texto):
        try:
            datas.append(datetime(int(a), int(mth), int(d)))
        except ValueError:
            pass
    for a, mth, d in re.findall(r"\b(20\d{2})-(\d{2})-(\d{2})\b", texto):
        try:
            datas.append(datetime(int(a), int(mth), int(d)))
        except ValueError:
            pass
    blocos = {(x - min(datas)).days // 7 for x in datas} if datas else set()
    marcadores = [int(n) for n in re.findall(r"semana\s+(\d{1,2})", texto, re.I)]
    marcadores += [int(n) for n in re.findall(r"^\|\s*(\d{1,2})\s*\|", texto, re.M)]  # coluna "Semana" numérica
    if len(blocos) >= semanas - 1 or (marcadores and max(marcadores) >= semanas):
        return None
    return (
        f"O calendário cobre {len(blocos) or 'menos de ' + str(semanas)} semana(s) pelas datas, mas a campanha tem {semanas}. "
        f"Entregue posts distribuídos por todas as {semanas} semanas, com ao menos 3 por semana, datando cada um."
    )


def _guardrail_calendario(saida):
    """O calendário deve cobrir todas as semanas da campanha (por datas ou por marcadores 'Semana N')."""
    base = _guardrail_producao(saida)
    if base[0] is False:
        return base
    erro = _cobertura_calendario(getattr(saida, "raw", None) or str(saida) or "")
    return (False, erro) if erro else (True, saida)


_CALENDARIO_REEMITIDO = re.compile(r"(pe[çc]a reemitida|reemiss[ãa]o)[^\n]*calend[áa]rio|calend[áa]rio[^\n]*reemitid", re.I)


def _trecho_calendario_reemitido(texto):
    """Da seção reemitida do calendário até a próxima peça reemitida ou o fim; vazio se o calendário não foi reemitido."""
    m = _CALENDARIO_REEMITIDO.search(texto or "")
    if not m:
        return ""
    resto = texto[m.start():]
    fim = re.search(r"\n#{1,4}\s*(pe[çc]a reemitida|parte c|lista de vers)", resto[m.end() - m.start():], re.I)
    return resto[: (m.end() - m.start()) + fim.start()] if fim else resto


_FONTE_INTERNA = re.compile(
    r"an[áa]lise interna|registros? internos?|dados internos|fontes? internas?|crm interno|relat[óo]rios? internos?|"
    r"sistema de crm|crm d[oa] [\w ]{3,40}|google analytics|search console|dados d[oa] hospital|sistema interno",
    re.I,
)
_FONTE_MERCADO = re.compile(r"dados? de mercado|relat[óo]rio de mercado|fontes?\s*:|\bfonte\b", re.I)
_ORGAO_REGULADOR = re.compile(r"conselho federal de medicina|\banvisa\b|\bconar\b|\bcfm\b|\bcdc\b", re.I)
_PCT_NOVO = re.compile(r"(?<![\d.,])(\d{1,3}(?:,\d+)?)\s?%")


def _guardrail_brief(saida):
    """O brief usa o objetivo do briefing literalmente e não cria baselines que ninguém informou."""
    base = _guardrail_producao(saida)
    if base[0] is False:
        return base
    texto = _sem_alerta(getattr(saida, "raw", None) or str(saida) or "")
    objetivo = _normalizar(str(_INPUTS_ATUAIS.get("objetivo", "")))
    if objetivo and objetivo not in _normalizar(texto):
        return False, (
            "O brief não reproduz o objetivo do briefing. Copie o objetivo literalmente, sem trocar a meta, o prazo ou o "
            f"baseline: \"{_INPUTS_ATUAIS.get('objetivo')}\". Não substitua por outro objetivo (percentuais, ocupação, etc.)."
        )
    permitido = _normalizar(_TEXTO_PERMITIDO["texto"])
    fontes = sorted({m.group(0).lower() for l in texto.splitlines() if "[validar" not in l.lower() for m in _FONTE_INTERNA.finditer(l)
                     if _normalizar(m.group(0)) not in permitido})
    if fontes:
        return False, (
            "O brief cita fonte que o briefing não menciona: " + ", ".join(fontes) + ". A origem do baseline é a do briefing "
            "(ferramenta de analytics e CRM informados). Remova a fonte inventada ou escreva [VALIDAR: fonte]."
        )
    regulador = [l.strip()[:90] for l in texto.splitlines() if "[validar" not in l.lower() and _FONTE_MERCADO.search(l) and _ORGAO_REGULADOR.search(l)]
    if regulador:
        return False, (
            f"O brief lista órgão regulador como fonte de dados de mercado (\"{regulador[0]}\"). CFM, ANVISA e CONAR são regras do setor, não "
            "dados de mercado fornecidos. Em Fontes cite só a ferramenta de dados do briefing e o guia de marca; para o resto escreva [VALIDAR: fonte]."
        )
    pct = []
    for linha in texto.splitlines():
        if "[validar" in linha.lower():
            continue
        for m in _PCT_NOVO.finditer(linha):
            n = m.group(1)
            if n not in ("100", "0") and not re.search(rf"(?<![\d.,]){re.escape(n)}\s?%", permitido):
                pct.append(f"{n}%")
    if pct:
        return False, (
            "O brief traz percentuais que não constam do briefing nem da base do cliente: " + ", ".join(sorted(set(pct))) + ". Metas, hipóteses "
            "e divisões de orçamento com número novo são premissas: escreva [VALIDAR] na mesma linha ou retire o número."
        )
    for chave in ("orcamento_midia", "orcamento_total"):
        valor = str(_INPUTS_ATUAIS.get(chave, ""))
        m = re.search(r"R\$\s*([\d.]+(?:,\d+)?)", valor)
        if not m:
            continue
        num = m.group(1)
        linhas_num = [l for l in texto.splitlines() if num in l]
        if chave == "orcamento_midia" and not linhas_num:
            return False, f"O brief não cita a verba de mídia do briefing (R$ {num}). A mídia paga do orçamento é essa verba: use-a e separe produção e conteúdo no restante."
        if "[validar" in valor.lower() and linhas_num and not any("[validar" in l.lower() for l in linhas_num):
            return False, f"O briefing marca R$ {num} como [VALIDAR]. Mantenha [VALIDAR] na linha do brief que traz esse valor."
    if permitido:
        inventados = []
        for linha in texto.splitlines():
            if "baseline" not in linha.lower() or "[validar" in linha.lower():
                continue
            for n in re.findall(r"\d[\d.,]*", linha):
                n = n.strip(".,")
                if n and not re.search(rf"(?<![\d.,]){re.escape(n)}(?![\d])", permitido):
                    inventados.append(n)
        if inventados:
            return False, (
                "O brief traz baseline com números que não constam do briefing nem da base do cliente: "
                + ", ".join(sorted(set(inventados))) + ". Use só o baseline informado; para o restante escreva "
                "\"[VALIDAR: baseline não informado]\" e não cite fontes (\"registros internos\", CRM, Analytics) que o briefing não cita."
            )
    return True, saida


_PECAS_RUBRICA = ("CONTEUDO", "CALENDARIO", "EMAIL", "MIDIA")
_RESUMO_RUBRICA = re.compile(
    r"^[\s*`>-]*RESUMO\s*\|\s*(?P<peca>[^|]+?)\s*\|\s*(?P<gates>[^|]+?)\s*\|\s*NOTA\s*=\s*(?P<nota>\d{1,3})\s*/\s*100\s*\|\s*"
    r"VEREDITO\s*=\s*(?P<ver>APROVAR COM AJUSTES MENORES|APROVAR|DEVOLVER|REFAZER)\s*\|\s*REVIS[ÃA]O\s+(?P<ciclo>[12])\s+DE\s+2[\s*`]*$",
    re.I | re.M,
)
_SEGMENTO_SAUDE = re.compile(r"sa[úu]de|hospital|cl[íi]nica|m[ée]dic|farm[áa]c|drogaria|odont", re.I)


def _sem_acento(texto):
    import unicodedata

    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").upper()


def _linhas_resumo_rubrica(texto):
    """Linhas RESUMO | ... da rubrica de qualidade, na forma como foram emitidas."""
    return [m.group(0).strip(" *`>-\t") for m in _RESUMO_RUBRICA.finditer(texto or "")]


def _guardrail_rubrica(saida):
    """
    Rubrica de qualidade: quatro peças, cada uma com a linha RESUMO (5 gates, nota, veredito, ciclo) coerente com as regras:
    gate em FALHA limita a nota a 59 e exige DEVOLVER ou REFAZER; sem falha, o veredito segue a faixa da nota.
    """
    base = _guardrail_documento(saida)
    if base[0] is False:
        return base
    texto = getattr(saida, "raw", None) or str(saida) or ""
    achados = {}
    for m in _RESUMO_RUBRICA.finditer(texto):
        peca = _sem_acento(m.group("peca")).replace("-", "").replace(" ", "")
        achados[peca] = m
    faltam = [p for p in _PECAS_RUBRICA if p not in achados]
    if faltam:
        return False, (
            "Faltam linhas RESUMO para as peças: " + ", ".join(faltam) + ". Use exatamente: RESUMO | <CONTEÚDO, CALENDÁRIO, E-MAIL "
            "ou MÍDIA> | G1=OK G2=OK G3=OK G4=NA G5=OK | NOTA=NN/100 | VEREDITO=<APROVAR, APROVAR COM AJUSTES MENORES, DEVOLVER "
            "ou REFAZER> | REVISÃO 1 DE 2, uma linha por peça."
        )
    for peca in _PECAS_RUBRICA:
        m = achados[peca]
        gates = dict(re.findall(r"G([1-5])\s*=\s*(OK|FALHA|NA)", m.group("gates"), re.I))
        if sorted(gates) != ["1", "2", "3", "4", "5"]:
            return False, f"A linha RESUMO de {peca} precisa dos 5 gates (G1 a G5), cada um OK, FALHA ou NA."
        nota = int(m.group("nota"))
        ver = m.group("ver").upper()
        falhou = any(v.upper() == "FALHA" for v in gates.values())
        if nota > 100:
            return False, f"A nota de {peca} ({nota}) passa de 100."
        if falhou:
            if nota > 59 or ver not in ("DEVOLVER", "REFAZER"):
                return False, (
                    f"{peca} tem gate em FALHA: a nota fica em no máximo 59 e o veredito é DEVOLVER ou REFAZER "
                    f"(recebeu NOTA={nota}, VEREDITO={ver})."
                )
        else:
            esperado = "APROVAR" if nota >= 90 else "APROVAR COM AJUSTES MENORES" if nota >= 80 else "DEVOLVER" if nota >= 60 else "REFAZER"
            if ver != esperado:
                return False, f"{peca}: a nota {nota} corresponde ao veredito {esperado}, não {ver}."
    if _SEGMENTO_SAUDE.search(str(_INPUTS_ATUAIS.get("segmento", ""))) and "aval m" not in _normalizar(texto):
        return False, "O segmento é saúde: inclua a marca AVAL MÉDICO PENDENTE em todas as peças e no quadro de notas."
    return True, saida


_CANAIS_PAGOS = ("meta ads", "linkedin ads", "tiktok ads", "youtube ads", "microsoft ads", "pinterest ads", "twitter ads", "display", "programática")
_LINHA_PROJECAO = re.compile(
    r"^\|\s*(?P<nome>[^|]+?)\s*\|\s*R\$\s*(?P<cpc>[\d.]+(?:,\d+)?)\s*\|\s*(?P<ctr>[\d.,]+)\s*%\s*\|\s*(?P<cvr>[\d.,]+)\s*%\s*\|\s*(?P<conv>\d[\d.]*)\s*\|?\s*$",
    re.M,
)


_LINHA_PROJECAO_LISTA = re.compile(
    r"(?P<nome>[^\n:|]{0,40})[:\-]\s*\**\s*CPC\s*:?\s*\**\s*R\$\s*(?P<cpc>[\d.]+(?:,\d+)?)\s*[,;]\s*\**\s*CTR\s*:?\s*\**\s*(?P<ctr>[\d.,]+)\s*%\s*[,;]\s*"
    r"\**\s*CVR\s*:?\s*\**\s*(?P<cvr>[\d.,]+)\s*%",
    re.I,
)


def _num(txt):
    t = str(txt).strip()
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        t = t.replace(".", "")
    try:
        return float(t)
    except ValueError:
        return None


def _problemas_midia(texto, brief_texto=""):
    """Mensagem de erro do plano de mídia (canal fora do brief, projeção sem fonte, conversões que não fecham) ou None."""
    texto = _sem_alerta(texto)
    baixo = (texto or "").lower()
    base = _normalizar((brief_texto or "") + " " + _TEXTO_PERMITIDO["texto"])
    if brief_texto:
        fora = [c for c in _CANAIS_PAGOS if c in baixo and _normalizar(c) not in base]
        if fora:
            return (
                "O plano de mídia usa canal que o brief aprovado e o briefing não preveem: " + ", ".join(fora) + ". Use só os canais "
                "do brief aprovado; para outro canal, escreva [VALIDAR: canal fora do brief] e não aloque verba."
            )
    linhas = list(_LINHA_PROJECAO.finditer(texto or ""))
    lista = list(_LINHA_PROJECAO_LISTA.finditer(texto or ""))
    if linhas or lista:
        todas = linhas + lista
        i0 = max(0, min(m.start() for m in todas) - 300)
        bloco = (texto[i0: max(m.end() for m in todas) + 150]).lower()
        if "[validar" not in bloco:
            return (
                "As projeções de CPC, CTR e CVR não têm fonte nos dados do briefing. Marque a tabela inteira como [VALIDAR] "
                "(premissas a confirmar) ou cite a fonte; não apresente estimativa como dado."
            )
        orcamentos = {_num(x) for x in re.findall(r"R\$\s*([\d.]+(?:,\d+)?)", texto)} | {_num(x) for x in re.findall(r"R\$\s*([\d.]+(?:,\d+)?)", str(_INPUTS_ATUAIS.get("orcamento_midia", "")))}
        orcamentos = {o for o in orcamentos if o and o >= 100}
        for m in linhas:
            cpc, cvr, conv = _num(m.group("cpc")), _num(m.group("cvr")), _num(m.group("conv"))
            if not (cpc and cvr is not None and conv is not None) or not orcamentos:
                continue
            esperados = [o / cpc * cvr / 100 for o in orcamentos]
            if not any(abs(conv - e) <= max(3, 0.15 * e) for e in esperados):
                return (
                    f"No cenário '{m.group('nome')}', conversões = verba ÷ CPC × CVR não bate: com CPC R$ {cpc:g} e CVR {cvr:g}% a verba "
                    f"de R$ {max(orcamentos):,.0f} rende cerca de {max(esperados):.0f}, e a tabela diz {conv:g}. Recalcule (ou use a verba do canal, "
                    "declarando-a) e refaça a coluna de conversões."
                ).replace(",", ".")
    return None


def _guardrail_midia_factory(brief_task):
    def guardrail(saida):
        base = _guardrail_producao(saida)
        if base[0] is False:
            return base
        texto = getattr(saida, "raw", None) or str(saida) or ""
        erro = _problemas_midia(texto, getattr(getattr(brief_task, "output", None), "raw", None) or "")
        if erro:
            return False, erro
        faltas = _faltas_rotina_midia(texto)
        if faltas:
            return False, (
                "O plano de mídia não traz elementos da rotina de mídia da Vanguarda: " + "; ".join(faltas) + ". Inclua as seções \"Insumos e pendências\", "
                "\"Rotina operacional (diária, semanal)\" e \"Alçadas e autorizações\" conforme a rotina parametrizada na descrição da tarefa."
            )
        return True, saida

    return guardrail


def _guardrail_auditoria_factory(plano_task, brief_task):
    """
    Auditoria técnica do Supervisor: sete linhas AUDITORIA (OK, PENDENTE ou FALHA) e a linha PARECER DO SUPERVISOR coerente (qualquer FALHA
    devolve ao gestor). A varredura em código do plano de mídia não pode passar batida: com problema achado, o parecer precisa ter FALHA.
    """
    chaves = [i["chave"] for i in (_ROTINA.get("auditoria") or {}).get("itens", [])]

    def guardrail(saida):
        base = _guardrail_documento(saida)
        if base[0] is False:
            return base
        texto = _sem_alerta(getattr(saida, "raw", None) or str(saida) or "")
        achados = {}
        for m in re.finditer(r"^[\s*`>-]*AUDITORIA\s*\|\s*(?P<item>[^|]+?)\s*\|\s*(?P<st>OK|PENDENTE|FALHA)\s*\|\s*(?P<obs>.+?)\s*$", texto, re.M | re.I):
            achados[_sem_acento(m.group("item")).replace(" ", "")] = (m.group("st").upper(), m.group("obs"))
        faltam = [c for c in chaves if _sem_acento(c).replace(" ", "") not in achados]
        if faltam:
            return False, (
                "Faltam linhas de auditoria: " + ", ".join(faltam) + ". Use exatamente: AUDITORIA | <ITEM> | OK, PENDENTE ou FALHA | <trecho literal ou motivo>, uma linha por item."
            )
        falhas = [c for c in chaves if achados[_sem_acento(c).replace(" ", "")][0] == "FALHA"]
        for c in falhas:
            if len(achados[_sem_acento(c).replace(" ", "")][1].strip()) < 12:
                return False, f"A FALHA em {c} precisa citar o trecho literal do plano e a regra violada."
        parecer = re.search(r"^[\s*`>-]*PARECER DO SUPERVISOR\s*\|\s*(?P<v>LIBERAR PARA G2|DEVOLVER AO GESTOR)\s*\|", texto, re.M | re.I)
        if not parecer:
            return False, "Falta a linha final: PARECER DO SUPERVISOR | LIBERAR PARA G2 ou DEVOLVER AO GESTOR | <resumo>."
        if falhas and parecer.group("v").upper() != "DEVOLVER AO GESTOR":
            return False, f"Há FALHA em {', '.join(falhas)}: o parecer só pode ser DEVOLVER AO GESTOR."
        if not falhas and parecer.group("v").upper() == "DEVOLVER AO GESTOR":
            return False, "O parecer devolve ao gestor, mas nenhum item está em FALHA. Marque a FALHA com o trecho literal ou libere para o G2."
        plano = getattr(getattr(plano_task, "output", None), "raw", None) or ""
        if plano and not falhas:
            problema = _problemas_midia(plano, getattr(getattr(brief_task, "output", None), "raw", None) or "") or ""
            sinais = [f"{t}: \"{l}\"" for t, l in _ocorrencias_proibidas(plano) if t not in texto.lower()]
            faltas = _faltas_rotina_midia(plano)
            if problema or sinais or faltas:
                detalhe = problema or (sinais[0] if sinais else "o plano não traz: " + "; ".join(faltas))
                return False, (
                    "A varredura em código achou problema no plano de mídia e a sua auditoria não marca nenhuma FALHA: " + detalhe +
                    " Marque a FALHA no item correspondente, com o trecho literal, e devolva ao gestor."
                )
        return True, saida

    return guardrail


def _ocorrencias_proibidas(texto):
    """(termo, trecho) de superlativo, garantia, placeholder ou nota interna, sem contar linhas com [VALIDAR] ou aviso de proibição."""
    texto = _sem_alerta(texto)
    achados = []
    for linha in (texto or "").splitlines():
        m = _PLACEHOLDERS.search(linha)  # nota interna e placeholder valem mesmo em linha com [VALIDAR] ou "evitar"
        if m:
            achados.append((m.group(0).lower(), linha.strip()[:110]))
        m = None if _LINHA_NEUTRA.search(linha) else _CLAIMS_PROIBIDOS.search(linha)
        if m:
            achados.append((m.group(0).lower(), linha.strip()[:110]))
    return achados


def _guardrail_rubrica_factory(pecas):
    """
    Rubrica + varredura em código: se a varredura acha superlativo, garantia, placeholder, nota interna, canal fora do brief ou
    conta de conversões errada numa peça, a linha RESUMO dela não pode marcar G1 e G3 como OK sem citar o trecho nos apontamentos.
    `pecas` mapeia CONTEUDO, CALENDARIO, EMAIL e MIDIA para (tarefa da peça, tarefa do brief aprovado ou None).
    """

    def guardrail(saida):
        base = _guardrail_rubrica(saida)
        if base[0] is False:
            return base
        texto = getattr(saida, "raw", None) or str(saida) or ""
        baixo = texto.lower()
        resumos = {}
        for m in _RESUMO_RUBRICA.finditer(texto):
            peca = _sem_acento(m.group("peca")).replace("-", "").replace(" ", "")
            resumos[peca] = dict(re.findall(r"G([1-5])\s*=\s*(OK|FALHA|NA)", m.group("gates"), re.I))
        for peca, (tarefa, brief) in pecas.items():
            raw = getattr(getattr(tarefa, "output", None), "raw", None)
            gates = resumos.get(peca)
            if not raw or not gates:
                continue
            gates = {k: v.upper() for k, v in gates.items()}
            if gates.get("1") == "FALHA" or gates.get("3") == "FALHA":
                continue
            nao_citados = [(t, l) for t, l in _ocorrencias_proibidas(raw) if t not in baixo]
            if nao_citados:
                t, l = nao_citados[0]
                return False, (
                    f"A varredura em código achou em {peca}: \"{l}\" (termo '{t}'), mas a sua linha RESUMO tem G1=OK e G3=OK e o trecho "
                    "não aparece nos apontamentos. Marque G1=FALHA (superlativo, garantia, promessa) ou G3=FALHA (fato sem fonte) e cite o "
                    "trecho literal, a regra e a correção; só deixe OK se explicar nos apontamentos, citando o trecho, por que não é falha."
                )
            if peca == "MIDIA":
                erro = _problemas_midia(raw, getattr(getattr(brief, "output", None), "raw", None) or "")
                if erro:
                    return False, f"A varredura em código achou problema no plano de mídia: {erro} Marque G3=FALHA e cite o trecho nos apontamentos."
        return True, saida

    return guardrail


def _rank_status(txt):
    n = _normalizar(txt)
    if "reprovad" in n:
        return 3
    if re.search(r"aprovad[oa] com ajustes", n):
        return 2
    return 1 if "aprovad" in n else 0


def _guardrail_parecer_geral(saida):
    """O 'Resultado Geral' do parecer é o pior resultado entre as dimensões: uma dimensão Reprovada torna o parecer Reprovado."""
    base = _guardrail_documento(saida)
    if base[0] is False:
        return base
    linhas = _sem_alerta(getattr(saida, "raw", None) or str(saida) or "").splitlines()
    geral, pior, ref = None, 0, ""
    esperando_geral = False
    for l in linhas:
        n = _normalizar(l)
        if not n:
            continue
        if "resultado geral" in n:
            r = _rank_status(n.split("resultado geral", 1)[1])
            if r:
                geral = geral or r
            else:
                esperando_geral = True
            continue
        if esperando_geral:
            esperando_geral = False
            r = _rank_status(n)
            if r:
                geral = geral or r
                continue
        dimensao = re.match(r"\s*#{2,4}\s*\d+\.", l) or n.startswith("status")
        if dimensao:
            r = _rank_status(l.rsplit(":", 1)[-1] if ":" in l else l)
            if r > pior:
                pior, ref = r, l.strip()[:120]
    if geral and pior and geral < pior:
        nome = {1: "Aprovado", 2: "Aprovado com ajustes", 3: "Reprovado"}
        return False, (
            f"O Resultado Geral do parecer é '{nome[geral]}', mas há dimensão '{nome[pior]}' ({ref}). O resultado geral é o PIOR resultado entre "
            "as dimensões: corrija o Resultado Geral (ou a dimensão, se estiver errada) e reemita o parecer completo."
        )
    return True, saida


def _cmp(texto):
    """Normalização para comparar trechos: minúsculas, sem pontuação nem marcação markdown."""
    return re.sub(r"[^a-z0-9à-ú]+", " ", (texto or "").lower()).strip()


def _citacoes_inexistentes(parecer, fonte):
    """Trechos entre aspas do parecer que não existem no texto revisado (nem no briefing). Linhas de regra ou correção sugerida não contam."""
    base = _cmp(fonte)
    ruins = []
    for linha in _sem_alerta(parecer).splitlines():
        if re.search(r"corre[çc][ãa]o|\bregra\b|sugest|exemplo", linha, re.I):
            continue
        for m in re.finditer(r'"([^"\n]{25,300})"|“([^”\n]{25,300})”', linha):
            q = m.group(1) or m.group(2)
            for seg in re.split(r"\.\.\.|…", q):
                n = _cmp(seg)
                if len(n) >= 20 and n not in base:
                    ruins.append(seg.strip()[:90])
                    break
    return ruins[:3]


_SEM_PROBLEMA = re.compile(r"nenhuma corre[çc][ãa]o|nenhum ajuste|est[áa] coerente|n[ãa]o h[áa] (diverg[êe]ncia|problema)|sem diverg[êe]ncia", re.I)


def _dimensoes_incoerentes(parecer):
    """Dimensão marcada Reprovada cujo próprio texto diz que está correta (nenhuma correção necessária, está coerente)."""
    blocos, atual = [], None
    for l in _sem_alerta(parecer).splitlines():
        if re.match(r"\s*#{2,4}\s*\d+\.", l):
            atual = [l, []]
            blocos.append(atual)
        elif atual is not None:
            atual[1].append(l)
    achados = []
    for cab, linhas in blocos:
        corpo = "\n".join(linhas)
        reprovada = "reprovad" in _normalizar(cab) or re.search(r"status\W{0,6}\s*reprovad", _normalizar(corpo))
        if reprovada and _SEM_PROBLEMA.search(corpo):
            achados.append(cab.strip("# ").strip()[:70])
    return achados


def _guardrail_parecer_factory(fontes):
    """
    Parecer do Guardião: (1) Resultado Geral = pior dimensão, (2) dimensão Reprovada não pode dizer que está correta, (3) todo trecho
    entre aspas precisa existir no texto revisado. `fontes` é a lista de tarefas cujo texto é revisado.
    """

    def guardrail(saida):
        base = _guardrail_parecer_geral(saida)
        if base[0] is False:
            return base
        texto = getattr(saida, "raw", None) or str(saida) or ""
        inc = _dimensoes_incoerentes(texto)
        if inc:
            return False, (
                f"A dimensão '{inc[0]}' está Reprovada, mas o próprio apontamento diz que está correta (nenhuma correção necessária). "
                "Se não há problema a corrigir, o status não pode ser Reprovado; se há, descreva o problema com o trecho literal."
            )
        revisado = "\n".join(getattr(getattr(t, "output", None), "raw", None) or "" for t in fontes) + "\n" + _TEXTO_PERMITIDO["texto"]
        if revisado.strip():
            ruins = _citacoes_inexistentes(texto, revisado)
            if ruins:
                return False, (
                    "O parecer cita trechos que não existem no texto revisado: " + "; ".join(f'"{r}"' for r in ruins) + ". Cada trecho entre aspas "
                    "deve ser cópia exata do documento (não parafraseie nem junte palavras). Se não achar o trecho, o apontamento não existe."
                )
        return True, saida

    return guardrail


def _guardrail_aplicacao_g1_factory(brief_task, portao_task):
    """Reemissão do brief: passa pela trava do brief e não pode perder [VALIDAR] do original quando o humano não deu feedback escrito."""

    def guardrail(saida):
        base = _guardrail_brief(saida)
        if base[0] is False:
            return base
        original = getattr(getattr(brief_task, "output", None), "raw", None) or ""
        portao = getattr(getattr(portao_task, "output", None), "raw", None) or ""
        sem_feedback = (not portao) or "nenhum feedback humano" in _normalizar(portao)
        if original and sem_feedback:
            antes = _sem_alerta(original).lower().count("[validar")
            depois = _sem_alerta(getattr(saida, "raw", None) or str(saida) or "").lower().count("[validar")
            if depois < antes:
                return False, (
                    f"O brief original tem {antes} marcações [VALIDAR] e a reemissão tem {depois}. Sem feedback humano escrito, nenhuma pendência foi "
                    "resolvida: mantenha todas as marcações [VALIDAR] e não altere o que já estava correto no brief original."
                )
        return True, saida

    return guardrail


def _carregar_rotina():
    import yaml

    caminho = Path(__file__).resolve().parent / "config" / "rotina_midia.yaml"
    try:
        return yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}


_ROTINA = _carregar_rotina()
_ALERTA_PCT = int((_ROTINA.get("parametros") or {}).get("alerta_consumo_pct", 90))


def _lista(itens, sep="; "):
    return sep.join(str(i) for i in (itens or []))


def _bloco_operacao():
    r = _ROTINA.get("operacao") or {}
    if not r:
        return ""
    verba = " ".join(str(x).replace("{alerta_consumo_pct}", str(_ALERTA_PCT)) for x in r.get("verba", []))
    return (
        "\n    ROTINA PARAMETRIZADA DO GESTOR DE MÍDIA (Vanguarda Martech; inclua no plano as seções \"Insumos e pendências\", \"Rotina operacional\" e \"Alçadas\"): "
        f"INSUMOS: {' '.join(str(r.get('insumos_obrigatorios', '')).split())} "
        f"VERBA: {verba} "
        f"FLUXO DE NOVA CAMPANHA (a ser executado só depois do G3): {_lista(r.get('fluxo_nova_campanha'), ' → ')}. "
        f"OTIMIZAÇÃO DIÁRIA: {_lista(r.get('otimizacao_diaria'), ' → ')}. SEMANAL: {r.get('rotina_semanal', '')} "
        f"COPIES: {r.get('copies', '')} KPIs ACOMPANHADOS: {_lista(_ROTINA.get('kpis'), ', ')}. "
        f"AUTONOMIA DO GESTOR: {_lista(r.get('autonomia'))}. EXIGE AUTORIZAÇÃO (Supervisor ou Diretoria): {_lista(r.get('exige_autorizacao'))}. "
        f"PRAZOS CRÍTICOS: {r.get('prazos_criticos', '')}"
    )


def _bloco_auditoria():
    a = _ROTINA.get("auditoria") or {}
    itens = a.get("itens") or []
    if not itens:
        return ""
    lista = "; ".join(f"{i['chave']} ({str(i['pergunta']).replace('{alerta_consumo_pct}', str(_ALERTA_PCT))})" for i in itens)
    return f"\n    ITENS DA AUDITORIA TÉCNICA (um por linha AUDITORIA): {lista}. {' '.join(str(a.get('regra', '')).split())}"


def _bloco_medicao():
    m = _ROTINA.get("medicao_relatorio") or {}
    if not m:
        return ""
    return (
        "\n    ROTINA PARAMETRIZADA DE MEDIÇÃO: AUDITORIA DE PIXEL E RASTREAMENTO (checklist antes do G3): "
        f"{_lista(m.get('auditoria_rastreamento'), ' → ')}. RELATÓRIO MENSAL (fluxo): {_lista(m.get('relatorio_mensal'), ' → ')}. "
        f"FECHAMENTO: {m.get('fechamento', '')} KPIs: {_lista(_ROTINA.get('kpis'), ', ')}."
    )


_FALTAS_ROTINA = (
    ("budget pace", r"budget pace|ritmo de consumo", "controle de verba por budget pace"),
    (f"alerta de {_ALERTA_PCT}%", rf"{_ALERTA_PCT}\s?%", f"alerta aos {_ALERTA_PCT}% do orçamento"),
    ("UTM", r"\butm", "parametrização de URLs com UTM"),
    ("revisão técnica do supervisor", r"revis[ãa]o t[ée]cnica|supervisor", "revisão técnica do Supervisor antes de ativar"),
    ("alçadas", r"autoriza[çc][ãa]o|al[çc]ada", "o que exige autorização"),
)


def _faltas_rotina_midia(texto):
    """Elementos da rotina de mídia que o plano precisa trazer e não trouxe."""
    baixo = _sem_alerta(texto).lower()
    return [rot for _, rx, rot in _FALTAS_ROTINA if not re.search(rx, baixo)]


def _g_doc():
    return _com_limite_de_rejeicoes(_guardrail_documento)


def _g_prod():
    return _com_limite_de_rejeicoes(_guardrail_producao)


def _aplicar_pasta_de_saida(tasks: list[Task]) -> str | None:
    """
    Reescreve os output_file das tarefas para caminhos absolutos dentro da pasta gravável,
    aplica a política de portões humanos e devolve o caminho do log (ou None).
    """
    pasta = _resolver_output_dir()
    for t in tasks:
        if t.output_file:
            t.output_file = str(pasta / Path(t.output_file).name) if pasta else None
        if (t.name or "").startswith("aplicacao_g") and "MODO DO PORTÃO:" not in t.description:
            t.description += _MODO_COM_HUMANO if HUMAN_GATES else _MODO_SEM_HUMANO
        if "REGRA DE INSUMOS:" not in t.description and not t.name.startswith("portao_g"):
            t.description += _REGRA_DE_INSUMOS
        if "BASE DE CONHECIMENTO DO CLIENTE" not in t.description and not t.name.startswith("portao_g"):
            t.description += _REGRA_CONTEXTO_CLIENTE
        if t.human_input and not HUMAN_GATES:
            t.human_input = False
            t.description += (
                "\n\nMODO SEM HUMANO NESTA EXECUÇÃO: não há aprovador disponível. Produza apenas o PEDIDO "
                "de aprovação com o campo Decisão = PENDENTE DE APROVAÇÃO HUMANA. É PROIBIDO inventar nome "
                "de aprovador, data de decisão, aprovação ou reprovação. Liste o que o humano precisa decidir "
                "e siga com as entregas como estão, marcando as pendências."
            )
    if LOG_FILE and pasta:
        return str(pasta / Path(LOG_FILE).name)
    return None


# Também na importação: cobre qualquer caminho de carga que não passe por crew().
_garantir_output_dir()


def _blindar_log_em_arquivo() -> None:
    """
    O runtime da plataforma CrewAI pode anexar um log relativo (ex.: output/crew_log.json)
    à crew depois de montada, e gravá-lo a partir de um diretório de trabalho que nós não
    controlamos. Um log que falha nunca deve derrubar uma campanha: antes de cada gravação,
    criamos a pasta do arquivo; se ainda assim falhar, registramos no stderr e seguimos.
    """
    try:
        from crewai.utilities import file_handler as fh
    except Exception:  # noqa: BLE001 - blindagem opcional
        return
    if getattr(fh.FileHandler, "_marketing_ops_blindado", False):
        return
    original_log = fh.FileHandler.log

    def log_resiliente(self, **kwargs):  # type: ignore[no-untyped-def]
        try:
            pasta = os.path.dirname(os.path.abspath(self._path))
            os.makedirs(pasta, exist_ok=True)
            return original_log(self, **kwargs)
        except Exception as exc:  # noqa: BLE001
            import sys

            print(f"[marketing_ops] log em arquivo ignorado: {exc}", file=sys.stderr)
            return None

    fh.FileHandler.log = log_resiliente  # type: ignore[method-assign]
    fh.FileHandler._marketing_ops_blindado = True  # type: ignore[attr-defined]


_blindar_log_em_arquivo()
MODEL_LIGHT = os.getenv("MODEL_LIGHT", MODEL if "MODEL" in os.environ else _PADRAO_LEVE)
MAX_RPM = int(os.getenv("CREW_MAX_RPM", "20"))
WRITE_TOOLS_ENABLED = os.getenv("CREW_ENABLE_WRITE_TOOLS", "false").lower() == "true"
# Portões humanos (G1/G2/G3) pausam a execução à espera de resposta. No terminal isso é um
# prompt; na plataforma CrewAI exige a configuração de Human-in-the-Loop (webhook). Sem
# essa configuração a execução trava ou é descartada, por isso o padrão aqui é desligado:
# os portões viram tarefas normais que produzem o pedido de aprovação como documento.
HUMAN_GATES = os.getenv("CREW_HUMAN_GATES", "false").lower() == "true"
# A memória do CrewAI persiste entre execuções da mesma automação. Num pipeline factual isso é perigoso: fatos
# inventados numa rodada (serviços, baselines, fontes) voltam nas seguintes como "memórias internas" e são
# tratados como verdade (observado). Por isso fica desligada por padrão.
MEMORY_ENABLED = os.getenv("CREW_MEMORY", "false").lower() == "true"

# Ferramentas compartilhadas (instanciadas uma vez). Pesquisa web só com SERPER_API_KEY:
# sem a chave, os agentes trabalham com o briefing, o conhecimento carregado e o scraping
# de URLs informadas, marcando dados externos como [VALIDAR].
search = SerperDevTool() if os.getenv("SERPER_API_KEY") else None
scrape = ScrapeWebsiteTool()
read_file = FileReadTool()
seo_tool = SeoKeywordTool()
analytics_tool = AnalyticsReadTool()
brand_book = BrandBookTool()
crm_tool = CrmReadTool()
paid_media_tool = PaidMediaReadTool()
publish_tool = PublishTool(enabled=WRITE_TOOLS_ENABLED)


def _tools(*itens):
    """Lista de ferramentas sem as indisponíveis (None)."""
    return [t for t in itens if t is not None]


@CrewBase
class MarketingOpsCrew:
    """Pipeline sequencial completo: estratégia → produção → medição/publicação."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ───────────────────────── Agentes ─────────────────────────

    @agent
    def gerente_operacoes(self) -> Agent:
        return Agent(config=self.agents_config["gerente_operacoes"], llm=MODEL, tools=[])

    @agent
    def estrategista_campanhas(self) -> Agent:
        return Agent(
            config=self.agents_config["estrategista_campanhas"],
            llm=MODEL,
            tools=_tools(brand_book, search, read_file),
        )

    @agent
    def pesquisador_mercado(self) -> Agent:
        return Agent(
            config=self.agents_config["pesquisador_mercado"],
            llm=MODEL,
            tools=_tools(brand_book, search, scrape, read_file, seo_tool),
        )

    @agent
    def especialista_seo(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_seo"],
            llm=MODEL,
            tools=_tools(search, scrape, read_file, seo_tool),
        )

    @agent
    def redator_conteudo(self) -> Agent:
        return Agent(
            config=self.agents_config["redator_conteudo"],
            llm=MODEL,
            tools=_tools(brand_book, search, read_file),
        )

    @agent
    def estrategista_social(self) -> Agent:
        return Agent(
            config=self.agents_config["estrategista_social"],
            llm=MODEL,
            tools=_tools(brand_book, search, read_file),
        )

    @agent
    def especialista_email_crm(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_email_crm"],
            llm=MODEL,
            tools=[brand_book, read_file, crm_tool],
        )

    @agent
    def gestor_midia_paga(self) -> Agent:
        return Agent(
            config=self.agents_config["gestor_midia_paga"],
            llm=MODEL,
            tools=_tools(brand_book, search, read_file, paid_media_tool),
        )

    @agent
    def supervisor_midia_paga(self) -> Agent:
        return Agent(
            config=self.agents_config["supervisor_midia_paga"],
            llm=MODEL,
            tools=[read_file, paid_media_tool],
        )

    @agent
    def diretor_arte(self) -> Agent:
        return Agent(config=self.agents_config["diretor_arte"], llm=MODEL, tools=[brand_book, read_file])

    @agent
    def analista_dados(self) -> Agent:
        return Agent(
            config=self.agents_config["analista_dados"],
            llm=MODEL,
            tools=[read_file, analytics_tool],
        )

    @agent
    def guardiao_marca_compliance(self) -> Agent:
        return Agent(
            config=self.agents_config["guardiao_marca_compliance"],
            llm=MODEL,
            tools=_tools(brand_book, search, read_file),
        )

    @agent
    def revisor_qualidade(self) -> Agent:
        return Agent(
            config=self.agents_config["revisor_qualidade"],
            llm=MODEL,
            tools=_tools(brand_book, read_file),
        )

    @agent
    def coordenador_publicacao(self) -> Agent:
        return Agent(
            config=self.agents_config["coordenador_publicacao"],
            llm=MODEL_LIGHT,
            tools=[read_file, publish_tool],
        )

    # ───────────────────────── Tarefas · Fase 1 ─────────────────────────

    @task
    def pesquisa_mercado(self) -> Task:
        return Task(guardrail=_g_doc(), guardrail_max_retries=2, config=self.tasks_config["pesquisa_mercado"])

    @task
    def mapa_seo(self) -> Task:
        return Task(guardrail=_g_doc(), guardrail_max_retries=2, config=self.tasks_config["mapa_seo"], context=[self.pesquisa_mercado()])

    @task
    def brief_estrategico(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_brief), guardrail_max_retries=2,
            config=self.tasks_config["brief_estrategico"],
            context=[self.pesquisa_mercado(), self.mapa_seo()],
        )

    @task
    def revisao_g1(self) -> Task:
        return Task(guardrail=_com_limite_de_rejeicoes(_guardrail_parecer_factory([self.brief_estrategico()])), guardrail_max_retries=2,
                    config=self.tasks_config["revisao_g1"], context=[self.brief_estrategico()])

    @task
    def portao_g1(self) -> Task:
        return Task(
            guardrail=_guardrail_portao_factory(self.revisao_g1()), guardrail_max_retries=2,
            config=self.tasks_config["portao_g1"],
            context=[self.brief_estrategico(), self.revisao_g1()],
        )

    @task
    def aplicacao_g1(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_aplicacao_g1_factory(self.brief_estrategico(), self.portao_g1())), guardrail_max_retries=2,
            config=self.tasks_config["aplicacao_g1"],
            context=[self.brief_estrategico(), self.revisao_g1(), self.portao_g1()],
        )

    # ───────────────────────── Tarefas · Fase 2 ─────────────────────────

    @task
    def producao_conteudo(self) -> Task:
        return Task(
            guardrail=_g_prod(), guardrail_max_retries=2,
            config=self.tasks_config["producao_conteudo"],
            context=[self.aplicacao_g1(), self.mapa_seo()],
        )

    @task
    def calendario_social(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_calendario), guardrail_max_retries=2,
            config=self.tasks_config["calendario_social"],
            context=[self.aplicacao_g1(), self.producao_conteudo(), self.pesquisa_mercado()],
        )

    @task
    def fluxos_email(self) -> Task:
        return Task(
            guardrail=_g_prod(), guardrail_max_retries=2,
            config=self.tasks_config["fluxos_email"],
            context=[self.aplicacao_g1(), self.producao_conteudo()],
        )

    def _com_rotina(self, nome, bloco):
        """Configuração da tarefa com o bloco da rotina parametrizada (config/rotina_midia.yaml) anexado à descrição."""
        cfg = dict(self.tasks_config[nome])
        cfg["description"] = str(cfg["description"]).rstrip() + (bloco or "")
        return cfg

    @task
    def plano_midia_paga(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_midia_factory(self.aplicacao_g1())), guardrail_max_retries=2,
            config=self._com_rotina("plano_midia_paga", _bloco_operacao()),
            context=[self.aplicacao_g1(), self.mapa_seo(), self.pesquisa_mercado(), self.fluxos_email()],
        )

    @task
    def auditoria_midia(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_auditoria_factory(self.plano_midia_paga(), self.aplicacao_g1())), guardrail_max_retries=2,
            config=self._com_rotina("auditoria_midia", _bloco_auditoria()),
            context=[self.plano_midia_paga(), self.aplicacao_g1()],
        )

    @task
    def direcao_arte(self) -> Task:
        return Task(
            guardrail=_g_prod(), guardrail_max_retries=2,
            config=self.tasks_config["direcao_arte"],
            context=[
                self.aplicacao_g1(),
                self.producao_conteudo(),
                self.calendario_social(),
                self.fluxos_email(),
                self.plano_midia_paga(),
            ],
        )

    @task
    def rubrica_qa(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_rubrica_factory({
                "CONTEUDO": (self.producao_conteudo(), None),
                "CALENDARIO": (self.calendario_social(), None),
                "EMAIL": (self.fluxos_email(), None),
                "MIDIA": (self.plano_midia_paga(), self.aplicacao_g1()),
            })), guardrail_max_retries=2,
            config=self.tasks_config["rubrica_qa"],
            context=[
                self.auditoria_midia(),
                self.aplicacao_g1(),
                self.producao_conteudo(),
                self.calendario_social(),
                self.fluxos_email(),
                self.plano_midia_paga(),
            ],
        )

    @task
    def revisao_g2(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_parecer_factory(
                [self.producao_conteudo(), self.calendario_social(), self.fluxos_email(), self.plano_midia_paga(), self.direcao_arte()])), guardrail_max_retries=2,
            config=self.tasks_config["revisao_g2"],
            context=[
                self.producao_conteudo(),
                self.calendario_social(),
                self.fluxos_email(),
                self.plano_midia_paga(),
                self.direcao_arte(),
            ],
        )

    @task
    def portao_g2(self) -> Task:
        return Task(
            guardrail=_guardrail_portao_factory(self.revisao_g2(), self.rubrica_qa(), self.auditoria_midia()), guardrail_max_retries=2,
            config=self.tasks_config["portao_g2"],
            context=[
                self.revisao_g2(),
                self.rubrica_qa(),
                self.auditoria_midia(),
                self.producao_conteudo(),
                self.calendario_social(),
                self.fluxos_email(),
                self.plano_midia_paga(),
                self.direcao_arte(),
            ],
        )

    @task
    def aplicacao_g2(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_aplicacao_g2), guardrail_max_retries=2,
            config=self.tasks_config["aplicacao_g2"],
            context=[
                self.portao_g2(),
                self.revisao_g2(),
                self.rubrica_qa(),
                self.auditoria_midia(),
                self.producao_conteudo(),
                self.calendario_social(),
                self.fluxos_email(),
                self.plano_midia_paga(),
                self.direcao_arte(),
            ],
        )

    # ───────────────────────── Tarefas · Fase 3 ─────────────────────────

    @task
    def plano_medicao(self) -> Task:
        return Task(
            guardrail=_g_doc(), guardrail_max_retries=2,
            config=self._com_rotina("plano_medicao", _bloco_medicao()),
            context=[self.aplicacao_g1(), self.calendario_social(), self.fluxos_email(), self.plano_midia_paga()],
        )

    @task
    def pacote_publicacao(self) -> Task:
        return Task(
            guardrail=_g_doc(), guardrail_max_retries=2,
            config=self.tasks_config["pacote_publicacao"],
            context=[
                self.aplicacao_g2(),
                self.plano_medicao(),
                self.direcao_arte(),
                self.producao_conteudo(),
                self.calendario_social(),
                self.fluxos_email(),
                self.plano_midia_paga(),
            ],
        )

    @task
    def revisao_g3(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_parecer_factory([self.pacote_publicacao(), self.plano_medicao(), self.aplicacao_g2()])), guardrail_max_retries=2,
            config=self.tasks_config["revisao_g3"],
            context=[self.pacote_publicacao(), self.plano_medicao(), self.aplicacao_g2()],
        )

    @task
    def portao_g3(self) -> Task:
        return Task(
            guardrail=_guardrail_portao_factory(self.revisao_g3()), guardrail_max_retries=2,
            config=self.tasks_config["portao_g3"],
            context=[self.pacote_publicacao(), self.revisao_g3(), self.plano_midia_paga()],
        )

    @task
    def aplicacao_g3(self) -> Task:
        return Task(
            guardrail=_g_doc(), guardrail_max_retries=2,
            config=self.tasks_config["aplicacao_g3"],
            context=[
                self.portao_g3(),
                self.pacote_publicacao(),
                self.revisao_g3(),
                self.plano_midia_paga(),
            ],
        )

    @task
    def execucao_publicacao(self) -> Task:
        return Task(
            guardrail=_g_doc(), guardrail_max_retries=2,
            config=self.tasks_config["execucao_publicacao"],
            context=[self.aplicacao_g3(), self.pacote_publicacao()],
        )

    @task
    def sumario_executivo(self) -> Task:
        return Task(
            guardrail=_g_doc(), guardrail_max_retries=2,
            config=self.tasks_config["sumario_executivo"],
            context=[
                self.aplicacao_g1(),
                self.aplicacao_g2(),
                self.aplicacao_g3(),
                self.execucao_publicacao(),
                self.plano_medicao(),
            ],
        )

    # ───────────────────────── Crew ─────────────────────────

    @crew
    def crew(self) -> Crew:
        log_file = _aplicar_pasta_de_saida(self.tasks)
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=MEMORY_ENABLED,  # desligada por padrão: ver CREW_MEMORY
            max_rpm=MAX_RPM,
            verbose=True,
            output_log_file=log_file,
            before_kickoff_callbacks=[_injetar_contexto_cliente],
            chat_llm=MODEL,  # habilita a aba Chat da plataforma (orquestra inputs e dispara a crew)
        )
