import { dadosPessoais, mensagemDadosPessoais } from "./dadosPessoais";
import { MAX_CAMPO, MAX_CAMPO_LONGO } from "./tamanhos";

/** Os 17 campos do briefing (chaves = variáveis {…} de config/tasks.yaml e inputs da automação). */
export type Campo = { chave: string; rotulo: string; dica: string; longo?: boolean; padrao?: string };

export const CAMPOS: Campo[] = [
  { chave: "briefing_titulo", rotulo: "Título da campanha", dica: "Ex.: Campanha de captação de pacientes Q4 2026" },
  { chave: "segmento", rotulo: "Segmento", dica: "Ex.: Saúde: hospital privado de alta complexidade (setor regulado)", longo: true },
  { chave: "regiao", rotulo: "Região", dica: "Ex.: Manaus e Região Metropolitana" },
  { chave: "publico_alvo", rotulo: "Público-alvo", dica: "Ex.: Adultos 30-60 anos, classes A/B, decisores de saúde da família", longo: true },
  { chave: "objetivo", rotulo: "Objetivo", dica: "Literal e com baseline. O Guardião reprova objetivo trocado. Ex.: Gerar 400 contatos qualificados (agendamentos e orçamentos) em 8 semanas (baseline: 863 conversões em 90 dias).", longo: true },
  { chave: "orcamento_total", rotulo: "Orçamento total", dica: "Ex.: R$ 25.000" },
  { chave: "orcamento_midia", rotulo: "Orçamento de mídia", dica: "Parte do total destinada a mídia paga. Ex.: R$ 15.000" },
  { chave: "prazo", rotulo: "Prazo", dica: "Ex.: 8 semanas", padrao: "8 semanas" },
  { chave: "duracao_semanas", rotulo: "Duração (semanas)", dica: "Número. O calendário cobre todas as semanas.", padrao: "8" },
  { chave: "plataformas_sociais", rotulo: "Plataformas sociais", dica: "Ex.: Instagram, Facebook, LinkedIn" },
  { chave: "ferramenta_crm", rotulo: "CRM", dica: "Ex.: RD Station", padrao: "RD Station" },
  { chave: "ferramenta_analytics", rotulo: "Analytics e fontes de dados", dica: "O que existe de fato. Ex.: Nekt Refined (rfn_midia__desempenho_diario + rfn_marketing__conversao)", longo: true },
  { chave: "site_url", rotulo: "Site", dica: "URL, ou escreva: nenhum informado", },
  { chave: "fuso_horario", rotulo: "Fuso horário", dica: "Ex.: America/Manaus", padrao: "America/Manaus" },
  { chave: "caminho_dados", rotulo: "Caminho dos dados", dica: "Onde estão os dados de desempenho (tabela ou arquivo)", longo: true },
  { chave: "periodo_relatorio", rotulo: "Período do relatório", dica: "Ex.: últimos 90 dias (até 2026-09-30)" },
];
// o 17º campo, "cliente", vem da lista de clientes (guia de marca) e não é digitado

export const CHAVES = ["cliente", ...CAMPOS.map((c) => c.chave)];

export function validar(b: Record<string, unknown>): string | null {
  for (const k of CHAVES) {
    const v = typeof b[k] === "string" ? (b[k] as string).trim() : "";
    if (!v) return `Preencha o campo: ${k}`;
  }
  for (const c of CAMPOS) {
    const teto = c.longo ? MAX_CAMPO_LONGO : MAX_CAMPO;
    if (String(b[c.chave]).trim().length > teto) return `O campo "${c.rotulo}" passa de ${teto} caracteres`;
  }
  const achados = dadosPessoais(CHAVES.map((k) => String(b[k] ?? "")).join("\n"));
  if (achados.length) return mensagemDadosPessoais(achados);
  if (!/^\d{1,2}$/.test(String(b.duracao_semanas).trim())) return "Duração (semanas) deve ser um número de 1 a 99";
  if ((b.objetivo as string).trim().length < 30) return "Objetivo muito curto: escreva o objetivo literal, com meta e baseline";
  return null;
}

/** Briefing validado no piloto do Hospital Santa Júlia. Itens sem dado confirmado seguem como [VALIDAR]. */
export const PILOTO_SANTA_JULIA = {
  slug: "hospital_santa_julia",
  valores: {
    briefing_titulo: "Campanha de captação de pacientes Hospital Santa Júlia Q4 2026",
    segmento: "Saúde: hospital privado de alta complexidade (setor regulado: CFM, ANVISA, CONAR)",
    regiao: "Manaus e Região Metropolitana",
    publico_alvo: "Adultos 30-60 anos, classes A/B, decisores de saúde da família, beneficiários de planos de saúde e pacientes particulares que buscam especialistas e exames",
    objetivo: "Gerar 400 contatos qualificados (agendamentos e orçamentos) em 8 semanas (baseline: 863 conversões RD em 90 dias, 343 vindas de mídia paga)",
    orcamento_total: "R$ 25.000 [VALIDAR]",
    orcamento_midia: "R$ 15.000 [VALIDAR] (run-rate Google Ads: R$ 11.654 em 90 dias; sem Meta Ads na Nekt)",
    prazo: "8 semanas",
    duracao_semanas: "8",
    plataformas_sociais: "Instagram, Facebook, LinkedIn",
    ferramenta_crm: "RD Station",
    ferramenta_analytics: "Nekt Refined (rfn_midia__desempenho_diario + rfn_marketing__conversao); GA4 + GTM fora da Nekt",
    site_url: "nenhum informado (confirmar o site institucional com o atendimento) [VALIDAR]",
    fuso_horario: "America/Manaus",
    caminho_dados: "vanguardamartech_refined.rfn_midia__desempenho_diario filtrado por cliente = 'HOSPITAL SANTA JULIA' + rfn_marketing__conversao filtrado por cliente = 'HOSPITAL SANTA JULIA'",
    periodo_relatorio: "últimos 90 dias (até 2026-09-30)",
  } as Record<string, string>,
};
