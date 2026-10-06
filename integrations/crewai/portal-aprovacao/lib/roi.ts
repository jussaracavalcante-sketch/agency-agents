import { listarExecucoes, type Execucao } from "./execucoes";
import { clientePorExecucao } from "./dados";
import { lerConfig, num } from "./admin";
import { TAREFAS } from "./agentes";

type Uso = { total_tokens: number; prompt_tokens: number; completion_tokens: number; cached_prompt_tokens: number; successful_requests: number };
export type Campanha = {
  chave: string; cliente: string; inicio: string; ultimo: string; status: string; tarefas: number; decisoes: number;
  tokens: Uso; estimado: boolean; custo_usd: number; custo_brl: number;
};
export type Precos = { entrada: number; saida: number; cache: number; cambio: number; valorRef: number; horas: number; custoHora: number };

const zero = (): Uso => ({ total_tokens: 0, prompt_tokens: 0, completion_tokens: 0, cached_prompt_tokens: 0, successful_requests: 0 });

function usoReal(e: Execucao): Uso | null {
  let u: Uso | null = null;
  for (const ev of e.eventos) {
    const tu = (ev.payload as { token_usage?: Partial<Uso> } | null)?.token_usage;
    if (ev.tipo !== "crew" || !tu) continue;
    u = u ?? zero();
    for (const k of Object.keys(u) as (keyof Uso)[]) u[k] += Number(tu[k] ?? 0);
  }
  return u;
}

export function custo(u: Uso, p: Precos) {
  const naoCache = Math.max(0, u.prompt_tokens - u.cached_prompt_tokens);
  const usd = (naoCache * p.entrada + u.cached_prompt_tokens * p.cache + u.completion_tokens * p.saida) / 1_000_000;
  return { usd, brl: usd * p.cambio };
}

export async function precos(): Promise<Precos> {
  const { valores: v } = await lerConfig();
  return { entrada: num(v.preco_entrada_usd_por_milhao, 3), saida: num(v.preco_saida_usd_por_milhao, 15), cache: num(v.preco_cache_usd_por_milhao, 0.3), cambio: num(v.cambio_usd_brl, 5.4),
    valorRef: num(v.valor_campanha_referencia_brl, 0), horas: num(v.horas_humanas_por_campanha, 0), custoHora: num(v.custo_hora_humana_brl, 0) };
}

/**
 * Custo por campanha. Token real vem do evento `crew` (fim da execução). Cadeia sem esse evento (pausada, reprovada ou em andamento)
 * recebe estimativa: tokens por tarefa observados nas cadeias completas × tarefas entregues. Ambas ficam marcadas.
 */
export async function analiseROI(p?: Precos) {
  const pr = p ?? (await precos());
  const [execs, clientes] = await Promise.all([listarExecucoes(1500), clientePorExecucao()]);
  const reais = execs.map((e) => ({ e, u: usoReal(e) })).filter((x) => x.u && x.u.total_tokens > 0);
  const tarefasReais = reais.reduce((s, x) => s + x.e.eventos.filter((ev) => ev.tipo === "task").length, 0);
  const porTarefa = tarefasReais ? reais.reduce((s, x) => s + x.u!.total_tokens, 0) / tarefasReais : 16_000;
  const proporcao = tarefasReais ? {
    prompt: reais.reduce((s, x) => s + x.u!.prompt_tokens, 0) / Math.max(1, reais.reduce((s, x) => s + x.u!.total_tokens, 0)),
    cache: reais.reduce((s, x) => s + x.u!.cached_prompt_tokens, 0) / Math.max(1, reais.reduce((s, x) => s + x.u!.total_tokens, 0)),
  } : { prompt: 0.9, cache: 0.25 };

  const campanhas: Campanha[] = execs.map((e) => {
    const tarefas = e.eventos.filter((ev) => ev.tipo === "task").length;
    const decisoes = e.eventos.filter((ev) => ev.tipo === "human_input").length;
    let u = usoReal(e); let estimado = false;
    if (!u || !u.total_tokens) {
      estimado = true;
      const total = Math.round(tarefas * porTarefa);
      const prompt = Math.round(total * proporcao.prompt);
      u = { total_tokens: total, prompt_tokens: prompt, completion_tokens: total - prompt, cached_prompt_tokens: Math.round(total * proporcao.cache), successful_requests: 0 };
    }
    const c = custo(u, pr);
    const status = e.pendente ? `Portão ${e.portao ?? ""} pendente` : e.encerrada ? "Reprovada" : e.concluida ? "Concluída" : "Em andamento";
    return { chave: e.chave, cliente: clientes.get(e.chave) || `Execução ${e.chave.slice(0, 8)}`, inicio: e.inicio, ultimo: e.ultimo, status, tarefas, decisoes, tokens: u, estimado, custo_usd: c.usd, custo_brl: c.brl };
  });

  // custo por agente: tokens da cadeia rateados pelo tamanho da saída de cada tarefa
  const porAgente = new Map<string, { tarefas: number; tokens: number; brl: number }>();
  for (const e of execs) {
    const camp = campanhas.find((c) => c.chave === e.chave)!;
    const tasks = e.eventos.filter((ev) => ev.tipo === "task");
    const total = tasks.reduce((s, ev) => s + (ev.output?.length ?? 0), 0) || 1;
    for (const ev of tasks) {
      const ag = TAREFAS[ev.task_name || ""]?.papel ?? "agente";
      const parte = (ev.output?.length ?? 0) / total;
      const a = porAgente.get(ag) ?? { tarefas: 0, tokens: 0, brl: 0 };
      porAgente.set(ag, { tarefas: a.tarefas + 1, tokens: a.tokens + camp.tokens.total_tokens * parte, brl: a.brl + camp.custo_brl * parte });
    }
  }

  const totais = campanhas.reduce((t, c) => ({ tokens: t.tokens + c.tokens.total_tokens, brl: t.brl + c.custo_brl, usd: t.usd + c.custo_usd, tarefas: t.tarefas + c.tarefas, decisoes: t.decisoes + c.decisoes }), { tokens: 0, brl: 0, usd: 0, tarefas: 0, decisoes: 0 });
  const concluidas = campanhas.filter((c) => c.status === "Concluída");
  const mediaConcluida = concluidas.length ? concluidas.reduce((s, c) => s + c.custo_brl, 0) / concluidas.length : 0;
  const custoPorToken = totais.tokens ? totais.brl / totais.tokens : 0;
  const roi = pr.valorRef && mediaConcluida ? (pr.valorRef - mediaConcluida) / mediaConcluida : null;
  const economiaHoras = pr.horas && pr.custoHora ? pr.horas * pr.custoHora : 0;
  return { campanhas, totais, porAgente: [...porAgente.entries()].map(([agente, v]) => ({ agente, ...v })).sort((a, b) => b.brl - a.brl), porTarefa, precos: pr, concluidas: concluidas.length, mediaConcluida, custoPorToken, roi, economiaHoras, reais: reais.length };
}
