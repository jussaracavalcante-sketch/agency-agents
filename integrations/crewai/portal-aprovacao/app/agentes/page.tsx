import { redirect } from "next/navigation";
import { admin, usuarioAtual } from "@/lib/supabase";
import { AGENTES, TAREFAS, TOTAL_TAREFAS, rotuloTarefa } from "@/lib/agentes";

export const dynamic = "force-dynamic";

export default async function Agentes() {
  const u = await usuarioAtual();
  if (!u) redirect("/login");

  // atividade: quantas entregas cada agente já produziu e quando foi a última
  const { data } = await admin().from("crewai_webhook_events").select("task_name,recebido_em").eq("tipo", "task").not("kickoff_id", "like", "teste-%").order("id", { ascending: false }).limit(2000);
  const atividade = new Map<string, { n: number; ultimo: string }>();
  for (const e of data || []) {
    const ag = TAREFAS[e.task_name || ""]?.agente;
    if (!ag) continue;
    const a = atividade.get(ag);
    atividade.set(ag, { n: (a?.n ?? 0) + 1, ultimo: a?.ultimo ?? e.recebido_em });
  }
  const fmt = (s: string) => new Date(s).toLocaleString("pt-BR", { timeZone: "America/Manaus" });

  return (
    <>
      <h2>Equipe de agentes ({AGENTES.length})</h2>
      <p className="mut">Fluxo de {TOTAL_TAREFAS} tarefas em três fases, com aprovação humana nos portões G1, G2 e G3. Os dados vêm dos arquivos de configuração da crew.</p>
      {AGENTES.map((a) => {
        const at = atividade.get(a.chave);
        return (
          <div key={a.chave} className="card">
            <div className="row">
              <strong>{a.papel}</strong>
              <span className="mut">{at ? `${at.n} entregas · última em ${fmt(at.ultimo)}` : "sem entregas registradas"}</span>
            </div>
            <p className="mut">{a.objetivo}</p>
            <p style={{ margin: "6px 0" }}>
              <span className="mut">Ferramentas: </span>
              {a.ferramentas.length ? a.ferramentas.map((f) => <span key={f} className="tag" style={{ marginRight: 4 }}>{f}</span>) : <span className="mut">nenhuma (coordena e consolida){a.delega ? "; pode delegar" : ""}</span>}
            </p>
            <p style={{ margin: "6px 0" }}>
              <span className="mut">Tarefas: </span>
              {a.tarefas.map((t) => <span key={t.nome} className="tag" style={{ marginRight: 4 }}>{t.ordem}. {rotuloTarefa(t.nome)}</span>)}
            </p>
          </div>
        );
      })}
    </>
  );
}
