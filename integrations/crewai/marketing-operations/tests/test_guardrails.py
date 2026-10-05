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
    "_PECAS_RUBRICA", "_RESUMO_RUBRICA", "_SEGMENTO_SAUDE", "_sem_acento", "_linhas_resumo_rubrica", "_guardrail_rubrica", "_FONTE_INTERNA", "_CANAIS_PAGOS", "_LINHA_PROJECAO", "_num", "_problemas_midia", "_guardrail_midia_factory", "_ocorrencias_proibidas", "_guardrail_rubrica_factory", "_TAG_ALERTA", "_sem_alerta", "_com_alerta", "_com_limite_de_rejeicoes", "_LINHA_PROJECAO_LISTA", "_ABERTURA_DE_CONVERSA", "_rank_status", "_guardrail_parecer_geral", "_texto_apos_documento", "_FONTE_MERCADO", "_ORGAO_REGULADOR", "_cmp", "_citacoes_inexistentes", "_SEM_PROBLEMA", "_dimensoes_incoerentes", "_guardrail_parecer_factory", "_guardrail_aplicacao_g1_factory", "_lista", "_bloco_operacao", "_bloco_auditoria", "_bloco_medicao", "_FALTAS_ROTINA", "_faltas_rotina_midia", "_guardrail_auditoria_factory", "_PREFIXO_AUTO", "_PCT_NOVO", "_guardrail_portao_factory", "_linhas_significativas", "_PALAVRAS_EN", "_PALAVRAS_PT", "_linha_em_ingles", "_CHAVE_PECA", "_pecas_para_refazer", "_guardrail_aplicacao_g2_factory", "_linhas_social", "_guardrail_pacote_factory", "_datas_do_texto", "_acrescentar_marca", "_sanear_claims", "_sanear_producao", "_sanear_reemissao", "_sanear_midia", "_hoje", "_trecho_reemitido", "_a_partir_da_reemissao", "_HISTORIAS_PACIENTES", "_historias_de_pacientes", "_tabela_sem_coluna_data", "_SERVICOS_LISTA", "_texto_permitido", "_servicos_nao_informados", "_saneador_aplicacao_g1_factory", "_MARCADOR_FALSO", "_FONTE_SECAO", "_ROTULO_FONTE", "_fontes_nao_informadas", "_sanear_brief", "_ARTIGO_MASCULINO", "_TERMOS_COM_ARTIGO", "_secoes_rotina_midia", "_validar_punido_pela_rubrica", "_extrair_datas", "_PECAS_G2", "_feedback_do_portao", "_saneador_aplicacao_g2_factory", "_SEM_PROBLEMA", "_datas_passadas", "_linha_solta_na_tabela", "_problemas_calendario", "_guardrail_calendario",
}


def _carregar():
    arvore = ast.parse(_FONTE.read_text())
    import yaml
    rotina = yaml.safe_load((_FONTE.parent / "config/rotina_midia.yaml").read_text(encoding="utf-8"))
    ns = {"re": re, "_ROTINA": rotina, "_ALERTA_PCT": int(rotina["parametros"]["alerta_consumo_pct"])}
    for no in arvore.body:
        nome = getattr(no, "name", None) or (no.targets[0].id if isinstance(no, ast.Assign) and isinstance(no.targets[0], ast.Name) else None)
        if nome in _NOMES:
            exec(compile(ast.Module([no], []), str(_FONTE), "exec"), ns)
    from datetime import date

    ns["_hoje"] = lambda: date(2026, 9, 1)   # data fixa: os calendários dos testes não podem "envelhecer"
    g = types.SimpleNamespace(**ns)
    g._ns = ns
    return g


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
    from datetime import date, timedelta
    linhas = "".join(f"| {i // 3 + 1} | {(date(2026, 10, 3) + timedelta(days=i * 2 + 1)).isoformat()} | Instagram |\n" for i in range(24))   # 3 posts por semana
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


# --- 5 melhorias (execução 8e11e98c): trechos reais -------------------------------------------------------------------------------
_BRIEF_REAL = """```markdown
# Brief Estratégico
## 4. Proposta de Valor
| Consideração | Conheça a diferença que um atendimento [VALIDAR] pode fazer | Agende uma visita |
## 9. Fontes
- Baseline: Nekt Refined
```

Este documento foi criado seguindo rigorosamente as diretrizes do guia de identidade visual. Todas as propostas e validações foram claramente indicadas."""

_PARECER_REAL = """# Parecer
## Resultado Geral: Reprovado
### 1. Coerência com o Briefing
- **Status:** Reprovado
- **Apontamento:** O objetivo está coerente com o briefing.
- **Correção Sugerida:** Nenhuma correção necessária quanto ao objetivo SMART.
### 3. Veracidade e Setor Regulamentado
- **Status:** Reprovado
- **Apontamento:** Trechos como "conhecimento da diferença que um atendimento [VALIDAR] pode fazer" carecem de validação.
"""


def _tarefa(raw):
    return types.SimpleNamespace(output=types.SimpleNamespace(raw=raw))


def test_texto_depois_do_documento_e_autocertificacao():
    assert G._texto_apos_documento(_BRIEF_REAL).startswith("Este documento foi criado")
    assert G._texto_apos_documento("```markdown\n# Doc\n```") == ""
    assert G._texto_apos_documento("# Doc sem bloco\n" + "x" * 50) == ""
    d = types.SimpleNamespace(raw=_BRIEF_REAL + "\n" + "y" * 800)
    assert G._guardrail_documento(d)[0] is False
    assert G._ocorrencias_proibidas("Todos os feedbacks e revisões foram considerados e incluídos. Não há ajustes pendentes.")
    assert G._ocorrencias_proibidas("Este documento foi criado seguindo rigorosamente as diretrizes")
    assert not G._ocorrencias_proibidas("O documento segue as diretrizes do guia de marca.")


def test_orgao_regulador_como_fonte_de_mercado():
    G._INPUTS_ATUAIS.clear(); G._INPUTS_ATUAIS.update(_INPUTS_STJ)
    G._TEXTO_PERMITIDO["texto"] = " ".join(_INPUTS_STJ.values()).lower()
    ruim = _brief_stj("- Dados de Mercado: Conselho Federal de Medicina, ANVISA, CONAR\n")
    assert "regulador" in G._guardrail_brief(ruim)[1]
    assert G._guardrail_brief(_brief_stj("- Regras do setor: CFM, ANVISA e CONAR [VALIDAR]\n"))[0] is True


def test_parecer_com_citacao_deturpada_e_dimensao_incoerente():
    brief = _tarefa(_BRIEF_REAL)
    g = G._guardrail_parecer_factory([brief])
    G._TEXTO_PERMITIDO["texto"] = ""
    r = g(types.SimpleNamespace(raw=_PARECER_REAL + "x" * 900))
    assert r[0] is False and ("Coerência" in r[1] or "Reprovada" in r[1])                     # dimensão incoerente vem primeiro
    sem_incoerencia = _PARECER_REAL.replace("- **Status:** Reprovado\n- **Apontamento:** O objetivo está coerente", "- **Status:** Aprovado\n- **Apontamento:** O objetivo está coerente", 1)
    r2 = g(types.SimpleNamespace(raw=sem_incoerencia + "x" * 900))
    assert r2[0] is False and "conhecimento da diferença" in r2[1]                              # citação deturpada
    certo = sem_incoerencia.replace("conhecimento da diferença que um atendimento [VALIDAR] pode fazer", "Conheça a diferença que um atendimento [VALIDAR] pode fazer")
    certo = certo.replace("Resultado Geral: Reprovado", "Resultado Geral: Reprovado")
    assert g(types.SimpleNamespace(raw=certo + "x" * 900))[0] is True
    assert G._citacoes_inexistentes('- Apontamento: "Conheça a diferença ... pode fazer uma diferença enorme"', _BRIEF_REAL)    # segmento inexistente
    assert not G._citacoes_inexistentes('- Correção Sugerida: "Trocar por texto sem promessa e sem superlativo"', _BRIEF_REAL)    # linha de correção não conta


def test_aplicacao_g1_preserva_validar():
    original = "# Brief\n" + "x" * 900 + "\n- Mídia R$ 15.000 [VALIDAR]\n- +20% [VALIDAR]\n- Total R$ 25.000 [VALIDAR]\n"
    portao = _tarefa("# G1\n## Histórico de Feedbacks Humanos\nNenhum feedback humano recebido.\n")
    g = G._guardrail_aplicacao_g1_factory(_tarefa(original), portao)
    nova = _brief_stj()
    nova.raw = nova.raw.replace(" [VALIDAR]", "", 2)
    G._INPUTS_ATUAIS.clear(); G._INPUTS_ATUAIS.update(_INPUTS_STJ)
    G._TEXTO_PERMITIDO["texto"] = " ".join(_INPUTS_STJ.values()).lower()
    perdeu = types.SimpleNamespace(raw="# Brief\n" + "x" * 1500 + "\n## Objetivos SMART\n> " + _INPUTS_STJ["objetivo"] + "\n- Fonte: Nekt\n- Mídia R$ 15.000 [VALIDAR]\n- Total R$ 25.000 [VALIDAR]\n")
    assert "[VALIDAR]" in g(perdeu)[1]                                                       # 2 marcações contra 3 do original
    mantem = types.SimpleNamespace(raw=perdeu.raw + "- +20% [VALIDAR]\n")
    assert g(mantem)[0] is True
    com_feedback = g.__class__ and G._guardrail_aplicacao_g1_factory(_tarefa(original), _tarefa("# G1\nFeedback: confirmado o orçamento"))
    assert com_feedback(perdeu)[0] is True                                                   # humano escreveu feedback: a regra não se aplica


# --- rotina de mídia paga e performance (formulários de Carlos André e João Araújo) ------------------------------------------------
_PLANO_OK = ("# Plano de Mídia\n" + "x" * 700 + "\n## Insumos e pendências\n- Verba por canal [VALIDAR]\n## Rotina operacional (diária, semanal)\n"
             "- Budget pace diário por conta; alerta aos 90% do orçamento.\n- URLs com UTM em minúsculas.\n- Revisão técnica do Supervisor antes de ativar.\n"
             "## Alçadas e autorizações\n- Alterar orçamento total exige autorização.\n")


def test_blocos_da_rotina_trazem_os_parametros():
    op = G._bloco_operacao()
    assert "90%" in op and "budget pace" in op.lower() and "UTM" in op and "e-mail ou chamado no VJOB" in op
    assert "alterar o valor total do orçamento do cliente" in op and "pausar criativos" in op
    aud = G._bloco_auditoria()
    for item in ("SEGMENTAÇÃO", "PIXEL/CAPI E TAGS", "CRIATIVOS", "URLS E UTM", "COPIES", "VERBA E BUDGET PACE", "ALÇADAS"):
        assert item in aud, item
    med = G._bloco_medicao()
    assert "GTM" in med and "GA4" in med and "Supervisor" in med and "Account" in med


def test_plano_de_midia_exige_a_rotina():
    assert G._faltas_rotina_midia(_PLANO_OK) == []
    faltas = G._faltas_rotina_midia("# Plano\nSó Google Ads e CPC.")
    assert len(faltas) == 5
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = "google ads"
    g = G._guardrail_midia_factory(types.SimpleNamespace(output=types.SimpleNamespace(raw="Mix: Google Ads")))
    assert "rotina de mídia" in g(types.SimpleNamespace(raw="# Plano\n" + "x" * 800 + "\nGoogle Ads"))[1]
    assert g(types.SimpleNamespace(raw=_PLANO_OK))[0] is True


_AUD = [
    "AUDITORIA | SEGMENTAÇÃO | OK | públicos coerentes com o briefing",
    "AUDITORIA | PIXEL/CAPI E TAGS | PENDENTE | [VALIDAR] eventos a configurar",
    "AUDITORIA | CRIATIVOS | OK | briefing de criativos presente",
    "AUDITORIA | URLS E UTM | OK | todas as URLs com UTM em minúsculas",
    "AUDITORIA | COPIES | OK | sem superlativos",
    "AUDITORIA | VERBA E BUDGET PACE | OK | soma R$ 15.000",
    "AUDITORIA | ALÇADAS | OK | alteração de orçamento exige autorização",
]


def _aud(linhas, parecer):
    return types.SimpleNamespace(raw="\n".join(linhas) + "\n" + parecer + "\n" + "x" * 800)


def test_auditoria_do_supervisor():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = "google ads"
    plano = types.SimpleNamespace(output=types.SimpleNamespace(raw=_PLANO_OK))
    brief = types.SimpleNamespace(output=types.SimpleNamespace(raw="Mix: Google Ads"))
    g = G._guardrail_auditoria_factory(plano, brief)
    lib = "PARECER DO SUPERVISOR | LIBERAR PARA G2 | pendências de pixel"
    assert g(_aud(_AUD, lib))[0] is True
    assert g(_aud(_AUD[:6], lib))[0] is False                                                       # falta o item ALÇADAS
    falha = [l.replace("| OK | sem superlativos", "| FALHA | \"garante o melhor atendimento\" é promessa") for l in _AUD]
    assert g(_aud(falha, lib))[0] is False                                                          # FALHA exige DEVOLVER
    assert g(_aud(falha, "PARECER DO SUPERVISOR | DEVOLVER AO GESTOR | copies"))[0] is True
    assert g(_aud(_AUD, "PARECER DO SUPERVISOR | DEVOLVER AO GESTOR | x"))[0] is False             # devolve sem FALHA
    assert g(_aud(_AUD, "sem parecer"))[0] is False
    ruim = types.SimpleNamespace(output=types.SimpleNamespace(raw=_PLANO_OK + "\nMeta Ads: 30% (R$ 4.500)\n"))
    g2 = G._guardrail_auditoria_factory(ruim, brief)
    r = g2(_aud(_AUD, lib))                                                                          # a varredura achou canal fora do brief e o parecer liberou
    assert r[0] is False and "varredura" in r[1]


def _saida(txt):
    return types.SimpleNamespace(raw=txt)


def test_frase_em_ingles_e_barrada():
    doc = "# Registro\n" + "texto em português do Brasil com bastante conteúdo útil para o leitor. " * 12
    G._INPUTS_ATUAIS.clear()
    assert G._guardrail_documento(_saida(doc))[0] is True
    ruim = doc + "\nThe document has been processed as per the requirements, with all decisions documented."
    r = G._guardrail_documento(_saida(ruim))
    assert r[0] is False and "inglês" in r[1]
    abertura = "I'll handle the application of decision G2 and its associated tasks for the team.\n" + doc
    assert G._guardrail_documento(_saida(abertura))[0] is False
    assert G._linha_em_ingles("| Hook | Descubra como a tecnologia transforma sua saúde |") == ""      # tabela e português passam
    assert G._linha_em_ingles("Use o Google Analytics com a tag do Meta Pixel para medir cada conversão do funil.") == ""


def _calendario(linhas):
    cab = "| Semana | Data | Plataforma | Formato | Pilar | Hook | CTA |\n|---|---|---|---|---|---|---|\n"
    return cab + "\n".join(linhas)


def test_calendario_so_com_a_ultima_semana_nao_cobre():
    G._INPUTS_ATUAIS.clear(); G._INPUTS_ATUAIS["duracao_semanas"] = "8"
    tres = _calendario(["| 1 | 01/11/2026 | Instagram | Carrossel | a | b | c |", "| 1 | 03/11/2026 | Facebook | Vídeo | a | b | c |", "| 8 | 20/12/2026 | Instagram | Vídeo | a | b | c |"])
    assert G._cobertura_calendario(tres)
    from datetime import date, timedelta
    completo = _calendario([f"| {i // 3 + 1} | {(date(2026, 11, 1) + timedelta(days=i * 2)).strftime('%d/%m/%Y')} | Instagram | Post | a | b | c |" for i in range(24)])
    assert G._cobertura_calendario(completo) is None


def _tarefa(txt):
    return types.SimpleNamespace(output=types.SimpleNamespace(raw=txt))


_RUB = "\n".join([
    "RESUMO | CONTEÚDO | G1=FALHA G2=OK G3=FALHA G4=NA G5=OK | NOTA=59/100 | VEREDITO=REFAZER | REVISÃO 1 DE 2",
    "RESUMO | CALENDÁRIO | G1=OK G2=OK G3=OK G4=NA G5=OK | NOTA=94/100 | VEREDITO=APROVAR | REVISÃO 1 DE 2",
    "RESUMO | E-MAIL | G1=OK G2=OK G3=FALHA G4=NA G5=OK | NOTA=59/100 | VEREDITO=REFAZER | REVISÃO 1 DE 2",
    "RESUMO | MÍDIA | G1=FALHA G2=OK G3=FALHA G4=NA G5=OK | NOTA=59/100 | VEREDITO=REFAZER | REVISÃO 1 DE 2",
])


def _aplicacao(bloqueadas):
    return _saida("# Parte A: Registro de decisão G2\n" + ("conteúdo registrado com a decisão e os ajustes pedidos pelo Guardião para cada entrega. " * 10)
                  + f"\n- **Liberadas**: Calendário Social\n- **Bloqueadas**: {bloqueadas}\n")


def test_aprovado_sem_texto_nao_libera_peca_refazer():
    G._INPUTS_ATUAIS.clear()
    g = G._guardrail_aplicacao_g2_factory(_tarefa(_RUB), _tarefa("Histórico de feedbacks humanos\nNenhum feedback humano recebido\n\"Aprovado.\""))
    r = g(_aplicacao("Produção de Conteúdo, Plano de Mídia Paga"))                      # e-mail REFAZER ficou liberado
    assert r[0] is False and "EMAIL" in r[1]
    assert g(_aplicacao("Produção de Conteúdo, Fluxos de E-mail, Plano de Mídia Paga"))[0] is True
    devolvido = _tarefa("DECISÃO G2: DEVOLVIDO COM FEEDBACK por X. Ajustes pedidos: refazer o e-mail")
    assert G._guardrail_aplicacao_g2_factory(_tarefa(_RUB), devolvido)(_aplicacao("Plano de Mídia Paga"))[0] is True


_CAL_ORIG = _calendario(["| 1 | 02/11/2026 | Instagram | Carrossel | a | b | c |", "| 2 | 09/11/2026 | Facebook | Vídeo | a | b | c |"])
_CAL_REEMIT = "### Peça reemitida: Calendário Social\n" + _calendario(["| 1 | 01/11/2026 | Instagram | Carrossel | a | b | c |", "| 1 | 03/11/2026 | Facebook | Vídeo | a | b | c |"])


def _pacote(linhas):
    return _saida("# Índice do Pacote\n" + ("peça listada no índice com o status de liberação e o nome padronizado do arquivo. " * 10)
                  + "\n# Cronograma\n| Semana | Data | Canal | Peça |\n|---|---|---|---|\n" + "\n".join(linhas) + "\n")


def test_pacote_usa_o_calendario_vigente():
    G._INPUTS_ATUAIS.clear()                                                                # sem duracao_semanas: só confere datas
    g = G._guardrail_pacote_factory(_tarefa(_CAL_ORIG), _tarefa(_CAL_REEMIT))
    ok = _pacote(["| 1 | 01/11/2026 | Instagram | Carrossel |", "| 1 | 03/11/2026 | Facebook | Vídeo |"])
    assert g(ok)[0] is True
    antigo = _pacote(["| 1 | 02/11/2026 | Instagram | Carrossel |"])                       # data do calendário substituído
    r = g(antigo)
    assert r[0] is False and "02/11/2026" in r[1]
    pendente = _pacote(["| 1 | a definir | Instagram | Carrossel |"])
    assert g(pendente)[0] is False
    assert g(_pacote(["| 1 | 15/11/2026 | E-mail | Boas-vindas |"]))[0] is True            # data de e-mail não é checada contra o calendário social


def test_saneador_troca_servico_e_claim_ao_esgotar_a_trava():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = "hospital santa júlia manaus agendamentos"
    doc = ("# Brief\n" + "Contexto do hospital em Manaus com bastante texto útil para atingir o tamanho mínimo exigido do documento. " * 10
           + "\nConheça a cirurgia robótica no hospital.\nNossa tecnologia de ponta cuida de você.\n| Canal | Nota |\n|---|---|\n| Site | tecnologia de ponta |\n")
    g = G._com_limite_de_rejeicoes(G._guardrail_producao, saneador=G._sanear_producao)
    s = _saida(doc)
    assert g(s)[0] is False and g(s)[0] is False
    ok, texto = g(s)                                                                  # 3ª rejeição: aceita já saneada
    assert ok is True and "ALERTA DE QUALIDADE" in texto
    corpo = texto.split("\n\n", 1)[1]
    assert "cirurgia robótica" not in corpo and "O serviço [VALIDAR: confirmar com o hospital]" not in corpo and "serviço [VALIDAR: confirmar com o hospital]" in corpo
    assert "tecnologia de ponta cuida de você. [VALIDAR MÉDICO]" in corpo
    assert "| Site | tecnologia de ponta [VALIDAR MÉDICO] |" in corpo                  # tabela continua íntegra
    assert G._guardrail_producao(_saida(corpo))[0] is True                           # o texto saneado passa na própria trava


def test_saneador_de_midia_marca_canal_fora_do_brief():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = "google ads"
    texto, trocas = G._sanear_midia("Google Ads: R$ 15.000\nYouTube Ads e Display: R$ 3.000")
    assert "Google Ads" in texto and "YouTube Ads" not in texto and "Display" not in texto and trocas


def test_saneador_de_reemissao_nao_mexe_no_registro():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = "hospital"
    texto = "### Parte A\n| Conteúdo | Remover tecnologia de ponta | Guardião |\n### Parte B\n#### Peça reemitida: Conteúdo\nA tecnologia de ponta do hospital.\n"
    novo, trocas = G._sanear_reemissao(texto)
    assert "Remover tecnologia de ponta | Guardião |" in novo and "hospital. [VALIDAR MÉDICO]" in novo and trocas


def test_calendario_com_data_passada_e_linha_solta():
    G._INPUTS_ATUAIS.clear(); G._INPUTS_ATUAIS["duracao_semanas"] = "2"
    from datetime import date, timedelta
    def cal(inicio, extra=""):
        linhas = [f"| {i // 3 + 1} | {(inicio + timedelta(days=i * 2)).strftime('%d/%m/%Y')} | Instagram | Post | a | b | c |" for i in range(6)]
        return _calendario(linhas) + extra
    G._ns["_hoje"] = lambda: date(2026, 10, 5)
    try:
        assert G._problemas_calendario(cal(date(2026, 10, 6))) is None
        r = G._problemas_calendario(cal(date(2026, 10, 2)))
        assert r and "já passaram" in r and "02/10/2026" in r
        solta = cal(date(2026, 10, 6)).replace("| 1 | 08/10/2026", "| Pode usar [VALIDAR MÉDICO] para algo |\n| 1 | 08/10/2026", 1)
        assert "fora do formato" in (G._problemas_calendario(solta) or "")
    finally:
        G._ns["_hoje"] = lambda: date(2026, 9, 1)


def test_calendario_com_datas_sem_ano():
    from datetime import date
    G._INPUTS_ATUAIS.clear(); G._INPUTS_ATUAIS["duracao_semanas"] = "8"
    sem_ano = _calendario(["| 1 | 02/10 | Instagram | Carrossel | a | b | c |", "| 1 | 04/10 | Facebook | Vídeo | a | b | c |", "| 2 | 09/10 | Instagram | Reels | a | b | c |"])
    G._ns["_hoje"] = lambda: date(2026, 10, 5)
    try:
        assert [d.day for d in G._extrair_datas(sem_ano)] == [2, 4, 9]
        assert G._datas_passadas(sem_ano) == ["02/10/2026", "04/10/2026"]
        assert "já passaram" in (G._problemas_calendario(sem_ano) or "") or "cobre" in (G._problemas_calendario(sem_ano) or "")
        assert G._extrair_datas("Período 10/2026 e 12/2026, razão 10/20") == []                        # mês/ano e frações não são datas
        assert [d.day for d in G._extrair_datas("01/11/2026 e 2026-11-02")] == [1, 2]
    finally:
        G._ns["_hoje"] = lambda: date(2026, 9, 1)


def test_dimensao_sem_problema_reconhece_nao_ha_necessidade():
    assert G._SEM_PROBLEMA.search("Não há necessidade de alteração imediata; mantimento do objetivo literal")
    assert G._SEM_PROBLEMA.search("O objetivo do brief estratégico não apresenta alterações em relação ao briefing")
    assert not G._SEM_PROBLEMA.search("Faltou citar a verba de mídia do briefing")


_PORTAO = ("```markdown\n## Histórico de feedbacks humanos\nDECISÃO G2: DEVOLVIDO COM FEEDBACK por X em 2026-10-05. Ajustes pedidos: 1. Calendário a partir de 06/10/2026.\n\nAprovado.\n\n"
           "## Parecer do Guardião (cópia literal)\nReprovado\n")


def test_aplicacao_g2_que_nao_leu_o_feedback_vira_registro_de_bloqueio():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = "hospital"
    recusa = _saida("Parece que não consegui obter o feedback necessário do portão G2. Recomendo verificar o acesso aos documentos com a equipe de TI.")
    assert G._guardrail_documento(recusa)[0] is False
    g = G._com_limite_de_rejeicoes(G._guardrail_aplicacao_g2_factory(_tarefa(_RUB), _tarefa(_PORTAO)), saneador=G._saneador_aplicacao_g2_factory(_tarefa(_PORTAO)))
    assert g(recusa)[0] is False and g(recusa)[0] is False
    ok, texto = g(recusa)
    assert ok is True and "ALERTA DE QUALIDADE" in texto
    corpo = texto.split("\n\n", 1)[1]
    assert "NÃO EXECUTADA" in corpo and "Nenhuma peça foi reemitida" in corpo and "Calendário a partir de 06/10/2026" in corpo
    assert "Entregas liberadas\n- Nenhuma." in corpo and "não consegui obter" not in corpo.lower()


def test_pacote_nao_lista_posts_quando_a_aplicacao_nao_foi_executada():
    G._INPUTS_ATUAIS.clear()
    apl = _tarefa("# Aplicação da decisão G2: NÃO EXECUTADA\nNenhuma peça foi reemitida.\n## Entregas liberadas\n- Nenhuma.")
    g = G._guardrail_pacote_factory(_tarefa(_CAL_ORIG), apl)
    assert g(_pacote(["| 1 | 02/11/2026 | Instagram | Carrossel |"]))[0] is False
    assert g(_pacote(["| E-mail | a definir | Boas-vindas |"]))[0] is True


def test_saneador_mantem_a_frase_legivel():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = "hospital consultas exames"
    texto, trocas = G._sanear_claims("A telemedicina proporciona conveniência.\nConheça a cirurgia robótica do hospital.\nAgende consultas e exames.\nNa maternidade, tudo é simples.")
    assert "O serviço [VALIDAR: confirmar com o hospital] proporciona conveniência." in texto
    assert "Conheça o serviço [VALIDAR: confirmar com o hospital] do hospital." in texto                  # "a cirurgia robótica" vira "o serviço ..."
    assert "No serviço [VALIDAR: confirmar com o hospital], tudo é simples." in texto
    assert "Agende consultas e exames." in texto and sorted(trocas) == ["cirurgia robótica", "maternidade", "telemedicina"]


_PLANO_SEM_ROTINA = "# Plano de Mídia\nGoogle Ads: R$ 15.000 [VALIDAR]\n" + ("Campanhas de busca com palavras-chave do mapa de SEO e anúncios responsivos. " * 12)


def test_secoes_da_rotina_sao_inseridas_quando_o_plano_as_omite():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = "google ads"
    assert G._faltas_rotina_midia(_PLANO_SEM_ROTINA)
    texto, trocas = G._sanear_midia(_PLANO_SEM_ROTINA)
    assert "## Insumos e pendências" in texto and "## Rotina operacional (diária, semanal)" in texto and "## Alçadas e autorizações" in texto
    assert "budget pace" in texto.lower() and "90%" in texto and "UTM" in texto
    assert G._faltas_rotina_midia(texto) == [] and "seções da rotina de mídia" in trocas
    assert G._secoes_rotina_midia(texto) == ""                                       # idempotente: plano completo não recebe nada


_RUB_LINHAS_OK = "\n".join([
    "- **G3 Fato falso ou sem fonte:** OK",
    "- **Compliance e precisão (14/20):** Há afirmações marcadas [VALIDAR], tratadas como pendência humana.",
])


def test_rubrica_nao_pune_validar():
    assert G._validar_punido_pela_rubrica(_RUB_LINHAS_OK) is None
    assert G._validar_punido_pela_rubrica('- **G3 Fato falso ou Sem Fonte:** FALHA ("A [VALIDAR: serviço fora do briefing]" sem fontes)')
    assert G._validar_punido_pela_rubrica('1. **G3 FALHA:** "Novidades tecnológicas em diagnósticos. [VALIDAR MÉDICO]" - Assegure a revisão')
    assert G._validar_punido_pela_rubrica("- **Compliance e precisão (0/20):** Dados marcados [VALIDAR] sem fontes afetam a precisão.")
    assert G._validar_punido_pela_rubrica('- **G1 Compliance CFM/CDC:** FALHA ("Experiência segura e diferenciada" é promessa sem fonte)') is None   # falha real, sem marcador
    assert G._validar_punido_pela_rubrica("RESUMO | CONTEÚDO | G1=OK G2=OK G3=FALHA G4=NA G5=OK | NOTA=59/100 | VEREDITO=REFAZER | REVISÃO 1 DE 2") is None


_BRIEF_FONTES = """```markdown
# Brief Estratégico
## 5. Mix de Canais
- **Mídia Paga** (R$ 15.000 [VALIDAR])
## 6. Orçamento
- **Mídia**: R$ 15.000 [VALIDAR]
  - **Google Ads**: R$ 11.654 [confirmado]
## 9. Fontes
- **Baseline**: Nekt Refined, CRM RD Station.
- **Tendências**: Anahp e Estadão (seções de saúde).
- Guia de Identidade Visual do Hospital Santa Júlia
---
**Nota**: Todos os elementos foram desenvolvidos em conformidade com o guia de identidade visual do Hospital Santa Júlia, respeitando a linguagem de confiança e cuidado humano.
```"""
_PERMITIDO_FONTES = "hospital santa júlia nekt refined rfn_midia crm rd station ga4 gtm guia de identidade visual r$ 15.000 r$ 11.654 25.000"


def test_brief_fonte_inventada_marcador_falso_e_nota_de_conformidade():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = _PERMITIDO_FONTES
    assert G._fontes_nao_informadas(_BRIEF_FONTES) == ["Anahp", "Estadão"]
    assert G._fontes_nao_informadas(_BRIEF_FONTES.replace("Anahp e Estadão (seções de saúde)", "[VALIDAR: fonte]")) == []
    assert G._MARCADOR_FALSO.search("R$ 11.654 [confirmado]") and not G._MARCADOR_FALSO.search("R$ 11.654 [VALIDAR]")
    assert G._placeholders("Todos os elementos foram desenvolvidos em conformidade com o guia, respeitando a linguagem de confiança")
    texto, trocas = G._sanear_brief(_BRIEF_FONTES)
    assert "Anahp" not in texto and "[confirmado]" not in texto and "Todos os elementos" not in texto
    assert "Nekt Refined" in texto and "- **Tendências**: [VALIDAR: fonte]" in texto and "R$ 11.654 [VALIDAR]" in texto
    assert {"fonte inventada", "marcador falso [confirmado]", "nota de conformidade"} <= set(trocas)
    assert G._fontes_nao_informadas(texto) == []                                      # o texto saneado passa na própria trava


def test_brief_trava_rejeita_fonte_inventada_e_marcador_falso():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = _PERMITIDO_FONTES
    corpo = _BRIEF_FONTES.replace("Todos os elementos foram desenvolvidos", "Texto neutro").replace("respeitando a linguagem de", "com a linguagem de")
    corpo = "# Brief\n" + "Contexto do hospital com bastante texto útil para atingir o tamanho mínimo do documento exigido. " * 10 + "\n" + corpo
    r = G._guardrail_brief(_saida(corpo))
    assert r[0] is False and ("confirmado" in r[1] or "Anahp" in r[1])
    r2 = G._guardrail_brief(_saida(corpo.replace("[confirmado]", "[VALIDAR]")))
    assert r2[0] is False and "Anahp" in r2[1]


def test_calendario_com_data_em_formato_estranho():
    from datetime import date
    G._INPUTS_ATUAIS.clear(); G._INPUTS_ATUAIS["duracao_semanas"] = "2"
    G._ns["_hoje"] = lambda: date(2026, 10, 5)
    try:
        estranho = _calendario([f"| {i // 3 + 1} | 01-Nov-23 | Instagram | Post | a | b | c |" for i in range(6)])
        assert [d.year for d in G._extrair_datas(estranho)] == [2023] * 6
        assert "já passaram" in G._problemas_calendario(estranho)
        ilegivel = _calendario([f"| {i // 3 + 1} | em breve | Instagram | Post | a | b | c |" for i in range(6)])
        assert "datas legíveis" in G._problemas_calendario(ilegivel)
    finally:
        G._ns["_hoje"] = lambda: date(2026, 9, 1)


def test_claim_seguranca_em_cada_diagnostico_e_garantir_em_checklist():
    assert G._claims_proibidos("Segurança em cada diagnóstico.")
    assert not G._claims_proibidos("- [ ] Garantir conformidade com LGPD no opt-in")
    assert G._claims_proibidos("Garantimos conformidade com LGPD em todas as peças")


def test_aplicacao_g1_sem_feedback_mantem_o_brief_original():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = ""
    original = "# Brief Estratégico\n" + "\n".join(f"Linha {i} do brief original com conteúdo suficiente para contar como significativa." for i in range(30)) + "\n"
    portao = "## Histórico de feedbacks humanos\nNenhum feedback humano recebido.\n\"Aprovado.\""
    brief, port = _tarefa(original), _tarefa(portao)
    reescrito = _saida("# Registro\n**Ajustes aplicados:** removidas garantias.\n# Brief reescrito\n" + "Texto totalmente novo sem relação com o original, escrito pelo modelo. " * 15)
    g = G._com_limite_de_rejeicoes(G._guardrail_aplicacao_g1_factory(brief, port), saneador=G._saneador_aplicacao_g1_factory(brief, port))
    assert g(reescrito)[0] is False and g(reescrito)[0] is False
    ok, texto = g(reescrito)
    assert ok is True and "Ajustes aplicados:** nenhum" in texto and "Linha 7 do brief original" in texto and "removidas garantias" not in texto


def test_calendario_sem_coluna_data_e_com_historias_de_pacientes():
    from datetime import date
    G._INPUTS_ATUAIS.clear(); G._INPUTS_ATUAIS["duracao_semanas"] = "2"
    sem_data = "| Semana | Plataforma | Formato | Hook |\n|---|---|---|---|\n" + "\n".join(f"| {i // 3 + 1} | Instagram | Post | texto |" for i in range(6))
    assert G._tabela_sem_coluna_data(sem_data) and "coluna Data" in G._problemas_calendario(sem_data)
    com_data = _calendario([f"| {i // 3 + 1} | {(date(2026, 11, 1)).strftime('%d/%m/%Y')} | Instagram | Post | a | b | c |" for i in range(6)])
    assert not G._tabela_sem_coluna_data(com_data)
    historia = _calendario(["| 2 | 10/11/2026 | Facebook | Story | Humanização | \"Histórias de pacientes no hospital.\" | \"Explore\" [VALIDAR MÉDICO] |"])
    assert G._historias_de_pacientes(historia) == ["histórias de pacientes"]                     # [VALIDAR] em outra célula não legitima
    assert G._historias_de_pacientes("Sem depoimentos de pacientes nas peças.") == []
    assert "histórias de pacientes" in G._problemas_calendario(com_data + "\n" + historia.splitlines()[-1])


_REEMISSAO = ("### Parte A\n" + ("registro com a decisão e os ajustes de cada entrega. " * 15) + "\n### Parte B\n#### Peça reemitida: Plano de Mídia Paga\n"
              "# Plano de Mídia\nGoogle Ads: R$ 11.654 [confirmado]\nVerba R$ 15.000 [VALIDAR]\n### Parte C: Lista de Versões\n- Plano: reemitido\n")


def test_reemissao_com_marcador_falso_e_plano_sem_rotina():
    G._INPUTS_ATUAIS.clear(); G._TEXTO_PERMITIDO["texto"] = "google ads"
    r = G._guardrail_aplicacao_g2(_saida(_REEMISSAO))
    assert r[0] is False and "confirmado" in r[1]
    sem_falso = _REEMISSAO.replace("[confirmado]", "[VALIDAR]")
    r2 = G._guardrail_aplicacao_g2(_saida(sem_falso))
    assert r2[0] is False and "rotina" in r2[1]
    # saneador: troca o marcador e insere as seções da rotina no plano reemitido
    portao = _tarefa("## Histórico de feedbacks humanos\nNenhum feedback humano recebido.\n")
    novo, trocas = G._saneador_aplicacao_g2_factory(portao)(_REEMISSAO)
    assert "[confirmado]" not in novo and "## Alçadas e autorizações" in novo and "marcador falso [confirmado]" in trocas
    assert G._faltas_rotina_midia(G._trecho_reemitido(novo, r"m[íi]dia") + novo) == []
    # a Parte A pode citar o problema sem disparar a trava
    parte_a = _REEMISSAO.replace("registro com a decisão", "registro: remover [confirmado] com a decisão", 1).replace("[confirmado]\nVerba", "[VALIDAR]\nVerba")
    assert "confirmado" not in G._a_partir_da_reemissao(parte_a)


def test_servicos_nao_informados_para_o_prompt():
    permitido = G._texto_permitido({"objetivo": "consultas e exames de cardiologia", "servicos_nao_informados": "telemedicina"})
    assert "telemedicina" not in permitido                                              # a lista não se autoriza
    lista = G._servicos_nao_informados(permitido)
    assert "telemedicina" in lista and "cirurgia robótica" in lista and "cardiologia" not in lista
    assert G._servicos_nao_informados(" ".join(s.lower() for s in G._SERVICOS_LISTA)) == "nenhum"
