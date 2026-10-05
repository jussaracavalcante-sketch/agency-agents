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
    "_PECAS_RUBRICA", "_RESUMO_RUBRICA", "_SEGMENTO_SAUDE", "_sem_acento", "_linhas_resumo_rubrica", "_guardrail_rubrica", "_FONTE_INTERNA", "_CANAIS_PAGOS", "_LINHA_PROJECAO", "_num", "_problemas_midia", "_guardrail_midia_factory", "_ocorrencias_proibidas", "_guardrail_rubrica_factory", "_TAG_ALERTA", "_sem_alerta", "_com_alerta", "_com_limite_de_rejeicoes", "_LINHA_PROJECAO_LISTA", "_ABERTURA_DE_CONVERSA", "_rank_status", "_guardrail_parecer_geral", "_PREFIXO_AUTO", "_PCT_NOVO", "_guardrail_portao_factory", "_linhas_significativas",
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


def _rubrica(linhas, extra=""):
    return types.SimpleNamespace(raw="# Rubrica\n" + ("x" * 900) + "\n" + "\n".join(linhas) + "\n" + extra)


_OK = [
    "RESUMO | CONTEÚDO | G1=OK G2=OK G3=OK G4=NA G5=OK | NOTA=92/100 | VEREDITO=APROVAR | REVISÃO 1 DE 2",
    "RESUMO | CALENDÁRIO | G1=OK G2=OK G3=OK G4=NA G5=OK | NOTA=84/100 | VEREDITO=APROVAR COM AJUSTES MENORES | REVISÃO 1 DE 2",
    "RESUMO | E-MAIL | G1=OK G2=OK G3=OK G4=OK G5=OK | NOTA=70/100 | VEREDITO=DEVOLVER | REVISÃO 1 DE 2",
    "RESUMO | MÍDIA | G1=FALHA G2=OK G3=OK G4=OK G5=OK | NOTA=55/100 | VEREDITO=REFAZER | REVISÃO 1 DE 2",
]


def test_rubrica_valida_e_regras_de_nota():
    G._INPUTS_ATUAIS.clear()
    assert G._guardrail_rubrica(_rubrica(_OK))[0] is True
    assert G._guardrail_rubrica(_rubrica(_OK[:3]))[0] is False                                    # falta a peça MÍDIA
    gate_falha_nota_alta = _OK[:3] + [_OK[3].replace("NOTA=55", "NOTA=75").replace("REFAZER", "DEVOLVER")]
    assert G._guardrail_rubrica(_rubrica(gate_falha_nota_alta))[0] is False                       # gate em FALHA exige nota <= 59
    faixa_errada = [_OK[0].replace("APROVAR |", "DEVOLVER |")] + _OK[1:]
    assert G._guardrail_rubrica(_rubrica(faixa_errada))[0] is False                               # 92 não é DEVOLVER
    sem_gate = [_OK[0].replace("G5=OK", "")] + _OK[1:]
    assert G._guardrail_rubrica(_rubrica(sem_gate))[0] is False                                   # faltam gates


def test_rubrica_exige_aval_medico_em_saude():
    G._INPUTS_ATUAIS.clear()
    G._INPUTS_ATUAIS["segmento"] = "Saúde: hospital privado"
    assert G._guardrail_rubrica(_rubrica(_OK))[0] is False
    assert G._guardrail_rubrica(_rubrica(_OK, "AVAL MÉDICO PENDENTE: todas as peças"))[0] is True
    G._INPUTS_ATUAIS.clear()


def test_linhas_resumo_para_copia_literal():
    r = _rubrica(["**" + _OK[0] + "**"] + _OK[1:])
    assert len(G._linhas_resumo_rubrica(r.raw)) == 4


# --- rodada de 05/10 (execução e3b795a7): trechos reais ---------------------------------------------------------------------
_MIDIA_REAL = """| Cenário | CPC Estimado | CTR Estimado | CVR Estimado | Conversões Calculadas |
|---|---|---|---|---|
| Conservador | R$ 3,00 | 1.5% | 1.5% | 100 |
| Moderado | R$ 2,50 | 2.0% | 2.0% | 200 |
| Otimista | R$ 2,00 | 2.5% | 2.5% | 300 |
"""


def test_termos_novos_e_notas_internas():
    for t in ["aliando infraestrutura de ponta a um atendimento personalizado", "Por que Um Hospital Privado Pode Ser Sua Melhor Escolha",
              "Escolha Segura para Seu Cuidado", "priorizam a precisão e segurança nos tratamentos",
              "posicionar o hospital como a escolha preferencial", "Provas de excelência médica através de certificações reconhecidas",
              "para evitar os problemas de superlativos e garantias não justificadas, reformulei o conteúdo"]:
        assert G._ocorrencias_proibidas(t), t
    for t in ["Trabalho de ponta a ponta com o time", "Escolha informada para a sua saúde.", "Evitar superlativos como o melhor atendimento."]:
        assert not G._ocorrencias_proibidas(t), t


def test_fonte_inventada_no_brief():
    G._INPUTS_ATUAIS.clear(); G._INPUTS_ATUAIS["objetivo"] = "Gerar 400 contatos"
    G._TEXTO_PERMITIDO["texto"] = "gerar 400 contatos nekt rd station"
    corpo = "# Brief\n" + ("x" * 1500) + "\n## Objetivo\nGerar 400 contatos\n- *Fonte:* Análise interna do Hospital\n"
    assert G._guardrail_brief(types.SimpleNamespace(raw=corpo))[0] is False
    assert G._guardrail_brief(types.SimpleNamespace(raw=corpo.replace("Análise interna do Hospital", "Nekt e RD Station")))[0] is True


def test_midia_conversoes_canal_e_projecao():
    G._INPUTS_ATUAIS.clear(); G._INPUTS_ATUAIS["orcamento_midia"] = "R$ 15.000 [VALIDAR]"
    G._TEXTO_PERMITIDO["texto"] = "google ads r$ 15.000"
    brief = "Mix: Google Ads, SEO, redes sociais"
    sem_validar = G._problemas_midia(_MIDIA_REAL, brief)
    assert sem_validar and "VALIDAR" in sem_validar                                   # projeção sem fonte
    assert "bate" in G._problemas_midia("Premissas [VALIDAR]\n" + _MIDIA_REAL, brief)   # 15000/3*1,5% = 75, não 100
    certo = _MIDIA_REAL.replace("| 100 |", "| 75 |").replace("| 200 |", "| 120 |").replace("| 300 |", "| 187 |")
    assert G._problemas_midia("Premissas [VALIDAR]\n" + certo, brief) is None
    assert "Meta Ads" in (G._problemas_midia("Meta Ads: 30% (R$ 4.500)", brief) or "") or "meta ads" in (G._problemas_midia("Meta Ads: 30%", brief) or "")
    assert G._problemas_midia("Meta Ads: 30%", "Mix: Google Ads e Meta Ads") is None


def test_rubrica_com_varredura_em_codigo():
    G._INPUTS_ATUAIS.clear()
    peca = lambda raw: types.SimpleNamespace(output=types.SimpleNamespace(raw=raw))
    fab = G._guardrail_rubrica_factory({
        "CONTEUDO": (peca("aliando infraestrutura de ponta a um atendimento"), None), "CALENDARIO": (peca("ok"), None),
        "EMAIL": (peca("ok"), None), "MIDIA": (peca("ok"), None)})
    ok_cego = _rubrica(_OK[:3] + ["RESUMO | MÍDIA | G1=OK G2=OK G3=OK G4=NA G5=OK | NOTA=98/100 | VEREDITO=APROVAR | REVISÃO 1 DE 2"])
    assert fab(ok_cego)[0] is False                                                    # G1=OK com "de ponta" na peça
    citado = _rubrica(ok_cego.raw.splitlines(), 'Apontamento: "infraestrutura de ponta" é superlativo sem fonte, mas marcado [VALIDAR]')
    assert fab(citado)[0] is True                                                      # o trecho foi citado nos apontamentos
    reprovou = _rubrica([_OK[0].replace("G1=OK", "G1=FALHA").replace("NOTA=92", "NOTA=50").replace("APROVAR", "REFAZER")] + _OK[1:])
    assert fab(reprovou)[0] is True                                                    # G1=FALHA já reconhece o problema


# --- rodada de 05/10 (execução 7ebd5877): melhorias ----------------------------------------------------------------------------
def test_listas_de_projecao_e_no_melhor():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = "google ads"
    lista = "- **Cenário Conservador:** CPC: R$ 5, CTR: 2%, CVR: 3%\n- **Cenário Realista:** CPC: R$ 4, CTR: 3%, CVR: 4%\n"
    assert "VALIDAR" in (G._problemas_midia(lista, "Google Ads") or "")
    assert G._problemas_midia("Premissas [VALIDAR]\n" + lista, "Google Ads") is None
    assert G._ocorrencias_proibidas("Sempre focados no melhor pra você. Conheça-nos.")
    assert not G._ocorrencias_proibidas("Aprender a cuidar melhor da saúde")


def test_alerta_quando_a_trava_esgota():
    peca = types.SimpleNamespace(raw="# Peça\n" + "x" * 800 + "\ninfraestrutura de ponta", name="producao_conteudo")
    g = G._com_limite_de_rejeicoes(lambda s: (False, "A saída cita 'de ponta'."), maximo=2)
    assert g(peca)[0] is False and g(peca)[0] is False
    ok, saida = g(peca)                                                  # terceira rejeição: aceita com alerta
    assert ok is True and isinstance(saida, str) and saida.splitlines()[0].startswith("> ⚠ ALERTA DE QUALIDADE (producao_conteudo)")
    assert "infraestrutura de ponta" in saida
    # a linha de alerta não conta como texto da peça nas varreduras seguintes
    assert not G._ocorrencias_proibidas(saida.splitlines()[0])
    assert "de ponta" in " ".join(t for t, _ in G._ocorrencias_proibidas(saida))   # o texto real continua sendo varrido


def test_resultado_geral_e_a_pior_dimensao():
    base = "# Parecer\n" + "x" * 800 + "\n"
    ruim = base + "## Resultado Geral: **Aprovado com ajustes**\n### 1. Coerência com o Briefing: **Reprovada**\n- **Apontamento**: x\n### 2. Objetivos: **Aprovado**\n"
    assert G._guardrail_parecer_geral(types.SimpleNamespace(raw=ruim))[0] is False
    ok = base + "## Resultado Geral: **Reprovado**\n### 1. Coerência com o Briefing: **Reprovada**\n### 2. Objetivos: **Aprovado**\n"
    assert G._guardrail_parecer_geral(types.SimpleNamespace(raw=ok))[0] is True
    outro = base + "## Resultado Geral\n**Aprovado**\n### 1. A\n**Status:** Aprovado com ajustes\n"
    assert G._guardrail_parecer_geral(types.SimpleNamespace(raw=outro))[0] is False
    sem_dims = base + "Resultado Geral: Aprovado\n"
    assert G._guardrail_parecer_geral(types.SimpleNamespace(raw=sem_dims))[0] is True


def test_abertura_de_conversa():
    doc = lambda ini: types.SimpleNamespace(raw=ini + "\n" + "# Registro\n" + "x" * 900)
    assert G._guardrail_documento(doc("Para proceder corretamente com a aplicação da Decisão G2, precisamos garantir rigor"))[0] is False
    assert G._guardrail_documento(doc("```markdown"))[0] is True
    assert G._guardrail_documento(doc("> ⚠ ALERTA DE QUALIDADE: x"))[0] is True


# --- melhorias 6/6 (execução c3298b2a) -----------------------------------------------------------------------------------------
_INPUTS_STJ = {"objetivo": "Gerar 400 contatos qualificados (agendamentos e orçamentos) em 8 semanas (baseline: 863 conversões RD em 90 dias, 343 vindas de mídia paga)",
               "orcamento_total": "R$ 25.000 [VALIDAR]", "orcamento_midia": "R$ 15.000 [VALIDAR]", "ferramenta_crm": "RD Station",
               "ferramenta_analytics": "Nekt Refined; GA4 + GTM fora da Nekt"}


def _brief_stj(extra="", obj=None):
    G._INPUTS_ATUAIS.clear(); G._INPUTS_ATUAIS.update(_INPUTS_STJ)
    G._TEXTO_PERMITIDO["texto"] = " ".join(_INPUTS_STJ.values()).lower()
    o = obj or _INPUTS_STJ["objetivo"]
    corpo = "# Brief\n" + ("x" * 1500) + f"\n## Objetivos SMART\n> {o}\n- Baseline: 863 conversões RD\n- Fonte: Nekt e RD Station\n"
    corpo += "## Orçamento\n- Total: R$ 25.000 [VALIDAR]\n- Mídia paga: R$ 15.000 [VALIDAR]\n" + extra
    return types.SimpleNamespace(raw=corpo)


def test_brief_regras_novas():
    assert G._guardrail_brief(_brief_stj())[0] is True                                                   # objetivo em bloco de citação
    assert "crm do hospital" in G._guardrail_brief(_brief_stj("- Fonte: CRM do Hospital Santa Júlia\n"))[1]
    assert "40%" in G._guardrail_brief(_brief_stj("1. Google Ads resultará em aumento de 40% em contatos\n"))[1]
    assert G._guardrail_brief(_brief_stj("1. Google Ads pode elevar contatos em 40% [VALIDAR]\n"))[0] is True
    sem_verba = _brief_stj()
    sem_verba.raw = sem_verba.raw.replace("R$ 15.000", "R$ 12.000")
    assert "mídia" in G._guardrail_brief(sem_verba)[1]
    sem_validar = _brief_stj()
    sem_validar.raw = sem_validar.raw.replace("Total: R$ 25.000 [VALIDAR]", "Total: R$ 25.000")
    assert "VALIDAR" in G._guardrail_brief(sem_validar)[1]


def test_vamos_e_prefixo_de_revisao_automatica():
    d = types.SimpleNamespace(raw="Vamos seguir a estrutura pedida e corrigir os objetivos\n# Brief\n" + "x" * 900)
    assert G._guardrail_documento(d)[0] is False
    g = G._com_limite_de_rejeicoes(lambda s: (False, "problema X"), maximo=1)
    ok, msg = g(types.SimpleNamespace(raw="y", name="t"))
    assert ok is False and msg.startswith("REVISÃO AUTOMÁTICA DE QUALIDADE (não é feedback humano") and msg.endswith("problema X")
    ok2, saida = (g(types.SimpleNamespace(raw="y", name="t")))
    assert ok2 is True and "Pendência: problema X" in saida and "REVISÃO AUTOMÁTICA" not in saida     # o alerta traz o motivo sem o prefixo
