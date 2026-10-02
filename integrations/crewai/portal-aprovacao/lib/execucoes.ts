import { admin } from "./supabase";

export type Evento = {
  id: number; tipo: string; kickoff_id: string; task_name: string | null; output: string | null; recebido_em: string;
  payload: { execution_id?: string; task_id?: string } | null;
};

export type Execucao = {
  chave: string;            // execution_id original da cadeia
  inicio: string; ultimo: string;
  eventos: Evento[];
  pendente: Evento | null;  // human_input aguardando decisão
  concluida: boolean;
  portao: "G1" | "G2" | "G3" | null;
};

/** Todos os resumes de uma execução compartilham payload.execution_id (o id original). */
function chaveDe(e: Evento) { return e.payload?.execution_id || e.kickoff_id; }

function portaoDe(eventos: Evento[], pendente: Evento | null): Execucao["portao"] {
  if (!pendente) return null;
  const anteriores = eventos.filter((e) => e.id < pendente.id && e.tipo === "task" && /^revisao_g[123]$/.test(e.task_name || ""));
  const ultima = anteriores[anteriores.length - 1]?.task_name;
  return ultima ? (("G" + ultima.slice(-1)) as "G1" | "G2" | "G3") : null;
}

export async function listarExecucoes(limite = 400): Promise<Execucao[]> {
  const { data } = await admin()
    .from("crewai_webhook_events")
    .select("id,tipo,kickoff_id,task_name,output,recebido_em,payload")
    .not("kickoff_id", "like", "teste-%")
    .order("id", { ascending: false })
    .limit(limite);
  const grupos = new Map<string, Evento[]>();
  for (const e of (data || []) as Evento[]) {
    const k = chaveDe(e);
    grupos.set(k, [...(grupos.get(k) || []), e]);
  }
  return [...grupos.entries()].map(([chave, evs]) => montar(chave, evs.sort((a, b) => a.id - b.id)))
    .sort((a, b) => (a.ultimo < b.ultimo ? 1 : -1));
}

export async function obterExecucao(chave: string): Promise<Execucao | null> {
  const { data } = await admin()
    .from("crewai_webhook_events")
    .select("id,tipo,kickoff_id,task_name,output,recebido_em,payload")
    .or(`kickoff_id.eq.${chave},payload->>execution_id.eq.${chave}`)
    .order("id", { ascending: true });
  if (!data?.length) return null;
  return montar(chave, data as Evento[]);
}

function montar(chave: string, eventos: Evento[]): Execucao {
  const ultimoEvento = eventos[eventos.length - 1];
  const pendente = ultimoEvento.tipo === "human_input" ? ultimoEvento : null;
  return {
    chave,
    inicio: eventos[0].recebido_em,
    ultimo: ultimoEvento.recebido_em,
    eventos,
    pendente,
    concluida: eventos.some((e) => e.tipo === "crew"),
    portao: portaoDe(eventos, pendente),
  };
}
