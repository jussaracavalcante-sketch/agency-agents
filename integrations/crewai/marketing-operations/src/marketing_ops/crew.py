"""
crew.py — Equipe de Operação de Marketing (CrewAI)

Define os 12 agentes e as 21 tarefas do pipeline de campanha (a 22ª, relatório de
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


def _guardrail_documento(saida):  # sem anotação de retorno: o validador do CrewAI a compara com tipos reais
    """
    Rejeita a saída de uma tarefa de documento quando ela é uma desculpa em vez de entrega: curta demais ou
    dizendo que não conseguiu acessar insumos. Os insumos estão sempre no contexto; a tarefa é refeita.
    """
    texto = (getattr(saida, "raw", None) or str(saida) or "").strip()
    baixo = texto.lower()
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


def _guardrail_portao_factory(revisao_task):
    """
    Portão humano: o pedido deve copiar o parecer do Guardião (mesmo resultado, pelo menos 70% das linhas) e ter as
    seções obrigatórias. Rejeita paráfrase e a troca de "Reprovado" por outro resultado.
    """

    tentativas = {"n": 0}

    def guardrail(saida):  # sem anotação de retorno (ver _guardrail_documento)
        veredito = _checar_portao(saida)
        if veredito[0] is False:
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


def _com_limite_de_rejeicoes(guardrail, maximo=2):
    """Aceita a saída depois de `maximo` rejeições: guardrail esgotado derruba a execução inteira na plataforma."""
    estado = {"n": 0}

    def envelope(saida):  # sem anotação de retorno (ver _guardrail_documento)
        veredito = guardrail(saida)
        if veredito[0] is False:
            estado["n"] += 1
            if estado["n"] > maximo:
                return True, saida
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
    r"\b(o|a|os|as|ao|do|pelo) melhor(es)?\b|\bmelhor (atendimento|cuidado|experi[êe]ncia|hospital|cl[íi]nica|estrutura)\b|"
    r"tecnologia de ponta|tecnologias? de ponta|equipamentos? de [úu]ltima gera[çc][ãa]o|[úu]ltima gera[çc][ãa]o|estado da arte|"
    r"diagn[óo]sticos? precis\w+|tratamentos? eficaz\w*|confian[çc]a em cada diagn[óo]stico|seguran[çc]a em cada tratamento|"
    r"garant\w+[^.\n]{0,60}(precis[ãa]o|seguran[çc]a|excel[êe]ncia|qualidade|efici[êe]ncia|resultados?|cura|"
    r"recupera[çc][ãa]o|lgpd|conformidade|ader[êe]ncia|atendimento|cuidado|diagn[óo]stico|tratamento)",
    re.I,
)
_LINHA_NEUTRA = re.compile(r"\[VALIDAR|\bsem (usar )?depoimento|proibid|n[ãa]o (use|usar|incluir|propor|citar)|evitar", re.I)


_PLACEHOLDERS = re.compile(r"example\.(com|org|net)|exemplo\.com(\.br)?|lorem ipsum|seu-?site\.com|\[(inserir|link|url)[^\]]*\]", re.I)


def _placeholders(texto):
    """Link ou texto de exemplo que iria para publicação como se fosse real."""
    return sorted({m.group(0).lower() for m in _PLACEHOLDERS.finditer(texto or "")})


def _claims_proibidos(texto):
    """Linhas com depoimento/testemunho/superlativo sem [VALIDAR] nem aviso de que o item é proibido."""
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
            "A saída contém link ou texto de exemplo (" + ", ".join(ph) + "). Peça publicável não pode ter placeholder: use "
            "[VALIDAR: link] no lugar e reemita o documento completo."
        )
    return True, saida


_INPUTS_ATUAIS = {}


def _cobertura_calendario(texto):
    """Devolve a mensagem de erro se o calendário não cobre todas as semanas da campanha; None se cobre (ou não há como medir)."""
    try:
        semanas = int(str(_INPUTS_ATUAIS.get("duracao_semanas", "")).strip())
    except ValueError:
        return None
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


def _guardrail_brief(saida):
    """O brief usa o objetivo do briefing literalmente e não cria baselines que ninguém informou."""
    base = _guardrail_producao(saida)
    if base[0] is False:
        return base
    texto = getattr(saida, "raw", None) or str(saida) or ""
    objetivo = _normalizar(str(_INPUTS_ATUAIS.get("objetivo", "")))
    if objetivo and objetivo not in _normalizar(texto):
        return False, (
            "O brief não reproduz o objetivo do briefing. Copie o objetivo literalmente, sem trocar a meta, o prazo ou o "
            f"baseline: \"{_INPUTS_ATUAIS.get('objetivo')}\". Não substitua por outro objetivo (percentuais, ocupação, etc.)."
        )
    permitido = _normalizar(_TEXTO_PERMITIDO["texto"])
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
        return Task(guardrail=_g_doc(), guardrail_max_retries=2, config=self.tasks_config["revisao_g1"], context=[self.brief_estrategico()])

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
            guardrail=_com_limite_de_rejeicoes(_guardrail_sem_claims), guardrail_max_retries=2,
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

    @task
    def plano_midia_paga(self) -> Task:
        return Task(
            guardrail=_g_prod(), guardrail_max_retries=2,
            config=self.tasks_config["plano_midia_paga"],
            context=[self.aplicacao_g1(), self.mapa_seo(), self.pesquisa_mercado(), self.fluxos_email()],
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
    def revisao_g2(self) -> Task:
        return Task(
            guardrail=_g_doc(), guardrail_max_retries=2,
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
            guardrail=_guardrail_portao_factory(self.revisao_g2()), guardrail_max_retries=2,
            config=self.tasks_config["portao_g2"],
            context=[
                self.revisao_g2(),
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
            config=self.tasks_config["plano_medicao"],
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
            guardrail=_g_doc(), guardrail_max_retries=2,
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
