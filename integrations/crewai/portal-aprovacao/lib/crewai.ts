/** URLs dos webhooks do receptor. A chave fica só no servidor. */
function webhooks() {
  const base = process.env.WEBHOOK_BASE!;
  const key = process.env.WEBHOOK_KEY!;
  const auto = process.env.WEBHOOK_AUTOMACAO || "agency-agents";
  const url = (tipo: string) => `${base}?tipo=${tipo}&automacao=${auto}&k=${key}`;
  return {
    taskWebhookUrl: url("task"),
    crewWebhookUrl: url("crew"),
    humanInputWebhook: {
      url: `${base}?tipo=human_input&automacao=${auto}`,
      authentication: { strategy: "bearer", token: key },
    },
  };
}

async function chamar(caminho: string, corpo: unknown) {
  const r = await fetch(`${process.env.CREWAI_API_URL}${caminho}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.CREWAI_TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
    cache: "no-store",
  });
  const texto = await r.text();
  let kickoff: string | null = null;
  try { kickoff = JSON.parse(texto).kickoff_id ?? null; } catch { /* resposta não JSON */ }
  return { ok: r.ok && !!kickoff, kickoff, texto: texto.slice(0, 500) };
}

/**
 * Quem executa as campanhas: "runner" (serviço próprio no Render, sem limite de execuções da plataforma) ou "amp" (CrewAI AMP).
 * Chave de comutação: variável EXECUTOR no portal. Padrão: amp, para não mudar nada sem decisão explícita.
 */
const usaRunner = () => (process.env.EXECUTOR || "amp").toLowerCase() === "runner";

async function chamarRunner(caminho: string, corpo: unknown) {
  try {
    const r = await fetch(`${process.env.RUNNER_URL}${caminho}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${process.env.RUNNER_TOKEN}`, "Content-Type": "application/json" },
      body: JSON.stringify(corpo),
      cache: "no-store",
      signal: AbortSignal.timeout(20_000),
    });
    const texto = await r.text();
    let kickoff: string | null = null;
    try { kickoff = JSON.parse(texto).kickoff_id ?? null; } catch { /* resposta não JSON */ }
    return { ok: r.ok, kickoff, texto: texto.slice(0, 500) };
  } catch (e) {
    return { ok: false, kickoff: null, texto: `runner inacessível: ${(e as Error).name}` };
  }
}

/** Retoma uma execução pausada em um portão. */
export async function retomar(opts: { executionId: string; taskId: string; humanFeedback: string }) {
  if (usaRunner()) {
    const r = await chamarRunner("/resume", { executionId: opts.executionId, taskId: opts.taskId, humanFeedback: opts.humanFeedback });
    return { ...r, kickoff: r.ok ? opts.executionId : null };   // no runner a execução é a mesma: o id não muda a cada retomada
  }
  return chamar("/resume", { executionId: opts.executionId, taskId: opts.taskId, humanFeedback: opts.humanFeedback, ...webhooks() });
}

/** Dispara uma campanha nova com o briefing informado. */
export function iniciar(inputs: Record<string, string>) {
  return usaRunner() ? chamarRunner("/kickoff", { inputs }) : chamar("/kickoff", { inputs, ...webhooks() });
}

/** Reprovação: no runner a execução que espera no portão é encerrada; na AMP não existe cancelamento (o portal só fecha a execução). */
export async function encerrar(executionId: string) {
  if (!usaRunner()) return;
  await chamarRunner("/cancel", { executionId });
}

/** Texto enviado à plataforma. "Aprovado." libera; qualquer outro texto reexecuta o portão (contrato validado). */
export function textoDeDecisao(d: { decisao: "aprovar" | "devolver"; portao: string | null; nome: string; instrucoes: string }) {
  if (d.decisao === "aprovar") return "Aprovado.";
  const hoje = new Date().toISOString().slice(0, 10);
  return `DECISÃO ${d.portao ?? "do portão"}: DEVOLVIDO COM FEEDBACK por ${d.nome} em ${hoje}. Ajustes pedidos: ${d.instrucoes.trim()}`;
}

/** Classifica a recusa da plataforma para o portal dizer ao usuário o que aconteceu (sem expor o texto técnico). */
export function motivoDaRecusa(texto: string | null | undefined): { tipo: "limite" | "outro"; mensagem: string } {
  if (/runner inacessível|execução não está mais ativa/i.test(texto || "")) {
    return { tipo: "outro", mensagem: "O executor das campanhas não respondeu ou perdeu esta execução (reinício do serviço). Avise o administrador com o número da execução." };
  }
  if (/monthly execution limit|execution limit reached|quota|limit reached/i.test(texto || "")) {
    return { tipo: "limite", mensagem: "A plataforma de agentes atingiu o limite mensal de execuções do plano. Nada foi enviado nem retomado. Avise o administrador: o limite precisa ser ampliado ou renovado antes de tentar de novo." };
  }
  return { tipo: "outro", mensagem: "A plataforma recusou o envio. O detalhe técnico ficou registrado; avise o administrador." };
}
