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

/**
 * Cada retomada ganha um kickoff_id novo e só o evento de pausa (human_input) traz o execution_id original. Para ligar as
 * tarefas que rodam depois de uma retomada, montamos um mapa kickoff → execução com (a) os eventos de pausa e (b) as
 * decisões gravadas pelo portal (novo_kickoff_id). Sem mapa, essas tarefas apareceriam como outra execução.
 */
type Mapa = Map<string, string>;

async function mapaDeRetomadas(eventos: Evento[]): Promise<Mapa> {
  const m: Mapa = new Map();
  for (const e of eventos) if (e.payload?.execution_id) m.set(e.kickoff_id, e.payload.execution_id);
  const { data } = await admin().from("portal_decisoes").select("execucao_id,novo_kickoff_id").not("novo_kickoff_id", "is", null);
  for (const d of data || []) m.set(d.novo_kickoff_id as string, d.execucao_id as string);
  return m;
}

const chaveDe = (e: Evento, m: Mapa) => m.get(e.kickoff_id) || e.payload?.execution_id || e.kickoff_id;

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
  const mapa = await mapaDeRetomadas((data || []) as Evento[]);
  for (const e of (data || []) as Evento[]) {
    const k = chaveDe(e, mapa);
    grupos.set(k, [...(grupos.get(k) || []), e]);
  }
  return [...grupos.entries()].map(([chave, evs]) => montar(chave, evs.sort((a, b) => a.id - b.id)))
    .sort((a, b) => (a.ultimo < b.ultimo ? 1 : -1));
}

export async function obterExecucao(chave: string): Promise<Execucao | null> {
  const db = admin();
  // todos os kickoffs da cadeia: o original, os das retomadas feitas pelo portal e os dos eventos de pausa
  const kickoffs = new Set<string>([chave]);
  const { data: decisoes } = await db.from("portal_decisoes").select("novo_kickoff_id").eq("execucao_id", chave).not("novo_kickoff_id", "is", null);
  for (const d of decisoes || []) kickoffs.add(d.novo_kickoff_id as string);
  const { data: pausas } = await db.from("crewai_webhook_events").select("kickoff_id").eq("tipo", "human_input").eq("payload->>execution_id", chave);
  for (const p of pausas || []) kickoffs.add(p.kickoff_id as string);
  const { data } = await db
    .from("crewai_webhook_events")
    .select("id,tipo,kickoff_id,task_name,output,recebido_em,payload")
    .in("kickoff_id", [...kickoffs])
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

/**
 * Trava de custo: existe execução consumindo modelo agora? Conta como ativa a execução sem evento de fim, sem portão
 * esperando humano e com evento nos últimos 15 minutos, ou um disparo do portal feito há menos de 10 minutos que ainda
 * não gerou nenhum evento (a plataforma demora a produzir o primeiro).
 */
export async function execucaoAtiva(): Promise<{ ativa: boolean; motivo?: string }> {
  const agora = Date.now();
  const execs = await listarExecucoes(200);
  const rodando = execs.find((e) => !e.concluida && !e.pendente && agora - new Date(e.ultimo).getTime() < 15 * 60_000);
  if (rodando) return { ativa: true, motivo: `a execução ${rodando.chave.slice(0, 8)} ainda está em andamento` };

  const { data: recentes } = await admin()
    .from("portal_disparos")
    .select("kickoff_id,criado_em")
    .eq("enviado_ao_crewai", true)
    .gt("criado_em", new Date(agora - 10 * 60_000).toISOString());
  for (const d of recentes || []) {
    if (!d.kickoff_id) continue;
    const { count } = await admin().from("crewai_webhook_events").select("id", { count: "exact", head: true }).eq("kickoff_id", d.kickoff_id);
    if (!count) return { ativa: true, motivo: "um disparo recente ainda não produziu o primeiro evento" };
  }
  return { ativa: false };
}
