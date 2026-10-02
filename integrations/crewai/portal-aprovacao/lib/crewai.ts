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

/** Retoma uma execução pausada em um portão. */
export function retomar(opts: { executionId: string; taskId: string; humanFeedback: string }) {
  return chamar("/resume", { executionId: opts.executionId, taskId: opts.taskId, humanFeedback: opts.humanFeedback, ...webhooks() });
}

/** Dispara uma campanha nova com o briefing informado. */
export function iniciar(inputs: Record<string, string>) {
  return chamar("/kickoff", { inputs, ...webhooks() });
}

/** Texto enviado à plataforma. "Aprovado." libera; qualquer outro texto reexecuta o portão (contrato validado). */
export function textoDeDecisao(d: { decisao: "aprovar" | "devolver"; portao: string | null; nome: string; instrucoes: string }) {
  if (d.decisao === "aprovar") return "Aprovado.";
  const hoje = new Date().toISOString().slice(0, 10);
  return `DECISÃO ${d.portao ?? "do portão"}: DEVOLVIDO COM FEEDBACK por ${d.nome} em ${hoje}. Ajustes pedidos: ${d.instrucoes.trim()}`;
}
