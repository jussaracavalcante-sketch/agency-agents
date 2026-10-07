"""
crew.py — Equipe de Operação de Marketing (CrewAI)

Define os 14 agentes e as 36 tarefas do pipeline de campanha (produção → revisão → correção automática → revisão final → portão; a aplicação pós-portão é condicional ao feedback humano) (a 24ª, relatório de
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
    "invente atributos da marca. Se o contexto trouxer a seção [AJUSTES DO ADMINISTRADOR], siga as instruções da subseção com o seu papel; "
    "elas complementam a tarefa e não liberam dado sem fonte nem removem marcações [VALIDAR].\n{contexto_cliente}"
)
_LIMITE_CONTEXTO_CLIENTE = 8000


_SERVICOS_LISTA = ("cirurgia", "cirurgia robótica", "telemedicina", "UTI", "cardiologia", "ortopedia", "urologia", "oncologia", "neurologia", "maternidade",
                   "pediatria", "pronto-socorro", "hemodinâmica", "transplante", "centro cirúrgico")
_MARCA_SERVICOS = "\n\n[SERVIÇOS NÃO INFORMADOS]"
_MARCA_AJUSTES = "[AJUSTES DO ADMINISTRADOR]"


def _sem_bloco_servicos(inputs):
    """Cópia dos inputs com o contexto do cliente sem o bloco de serviços que a própria crew acrescenta (numa retomada ele já vem anexado)."""
    limpo = dict(inputs)
    if isinstance(limpo.get("contexto_cliente"), str):
        limpo["contexto_cliente"] = limpo["contexto_cliente"].split(_MARCA_SERVICOS)[0]
    return limpo


def _sem_bloco_ajustes(texto):
    """Contexto sem a seção [AJUSTES DO ADMINISTRADOR] (instruções por agente que o portal acrescenta): ela orienta, não autoriza termos."""
    t = str(texto or "")
    if _MARCA_AJUSTES not in t:
        return t
    antes, _, resto = t.partition(_MARCA_AJUSTES)
    m = re.search(r"\n(?=# |\[|---)", resto)      # a seção termina no próximo título de nível 1, bloco [..] ou separador
    return antes + (resto[m.start():] if m else "")


_LISTA_NEGATIVA = "[lista negativa"


def _sem_secoes_negativas(texto):
    """
    Remove do contexto as seções marcadas "[LISTA NEGATIVA ...]" (regras inegociáveis e "evitar" do setup do cliente no VJOB). Elas citam termos
    justamente para PROIBI-LOS ("a melhor locadora da Flórida", "garantia total"); se contassem como texto permitido, a trava de claims os liberaria.
    A seção vai do título marcado até o próximo título de nível 1 ou 2.
    """
    saida, pulando = [], False
    for linha in str(texto or "").split("\n"):
        titulo = re.match(r"^#{1,2}\s", linha) is not None
        if titulo:
            pulando = _LISTA_NEGATIVA in linha.lower()
        if not pulando:
            saida.append(linha)
    return "\n".join(saida)


def _texto_permitido(inputs):
    """Texto que o briefing e a base do cliente permitem citar. Não inclui o bloco de serviços não informados nem os ajustes do administrador, para eles não se autorizarem."""
    limpo = _sem_bloco_servicos(inputs)
    if isinstance(limpo.get("contexto_cliente"), str):
        limpo["contexto_cliente"] = _sem_secoes_negativas(_sem_bloco_ajustes(limpo["contexto_cliente"]))
    return " ".join(str(v) for v in limpo.values()).lower()


def _servicos_nao_informados(permitido):
    return ", ".join(sv for sv in _SERVICOS_LISTA if not re.search(rf"\b{re.escape(sv.lower())}\b", permitido)) or "nenhum"


def _injetar_contexto_cliente(inputs):
    """
    before_kickoff: carrega a base de conhecimento do cliente informado em inputs['cliente'] e a expõe como
    inputs['contexto_cliente'], usada por todas as tarefas. Determinístico: não depende de o agente decidir
    consultar a ferramenta. Ao fim do contexto acrescenta o bloco [SERVIÇOS NÃO INFORMADOS]: serviços e especialidades que o briefing e a base
    não citam e que as peças não podem usar (o modelo costuma "lembrar" serviços reais do cliente que ninguém informou). Vai dentro do
    contexto, e não como campo novo, porque a plataforma exige todos os campos {...} das tarefas antes de rodar este callback.
    """
    inputs = dict(inputs or {})
    if inputs.get("contexto_cliente"):
        inputs["contexto_cliente"] = str(inputs["contexto_cliente"]).split(_MARCA_SERVICOS)[0]
        definir_contexto_do_portal(str(inputs.get("cliente") or ""), str(inputs["contexto_cliente"]))
    else:
        cliente = str(inputs.get("cliente") or "").strip()
        if not cliente:
            inputs["contexto_cliente"] = "[SEM CLIENTE INFORMADO] Marque decisões de marca como [VALIDAR]."
        else:
            texto = BrandBookTool()._run(cliente)
            inputs["contexto_cliente"] = texto[:_LIMITE_CONTEXTO_CLIENTE]
    permitido = _texto_permitido(inputs)
    inputs["contexto_cliente"] += (
        f"{_MARCA_SERVICOS} {_servicos_nao_informados(permitido)}. O briefing e a base do cliente não citam esses serviços: não podem ser tema, "
        "título, exemplo nem copy; só aparecem com [VALIDAR]. Use apenas os serviços que constam do briefing e da base."
    )
    _TEXTO_PERMITIDO["texto"] = permitido
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
    "não consegui obter",
    "não consigo obter",
    "recomendo verificar o acesso",
    "entre em contato com a equipe de ti",
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
def _fim_do_documento(t):
    """
    Posição do fechamento do bloco ``` onde o documento termina, ou None. Com número PAR de cercas é a última. Com número ÍMPAR e texto que abre com ```,
    o comentário do agente costuma vir entre o fechamento do documento e uma cerca solta no fim (```...```, "Notas para o Diretor de Arte", ```):
    o documento termina na segunda cerca.
    """
    n = t.count("```")
    if n < 2:
        return None
    if n % 2 == 0:
        return t.rfind("```") + 3
    if t.lstrip().startswith("```"):
        primeira = t.find("```")
        segunda = t.find("```", primeira + 3)
        return segunda + 3 if segunda > 0 else None
    return None


def _texto_apos_documento(texto):
    """Texto escrito depois do fechamento do documento (comentário do agente fora do bloco ```); vazio se não houver."""
    t = _sem_alerta(texto or "")
    fim = _fim_do_documento(t)
    if fim is None:
        return ""
    resto = t[fim:].replace("```", "").strip()
    return resto if len(resto) > 20 else ""


_ABERTURA_DE_CONVERSA = re.compile(
    r"^(para (proceder|aplicar|atender|seguir)|vou |vamos|a seguir|abaixo (est[aá]|segue|apresento)|segue |com base n[oa]s?|claro[,!.]|certo[,!.]|entendi|aqui est[aá]|ok[,!.]|"
    r"prezad[oa]s?)\b",
    re.I,
)


_PALAVRAS_EN = frozenset("the and with has have been will is are was were as per to for of if please that this all any further i'll i we our your you its be by on at from it not or but also should must can may these those into in an how why what about care trust medical health patients building techniques best better".split())
_PALAVRAS_PT = frozenset("o a os as de do da dos das e que para com um uma em no na nos nas por se ao à são é não ou mais como sua seu suas seus foi ser".split())


def _trecho_em_ingles(trecho):
    palavras = re.findall(r"[a-zA-Zà-úÀ-Ú']+", trecho.lower())
    if len(palavras) < 6:
        return False
    en = sum(1 for p in palavras if p in _PALAVRAS_EN)
    pt = sum(1 for p in palavras if p in _PALAVRAS_PT)
    return en / len(palavras) >= 0.28 and pt / len(palavras) <= 0.1


_PALAVRAS_TITULO_EN = frozenset("of and the legal claim technical visual details deliverables completeness summary findings recommendations risks overview issues proper".split())
_PT_PT = {"equipas": "equipes", "equipa": "equipe", "utilizadores": "usuários", "utilizador": "usuário", "telemóvel": "celular", "telemóveis": "celulares",
          "ecrã": "tela", "ecrãs": "telas", "contactos": "contatos", "contacto": "contato"}
_ECRA_COM_ARTIGO = re.compile(r"\b(no|do|ao|um|o|nos|dos|aos|os)\s+(ecrã|ecrãs)\b", re.I)
_ECRA_ARTIGO = {"no": "na", "do": "da", "ao": "à", "um": "uma", "o": "a", "nos": "nas", "dos": "das", "aos": "às", "os": "as"}
_PT_PT_RE = re.compile(r"\b(" + "|".join(sorted(_PT_PT, key=len, reverse=True)) + r")\b", re.I)


def _titulo_em_ingles(linha):
    """Título ou rótulo curto em inglês ("### Completeness of Deliverables", "**Legal and Claim Compliance:**"): duas palavras de título em inglês, ou "of the"."""
    l = re.sub(r"^[\s#>*_\-\d.)]+|[\s*_:]+$", "", linha)
    palavras = re.findall(r"[a-zA-Z']+", l.lower())
    if not 2 <= len(palavras) <= 7:
        return False
    return sum(1 for p in palavras if p in _PALAVRAS_TITULO_EN) >= 2 and not any(p in _PALAVRAS_PT for p in palavras)


def _portugues_de_portugal(texto):
    """Palavras do português de Portugal ("equipas", "utilizadores", "ecrã"): a crew escreve em português do Brasil."""
    return sorted({m.group(0).lower() for m in _PT_PT_RE.finditer(_sem_alerta(texto or ""))})


def _linha_em_ingles(texto):
    """Primeira frase em inglês (inclusive numa célula de tabela; a crew escreve em português do Brasil); vazio se não houver."""
    for linha in _sem_alerta(texto or "").splitlines():
        l = linha.strip()
        if not l or l.startswith("```"):
            continue
        if len(l) < 90 and _titulo_em_ingles(l):
            return l[:80]
        if l.startswith("#"):
            continue
        if l.startswith("|"):
            for celula in l.strip("|").split("|"):
                c = celula.strip()
                if c.count(" ") >= 4 and _trecho_em_ingles(c):
                    return c[:80]
        elif l.count(" ") >= 5 and _trecho_em_ingles(l):
            return l[:80]
    return ""


_NOTA_FINAL = re.compile(r"^[\s>*_-]*(nota|observa[çc][ãa]o|obs\.?|aviso|coment[áa]rio)\s*[:：]", re.I)
_MARCADOR_MALFORMADO = re.compile(r"\[\s*VALIDAR\s+(?!M[ÉE]DICO\s*\])[^\]:]{1,40}\]", re.I)


def _nota_final(texto):
    """Última linha do documento quando é uma nota do agente ("**Nota:** algumas seções requerem confirmação…"); vazio se não houver."""
    linhas = [l for l in _sem_alerta(texto or "").splitlines() if l.strip() and l.strip() != "```"]
    if not linhas:
        return ""
    ultima = linhas[-1].strip()
    return ultima[:90] if _NOTA_FINAL.match(ultima) and not ultima.startswith("|") else ""


def _marcadores_malformados(texto):
    """Marcadores inventados a partir de [VALIDAR] ("[VALIDAR NOS UM]", "[VALIDAR URGENTE]"): só existem [VALIDAR], [VALIDAR MÉDICO] e [VALIDAR: motivo]."""
    return sorted({m.group(0) for m in _MARCADOR_MALFORMADO.finditer(_sem_alerta(texto or ""))})


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
    ingles = _linha_em_ingles(texto)
    if ingles:
        return False, (
            f"A saída tem frase em inglês (\"{ingles}\"). Escreva tudo em português do Brasil, só o documento, sem introdução nem fechamento em outro idioma."
        )
    nota = _nota_final(texto)
    if nota:
        return False, (
            f"O documento termina com uma nota do agente (\"{nota}\"). Entregue só o documento: a última linha é a última seção, sem nota, "
            "observação ou aviso sobre pendências (as pendências já estão marcadas [VALIDAR] no texto)."
        )
    malformados = _marcadores_malformados(texto)
    if malformados:
        return False, (
            "Marcador inválido: " + ", ".join(malformados) + ". Os únicos marcadores são [VALIDAR], [VALIDAR MÉDICO] e [VALIDAR: motivo]."
        )
    pt_pt = _portugues_de_portugal(texto)
    if pt_pt:
        return False, (
            "A saída usa português de Portugal (" + ", ".join(pt_pt) + "). Escreva em português do Brasil (equipe, usuário, tela, celular, contato)."
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


# Portões: há feedback humano escrito? Preenchido pela trava do portão a partir da saída final dele. As tarefas de aplicação pós-portão
# são condicionais a isso: aprovação pura ("Aprovado.") não reescreve nada, porque as correções já aconteceram antes do portão.
_FEEDBACK = {"G1": False, "G2": False, "G3": False}


def _ha_feedback_humano(texto):
    n = _normalizar(texto)
    return ("ajustes pedidos" in n or "devolvido com feedback" in n) and "nenhum feedback humano" not in n.split("parecer do guardi")[0]


def _tem_feedback(portao):
    return bool(_FEEDBACK.get(portao))


class _Vigente:
    """Versão vigente de uma peça: a última tarefa da lista que produziu texto (reemissão pós-portão, se rodou; senão a versão corrigida antes do portão)."""

    def __init__(self, *tarefas):
        self._tarefas = tarefas

    @property
    def output(self):
        for t in reversed(self._tarefas):
            raw = getattr(getattr(t, "output", None), "raw", None)
            if raw and str(raw).strip():
                return type("Saida", (), {"raw": raw})()
        return None


_MARCA_PENDENTE = "> AJUSTES PENDENTES"


def _com_copia_sem_feedback(portao_task, correcao_task, guardrail):
    """
    Aplicação pós-portão sem ConditionalTask (a CrewAI AMP falha ao retomar o fluxo com ela: AttributeError 'reloaded'). Se o portão foi aprovado sem
    feedback humano, a saída é a versão corrigida COPIADA POR CÓDIGO (o modelo não reescreve nada); com feedback, vale a reemissão e a trava normal.
    """

    def g(saida):
        portao = getattr(getattr(portao_task, "output", None), "raw", None) or ""
        if not _ha_feedback_humano(portao):
            orig = getattr(getattr(correcao_task, "output", None), "raw", None) or ""
            if orig.strip():
                return True, orig
        return guardrail(saida)

    return g


def _guardrail_reemissao_factory(original_task, nome, base):
    """
    Reemissão de uma peça (correção antes do portão ou aplicação do feedback humano): passa pela trava da própria peça (`base`), não pode ser esqueleto,
    não pode encolher abaixo de 60% da versão anterior e tem de ser a peça, não um registro ("versão original", "sem necessidade de reemissão").
    """

    def guardrail(saida):
        r = base(saida)
        if r[0] is False:
            return r
        texto = _sem_alerta(getattr(saida, "raw", None) or str(saida) or "")
        esq = _esqueleto(texto)
        if esq:
            return False, (
                f"A reemissão de {nome} é um esqueleto: " + "; ".join(f'"{e}"' for e in esq[:3]) + ". Entregue a peça INTEIRA, com todas as seções, campos, "
                "tabelas e textos, trocando só o que o ajuste pede."
            )
        if re.search(r"vers[ãa]o original|sem necessidade de reemiss|n[ãa]o (h[áa]|foi) (necess[áa]ri[ao]|preciso) reemitir|mantida sem altera", texto, re.I) and _tamanho_util(texto) < 1500:
            return False, f"A saída é um registro, não a peça. Esta tarefa entrega {nome} completo, mesmo que o ajuste seja pequeno: copie a peça inteira com o ajuste aplicado."
        orig = getattr(getattr(original_task, "output", None), "raw", None) or ""
        if orig and _tamanho_util(orig) > 600 and _tamanho_util(texto) < 0.6 * _tamanho_util(orig):
            pct = round(100 * _tamanho_util(texto) / _tamanho_util(orig))
            return False, (
                f"A reemissão de {nome} ficou com {pct}% do tamanho da versão anterior. Reemitir é copiar a peça inteira (metadados, texto, tabelas, todos os "
                "e-mails e seções) trocando só o trecho ajustado; não resuma."
            )
        if orig and _tamanho_util(orig) > 600 and _tamanho_util(texto) > _LIMITE_CRESCIMENTO * _tamanho_util(orig):
            pct = round(100 * _tamanho_util(texto) / _tamanho_util(orig))
            return False, (
                f"A reemissão de {nome} ficou com {pct}% do tamanho da versão anterior: cresceu demais. Reemitir é trocar só o trecho que o ajuste pede; "
                "não acrescente semanas, posts, valores, canais nem seções que a versão anterior não tinha."
            )
        return True, saida

    return guardrail


_LIMITE_CRESCIMENTO = 1.3


def _sem_autocertificacao(texto):
    """Remove da reemissão as linhas (fora de tabela) em que o próprio agente certifica conformidade ou afirma que os ajustes foram cumpridos."""
    saida, tirou = [], False
    for linha in (texto or "").splitlines():
        if not linha.strip().startswith("|") and (_PLACEHOLDERS.search(linha) or _AUTOCERTIFICACAO.search(linha)):
            tirou = True
            continue
        saida.append(linha)
    return "\n".join(saida), tirou


_AUTOCERTIFICACAO = re.compile(
    r"(ajustes|corre[çc][õo]es|altera[çc][õo]es)[^.\n]{0,40}(foram|foi) (aplicad|incorporad|realizad|feit)\w+|"
    r"todos os (ajustes|pontos|feedbacks)[^.\n]{0,60}(atendid|aplicad|incorporad|considerad)\w*|"
    r"(conforme|em conformidade com) (o )?(feedback|pedido|cfm|conar|anvisa|lgpd)|"
    r"(pe[çc]a|calend[áa]rio|conte[úu]do|plano)[^.\n]{0,40}(est[áa]|fica) (em conformidade|conforme|aprovad)",
    re.I,
)


def _saneador_reemissao_factory(original_task, saneador_peca):
    """Última barreira da reemissão: se ela veio em esqueleto ou encolhida, vale a versão anterior (saneada) com a marca de ajustes pendentes; senão, o saneador da peça."""

    def saneador(texto):
        orig = _sem_alerta(getattr(getattr(original_task, "output", None), "raw", None) or "")
        encolhida = orig and _tamanho_util(orig) > 600 and _tamanho_util(_sem_alerta(texto)) < 0.6 * _tamanho_util(orig)
        inchada = orig and _tamanho_util(orig) > 600 and _tamanho_util(_sem_alerta(texto)) > _LIMITE_CRESCIMENTO * _tamanho_util(orig)
        if orig and inchada:
            novo, trocas = saneador_peca(orig)
            aviso = f"{_MARCA_PENDENTE}: a reemissão cresceu além do limite e acrescentou conteúdo novo; esta é a versão anterior, saneada, com os ajustes pedidos ainda por aplicar.\n\n"
            return aviso + novo.lstrip(), list(trocas) + ["reemissão inchada: mantida a versão anterior"]
        if orig and (encolhida or _esqueleto(texto)):
            novo, trocas = saneador_peca(orig)
            aviso = f"{_MARCA_PENDENTE}: a reemissão veio incompleta; esta é a versão anterior, saneada, com os ajustes pedidos ainda por aplicar.\n\n"
            return aviso + novo.lstrip(), list(trocas) + ["reemissão incompleta: mantida a versão anterior"]
        limpo, tirou = _sem_autocertificacao(texto)
        novo, trocas = saneador_peca(limpo)
        return novo, list(trocas) + (["autocertificação removida"] if tirou else [])

    return saneador


def _bloco_versoes_g2(pecas):
    """
    Bloco gerado por código com a versão vigente de cada peça do G2 e a lista de bloqueadas. `pecas`: {nome: (tarefa de correção, tarefa condicional de aplicação)}.
    Bloqueada = a versão vigente carrega a marca de ajustes pendentes (reemissão incompleta).
    """
    linhas, bloqueadas = [], []
    for nome, (correcao, aplicacao) in pecas.items():
        apl = getattr(getattr(aplicacao, "output", None), "raw", None) or ""
        cor = getattr(getattr(correcao, "output", None), "raw", None) or ""
        reemitida = bool(apl.strip()) and apl.strip() != cor.strip()
        vigente = apl if apl.strip() else cor
        origem = "reemitida após o feedback humano" if reemitida else "corrigida antes do portão e aprovada sem alterações"
        pendente = _MARCA_PENDENTE in vigente
        if pendente:
            bloqueadas.append(nome)
        linhas.append(f"- {nome}: {origem}" + (" — **BLOQUEADA** (reemissão incompleta, ajustes pendentes)" if pendente else ""))
    return (
        "\n\n## Versões vigentes (geradas automaticamente pelo código)\n" + "\n".join(linhas)
        + "\n\nBloqueadas: " + (", ".join(bloqueadas) if bloqueadas else "nenhuma") + "\n"
    )


def _sem_secao_ajustes(texto):
    """Tira do registro as seções "Ajustes aplicados" escritas pelo modelo: o código as gera a partir da comparação das versões."""
    return re.sub(r"(?ims)^#{1,4}[ \t]*[^\n]*ajustes (humanos )?aplicados[^\n]*\n.*?(?=^#{1,4}[ \t]|\Z)", "", texto).rstrip()


def _bloco_ajustes_g2(pecas):
    """
    "Ajustes aplicados" por entrega, gerado por código: compara a versão vigente com a corrigida antes do portão. Não descreve o que mudou
    (o código não sabe), só o que é verificável: reemitida ou não, tamanho e quantidade de linhas diferentes.
    """
    import difflib

    linhas = []
    for nome, (correcao, aplicacao) in pecas.items():
        apl = _sem_alerta(getattr(getattr(aplicacao, "output", None), "raw", None) or "")
        cor = _sem_alerta(getattr(getattr(correcao, "output", None), "raw", None) or "")
        if not apl.strip() or apl.strip() == cor.strip():
            linhas.append(f"- {nome}: nenhum ajuste humano aplicado; versão corrigida mantida sem alteração.")
            continue
        a, b = cor.splitlines(), apl.splitlines()
        trocadas = sum(1 for l in difflib.ndiff(a, b) if l[:2] in ("- ", "+ "))
        if _MARCA_PENDENTE in apl:
            linhas.append(f"- {nome}: reemissão incompleta; ajustes NÃO aplicados (bloqueada).")
        else:
            linhas.append(f"- {nome}: reemitida após o feedback ({_tamanho_util(cor)} para {_tamanho_util(apl)} caracteres; {trocadas} linhas diferentes). Conferir o diff antes de aprovar.")
    return "\n\n## Ajustes aplicados (gerado automaticamente pelo código)\n" + "\n".join(linhas) + "\n"


def _guardrail_registro_factory(pecas):
    """Registro da decisão do G2: documento válido; o bloco de versões vigentes e bloqueadas é acrescentado por código, não pelo modelo."""

    def guardrail(saida):
        base = _guardrail_documento(saida)
        if base[0] is False:
            return base
        raw = getattr(saida, "raw", None) or str(saida) or ""
        texto = re.sub(r"\n## (Ajustes aplicados|Versões vigentes) \(gerad[oa]s? automaticamente pelo código\).*", "", raw, flags=re.S).rstrip()
        texto = _sem_secao_ajustes(texto)
        return True, texto + _bloco_ajustes_g2(pecas) + _bloco_versoes_g2(pecas)

    return guardrail


_NOTA_VERSAO_INICIAL = "> Atenção: esta avaliação foi feita sobre a VERSÃO INICIAL das peças, antes da correção automática. Vale o parecer final do Guardião acima."


def _notas_de_versao_g2(texto):
    """
    No G2 a rubrica e a auditoria de mídia avaliam as peças ANTES da correção automática, e o parecer final avalia as versões corrigidas.
    O código acrescenta uma nota logo abaixo do título dessas duas seções, para o aprovador não tomar os dois como a mesma versão.
    """
    if _NOTA_VERSAO_INICIAL in texto:
        return texto
    return re.sub(
        r"^([ \t]*(?:#+[ \t]*)?(?:Quadro da rubrica de qualidade|Auditoria técnica de mídia)[^\n]*\n)",
        lambda m: m.group(1) + _NOTA_VERSAO_INICIAL + "\n",
        texto, flags=re.M | re.I,
    )


def _guardrail_cobertura_g2_factory(base):
    """Revisão final do G2: as cinco entregas precisam de parecer, a direção de arte inclusive (já saiu um parecer sem ela no portão)."""

    def guardrail(saida):
        r = base(saida)
        if r[0] is False:
            return r
        n = _normalizar(_sem_alerta(getattr(saida, "raw", None) or str(saida) or ""))
        if not re.search(r"dire[cç][aã]o de arte|conceito criativo|pe[cç]as criativas|criativo", n):
            return False, "Falta o parecer da DIREÇÃO DE ARTE. A revisão final cobre as cinco entregas: conteúdo, calendário, e-mail, plano de mídia e direção de arte, com cinco linhas no quadro-resumo."
        return r

    return guardrail


def _guardrail_portao_factory(revisao_task, rubrica_task=None, auditoria_task=None, portao=None):
    """
    Portão humano: o pedido deve copiar o parecer do Guardião (mesmo resultado, pelo menos 70% das linhas) e ter as
    seções obrigatórias. Rejeita paráfrase e a troca de "Reprovado" por outro resultado.
    """

    tentativas = {"n": 0}

    def guardrail(saida):  # sem anotação de retorno (ver _guardrail_documento)
        if portao:
            _FEEDBACK[portao] = _ha_feedback_humano(getattr(saida, "raw", None) or str(saida) or "")
        veredito = _checar_portao(saida)
        if veredito[0] is False:
            veredito = (False, _PREFIXO_AUTO + str(veredito[1]))
            # Após duas rejeições a saída é aceita: o CrewAI derruba a execução inteira quando o guardrail esgota as
            # tentativas, e a plataforma não recupera uma execução pausada que falhou (observado em 02/10).
            tentativas["n"] += 1
            if tentativas["n"] > 2:
                return True, (_notas_de_versao_g2(getattr(saida, "raw", None) or str(saida) or "") if portao == "G2" else saida)
            return veredito
        if portao == "G2":
            return True, _notas_de_versao_g2(getattr(saida, "raw", None) or str(saida) or "")
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


def _trecho_reemitido(texto, nome_regex):
    """Da seção "Peça reemitida: <nome>" até a próxima peça reemitida ou a lista de versões; vazio se a peça não foi reemitida."""
    m = re.search(rf"(pe[çc]a reemitida|reemiss[ãa]o)[^\n]*(?:{nome_regex})|(?:{nome_regex})[^\n]*reemitid", texto or "", re.I)
    if not m:
        return ""
    resto = texto[m.start():]
    fim = re.search(r"\n#{1,4}\s*(pe[çc]a reemitida|parte c|lista (final )?de vers)", resto[m.end() - m.start():], re.I)
    return resto[: (m.end() - m.start()) + fim.start()] if fim else resto


def _a_partir_da_reemissao(texto):
    """Texto da Parte B em diante (peças reemitidas); o registro da Parte A pode citar o problema e não entra."""
    m = re.search(r"parte b|pe[çc]a reemitida", texto or "", re.I)
    return texto[m.start():] if m else ""


def _tamanho_util(texto):
    return len(re.sub(r"\s+", " ", _sem_alerta(texto or "")).strip())


def _pecas_encolhidas(texto, originais, minimo=0.6):
    """
    Peças reemitidas que ficaram com menos de 60% do tamanho da original: reemitir é copiar a peça INTEIRA trocando só o trecho ajustado; um resumo ou esqueleto
    perde metadados, e-mails, seções e tabelas. `originais`: {nome da entrega: (regex do nome, tarefa da peça original)}. Devolve [(nome, % do original)].
    """
    achadas = []
    for nome, (rx, tarefa) in (originais or {}).items():
        orig = getattr(getattr(tarefa, "output", None), "raw", None) or ""
        novo = _trecho_calendario_reemitido(texto) if "calend" in rx else _trecho_reemitido(texto, rx)
        if novo and _tamanho_util(orig) > 600 and _tamanho_util(novo) < minimo * _tamanho_util(orig):
            achadas.append((nome, round(100 * _tamanho_util(novo) / _tamanho_util(orig))))
    return achadas


_ESQUELETO = re.compile(
    r"^\s*(\.{3}|\[\.{3}\]|…)\s*$|"
    r"\[(o |a |os |as )?(conte[úu]do|texto|restante|continua[çc][ãa]o|incluindo|demais|inclua|inserir|repetir|manter|sem necessidade|idem|igual ao original|"
    r"o fluxo|os e-?mails?|as semanas|calend[áa]rio completo|plano completo)[^\]]{3,}\]",
    re.I | re.M,
)


def _esqueleto(texto):
    """Trechos em que a reemissão só aponta para a peça em vez de copiá-la: "...", "[O conteúdo completo original com ajustes…]", "[CONTINUAÇÃO do fluxo…]"."""
    return sorted({m.group(0).strip()[:70] for m in _ESQUELETO.finditer(_sem_alerta(texto or ""))})


def _guardrail_aplicacao_g2(saida):
    """Ajuste de veracidade só remove ou marca [VALIDAR]: nunca afirma que depoimento é real ou autorizado."""
    base = _guardrail_documento(saida)
    if base[0] is False:
        return base
    texto = (getattr(saida, "raw", None) or str(saida) or "")
    esqueleto = _esqueleto(_a_partir_da_reemissao(texto))
    if esqueleto:
        return False, (
            "A reemissão é um esqueleto: " + "; ".join(f'"{e}"' for e in esqueleto[:3]) + ". Não aponte para a peça original nem resuma: copie a peça INTEIRA "
            "(metadados, texto, tabelas, todos os e-mails e seções) com os ajustes aplicados. Peça que não precisa de ajuste não é reemitida."
        )
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
        erro = _problemas_calendario(cal)
        if erro:
            return False, "O calendário reemitido tem problema. " + erro + " Reemita o calendário inteiro, não só as linhas ajustadas."
    reemitido = _sem_alerta(_a_partir_da_reemissao(texto))
    permitido_srv = _TEXTO_PERMITIDO["texto"]
    if permitido_srv and reemitido:
        fora = sorted({m.group(0).lower() for m in _TERMOS_SENSIVEIS.finditer(reemitido)
                       if not re.search(rf"\b{re.escape(m.group(0).lower())}\b", permitido_srv)})
        if fora:
            return False, (
                "A reemissão cita serviços, especialidades ou tecnologias que o briefing e a base do cliente não citam: " + ", ".join(fora) + ". Reemitir não é "
                "trocar o tema: mantenha o assunto da peça original e remova ou marque [VALIDAR] só o que o Guardião apontou."
            )
    falso = sorted({m.group(0) for m in _MARCADOR_FALSO.finditer(reemitido)})
    if falso:
        return False, (
            "A reemissão usa o marcador " + ", ".join(falso) + ", que não existe: nada foi confirmado. O único marcador é [VALIDAR]; troque-o e diga o que o valor é."
        )
    plano = _trecho_reemitido(texto, r"m[íi]dia")
    if plano:
        faltas = _faltas_rotina_midia(plano)
        if faltas:
            return False, (
                "O plano de mídia reemitido perdeu a rotina da Vanguarda: " + "; ".join(faltas) + ". Reemita o plano inteiro, mantendo as seções "
                "\"Insumos e pendências\", \"Rotina operacional (diária, semanal)\" e \"Alçadas e autorizações\"."
            )
        canais = _problemas_midia(plano, " ")
        if canais and ("canal" in canais or "gasto histórico" in canais):
            return False, "No plano de mídia reemitido: " + canais
    if _AFIRMACOES_FALSAS.search(texto):
        return False, (
            "A saída afirma que depoimentos/testemunhos são reais, colhidos com consentimento ou autorizados. Isso não "
            "pode ser afirmado: não há depoimento real nem consentimento. Remova os depoimentos e testemunhos das peças "
            "ou marque [VALIDAR]; nunca declare autorização."
        )
    return True, saida


_CHAVE_PECA = {"CONTEUDO": r"conte[úu]do", "CALENDARIO": r"calend[áa]rio", "EMAIL": r"e-?mail", "MIDIA": r"m[íi]dia"}


def _pecas_para_refazer(rubrica):
    """Peças com VEREDITO=REFAZER na rubrica (nomes sem acento, como em _PECAS_RUBRICA)."""
    saida = []
    for m in _RESUMO_RUBRICA.finditer(_sem_alerta(rubrica or "")):
        if m.group("ver").upper() == "REFAZER":
            saida.append(_sem_acento(m.group("peca")).replace("-", "").replace(" ", ""))
    return saida


def _guardrail_aplicacao_g2_factory(rubrica_task, portao_task, originais=None):
    """
    "Aprovado." sozinho não carrega correções. Peça que a rubrica mandou REFAZER não pode sair liberada quando o humano não escreveu
    nenhum ajuste: tem de constar na lista de bloqueadas. Se o humano devolveu com texto, as correções dele são aplicadas e a regra não vale.
    """

    def guardrail(saida):
        base = _guardrail_aplicacao_g2(saida)
        if base[0] is False:
            return base
        encolhidas = _pecas_encolhidas(_sem_alerta(getattr(saida, "raw", None) or str(saida) or ""), originais)
        if encolhidas:
            return False, (
                "A reemissão ficou resumida: " + ", ".join(f"{n} com {p}% do tamanho da original" for n, p in encolhidas) + ". Reemitir é copiar a peça INTEIRA, "
                "com todas as seções, campos, metadados, e-mails, tabelas e checklists da original, trocando só o trecho ajustado. Reemita cada peça completa."
            )
        rubrica = getattr(getattr(rubrica_task, "output", None), "raw", None) or ""
        portao = getattr(getattr(portao_task, "output", None), "raw", None) or ""
        devolvido = "ajustes pedidos" in _normalizar(portao)
        refazer = _pecas_para_refazer(rubrica)
        if refazer and not devolvido:
            texto = _sem_alerta(getattr(saida, "raw", None) or str(saida) or "")
            m = re.search(r"bloquead[ao]s?\W{0,6}([^\n]+)", texto, re.I)
            bloqueadas = (m.group(1) if m else "").lower()
            fora = [p for p in refazer if not re.search(_CHAVE_PECA[p], bloqueadas, re.I)]
            if fora:
                return False, (
                    "A rubrica de qualidade mandou REFAZER " + ", ".join(fora) + " e o humano aprovou sem escrever ajustes: aprovação sem "
                    "correção não libera peça reprovada. Registre essas entregas como BLOQUEADAS na lista de bloqueadas (\"Bloqueadas: ...\") "
                    "com a pendência da rubrica, e não as inclua entre as liberadas."
                )
        return True, saida

    return guardrail


_PECAS_G2 = ("Conteúdo longo", "Calendário social", "Fluxos de e-mail", "Plano de mídia paga", "Direção de arte / conceito criativo")


def _feedback_do_portao(portao_texto):
    """Seção "Histórico de feedbacks humanos" do pedido do portão (cópia literal), sem o parecer; vazio se não houver."""
    t = _sem_alerta(portao_texto or "")
    m = re.search(r"hist[óo]rico de feedbacks[^\n]*\n(.*?)(?=\n#+\s*parecer|\Z)", t, re.I | re.S)
    return (m.group(1).strip() if m else "")[:3000]


def _retirar_das_liberadas(texto, nomes):
    """Tira das linhas "Liberadas: …" (e das linhas "Versão reemitida") as peças que o saneador bloqueou, para o registro não se contradizer."""
    chaves = [(_CHAVE_PECA.get(k) or re.escape(n)) for n in nomes for k in [_sem_acento(n.split()[0]).replace("-", "")]]
    saida = []
    for l in texto.splitlines():
        if re.search(r"liberad[ao]s?\W{0,4}:", l, re.I):
            cab, _, resto = l.partition(":")
            itens = [i.strip() for i in re.split(r",|;", resto) if i.strip()]
            itens = [i for i in itens if not any(re.search(rx, i, re.I) for rx in chaves)]
            l = f"{cab}: " + (", ".join(itens) if itens else "nenhuma (ver Reemissão incompleta)")
        elif re.search(r"vers[ãa]o reemitida", l, re.I) and any(re.search(rx, l, re.I) for rx in chaves):
            l = re.sub(r"vers[ãa]o reemitida", "versão original, BLOQUEADA (reemissão incompleta)", l, flags=re.I)
        saida.append(l)
    return "\n".join(saida)


def _saneador_aplicacao_g2_factory(portao_task, originais=None):
    """
    Última barreira da aplicação do G2. Saída curta ou que "não conseguiu ler o feedback" não pode seguir adiante como se as peças tivessem
    sido ajustadas (o pacote de publicação usaria as peças antigas). Nesse caso a saída vira um registro honesto: aplicação NÃO executada, nenhuma
    peça reemitida, todas bloqueadas, com o feedback humano copiado. Saída válida segue só com o saneamento do trecho reemitido.
    """

    def saneador(texto):
        invalida = len(texto.strip()) < _MIN_CARACTERES_DOCUMENTO or any(f in texto.lower()[:900] for f in _FRASES_DE_FALHA)
        if not invalida:
            novo, trocas = _sanear_reemissao(texto)
            sem_falso = _MARCADOR_FALSO.sub("[VALIDAR]", novo)
            if sem_falso != novo:
                trocas.append("marcador falso [confirmado]")
                novo = sem_falso
            plano = _trecho_reemitido(novo, r"m[íi]dia")
            if plano and _faltas_rotina_midia(plano):
                novo = novo.rstrip() + "\n\n### Plano de mídia: seções da rotina (inseridas automaticamente)\n" + _secoes_rotina_midia(plano) + "\n"
                trocas.append("seções da rotina de mídia")
            encolhidas = _pecas_encolhidas(novo, originais)
            if _esqueleto(_a_partir_da_reemissao(novo)):
                ja = {n for n, _ in encolhidas}
                for nome, (rx, _t) in (originais or {}).items():
                    trecho = _trecho_calendario_reemitido(novo) if "calend" in rx else _trecho_reemitido(novo, rx)
                    if nome not in ja and trecho and _esqueleto(trecho):
                        encolhidas.append((nome, 0))
            if encolhidas:
                nomes = ", ".join(n for n, _ in encolhidas)
                novo = _retirar_das_liberadas(novo, [n for n, _ in encolhidas])
                novo = novo.rstrip() + (
                    "\n\n### Reemissão incompleta (inserida automaticamente)\n"
                    f"Bloqueadas: {nomes}. A reemissão perdeu partes da peça original (seções, metadados, e-mails ou tabelas): mantenha a versão original e reaplique "
                    "os ajustes pedidos antes de liberar.\n"
                )
                trocas.append("reemissão incompleta: " + nomes)
            return novo, trocas
        feedback = _feedback_do_portao(getattr(getattr(portao_task, "output", None), "raw", None) or "")
        linhas = [
            "# Aplicação da decisão G2: NÃO EXECUTADA",
            "",
            "A tarefa não conseguiu aplicar os ajustes depois de três tentativas. **Nenhuma peça foi reemitida.** Todas as entregas permanecem na versão original, "
            "com os ajustes pendentes, e estão **BLOQUEADAS** até uma nova rodada de aplicação.",
            "",
            "## Feedback humano recebido (cópia literal)",
            feedback or "Nenhum feedback humano recebido.",
            "",
            "## Entregas bloqueadas",
        ] + [f"- {p}: versão original, ajustes pendentes." for p in _PECAS_G2] + [
            "",
            "## Entregas liberadas",
            "- Nenhuma.",
        ]
        return "\n".join(linhas), ["aplicação não executada: saída inválida substituída por registro de bloqueio"]

    return saneador


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


def _limpar_final(texto):
    """
    Limpeza de última tentativa: frase em inglês solta é removida (em célula de tabela vira [VALIDAR: texto em inglês]) e o comentário depois do último bloco
    ``` é cortado. Devolve (texto, lista do que foi feito).
    """
    feitos, saida = [], []
    for linha in (texto or "").splitlines():
        l = linha.strip()
        if l.startswith("|"):
            celulas = linha.split("|")
            novas = []
            for c in celulas:
                if c.strip() and c.count(" ") >= 4 and not l.startswith("|--") and _trecho_em_ingles(c.strip()):
                    novas.append(" [VALIDAR: texto em inglês] ")
                    feitos.append("frase em inglês")
                else:
                    novas.append(c)
            saida.append("|".join(novas))
        elif l and not l.startswith(("```", "#")) and l.count(" ") >= 5 and _trecho_em_ingles(l):
            feitos.append("frase em inglês removida")
        else:
            saida.append(linha)
    novo = "\n".join(saida)
    if _marcadores_malformados(novo):
        novo = _MARCADOR_MALFORMADO.sub("[VALIDAR]", novo)
        feitos.append("marcador inválido normalizado para [VALIDAR]")
    if _nota_final(novo):
        linhas_doc = novo.splitlines()
        for i in range(len(linhas_doc) - 1, -1, -1):
            if linhas_doc[i].strip() and linhas_doc[i].strip() != "```":
                del linhas_doc[i]
                break
        novo = "\n".join(linhas_doc)
        feitos.append("nota final do agente removida")
    if _portugues_de_portugal(novo):
        def _tela(m):  # "no ecrã" vira "na tela": o gênero muda junto com o artigo
            art = _ECRA_ARTIGO[m.group(1).lower()]
            return (art.capitalize() if m.group(1)[:1].isupper() else art) + (" telas" if m.group(2).lower().endswith("s") else " tela")
        novo = _ECRA_COM_ARTIGO.sub(_tela, novo)

        def _br(m):
            t = _PT_PT[m.group(0).lower()]
            return t.capitalize() if m.group(0)[:1].isupper() else t
        novo = _PT_PT_RE.sub(_br, novo)
        feitos.append("português de Portugal trocado por português do Brasil")
    apos = _texto_apos_documento(novo)
    if apos:
        novo = novo[: _fim_do_documento(novo)] + "\n"
        feitos.append("comentário depois do documento removido")
    return novo, feitos


def _com_limite_de_rejeicoes(guardrail, maximo=2, saneador=None):
    """
    Aceita a saída depois de `maximo` rejeições, porque guardrail esgotado derruba a execução inteira na plataforma. A saída aceita
    leva uma linha "ALERTA DE QUALIDADE" no topo com a pendência que a trava não conseguiu corrigir. Com `saneador`, o texto aceito
    sai antes com os termos proibidos trocados por [VALIDAR]: o humano recebe a peça já neutralizada, não só o aviso.
    """
    estado = {"n": 0}

    def envelope(saida):  # sem anotação de retorno (ver _guardrail_documento)
        veredito = guardrail(saida)
        if veredito[0] is False:
            estado["n"] += 1
            if estado["n"] > maximo:
                if saneador is None:
                    return True, _com_alerta(saida, veredito[1])
                original = getattr(saida, "raw", None) or str(saida) or ""
                pre, feitos = _limpar_final(_sem_alerta(original))
                limpo, trocas = saneador(pre)
                trocas = list(trocas) + feitos
                if not trocas:
                    return True, _com_alerta(saida, veredito[1])
                tipo = type("SaidaSaneada", (), {"raw": limpo, "name": getattr(saida, "name", None) or ""})()
                return True, _com_alerta(tipo, f"{veredito[1]} Saneamento automático aplicado (linha marcada com [VALIDAR] ou [VALIDAR MÉDICO], trecho trocado ou removido): {', '.join(sorted(set(trocas)))[:200]}.")
            return False, _PREFIXO_AUTO + str(veredito[1])
        return veredito

    return envelope


_TEXTO_PERMITIDO = {"texto": ""}
_TERMOS_SENSIVEIS = re.compile(
    r"cirurgia rob[óo]tica|\brob[óo]tic[ao]s?\b|\bUTI\b|telemedicina|cardiologia|ortopedia|urologia|oncologia|"
    r"neurologia|maternidade|pediatria|pronto[- ]socorro|hemodin[âa]mica|transplante|centro cirúrgico|cirurgi\w+|cir[úu]rgic\w+",
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
    r"diagn[óo]sticos? precis\w+|tratamentos? eficaz\w*|(confian[çc]a|seguran[çc]a) em cada (diagn[óo]stico|tratamento)|"
    r"(que nos torna|que faz d[oa] [\w ]{2,30}) uma refer[êe]ncia|\buma refer[êe]ncia\b|"
    r"\bde ponta\b(?! a ponta)|melhor escolha|escolha preferencial|escolha segura|precis[ãa]o e seguran[çc]a|"
    r"certifica[çc][õo]es? reconhecid\w+|guia definitivo|"
    r"garant\w+[^.\n]{0,60}(precis[ãa]o|seguran[çc]a|excel[êe]ncia|qualidade|efici[êe]ncia|resultados?|cura|"
    r"recupera[çc][ãa]o|lgpd|conformidade|ader[êe]ncia|atendimento|cuidado|diagn[óo]stico|tratamento)",
    re.I,
)
_LINHA_NEUTRA = re.compile(r"\[VALIDAR|\bsem (usar )?depoimento|proibid|n[ãa]o (use|usar|incluir|propor|citar)|evitar|^\s*[-*]\s*(\[[ xX]\]\s*)?garantir\b|"
                           r"garant\w+[^.\n]{0,40}(acessibilidade|contraste|wcag|leitura assistiva|alt text|carregamento)", re.I)


_PLACEHOLDERS = re.compile(
    r"example\.(com|org|net)|exemplo\.com(\.br)?|lorem ipsum|seu-?site\.com|\[(inserir|link|url)[^\]]*\]|"
    # nota interna do agente que vazou para dentro da peça (texto de retrabalho)
    r"\breformulei\b|\breescrevi\b|ajustei (o|a|os|as) (conte[úu]do|texto|pe[çc]as?)|para evitar os problemas|"
    r"conforme (solicitado|pedido|orienta[çc][ãa]o)|como solicitado|a pedido d[oa]|"
    # autocertificação de conformidade e afirmação de que não há pendência
    r"seguindo rigorosamente|(foi|foram) (criad|elaborad|redigid)\w+ seguindo|em total conformidade|"
    r"todas as (propostas|valida[çc][õo]es|corre[çc][õo]es) foram|n[ãa]o h[áa] ajustes pendentes|todos os feedbacks[^.\n]{0,40}(considerad|inclu[íi]d)|"
    r"todos os elementos foram|(foi|foram) (desenvolvid|produzid|constru[íi]d)\w+ em conformidade|respeitando a linguagem de|"
    r"acreditamos que (o caminho|o documento|o brief|a campanha|as pe[çc]as|o plano)|est[áa] pronto para (a )?(aprova[çc][ãa]o|execu[çc][ãa]o)|caminho est[áa] pronto|"
    r"com os ajustes realizados|este parecer serve|este documento (foi|serve|segue)",
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


_ARTIGO_MASCULINO = {"a": "o", "as": "os", "da": "do", "das": "dos", "na": "no", "nas": "nos", "pela": "pelo", "pelas": "pelos", "à": "ao", "às": "aos",
                     "uma": "um", "umas": "uns", "o": "o", "os": "os", "do": "do", "dos": "dos", "no": "no", "nos": "nos", "um": "um"}
_TERMOS_COM_ARTIGO = re.compile(r"(?:\b(?P<art>a|as|o|os|da|das|do|dos|na|nas|no|nos|pela|pelas|à|às|uma|umas|um)\s+)?(?P<termo>" + _TERMOS_SENSIVEIS.pattern + r")", re.I)


def _acrescentar_marca(linha, marca):
    """Põe a marca no fim da linha; em linha de tabela, antes do último separador, para não quebrar a tabela."""
    if linha.rstrip().endswith("|"):
        corpo = linha.rstrip()[:-1].rstrip()
        return f"{corpo} {marca} |"
    return f"{linha.rstrip()} {marca}"


def _sanear_claims(texto, so_apos=None):
    """
    Última barreira quando a trava esgota: linha com superlativo/garantia/depoimento sem [VALIDAR] ganha [VALIDAR MÉDICO]; serviço ou
    especialidade que o briefing não cita é trocado por [VALIDAR: serviço fora do briefing]. `so_apos` limita ao trecho depois de um
    marcador (peças reemitidas), para não mexer no registro que cita o problema. Devolve (texto, lista do que foi trocado).
    """
    linhas = (texto or "").splitlines()
    inicio = 0
    if so_apos:
        for i, l in enumerate(linhas):
            if re.search(so_apos, l, re.I):
                inicio = i
                break
        else:
            return texto, []
    permitido = _TEXTO_PERMITIDO["texto"]
    trocas = []
    for i in range(inicio, len(linhas)):
        l = linhas[i]
        if "[validar" in l.lower() or _TAG_ALERTA in l:
            continue
        if permitido:
            def _trocar(m):
                termo = m.group("termo").lower()
                if re.search(rf"\b{re.escape(termo)}\b", permitido):
                    return m.group(0)
                trocas.append(termo)
                # "A telemedicina proporciona" vira "O serviço [VALIDAR...] proporciona": o artigo vai para o masculino de "serviço" e a frase continua legível
                original = m.group("art") or ""
                artigo = _ARTIGO_MASCULINO.get(original.lower(), original)
                if original[:1].isupper():
                    artigo = artigo[:1].upper() + artigo[1:]
                return f"{artigo}{' ' if artigo else ''}serviço [VALIDAR: confirmar com o hospital]"
            l = _TERMOS_COM_ARTIGO.sub(_trocar, l)
        if "[validar" not in l.lower() and _CLAIMS_PROIBIDOS.search(l) and not _LINHA_NEUTRA.search(l):
            trocas.append(_CLAIMS_PROIBIDOS.search(l).group(0).lower())
            l = _acrescentar_marca(l, "[VALIDAR MÉDICO]")
        linhas[i] = l
    return "\n".join(linhas), trocas


def _sanear_producao(texto):
    return _sanear_claims(texto)


def _sanear_reemissao(texto):
    return _sanear_claims(texto, so_apos=r"parte b|pe[çc]a reemitida")


def _sanear_midia(texto):
    """Plano de mídia: além das afirmações, canal pago que o briefing não prevê vira [VALIDAR: canal fora do brief] (a verba segue para o humano decidir)."""
    texto, trocas = _sanear_claims(texto)
    extra = _secoes_rotina_midia(texto)
    if extra:
        texto = texto.rstrip() + "\n\n" + extra + "\n"
        trocas.append("seções da rotina de mídia")
    base = _normalizar(_TEXTO_PERMITIDO["texto"])
    for canal in _CANAIS_PAGOS:
        if _normalizar(canal) in base:
            continue
        novo = re.sub(re.escape(canal), "[VALIDAR: canal fora do brief]", texto, flags=re.I)
        if novo != texto:
            trocas.append(canal)
            texto = novo
    return texto, trocas


_INPUTS_ATUAIS = {}


def _extrair_datas(texto):
    """Datas do texto como datetime: dd/mm/aaaa, aaaa-mm-dd e dd/mm sem ano (vale o ano de hoje; calendários costumam omitir o ano)."""
    from datetime import datetime

    achadas = []
    for d, mth, a in re.findall(r"\b(\d{2})/(\d{2})/(20\d{2})\b", texto or ""):
        achadas.append((a, mth, d))
    for a, mth, d in re.findall(r"\b(20\d{2})-(\d{2})-(\d{2})\b", texto or ""):
        achadas.append((a, mth, d))
    ano = str(_hoje().year)
    for d, mth in re.findall(r"(?<![\d/])(\d{2})/(\d{2})(?![\d/])", texto or ""):
        achadas.append((ano, mth, d))
    meses = {"jan": 1, "fev": 2, "feb": 2, "mar": 3, "abr": 4, "apr": 4, "mai": 5, "may": 5, "jun": 6, "jul": 7, "ago": 8, "aug": 8,
             "set": 9, "sep": 9, "out": 10, "oct": 10, "nov": 11, "dez": 12, "dec": 12}
    for d, nome, a in re.findall(r"\b(\d{1,2})[-/ ]([A-Za-zç]{3,9})\.?[-/ ](\d{2,4})\b", texto or ""):
        mes = meses.get(nome[:3].lower())
        if mes:
            achadas.append(((("20" + a) if len(a) == 2 else a), f"{mes:02d}", f"{int(d):02d}"))
    saida = []
    for a, mth, d in achadas:
        try:
            saida.append(datetime(int(a), int(mth), int(d)))
        except ValueError:
            pass
    return saida


def _cobertura_calendario(texto):
    """Devolve a mensagem de erro se o calendário não cobre todas as semanas da campanha; None se cobre (ou não há como medir)."""
    try:
        semanas = int(str(_INPUTS_ATUAIS.get("duracao_semanas", "")).strip())
    except ValueError:
        return None
    texto = _sem_alerta(texto)
    datas = _extrair_datas(texto)
    blocos = {(x - min(datas)).days // 7 for x in datas} if datas else set()
    marcadores = [int(n) for n in re.findall(r"semana\s+(\d{1,2})", texto, re.I)]
    linhas_tabela = [int(n) for n in re.findall(r"^\|\s*(\d{1,2})\s*\|", texto, re.M)]  # coluna "Semana" numérica
    marcadores += linhas_tabela
    # Cobrir é ter conteúdo em (quase) todas as semanas, não só citar a última: um calendário de 3 linhas com a semana 8 não cobre.
    distintas = len({m for m in marcadores if 1 <= m <= semanas})
    cobre_semanas = len(blocos) >= semanas - 1 or distintas >= semanas - 1
    posts = max(len(datas), len(linhas_tabela))
    if cobre_semanas and posts >= 2 * semanas:
        return None
    return (
        f"O calendário cobre {max(len(blocos), distintas) or 'menos de ' + str(semanas)} das {semanas} semanas da campanha e tem {posts} post(s). "
        f"Entregue posts distribuídos por todas as {semanas} semanas, com ao menos 3 por semana, datando cada um."
    )


def _hoje():
    """Data de hoje no fuso da campanha; o campo "hoje" em _INPUTS_ATUAIS (ISO) a substitui nos testes."""
    from datetime import date, datetime

    fixo = str(_INPUTS_ATUAIS.get("hoje", "")).strip()
    if fixo:
        return date.fromisoformat(fixo)
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo(str(_INPUTS_ATUAIS.get("fuso_horario") or "America/Manaus"))).date()
    except Exception:  # noqa: BLE001 - sem tzdata, usa a data do servidor
        return date.today()


def _datas_passadas(texto):
    """Datas do calendário anteriores a hoje (um post não pode ser agendado no passado). Lista de dd/mm/aaaa."""
    hoje = _hoje()
    return sorted({x.strftime("%d/%m/%Y") for x in _extrair_datas(texto) if x.date() < hoje})


def _linha_solta_na_tabela(texto):
    """Linha de tabela com número de colunas diferente do cabeçalho (nota ou instrução que vazou para dentro da tabela); vazio se não houver."""
    cabecalho = None
    for linha in _sem_alerta(texto or "").splitlines():
        l = linha.strip()
        if not l.startswith("|"):
            cabecalho = None
            continue
        if re.fullmatch(r"\|[\s:|-]+\|?", l):
            continue
        colunas = l.strip("|").count("|") + 1
        if cabecalho is None:
            cabecalho = colunas
        elif colunas != cabecalho:
            return l[:80]
    return ""


_HISTORIAS_PACIENTES = re.compile(r"hist[óo]rias? de pacientes?|relatos? (inspiradores )?de (recupera[çc][ãa]o|pacientes?)|depoimentos?|antes e depois|casos? de sucesso", re.I)


def _historias_de_pacientes(texto):
    """Post ou peça que usa história, relato ou depoimento de paciente: não existe nos insumos e [VALIDAR] em outra célula da linha não o legitima."""
    achados = []
    for linha in _sem_alerta(texto or "").splitlines():
        m = _HISTORIAS_PACIENTES.search(linha)
        if m and not re.search(r"\bsem\b|n[ãa]o\b|proibid|evitar|nunca", linha, re.I):
            achados.append(m.group(0).lower())
    return sorted(set(achados))


def _tabela_sem_coluna_data(texto):
    """True se a tabela do calendário (cabeçalho com 'Semana') não tem coluna de data."""
    linhas = _sem_alerta(texto or "").splitlines()
    for i, linha in enumerate(linhas[:-1]):
        l = linha.strip()
        if l.startswith("|") and re.fullmatch(r"\|[\s:|-]+\|?", linhas[i + 1].strip()):
            celulas = [c.strip().lower() for c in l.strip("|").split("|")]
            if any(c.startswith("semana") for c in celulas):
                return not any(c.startswith("data") for c in celulas)
    return False


def _problemas_calendario(texto):
    """Erro do calendário (cobertura, data passada, linha solta na tabela) ou None."""
    if _tabela_sem_coluna_data(texto):
        return (
            "A tabela do calendário não tem a coluna Data. Cada post precisa da data completa (dd/mm/aaaa) numa coluna chamada Data, ao lado de Semana e Plataforma."
        )
    historias = _historias_de_pacientes(texto)
    if historias:
        return (
            "O calendário usa " + ", ".join(historias) + ". Não há histórias, relatos nem depoimentos de pacientes nos insumos, e [VALIDAR] não os legitima: "
            "troque esses posts por conteúdo institucional ou educativo que o briefing e a base do cliente sustentem."
        )
    linhas_tabela = len(re.findall(r"^\|\s*\d{1,2}\s*\|", _sem_alerta(texto), re.M | re.I))
    if linhas_tabela >= 6 and len(_extrair_datas(_sem_alerta(texto))) < linhas_tabela * 0.5:
        return (
            f"A tabela tem {linhas_tabela} posts, mas só {len(_extrair_datas(_sem_alerta(texto)))} datas legíveis. Escreva a data de cada post como dd/mm/aaaa "
            "(por exemplo 06/10/2026), uma data por linha, sem formatos como 01-Nov-23."
        )
    erro = _cobertura_calendario(texto)
    if erro:
        return erro
    passadas = _datas_passadas(_sem_alerta(texto))
    if passadas:
        amanha = (_hoje()).strftime("%d/%m/%Y")
        return (
            f"O calendário tem posts em datas que já passaram ({', '.join(passadas[:4])}). Hoje é {amanha}: o primeiro post é de hoje em diante, "
            "mantendo todas as semanas e ao menos 3 posts por semana."
        )
    solta = _linha_solta_na_tabela(texto)
    if solta:
        return (
            f"Há uma linha fora do formato dentro da tabela do calendário (\"{solta}\"). Toda linha da tabela tem as mesmas colunas; notas ou "
            "instruções não entram na tabela nem na peça."
        )
    return None


def _guardrail_calendario(saida):
    """
    O calendário deve cobrir todas as semanas da campanha com datas futuras. A estrutura e as datas são checadas ANTES dos claims: quando
    só o primeiro problema é devolvido, o modelo corrige claims e deixa a data passada (observado: calendário inteiro em 2023 aceito).
    """
    base = _guardrail_documento(saida)
    if base[0] is False:
        return base
    erro = _problemas_calendario(getattr(saida, "raw", None) or str(saida) or "")
    if erro:
        return False, erro
    inventados = _valores_rs_inventados(getattr(saida, "raw", None) or str(saida) or "", _normalizar(_TEXTO_PERMITIDO["texto"]))
    if inventados:
        return False, (
            "O calendário traz valores em R$ que o briefing não informa: " + ", ".join(inventados) + ". Verba por semana ou por rede é decisão do plano de mídia, "
            "não do calendário: retire o valor ou marque [VALIDAR] na mesma linha."
        )
    return _guardrail_producao(saida)


def _sanear_datas_passadas(texto):
    """Última barreira do calendário: data passada vira a mesma data (dia e mês) no primeiro ano em que ela fica no futuro. Devolve (texto, trocas)."""
    from datetime import datetime

    hoje = _hoje()
    trocas = []

    def _ano_futuro(d, m):
        for ano in (hoje.year, hoje.year + 1):
            try:
                if datetime(ano, m, d).date() >= hoje:
                    return ano
            except ValueError:
                continue
        return None

    def _troca_iso(mt):
        a, m, d = int(mt.group(1)), int(mt.group(2)), int(mt.group(3))
        try:
            if datetime(a, m, d).date() >= hoje:
                return mt.group(0)
        except ValueError:
            return mt.group(0)
        novo = _ano_futuro(d, m)
        if novo is None:
            return mt.group(0)
        trocas.append("data passada")
        return f"{d:02d}/{m:02d}/{novo}"

    def _troca_br(mt):
        d, m, a = int(mt.group(1)), int(mt.group(2)), int(mt.group(3))
        try:
            if datetime(a, m, d).date() >= hoje:
                return mt.group(0)
        except ValueError:
            return mt.group(0)
        novo = _ano_futuro(d, m)
        if novo is None:
            return mt.group(0)
        trocas.append("data passada")
        return f"{d:02d}/{m:02d}/{novo}"

    linhas = []
    for l in (texto or "").splitlines():
        if l.strip().startswith("|") and _TAG_ALERTA not in l:
            l = re.sub(r"\b(20\d{2})-(\d{2})-(\d{2})\b", _troca_iso, l)
            l = re.sub(r"\b(\d{2})/(\d{2})/(20\d{2})\b", _troca_br, l)
        linhas.append(l)
    return "\n".join(linhas), (["datas passadas movidas para o próximo ano em que ficam no futuro"] if trocas else [])


def _sanear_calendario(texto):
    novo, trocas = _sanear_producao(texto)
    novo, t2 = _sanear_datas_passadas(novo)
    permitido, t3, linhas = _normalizar(_TEXTO_PERMITIDO["texto"]), [], []
    for linha in novo.splitlines():
        if _valores_rs_inventados(linha, permitido):
            t3 = ["valor em R$ não informado"]
            linha = _acrescentar_marca(linha, "[VALIDAR]")
        linhas.append(linha)
    return "\n".join(linhas), trocas + t2 + t3


_CALENDARIO_REEMITIDO = re.compile(r"(pe[çc]a reemitida|reemiss[ãa]o)[^\n]*calend[áa]rio|calend[áa]rio[^\n]*reemitid", re.I)


def _trecho_calendario_reemitido(texto):
    """Da seção reemitida do calendário até a próxima peça reemitida ou o fim; vazio se o calendário não foi reemitido."""
    m = _CALENDARIO_REEMITIDO.search(texto or "")
    if not m:
        return ""
    resto = texto[m.start():]
    fim = re.search(r"\n#{1,4}\s*(pe[çc]a reemitida|parte c|lista de vers)", resto[m.end() - m.start():], re.I)
    return resto[: (m.end() - m.start()) + fim.start()] if fim else resto


_REDES = ("instagram", "facebook", "linkedin", "tiktok", "youtube")
_HORA_COM_FUSO_COLADO = re.compile(r"\b\d{1,2}:\d{2}\s?[-+]\d{2}(?::?\d{2})?\b")


def _posts_da_tabela(texto):
    """Pares (data dd/mm/aaaa, rede) de cada linha de tabela que tem colunas Data e Plataforma/Canal e cuja rede é social."""
    linhas = _sem_alerta(texto or "").splitlines()
    posts, cab = [], None
    for i, linha in enumerate(linhas):
        l = linha.strip()
        if not l.startswith("|"):
            cab = None
            continue
        if re.fullmatch(r"\|[\s:|-]+\|?", l):
            continue
        celulas = [c.strip() for c in l.strip("|").split("|")]
        baixo = [c.lower() for c in celulas]
        if cab is None and i + 1 < len(linhas) and re.fullmatch(r"\|[\s:|-]+\|?", linhas[i + 1].strip()):
            col_data = next((k for k, c in enumerate(baixo) if c.startswith("data")), None)
            col_rede = next((k for k, c in enumerate(baixo) if c.startswith(("plataforma", "canal"))), None)
            cab = (col_data, col_rede) if col_data is not None and col_rede is not None else ()
            continue
        if cab:
            col_data, col_rede = cab
            if max(col_data, col_rede) >= len(celulas):
                continue
            datas = _extrair_datas(celulas[col_data])
            rede = next((r for r in _REDES if r in celulas[col_rede].lower()), None)
            if datas and rede:
                posts.append((datas[0].strftime("%d/%m/%Y"), rede))
    return posts


def _bloqueadas_do_g2(aplicacao):
    """Texto da lista de entregas bloqueadas da aplicação do G2 (na mesma linha ou nos itens que seguem); vazio se não houver."""
    linhas = _sem_alerta(aplicacao or "").splitlines()
    coletado = []
    for i, l in enumerate(linhas):
        if re.search(r"entregas? bloquead|bloquead[ao]s?\W{0,4}:", l, re.I):
            coletado.append(l.split(":", 1)[1] if ":" in l else "")
            for prox in linhas[i + 1:]:
                if prox.strip().startswith(("-", "*")):
                    coletado.append(prox)
                elif prox.strip() == "":
                    continue
                else:
                    break
    return "\n".join(coletado)


def _linhas_social(texto):
    return [l for l in (texto or "").splitlines() if l.strip().startswith("|") and re.search(r"instagram|facebook|linkedin|tiktok|youtube", l, re.I)]


def _linhas_do_calendario(texto):
    """Linhas de post do calendário (tabela com colunas Data e Plataforma/Canal): dicts com data dd/mm/aaaa, rede, formato e texto do post."""
    linhas = _sem_alerta(texto or "").splitlines()
    saida, cab = [], None
    for i, linha in enumerate(linhas):
        l = linha.strip()
        if not l.startswith("|"):
            cab = None
            continue
        if re.fullmatch(r"\|[\s:|-]+\|?", l):
            continue
        celulas = [c.strip() for c in l.strip("|").split("|")]
        baixo = [c.lower() for c in celulas]
        if cab is None and i + 1 < len(linhas) and re.fullmatch(r"\|[\s:|-]+\|?", linhas[i + 1].strip()):
            idx = lambda *nomes: next((k for k, c in enumerate(baixo) if c.startswith(nomes)), None)  # noqa: E731
            d, r = idx("data"), idx("plataforma", "canal")
            cab = {"data": d, "rede": r, "formato": idx("formato"), "hook": idx("hook", "copy")} if d is not None and r is not None else ()
            continue
        if cab:
            def cel(k):
                return celulas[cab[k]] if cab[k] is not None and cab[k] < len(celulas) else ""
            datas = _extrair_datas(cel("data"))
            rede = next((x for x in _REDES if x in cel("rede").lower()), None)
            if datas and rede:
                saida.append({"data": datas[0].strftime("%d/%m/%Y"), "rede": rede, "formato": cel("formato"), "hook": cel("hook")})
    return saida


def _linhas_do_cronograma(texto):
    """Posts de rede social do cronograma do pacote: dicts com peça, hora e UTM (cabeçalho da tabela com Canal e Peça); vazio se não houver."""
    linhas = _sem_alerta(texto or "").splitlines()
    saida, cab = [], None
    for i, linha in enumerate(linhas):
        l = linha.strip()
        if not l.startswith("|"):
            cab = None
            continue
        if re.fullmatch(r"\|[\s:|-]+\|?", l):
            continue
        celulas = [c.strip() for c in l.strip("|").split("|")]
        baixo = [_sem_acento(c).lower() for c in celulas]
        if cab is None and i + 1 < len(linhas) and re.fullmatch(r"\|[\s:|-]+\|?", linhas[i + 1].strip()):
            idx = lambda *nomes: next((k for k, c in enumerate(baixo) if c.startswith(nomes)), None)  # noqa: E731
            canal, peca = idx("canal", "plataforma"), idx("peca")
            cab = {"canal": canal, "peca": peca, "hora": idx("hora"), "utm": idx("utm")} if canal is not None and peca is not None else ()
            continue
        if cab:
            def cel(k):
                return celulas[cab[k]] if cab[k] is not None and cab[k] < len(celulas) else ""
            if any(x in cel("canal").lower() for x in _REDES):
                saida.append({"peca": cel("peca"), "hora": cel("hora"), "utm": cel("utm")})
    return saida


def _problemas_cronograma(texto, vigente):
    """Defeitos do cronograma de posts que o código sabe refazer: Peça repetida, UTM não preenchida, hora inventada. None se estiver correto."""
    posts = _linhas_do_cronograma(texto)
    if len(posts) < 3:
        return None
    pecas = {_normalizar(p["peca"]) for p in posts}
    if len(pecas) == 1:
        return (
            "A coluna Peça repete o mesmo valor em todos os posts. Cada linha identifica o post do calendário vigente (formato e hook dele), "
            "não o título do conteúdo longo."
        )
    sem_utm = [p for p in posts if "utm_source=" not in p["utm"].lower()]
    if sem_utm:
        return (
            f"{len(sem_utm)} post(s) estão sem UTM. Preencha a UTM de cada post com utm_source=<rede>&utm_medium=social&utm_campaign=<campanha>, "
            "em minúsculas e sem espaços, conforme o dicionário de UTMs do plano de medição."
        )
    if not re.search(r"\b\d{1,2}[:h]\d{2}\b", vigente or ""):
        com_hora = [p for p in posts if re.search(r"\d{1,2}:\d{2}", p["hora"])]
        if com_hora:
            return "O calendário vigente não traz horário: escreva \"a definir\" na coluna Hora em vez de assumir um horário (ex.: 10:00)."
    return None


def _saneador_pacote_factory(calendario_task, aplicacao_task):
    """
    Última barreira do pacote: o cronograma de redes sociais é DADO do calendário, não texto livre. Se a trava esgotou, a tabela do cronograma é refeita por código
    a partir do calendário vigente (uma linha por post, data e rede dele; hora, link e responsável "a definir"; UTM padronizada).
    """

    def saneador(texto):
        aplicacao = _sem_alerta(getattr(getattr(aplicacao_task, "output", None), "raw", None) or "")
        original = _sem_alerta(getattr(getattr(calendario_task, "output", None), "raw", None) or "")
        nao_executada = "não executada" in aplicacao.lower() and "nenhuma peça foi reemitida" in aplicacao.lower()
        if nao_executada or re.search(r"calend", _bloqueadas_do_g2(aplicacao), re.I):
            if not _posts_da_tabela(texto):
                return texto, []
            # calendário bloqueado: as linhas de post de rede social saem do cronograma
            sociais = set(_linhas_social(texto))
            corpo = [l for l in texto.splitlines() if l not in sociais]
            aviso = "> Nenhum post de rede social liberado: o calendário social está bloqueado em aplicacao_g2 (reemissão incompleta ou aplicação não executada)."
            for i, l in enumerate(corpo):
                if re.match(r"\s*#{1,4}\s*.*cronograma", l, re.I):
                    corpo.insert(i + 1, "\n" + aviso)
                    break
            else:
                corpo.append(aviso)
            return "\n".join(corpo), ["posts de rede social removidos do cronograma (calendário bloqueado)"]
        reemitido = _trecho_calendario_reemitido(aplicacao)
        posts = _linhas_do_calendario(reemitido if _posts_da_tabela(reemitido) else original)
        if not posts:
            return texto, []
        linhas = ["| Data | Hora | Fuso | Canal | Peça | Link | UTM | Responsável | Status |", "|---|---|---|---|---|---|---|---|---|"]
        pecas = [" – ".join(x for x in (p["formato"], re.sub(r"\s+", " ", p["hook"])[:70]) if x) or f"post {p['rede'].capitalize()}" for p in posts]
        if len(set(pecas)) < len(pecas):  # hooks repetidos: a data distingue o post na coluna Peça
            pecas = [f"{x} ({p['data'][:5]})" for x, p in zip(pecas, posts)]
        for p, peca in zip(posts, pecas):
            utm = f"utm_source={p['rede']}&utm_medium=social&utm_campaign=calendario_social"
            linhas.append(f"| {p['data']} | a definir | America/Manaus | {p['rede'].capitalize()} | {peca} | a definir após a publicação | {utm} | a definir | A definir |")
        tabela = "\n".join(linhas)
        corpo = texto.splitlines()
        # substitui a primeira tabela depois de um título "cronograma"; sem título, acrescenta a seção
        for i, l in enumerate(corpo):
            if re.match(r"\s*#{1,4}\s*.*cronograma", l, re.I):
                j = i + 1
                while j < len(corpo) and not corpo[j].strip().startswith("|"):
                    j += 1
                k = j
                while k < len(corpo) and corpo[k].strip().startswith("|"):
                    k += 1
                if j < len(corpo):
                    novo = "\n".join(corpo[:j] + [tabela] + corpo[k:])
                    return novo, ["cronograma refeito a partir do calendário vigente"]
        fecha = texto.rstrip().endswith("```")
        base = texto.rstrip()[:-3].rstrip() if fecha else texto.rstrip()
        novo = base + "\n\n## Cronograma de Publicação\n\n" + tabela + ("\n```\n" if fecha else "\n")
        return novo, ["cronograma refeito a partir do calendário vigente"]

    return saneador


def _guardrail_pacote_factory(calendario_task, aplicacao_task):
    """
    O cronograma do pacote usa o calendário VIGENTE (a versão reemitida em aplicacao_g2, se houver; senão o original): as linhas de rede social não
    trazem data que o calendário vigente não tem, não ficam "a definir" onde o calendário já tem data e cobrem a campanha inteira.
    """

    def guardrail(saida):
        base = _guardrail_documento(saida)
        if base[0] is False:
            return base
        texto = _sem_alerta(getattr(saida, "raw", None) or str(saida) or "")
        aplicacao = _sem_alerta(getattr(getattr(aplicacao_task, "output", None), "raw", None) or "")
        original = _sem_alerta(getattr(getattr(calendario_task, "output", None), "raw", None) or "")
        if "não executada" in aplicacao.lower() and "nenhuma peça foi reemitida" in aplicacao.lower() and _linhas_social(texto):
            return False, (
                "A aplicação do G2 não foi executada e nenhuma entrega foi liberada. O cronograma não pode listar posts: escreva que não há peça liberada "
                "para publicação (cronograma vazio) e mantenha só o índice e o checklist."
            )
        if _HORA_COM_FUSO_COLADO.search(texto):
            return False, (
                "Há horário com o fuso colado (ex.: \"10:00-04:00\"). Escreva a hora como HH:MM (ex.: 10:00) e deixe o fuso na coluna própria (America/Manaus)."
            )
        nao_executada = "não executada" in aplicacao.lower() and "nenhuma peça foi reemitida" in aplicacao.lower()
        calendario_bloqueado = nao_executada or bool(re.search(r"calend", _bloqueadas_do_g2(aplicacao), re.I))
        if calendario_bloqueado and _posts_da_tabela(texto):
            return False, (
                "O calendário social está entre as entregas bloqueadas em aplicacao_g2: o cronograma não pode listar posts de rede social. "
                "Liste só e-mail e artigo liberados, ou escreva que não há post liberado."
            )
        reemitido = _trecho_calendario_reemitido(aplicacao)
        vigente = reemitido if _posts_da_tabela(reemitido) else original  # reemissão sem tabela (esqueleto) não é calendário: vale o original
        posts_vigentes = _posts_da_tabela(vigente)
        if posts_vigentes and not calendario_bloqueado:
            do_pacote = _posts_da_tabela(texto)
            from collections import Counter

            vig, pac = Counter(posts_vigentes), Counter(do_pacote)
            inventados = sorted(k for k in pac if pac[k] > vig.get(k, 0))
            if inventados:
                return False, (
                    "O cronograma traz posts que o calendário vigente não tem (data e rede: " + "; ".join(f"{d} {r}" for d, r in inventados[:4]) + "). "
                    "Copie só as linhas do calendário, sem criar posts nem títulos novos."
                )
            faltam = sorted(k for k in vig if pac.get(k, 0) < vig[k])
            if faltam:
                return False, (
                    f"O cronograma tem {sum(pac.values())} posts de rede social e o calendário vigente tem {sum(vig.values())}. Copie TODAS as linhas do calendário, "
                    "uma por post, com a data e a rede dele (faltam, por exemplo: " + "; ".join(f"{d} {r}" for d, r in faltam[:4]) + ")."
                )
        if posts_vigentes and not calendario_bloqueado:
            erro = _problemas_cronograma(texto, vigente)
            if erro:
                return False, erro
        datas_vigentes = _datas_do_texto(vigente)
        sociais = "\n".join(_linhas_social(texto))
        if datas_vigentes and sociais:
            alheias = sorted(_datas_do_texto(sociais) - datas_vigentes)
            if alheias:
                return False, (
                    "O cronograma traz datas de posts que não estão no calendário vigente (" + ", ".join(alheias[:4]) + "). Use só os posts, datas e plataformas do "
                    "calendário liberado; se o calendário foi reemitido em aplicacao_g2, vale a versão reemitida, não a original."
                )
            pendentes = [l for l in sociais.splitlines() if re.match(r"\|\s*\d{1,2}\s*\|\s*a definir\s*\|", l, re.I)]
            if pendentes:
                return False, (
                    f"{len(pendentes)} post(s) do cronograma estão com data \"a definir\", mas o calendário liberado já traz a data de cada um. "
                    "Copie data e plataforma do calendário vigente."
                )
            erro = _cobertura_calendario(sociais)
            if erro:
                return False, "O cronograma de redes sociais não cobre a campanha inteira. " + erro.replace("O calendário", "O cronograma")
        return True, saida

    return guardrail


def _datas_do_texto(texto):
    """Datas do texto normalizadas em dd/mm/aaaa (aceita também aaaa-mm-dd), só as com ano explícito."""
    t = texto or ""
    achadas = set(re.findall(r"\b\d{2}/\d{2}/20\d{2}\b", t))
    for a, m, d in re.findall(r"\b(20\d{2})-(\d{2})-(\d{2})\b", t):
        achadas.add(f"{d}/{m}/{a}")
    return achadas


_FONTE_INTERNA = re.compile(
    r"an[áa]lise interna|registros? internos?|dados internos|fontes? internas?|crm interno|relat[óo]rios? internos?|"
    r"sistema de crm|crm d[oa] [\w ]{3,40}|google analytics|search console|dados d[oa] hospital|sistema interno",
    re.I,
)
_FONTE_MERCADO = re.compile(r"dados? de mercado|relat[óo]rio de mercado|fontes?\s*:|\bfonte\b", re.I)
_ORGAO_REGULADOR = re.compile(r"conselho federal de medicina|\banvisa\b|\bconar\b|\bcfm\b|\bcdc\b", re.I)
_PCT_NOVO = re.compile(r"(?<![\d.,])(\d{1,3}(?:,\d+)?)\s?%")


_MARCADOR_FALSO = re.compile(r"\[\s*(confirmad|validad|aprovad|verificad|checad|ok\b)\w*\s*\]", re.I)
_FONTE_SECAO = re.compile(r"^#{1,4}\s*(\d+\.\s*)?fontes?\b", re.I)
_PALAVRAS_COMUNS = frozenset("este esta estes estas esse essa isso isto aquele aquela todos todas nenhum nenhuma algumas alguns conforme segundo dados fonte fontes documento documentos sem com para por nas nos das dos uma umas uns observação nota".split())
_ROTULO_FONTE = frozenset("guia identidade visual briefing marca hospital base conhecimento cliente baseline fonte fontes tendências tendencias dados mercado relatório relatorio nekt".split())


def _fontes_nao_informadas(texto):
    """Nomes próprios na seção Fontes que o briefing e a base do cliente não citam (veículos, associações, relatórios inventados)."""
    permitido = _normalizar(_TEXTO_PERMITIDO["texto"])
    if not permitido:
        return []
    achados, dentro = [], False
    # links e domínios na seção Fontes que o briefing e a base não trazem; órgão regulador citado como fonte (CFM, ANVISA, CONAR são regras do setor, não fontes de dados)
    em_fontes = False
    for linha in _sem_alerta(texto or "").splitlines():
        l = linha.strip()
        if _FONTE_SECAO.match(l):
            em_fontes = True
            continue
        if em_fontes and (l.startswith("#") or l.startswith("---") or l.startswith("```")):
            em_fontes = False
        if em_fontes and "[validar" not in l.lower():
            for url in re.findall(r"https?://[^\s)\]]+|\b[\w-]+(?:\.[\w-]+)*\.(?:org|com|gov|net)(?:\.br)?\b", l):
                if _normalizar(url) not in permitido:
                    achados.append(url)
            if _ORGAO_REGULADOR.search(l) or re.search(r"conselho federal de medicina", l, re.I):
                achados.append("órgão regulador como fonte")
    for linha in _sem_alerta(texto or "").splitlines():
        l = linha.strip()
        if _FONTE_SECAO.match(l):
            dentro = True
            continue
        if dentro and (l.startswith("#") or l.startswith("---") or l.startswith("```")):
            dentro = False
        if not dentro or "[validar" in l.lower():
            continue
        corpo = re.sub(r"^[-*\d.\s]+", "", l)
        corpo = re.sub(r"^\*{0,2}[^:*]{1,40}\*{0,2}\s*:\s*", "", corpo)       # tira o rótulo ("Tendências:")
        for m in re.finditer(r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÁÉÍÓÚÂÊÔÃÕÇáéíóúâêôãõç]{2,}", corpo):
            nome = m.group(0)
            n = _normalizar(nome)
            inicio_de_frase = m.start() > 0 and corpo[:m.start()].rstrip().endswith((".", "!", "?", ";"))
            if n in _ROTULO_FONTE or n in permitido or _sem_acento(nome).lower() in _ROTULO_FONTE or n in _PALAVRAS_COMUNS or inicio_de_frase:
                continue
            achados.append(nome)
    return sorted(set(achados))


def _sanear_brief(texto):
    """Brief na última tentativa: marcador falso vira [VALIDAR], linha de fonte com nome inventado vira [VALIDAR: fonte] e nota de conformidade é removida."""
    texto, trocas = _sanear_claims(texto)
    novo = _MARCADOR_FALSO.sub("[VALIDAR]", texto)
    if novo != texto:
        trocas.append("marcador falso [confirmado]")
        texto = novo
    saida, dentro = [], False
    for linha in texto.splitlines():
        l = linha.strip()
        if _FONTE_SECAO.match(l):
            dentro = True
        elif dentro and (l.startswith("#") or l.startswith("---") or l.startswith("```")):
            dentro = False
        if dentro and _fontes_nao_informadas("## Fontes\n" + linha):
            trocas.append("fonte inventada")
            saida.append(re.sub(r"(?<=:).*$", " [VALIDAR: fonte]", linha) if ":" in linha else "- [VALIDAR: fonte]")
            continue
        if _PLACEHOLDERS.search(linha) and not l.startswith("|"):
            trocas.append("nota de conformidade")
            continue
        if _valores_rs_inventados(linha, _normalizar(_TEXTO_PERMITIDO["texto"])):
            trocas.append("valor em R$ não informado")
            linha = _acrescentar_marca(linha, "[VALIDAR]")
        saida.append(linha)
    return "\n".join(saida), trocas


def _numeros_informados(permitido):
    """Números (sem R$) que o briefing e a base do cliente trazem, para conferir valores do brief."""
    nums = set(re.findall(r"\d[\d.]*(?:,\d+)?", permitido or ""))
    for v in _INPUTS_ATUAIS.values():
        nums |= set(re.findall(r"\d[\d.]*(?:,\d+)?", str(v)))
    return {n.strip(".,") for n in nums}


def _valores_rs_inventados(texto, permitido):
    """Valores "R$ N" em linha sem [VALIDAR] que não constam do briefing, dos inputs nem da base do cliente."""
    if not permitido and not _INPUTS_ATUAIS:
        return []
    informados = _numeros_informados(permitido)
    achados = []
    for linha in _sem_alerta(texto or "").splitlines():
        if "[validar" in linha.lower():
            continue
        for n in re.findall(r"R\$\s*(\d[\d.]*(?:,\d+)?)", linha):
            n = n.strip(".,")
            if n not in informados and _num(n) and _num(n) >= 100:
                achados.append(f"R$ {n}")
    return sorted(set(achados))


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
    falso = sorted({m.group(0) for m in _MARCADOR_FALSO.finditer(texto)})
    if falso:
        return False, (
            "O brief usa o marcador " + ", ".join(falso) + ", que não existe: nada foi confirmado. O único marcador é [VALIDAR]. Valor que o briefing "
            "traz só como histórico (consumo dos últimos 90 dias, run-rate) não é verba aprovada: escreva [VALIDAR] e diga o que ele é."
        )
    inventadas = _fontes_nao_informadas(texto)
    if inventadas:
        return False, (
            "A seção Fontes cita nomes que o briefing e a base do cliente não trazem: " + ", ".join(inventadas) + ". Cite só as fontes do briefing "
            "(ferramentas de dados e CRM informados) e o guia de marca; para qualquer outra escreva [VALIDAR: fonte]."
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
    inventados_rs = _valores_rs_inventados(texto, permitido)
    if inventados_rs:
        return False, (
            "O brief traz valores em R$ que o briefing não informa e que estão sem [VALIDAR]: " + ", ".join(inventados_rs) + ". O briefing só traz o "
            "orçamento total e a verba de mídia; qualquer divisão, estimativa ou gasto adicional é premissa: escreva [VALIDAR] na mesma linha ou retire o valor."
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
    r"^[\s*`>-]*RESUMO\s*\|\s*(?P<peca>[^|]+?)\s*\|\s*(?P<gates>[^|]+?)\s*\|\s*NOTA\s*=\s*(?P<nota>\d{1,3})\s*/\s*(?P<den>\d{2,3})\s*\|\s*"
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


def _validar_punido_pela_rubrica(texto):
    """
    [VALIDAR] é pendência humana: não reprova gate nem zera "Compliance e precisão". Devolve a mensagem se a rubrica tratou o marcador como falha
    (FALHA citando trecho com [VALIDAR], ou critério de compliance ≤ 5/20 justificado pelo marcador); None se não.
    """
    for linha in _sem_alerta(texto or "").splitlines():
        if re.search(r"\bFALHA\b", linha) and not linha.lstrip().upper().startswith("RESUMO"):
            for citado in re.findall(r"[\"“]([^\"”]{3,200})[\"”]", linha):
                if "[validar" in citado.lower():
                    return (
                        f"A rubrica deu FALHA citando um trecho que já tem [VALIDAR] (\"{citado[:70]}\"). [VALIDAR] é pendência humana e não reprova gate. "
                        "Só há FALHA para afirmação sem fonte e SEM marcação; cite o trecho que está sem [VALIDAR] ou troque o gate para OK."
                    )
        m = re.search(r"compliance e precis[ãa]o[^\d\n]{0,12}(\d{1,2})\s*/\s*20", linha, re.I)
        if m and int(m.group(1)) <= 5 and "validar" in linha.lower():
            return (
                "A nota de Compliance e precisão está em " + m.group(1) + "/20 por causa do marcador [VALIDAR]. O marcador é pendência humana: avalie só o que está "
                "afirmado sem marcação e não reduza a nota por ele."
            )
    return None


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
        # Com gate NA a rubrica às vezes escala o denominador (90/90, 80/100): a nota vale em percentual do denominador declarado.
        den = int(m.group("den"))
        if den <= 0 or den > 100:
            return False, f"A nota de {peca} usa denominador {den}: escreva NOTA=NN/100."
        nota = round(100 * int(m.group("nota")) / den)
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
    punido = _validar_punido_pela_rubrica(texto)
    if punido:
        return False, punido
    if _SEGMENTO_SAUDE.search(str(_INPUTS_ATUAIS.get("segmento", ""))) and "aval m" not in _normalizar(texto):
        return False, "O segmento é saúde: inclua a marca AVAL MÉDICO PENDENTE em todas as peças e no quadro de notas."
    return True, saida


_CANAIS_PAGOS = ("meta ads", "linkedin ads", "tiktok ads", "youtube ads", "youtube", "pmax", "performance max", "demand gen", "discovery", "microsoft ads",
                 "pinterest ads", "twitter ads", "display", "programática")
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


_MARCA_HISTORICO = re.compile(r"run-?rate|[úu]ltimos? \d+ dias|\bem \d+ dias|hist[óo]ric|gasto", re.I)


def _orcamento_de_historico(texto):
    """Mensagem quando o gasto histórico (run-rate de N dias) aparece como orçamento do plano; None se não houver."""
    linhas = _sem_alerta(texto or "").splitlines()
    historico = set()
    for l in linhas:
        if _MARCA_HISTORICO.search(l):
            historico |= {_num(x) for x in re.findall(r"R\$\s*([\d.]+(?:,\d+)?)", l)}
    historico = {h for h in historico if h and h >= 100}
    aprovados = {_num(x) for k in ("orcamento_midia", "orcamento_total") for x in re.findall(r"R\$\s*([\d.]+(?:,\d+)?)", str(_INPUTS_ATUAIS.get(k, "")))}
    for l in linhas:
        if re.search(r"or[çc]amento|verba", l, re.I):
            valores = {_num(x) for x in re.findall(r"R\$\s*([\d.]+(?:,\d+)?)", l)}
            if _MARCA_HISTORICO.search(l) and (valores & aprovados or not re.match(r"^\W{0,6}\**\s*(or[çc]amento|verba)", l.strip(), re.I)):
                continue  # linha que traz a verba aprovada e cita o histórico, ou menção ao histórico fora do rótulo de orçamento
            achados = valores & historico if not _MARCA_HISTORICO.search(l) else {v for v in valores if v and v >= 100}
            if achados:
                total = str(_INPUTS_ATUAIS.get("orcamento_midia", "") or "o orçamento do briefing")
                return (
                    f"R$ {max(achados):,.0f} é gasto histórico (run-rate de dias passados), não orçamento. O orçamento do plano é {total}: declare a verba de cada canal "
                    "como parte desse total, marcada [VALIDAR], e cite o histórico só como referência."
                ).replace(",", ".")
    return None


_CANAIS_ORGANICOS = re.compile(r"\bseo\b|org[âa]nic|blog|conte[úu]do|social media|redes sociais|e-?mail", re.I)


def _verba_rateada_em_organico(texto):
    """Mensagem quando a verba de mídia do briefing é dividida com canais orgânicos (SEO, blog, social orgânico, e-mail); None se não houver."""
    aprovados = {_num(x) for x in re.findall(r"R\$\s*([\d.]+(?:,\d+)?)", str(_INPUTS_ATUAIS.get("orcamento_midia", "")))}
    aprovados = {a for a in aprovados if a}
    if not aprovados:
        return None
    for l in _sem_alerta(texto or "").splitlines():
        valores = {_num(x) for x in re.findall(r"R\$\s*([\d.]+(?:,\d+)?)", l)}
        if valores & aprovados and re.search(r"dividid|distribu|ratead|repartid|alocad[oa]s? entre|entre ", l, re.I) and _CANAIS_ORGANICOS.search(l):
            return (
                f"A linha \"{l.strip()[:110]}\" divide a verba de mídia do briefing com canal orgânico (SEO, blog, conteúdo, social orgânico ou e-mail). "
                "A verba de mídia é só dos canais pagos do brief aprovado; produção, SEO e social orgânico saem do restante do orçamento total, marcados [VALIDAR]."
            )
    return None


def _projecao_em_bloco_sem_validar(texto):
    """Trecho de projeções CPC/CTR/CVR em linhas separadas (listas ou cenários) sem [VALIDAR] por perto; vazio se não houver."""
    t = _sem_alerta(texto or "")
    baixo = t.lower()
    for m in re.finditer(r"\bcpc\b", baixo):
        janela = baixo[max(0, m.start() - 200): m.start() + 450]
        if re.search(r"\bctr\b", janela) and re.search(r"\bcvr\b|convers[ãa]o", janela) and re.search(r"r\$\s*\d|\d\s?%", janela) and "[validar" not in janela:
            inicio = t.rfind("\n", 0, m.start()) + 1
            return t[inicio: t.find("\n", m.start())].strip()[:90] or "cenários"
    return ""


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
    historico = _orcamento_de_historico(texto)
    if historico:
        return historico
    rateio = _verba_rateada_em_organico(texto)
    if rateio:
        return rateio
    bloco_sem_validar = _projecao_em_bloco_sem_validar(texto)
    if bloco_sem_validar:
        return (
            "As projeções de CPC, CTR e CVR (" + bloco_sem_validar + ") não têm fonte nos dados do briefing. Marque o bloco de cenários como [VALIDAR] "
            "(premissas a confirmar) ou cite a fonte; não apresente estimativa como dado."
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


def _trechos_entre_aspas(linha):
    """
    Trechos entre aspas da linha, pareando as aspas retas na ordem (1ª com 2ª, 3ª com 4ª). Pareamento por regex global erra quando há citação curta
    (ex.: "última geração" e "tecnologia de ponta", ...): o texto ENTRE duas citações vira "citação" falsa. Só entram trechos de 25 a 300 caracteres.
    """
    saida = [m.group(1) for m in re.finditer(r"“([^”\n]{25,300})”", linha)]
    pos = [i for i, c in enumerate(linha) if c == '"']
    for a, b in zip(pos[0::2], pos[1::2]):
        q = linha[a + 1:b]
        if 25 <= len(q) <= 300:
            saida.append(q)
    return saida


def _citacoes_inexistentes(parecer, fonte):
    """Trechos entre aspas do parecer que não existem no texto revisado (nem no briefing). Linhas de regra ou correção sugerida não contam."""
    base = _cmp(fonte)
    ruins = []
    for linha in _sem_alerta(parecer).splitlines():
        if re.search(r"corre[çc][ãa]o|\bregra\b|sugest|exemplo", linha, re.I):
            continue
        for q in _trechos_entre_aspas(linha):
            for seg in re.split(r"\.\.\.|…", q):
                n = _cmp(seg)
                if len(n) >= 20 and n not in base:
                    ruins.append(seg.strip()[:90])
                    break
    return ruins[:3]


_SEM_PROBLEMA = re.compile(
    r"nenhuma corre[çc][ãa]o|nenhum ajuste|est[áa] coerente|n[ãa]o h[áa] (diverg[êe]ncia|problema)|sem diverg[êe]ncia|"
    r"n[ãa]o h[áa] necessidade de (altera|corre|ajust)|n[ãa]o (apresenta|traz|possui) (altera[çc][õo]es|diverg[êe]ncias|problemas)|n[ãa]o aplic[áa]vel",
    re.I,
)


def _dimensoes_incoerentes(parecer):
    """Dimensão marcada Reprovada cujo próprio texto diz que está correta (nenhuma correção necessária, está coerente)."""
    blocos, atual = [], None
    for l in _sem_alerta(parecer).splitlines():
        if re.match(r"\s*#{2,4}\s*\S", l):  # qualquer título de seção, numerado ou não ("### Coerência com o Briefing")
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
        elif reprovada:
            objetivo = _normalizar(str(_INPUTS_ATUAIS.get("objetivo", ""))).rstrip(". ")
            citados = [_normalizar(q) for q in re.findall(r"[\"“]([^\"”]{3,})[\"”]", corpo)]
            ncorpo = _normalizar(corpo)
            if re.search(r"coer", _normalizar(cab)) and objetivo and any(objetivo in q for q in citados) and re.search(
                    r"diverg|difere|n[ãa]o corresponde|est[áa] conforme|est[áa] alinhad|id[êe]ntic|igual ao briefing|foi mantido", ncorpo):
                achados.append(cab.strip("# ").strip()[:70] + " (o trecho citado é idêntico ao objetivo do briefing)")
            elif citados and all((q.startswith("validar") and len(q) < 40) or q.startswith("a definir") or (objetivo and objetivo in q) for q in citados):
                achados.append(cab.strip("# ").strip()[:70] + " (só cita trechos já marcados [VALIDAR] ou o objetivo do briefing)")
    return achados


def _reprovadas_sem_trecho(parecer):
    """Dimensões ou entregas Reprovadas cujo bloco não cita nenhum trecho entre aspas: pela regra de evidência, apontamento sem trecho não existe."""
    blocos, atual = [], None
    for l in _sem_alerta(parecer).splitlines():
        if re.match(r"\s*#{2,4}\s*\S", l):
            atual = [l, []]
            blocos.append(atual)
        elif atual is not None:
            atual[1].append(l)
    achados = []
    for cab, linhas in blocos:
        corpo = "\n".join(linhas)
        ncab = _normalizar(cab)
        if re.search(r"resultado|resumo|risco|quadro|recomenda|conclus", ncab):
            continue
        dimensao = re.match(r"\s*#{2,4}\s*\d+[.)]", cab) or re.search(r"status|resultado", _normalizar(corpo))
        reprovada = "reprovad" in ncab or re.search(r"(status|resultado)\W{0,8}reprovad", _normalizar(corpo))
        if dimensao and reprovada and not re.search(r"[\"“«]([^\"”»\n]{10,})[\"”»]", corpo):
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
                f"A dimensão '{inc[0]}' está Reprovada, mas o próprio apontamento diz que está correta, ou só cita o objetivo do briefing (que está "
                "correto), trechos já marcados [VALIDAR] (pendência humana, não erro) ou \"a definir\" (padrão antes da publicação). Se não há problema a corrigir, o status não pode ser Reprovado; "
                "se há, descreva o problema com o trecho literal que está errado."
            )
        sem_trecho = _reprovadas_sem_trecho(texto)
        if sem_trecho:
            return False, (
                f"A dimensão '{sem_trecho[0]}' está Reprovada sem citar nenhum trecho literal entre aspas. Pela regra de evidência, apontamento sem trecho "
                "não existe: cite o trecho exato do documento que motiva a reprovação ou mude o status."
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


def _saneador_aplicacao_g1_factory(brief_task, portao_task):
    """Última barreira da aplicação do G1: sem feedback humano escrito, o brief original (saneado) segue, com o registro "ajustes aplicados: nenhum"."""

    def saneador(texto):
        original = _sem_alerta(getattr(getattr(brief_task, "output", None), "raw", None) or "")
        portao = getattr(getattr(portao_task, "output", None), "raw", None) or ""
        sem_feedback = (not portao) or "nenhum feedback humano" in _normalizar(portao)
        if original and sem_feedback:
            limpo, trocas = _sanear_brief(original)
            cab = ("# Registro de decisão G1\n\n**Status:** Aprovado sem feedback escrito.\n**Ajustes aplicados:** nenhum.\n"
                   "**Ajustes não aplicados e por quê:** não houve feedback humano; o brief original foi mantido.\n\n---\n\n")
            return cab + limpo, trocas + ["brief original mantido (sem feedback humano)"]
        return _sanear_brief(texto)

    return saneador


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
            linhas = _linhas_significativas(_sem_alerta(original))
            norm = _normalizar(getattr(saida, "raw", None) or str(saida) or "")
            if linhas and sum(1 for l in linhas if l in norm) / len(linhas) < 0.7:
                return False, (
                    "Não houve feedback humano escrito: a aprovação foi só \"Aprovado.\". A reemissão deve ser o brief original, sem reescrever, "
                    "sem acrescentar afirmações e sem declarar ajustes que ninguém pediu. Copie o brief original integralmente e registre \"Ajustes aplicados: nenhum\"."
                )
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


def _secoes_rotina_midia(texto):
    """Seções da rotina parametrizada que o plano de mídia omitiu, em Markdown e a partir de _ROTINA (nada inventado). Vazio se o plano já traz tudo."""
    r = _ROTINA.get("operacao") or {}
    if not r:
        return ""
    baixo = _sem_alerta(texto).lower()
    nota = "> Seção inserida automaticamente a partir da rotina parametrizada da Vanguarda, porque a trava esgotou: o gestor de mídia deve revisar e completar."
    partes = []
    if "insumos e pendências" not in baixo and "insumos e pendencias" not in baixo:
        partes.append("## Insumos e pendências\n" + nota + "\n" + " ".join(str(r.get("insumos_obrigatorios", "")).split()) + "\n- Verba, canais e objetivo vêm do brief aprovado; o que faltar fica [VALIDAR] para o Account.")
    if not re.search(r"rotina operacional", baixo) or _faltas_rotina_midia(texto):
        verba = [str(x).replace("{alerta_consumo_pct}", str(_ALERTA_PCT)) for x in r.get("verba", [])]
        itens = verba + [f"URLs de todos os anúncios com UTM (minúsculas e sem espaços)."] + [f"Diária: {_lista(r.get('otimizacao_diaria'), ' → ')}.", f"Semanal: {r.get('rotina_semanal', '')}"]
        partes.append("## Rotina operacional (diária, semanal)\n" + nota + "\n" + "\n".join(f"- {i}" for i in itens if i))
    if not re.search(r"al[çc]adas", baixo):
        partes.append("## Alçadas e autorizações\n" + nota + "\n- Autonomia do gestor: " + _lista(r.get("autonomia")) + ".\n- Exige autorização (Supervisor ou Diretoria): " + _lista(r.get("exige_autorizacao")) + ".\n- Revisão técnica do Supervisor de Mídia Paga antes de ativar; ativação só após o G3.")
    return "\n\n".join(partes)


def _g_doc():
    return _com_limite_de_rejeicoes(_guardrail_documento)


def _g_prod():
    return _com_limite_de_rejeicoes(_guardrail_producao, saneador=_sanear_producao)


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
    # Desenho "aprovar sem corrigir depois": produção → revisão preliminar → CORREÇÃO automática (cada autor reemite a própria peça) →
    # revisão final → portão. Depois do portão só há reescrita se o humano escreveu ajustes (tarefas condicionais); "Aprovado." não reescreve nada.

    @task
    def pesquisa_mercado(self) -> Task:
        return Task(guardrail=_g_doc(), guardrail_max_retries=2, config=self.tasks_config["pesquisa_mercado"])

    @task
    def mapa_seo(self) -> Task:
        return Task(guardrail=_g_doc(), guardrail_max_retries=2, config=self.tasks_config["mapa_seo"], context=[self.pesquisa_mercado()])

    @task
    def brief_estrategico(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_brief, saneador=_sanear_brief), guardrail_max_retries=2,
            config=self.tasks_config["brief_estrategico"],
            context=[self.pesquisa_mercado(), self.mapa_seo()],
        )

    @task
    def revisao_g1(self) -> Task:
        return Task(guardrail=_com_limite_de_rejeicoes(_guardrail_parecer_factory([self.brief_estrategico()])), guardrail_max_retries=2,
                    config=self.tasks_config["revisao_g1"], context=[self.brief_estrategico()])

    @task
    def correcao_brief(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_reemissao_factory(self.brief_estrategico(), "o brief", _guardrail_brief),
                                               saneador=_saneador_reemissao_factory(self.brief_estrategico(), _sanear_brief)), guardrail_max_retries=2,
            config=self.tasks_config["correcao_brief"],
            context=[self.brief_estrategico(), self.revisao_g1()],
        )

    @task
    def revisao_g1_final(self) -> Task:
        return Task(guardrail=_com_limite_de_rejeicoes(_guardrail_parecer_factory([self.correcao_brief()])), guardrail_max_retries=2,
                    config=self.tasks_config["revisao_g1_final"], context=[self.correcao_brief()])

    @task
    def portao_g1(self) -> Task:
        return Task(
            guardrail=_guardrail_portao_factory(self.revisao_g1_final(), portao="G1"), guardrail_max_retries=2,
            config=self.tasks_config["portao_g1"],
            context=[self.correcao_brief(), self.revisao_g1_final()],
        )

    @task
    def aplicacao_g1(self) -> Task:
        # Só reescreve quando o humano devolveu com ajustes; "Aprovado." mantém o brief corrigido, copiado por código.
        return Task(
            guardrail=_com_copia_sem_feedback(self.portao_g1(), self.correcao_brief(), _com_limite_de_rejeicoes(
                _guardrail_reemissao_factory(self.correcao_brief(), "o brief", _guardrail_brief),
                saneador=_saneador_reemissao_factory(self.correcao_brief(), _sanear_brief))), guardrail_max_retries=2,
            config=self.tasks_config["aplicacao_g1"],
            context=[self.correcao_brief(), self.portao_g1()],
        )

    def _brief_vigente(self):
        return _Vigente(self.correcao_brief(), self.aplicacao_g1())

    # ───────────────────────── Tarefas · Fase 2 ─────────────────────────

    @task
    def producao_conteudo(self) -> Task:
        return Task(
            guardrail=_g_prod(), guardrail_max_retries=2,
            config=self.tasks_config["producao_conteudo"],
            context=[self.correcao_brief(), self.aplicacao_g1(), self.mapa_seo(), self.pesquisa_mercado()],
        )

    @task
    def calendario_social(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_calendario, saneador=_sanear_calendario), guardrail_max_retries=2,
            config=self.tasks_config["calendario_social"],
            context=[self.correcao_brief(), self.aplicacao_g1(), self.producao_conteudo(), self.pesquisa_mercado()],
        )

    @task
    def fluxos_email(self) -> Task:
        return Task(
            guardrail=_g_prod(), guardrail_max_retries=2,
            config=self.tasks_config["fluxos_email"],
            context=[self.correcao_brief(), self.aplicacao_g1(), self.producao_conteudo()],
        )

    def _com_rotina(self, nome, bloco):
        """Configuração da tarefa com o bloco da rotina parametrizada (config/rotina_midia.yaml) anexado à descrição."""
        cfg = dict(self.tasks_config[nome])
        cfg["description"] = str(cfg["description"]).rstrip() + (bloco or "")
        return cfg

    @task
    def plano_midia_paga(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_midia_factory(self._brief_vigente()), saneador=_sanear_midia), guardrail_max_retries=2,
            config=self._com_rotina("plano_midia_paga", _bloco_operacao()),
            context=[self.correcao_brief(), self.aplicacao_g1(), self.mapa_seo(), self.pesquisa_mercado(), self.fluxos_email()],
        )

    @task
    def auditoria_midia(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_auditoria_factory(self.plano_midia_paga(), self._brief_vigente())), guardrail_max_retries=2,
            config=self._com_rotina("auditoria_midia", _bloco_auditoria()),
            context=[self.plano_midia_paga(), self.correcao_brief(), self.aplicacao_g1()],
        )

    @task
    def direcao_arte(self) -> Task:
        return Task(
            guardrail=_g_prod(), guardrail_max_retries=2,
            config=self.tasks_config["direcao_arte"],
            context=[self.correcao_brief(), self.aplicacao_g1(), self.producao_conteudo(), self.calendario_social(), self.fluxos_email(), self.plano_midia_paga()],
        )

    @task
    def rubrica_qa(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_rubrica_factory({
                "CONTEUDO": (self.producao_conteudo(), None),
                "CALENDARIO": (self.calendario_social(), None),
                "EMAIL": (self.fluxos_email(), None),
                "MIDIA": (self.plano_midia_paga(), self._brief_vigente()),
            })), guardrail_max_retries=2,
            config=self.tasks_config["rubrica_qa"],
            context=[self.auditoria_midia(), self.correcao_brief(), self.aplicacao_g1(), self.producao_conteudo(), self.calendario_social(), self.fluxos_email(), self.plano_midia_paga()],
        )

    @task
    def revisao_g2(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_parecer_factory(
                [self.producao_conteudo(), self.calendario_social(), self.fluxos_email(), self.plano_midia_paga(), self.direcao_arte()])), guardrail_max_retries=2,
            config=self.tasks_config["revisao_g2"],
            context=[self.producao_conteudo(), self.calendario_social(), self.fluxos_email(), self.plano_midia_paga(), self.direcao_arte()],
        )

    # Correções automáticas antes do portão: cada autor reemite a própria peça com os apontamentos do Guardião, da rubrica e da auditoria.

    @task
    def correcao_conteudo(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_reemissao_factory(self.producao_conteudo(), "o conteúdo", _guardrail_producao),
                                               saneador=_saneador_reemissao_factory(self.producao_conteudo(), _sanear_producao)), guardrail_max_retries=2,
            config=self.tasks_config["correcao_conteudo"],
            context=[self.producao_conteudo(), self.revisao_g2(), self.rubrica_qa(), self.correcao_brief(), self.aplicacao_g1()],
        )

    @task
    def correcao_calendario(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_reemissao_factory(self.calendario_social(), "o calendário", _guardrail_calendario),
                                               saneador=_saneador_reemissao_factory(self.calendario_social(), _sanear_calendario)), guardrail_max_retries=2,
            config=self.tasks_config["correcao_calendario"],
            context=[self.calendario_social(), self.revisao_g2(), self.rubrica_qa(), self.correcao_brief(), self.aplicacao_g1()],
        )

    @task
    def correcao_email(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_reemissao_factory(self.fluxos_email(), "os fluxos de e-mail", _guardrail_producao),
                                               saneador=_saneador_reemissao_factory(self.fluxos_email(), _sanear_producao)), guardrail_max_retries=2,
            config=self.tasks_config["correcao_email"],
            context=[self.fluxos_email(), self.revisao_g2(), self.rubrica_qa(), self.correcao_brief(), self.aplicacao_g1()],
        )

    @task
    def correcao_midia(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_reemissao_factory(self.plano_midia_paga(), "o plano de mídia", _guardrail_midia_factory(self._brief_vigente())),
                                               saneador=_saneador_reemissao_factory(self.plano_midia_paga(), _sanear_midia)), guardrail_max_retries=2,
            config=self._com_rotina("correcao_midia", _bloco_operacao()),
            context=[self.plano_midia_paga(), self.auditoria_midia(), self.revisao_g2(), self.rubrica_qa(), self.correcao_brief(), self.aplicacao_g1()],
        )

    @task
    def correcao_arte(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_reemissao_factory(self.direcao_arte(), "a direção de arte", _guardrail_producao),
                                               saneador=_saneador_reemissao_factory(self.direcao_arte(), _sanear_producao)), guardrail_max_retries=2,
            config=self.tasks_config["correcao_arte"],
            context=[self.direcao_arte(), self.revisao_g2(), self.correcao_conteudo(), self.correcao_calendario(), self.correcao_email(), self.correcao_midia()],
        )

    def _pecas_corrigidas(self):
        return [self.correcao_conteudo(), self.correcao_calendario(), self.correcao_email(), self.correcao_midia(), self.correcao_arte()]

    @task
    def revisao_g2_final(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_cobertura_g2_factory(_guardrail_parecer_factory(self._pecas_corrigidas()))), guardrail_max_retries=2,
            config=self.tasks_config["revisao_g2_final"],
            context=self._pecas_corrigidas(),
        )

    @task
    def portao_g2(self) -> Task:
        return Task(
            guardrail=_guardrail_portao_factory(self.revisao_g2_final(), self.rubrica_qa(), self.auditoria_midia(), portao="G2"), guardrail_max_retries=2,
            config=self.tasks_config["portao_g2"],
            context=[self.revisao_g2_final(), self.rubrica_qa(), self.auditoria_midia()] + self._pecas_corrigidas(),
        )

    # Aplicação do feedback humano, por peça; sem feedback a saída é a cópia literal da versão corrigida (feita em código). "Aprovado." não executa nenhuma delas.

    def _aplicacao(self, nome_cfg, correcao, rotulo, base, saneador, extras=()):
        return Task(
            guardrail=_com_copia_sem_feedback(self.portao_g2(), correcao, _com_limite_de_rejeicoes(
                _guardrail_reemissao_factory(correcao, rotulo, base), saneador=_saneador_reemissao_factory(correcao, saneador))), guardrail_max_retries=2,
            config=self.tasks_config[nome_cfg],
            context=[correcao, self.portao_g2(), *extras],
        )

    @task
    def aplicacao_g2_conteudo(self) -> Task:
        return self._aplicacao("aplicacao_g2_conteudo", self.correcao_conteudo(), "o conteúdo", _guardrail_producao, _sanear_producao)

    @task
    def aplicacao_g2_calendario(self) -> Task:
        return self._aplicacao("aplicacao_g2_calendario", self.correcao_calendario(), "o calendário", _guardrail_calendario, _sanear_calendario)

    @task
    def aplicacao_g2_email(self) -> Task:
        return self._aplicacao("aplicacao_g2_email", self.correcao_email(), "os fluxos de e-mail", _guardrail_producao, _sanear_producao)

    @task
    def aplicacao_g2_midia(self) -> Task:
        return self._aplicacao("aplicacao_g2_midia", self.correcao_midia(), "o plano de mídia", _guardrail_midia_factory(self._brief_vigente()), _sanear_midia,
                               extras=(self.auditoria_midia(),))

    @task
    def aplicacao_g2_arte(self) -> Task:
        return self._aplicacao("aplicacao_g2_arte", self.correcao_arte(), "a direção de arte", _guardrail_producao, _sanear_producao)

    def _pecas_g2(self):
        """{nome: (correção, aplicação condicional)} para o registro, o pacote e o sumário."""
        return {
            "Conteúdo longo": (self.correcao_conteudo(), self.aplicacao_g2_conteudo()),
            "Calendário social": (self.correcao_calendario(), self.aplicacao_g2_calendario()),
            "Fluxos de e-mail": (self.correcao_email(), self.aplicacao_g2_email()),
            "Plano de mídia paga": (self.correcao_midia(), self.aplicacao_g2_midia()),
            "Direção de arte": (self.correcao_arte(), self.aplicacao_g2_arte()),
        }

    def _calendario_vigente(self):
        return _Vigente(self.correcao_calendario(), self.aplicacao_g2_calendario())

    @task
    def registro_g2(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_registro_factory(self._pecas_g2())), guardrail_max_retries=2,
            config=self.tasks_config["registro_g2"],
            context=[self.portao_g2(), self.revisao_g2_final()] + [t for par in self._pecas_g2().values() for t in par],
        )

    # ───────────────────────── Tarefas · Fase 3 ─────────────────────────

    def _vigentes_g2(self):
        return [t for par in self._pecas_g2().values() for t in par]

    @task
    def plano_medicao(self) -> Task:
        return Task(
            guardrail=_g_doc(), guardrail_max_retries=2,
            config=self._com_rotina("plano_medicao", _bloco_medicao()),
            context=[self.correcao_brief(), self.aplicacao_g1(), self.registro_g2()] + self._vigentes_g2(),
        )

    @task
    def pacote_publicacao(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_pacote_factory(self._calendario_vigente(), self.registro_g2()),
                                               saneador=_saneador_pacote_factory(self._calendario_vigente(), self.registro_g2())), guardrail_max_retries=2,
            config=self.tasks_config["pacote_publicacao"],
            context=[self.registro_g2(), self.plano_medicao()] + self._vigentes_g2(),
        )

    @task
    def revisao_g3(self) -> Task:
        return Task(
            guardrail=_com_limite_de_rejeicoes(_guardrail_parecer_factory([self.pacote_publicacao(), self.plano_medicao(), self.registro_g2()] + self._vigentes_g2())), guardrail_max_retries=2,
            config=self.tasks_config["revisao_g3"],
            context=[self.pacote_publicacao(), self.plano_medicao(), self.registro_g2()],
        )

    @task
    def portao_g3(self) -> Task:
        return Task(
            guardrail=_guardrail_portao_factory(self.revisao_g3(), portao="G3"), guardrail_max_retries=2,
            config=self.tasks_config["portao_g3"],
            context=[self.pacote_publicacao(), self.revisao_g3(), self.correcao_midia(), self.aplicacao_g2_midia()],
        )

    @task
    def aplicacao_g3(self) -> Task:
        return Task(
            guardrail=_g_doc(), guardrail_max_retries=2,
            config=self.tasks_config["aplicacao_g3"],
            context=[self.portao_g3(), self.pacote_publicacao(), self.revisao_g3(), self.registro_g2(), self.correcao_midia(), self.aplicacao_g2_midia()],
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
            context=[self.correcao_brief(), self.aplicacao_g1(), self.registro_g2(), self.aplicacao_g3(), self.execucao_publicacao(), self.plano_medicao()],
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
