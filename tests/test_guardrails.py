"""Testes dos guardrails em código. Carrega só as funções puras de crew.py (não exige o crewai instalado)."""
import ast
import pathlib
import re
import types

_FONTE = pathlib.Path(__file__).parent.parent / "src/marketing_ops/crew.py"
_NOMES = {
    "_MIN_CARACTERES_DOCUMENTO", "_FRASES_DE_FALHA", "_guardrail_documento", "_normalizar", "_CLAIMS_NOVOS", "_AFIRMACOES_FALSAS",
    "_guardrail_aplicacao_g2", "_TEXTO_PERMITIDO", "_TERMOS_SENSIVEIS", "_guardrail_producao", "_CLAIMS_PROIBIDOS",
    "_LINHA_NEUTRA", "_PLACEHOLDERS", "_placeholders", "_claims_proibidos", "_guardrail_sem_claims", "_INPUTS_ATUAIS",
    "_guardrail_brief", "_cobertura_calendario", "_CALENDARIO_REEMITIDO", "_trecho_calendario_reemitido",
}


def _carregar():
    arvore = ast.parse(_FONTE.read_text())
    ns = {"re": re}
    for no in arvore.body:
        nome = getattr(no, "name", None) or (no.targets[0].id if isinstance(no, ast.Assign) and isinstance(no.targets[0], ast.Name) else None)
        if nome in _NOMES:
            exec(compile(ast.Module([no], []), str(_FONTE), "exec"), ns)
    return types.SimpleNamespace(**ns)


G = _carregar()
RUIM = [
    "alia tecnologia de ponta ao cuidado humano, garantindo excelência no atendimento",
    "garante que cada consulta seja realizada com precisão e eficiência",
    "O cuidado que conecta você ao melhor.",
    "O melhor atendimento com compromisso e respeito.",
    "Nosso compromisso é proporcionar sempre o melhor cuidado.",
    "Equipamentos de última geração e sistemas inteligentes",
    "Este plano garante aderência à LGPD",
    "permitindo diagnósticos precisos e tratamentos eficazes",
    "Confiança em cada diagnóstico, segurança em cada tratamento.",
    "![CTA](https://example.com/cta-button)",
]
BOM = [
    "Dados que ajudam a cuidar melhor de você [VALIDAR].",
    "Confiança em cada diagnóstico [VALIDAR MÉDICO].",
    "Contraste AA garantido com fundo #003B70 e textos em #FFFFFF",
    "Garantir carregamento correto de imagens e links.",
    "Evitar superlativos como o melhor atendimento.",
    "Excelência Médica (pilar)",
    "Agende sua consulta e conheça nossos serviços [VALIDAR: link].",
]


def test_claims_barrados():
    for t in RUIM:
        assert G._claims_proibidos(t) or G._placeholders(t), t


def test_linhas_legitimas_passam():
    for t in BOM:
        assert not G._claims_proibidos(t) and not G._placeholders(t), t


def _brief(objetivo_no_texto, baseline):
    corpo = "# Brief\n" + ("x" * 1500) + f"\n## Objetivo\n{objetivo_no_texto}\n- Baseline: {baseline}\n"
    return types.SimpleNamespace(raw=corpo)


def test_brief_exige_objetivo_literal_e_baseline_informado():
    G._INPUTS_ATUAIS.clear()
    G._INPUTS_ATUAIS["objetivo"] = "Gerar 400 contatos qualificados (agendamentos e orçamentos) em 8 semanas (baseline: 863 conversões RD em 90 dias)"
    G._TEXTO_PERMITIDO["texto"] = (G._INPUTS_ATUAIS["objetivo"] + " 25.000").lower()
    obj = G._INPUTS_ATUAIS["objetivo"]
    assert G._guardrail_brief(_brief(obj, "863 conversões RD em 90 dias"))[0] is True
    assert G._guardrail_brief(_brief("Aumentar em 20% os agendamentos", "100 consultas mensais"))[0] is False   # objetivo trocado
    assert G._guardrail_brief(_brief(obj, "100 consultas mensais (registros internos)"))[0] is False             # baseline inventado
    assert G._guardrail_brief(_brief(obj, "[VALIDAR: baseline não informado]"))[0] is True


def test_calendario_reemitido_incompleto_e_completo():
    G._INPUTS_ATUAIS.clear()
    G._INPUTS_ATUAIS["duracao_semanas"] = "8"
    G._TEXTO_PERMITIDO["texto"] = ""
    base = "### Parte A\n" + ("a" * 800) + "\n### Parte B\n#### Peça Reemitida: Calendário Social\n"
    curto = base + "| Semana | Data | Plataforma |\n|---|---|---|\n| 1 | 2026-10-03 | Instagram |\n| 1 | 2026-10-05 | LinkedIn |\n\n### Parte C: Lista de Versões\n"
    linhas = "".join(f"| {w} | 2026-10-{3 + 7 * (w - 1):02d} | Instagram |\n" for w in range(1, 9)).replace("2026-10-31", "2026-10-31")
    completo = base + "| Semana | Data | Plataforma |\n|---|---|---|\n" + linhas + "\n### Parte C: Lista de Versões\n"
    assert G._guardrail_aplicacao_g2(types.SimpleNamespace(raw=curto))[0] is False
    assert G._guardrail_aplicacao_g2(types.SimpleNamespace(raw=completo))[0] is True
    sem_calendario = "### Parte A\n" + ("a" * 800) + "\n#### Peça Reemitida: Conteúdo Editorial\ntexto simples\n"
    assert G._guardrail_aplicacao_g2(types.SimpleNamespace(raw=sem_calendario))[0] is True
