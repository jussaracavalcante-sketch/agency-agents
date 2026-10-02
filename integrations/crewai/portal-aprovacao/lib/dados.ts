import { admin } from "./supabase";

export const fmt = (s: string) => new Date(s).toLocaleString("pt-BR", { timeZone: "America/Manaus" });
export const hora = (s: string) => new Date(s).toLocaleTimeString("pt-BR", { timeZone: "America/Manaus", hour: "2-digit", minute: "2-digit" });
export const iniciais = (nome: string) => nome.split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0]).join("").toUpperCase();

export function haQuanto(s: string) {
  const min = Math.max(0, Math.round((Date.now() - new Date(s).getTime()) / 60_000));
  if (min < 1) return "agora";
  if (min < 60) return `há ${min} min`;
  if (min < 1440) return `há ${Math.floor(min / 60)} h`;
  return `há ${Math.floor(min / 1440)} d`;
}

/** Disparos feitos pelo portal: kickoff_id → nome oficial do cliente. Execuções iniciadas fora do portal não têm cliente conhecido. */
export async function clientePorExecucao(): Promise<Map<string, string>> {
  const db = admin();
  const { data: d } = await db.from("portal_disparos").select("kickoff_id,briefing").not("kickoff_id", "is", null);
  const m = new Map<string, string>();
  for (const x of d || []) m.set(x.kickoff_id as string, String((x.briefing as { cliente?: string })?.cliente || ""));
  return m;
}

export type Tarefa = { id: number; task_name: string | null; kickoff_id: string; recebido_em: string; tipo: string };

/** Últimas entregas de tarefas (webhooks `task`), sem eventos de teste. */
export async function entregasRecentes(limite: number, desde?: string): Promise<Tarefa[]> {
  let q = admin().from("crewai_webhook_events").select("id,task_name,kickoff_id,recebido_em,tipo").eq("tipo", "task").not("kickoff_id", "like", "teste-%");
  if (desde) q = q.gt("recebido_em", desde);
  const { data } = await q.order("id", { ascending: false }).limit(limite);
  return (data || []) as Tarefa[];
}
