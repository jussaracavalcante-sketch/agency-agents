import dados from "./agentes.json";

export type Agente = { chave: string; papel: string; objetivo: string; delega: boolean; ferramentas: string[]; tarefas: { nome: string; ordem: number }[] };
export const AGENTES = dados.agentes as Agente[];
export const TAREFAS = dados.tarefas as Record<string, { agente: string; papel: string; ordem: number }>;
export const TOTAL_TAREFAS = Object.keys(TAREFAS).length;

/** Nome legível da tarefa: pesquisa_mercado → Pesquisa mercado. */
export const rotuloTarefa = (nome: string) => nome.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());
