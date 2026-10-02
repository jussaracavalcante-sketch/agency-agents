import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { admin, usuarioAtual } from "@/lib/supabase";
import { AGENTES, rotuloTarefa } from "@/lib/agentes";
import { fmt } from "@/lib/dados";

export const dynamic = "force-dynamic";
const ABAS: [string, string][] = [["config", "Configuração"], ["conhecimento", "Conhecimento"], ["acoes", "Ações"], ["historico", "Histórico"]];

export default async function Agente({ params, searchParams }: { params: { chave: string }; searchParams: { aba?: string } }) {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  const a = AGENTES.find((x) => x.chave === params.chave);
  if (!a) notFound();
  const aba = ABAS.some(([k]) => k === searchParams.aba) ? searchParams.aba! : "config";
  const nomes = a.tarefas.map((t) => t.nome);
  const { data: hist } = aba === "historico"
    ? await admin().from("crewai_webhook_events").select("id,task_name,recebido_em,output").eq("tipo", "task").in("task_name", nomes).not("kickoff_id", "like", "teste-%").order("id", { ascending: false }).limit(20)
    : { data: [] };
  const { count: guias } = aba === "conhecimento" ? await admin().from("portal_clientes").select("slug", { count: "exact", head: true }) : { count: 0 };

  return (
    <>
      <div className="head">
        <div>
          <div className="mut"><Link href="/agentes">Agentes</Link> › {a.papel}</div>
          <h1>{a.papel} <span className="st ok" style={{ verticalAlign: "middle" }}>Ativo</span></h1>
          <p className="sub" style={{ margin: 0 }}>Configuração versionada no repositório (somente leitura no portal).</p>
        </div>
      </div>
      <div className="tabs">{ABAS.map(([k, r]) => <Link key={k} href={`/agentes/${a.chave}?aba=${k}`} className={aba === k ? "on" : ""}>{r}</Link>)}</div>

      {aba === "config" && (
        <div className="card">
          <h2>Como o agente trabalha</h2>
          <div className="kv"><span>Objetivo</span><span>{a.objetivo}</span></div>
          <div className="kv"><span>Delegação</span><span>{a.delega ? "Pode delegar tarefas a outros agentes" : "Executa as próprias tarefas"}</span></div>
          <div className="kv"><span>Tarefas</span><span>{a.tarefas.map((t) => <span key={t.nome} className="tag">{t.ordem}. {rotuloTarefa(t.nome)}</span>)}</span></div>
        </div>
      )}
      {aba === "conhecimento" && (
        <div className="card">
          <h2>Base de conhecimento</h2>
          <p>Antes de cada campanha, o fluxo carrega automaticamente o guia de marca do cliente selecionado. Há {guias} guias cadastrados.</p>
          <p className="mut">O agente só usa informações do briefing e do guia do cliente. O que faltar sai como [VALIDAR]. <Link href="/conhecimento">Ver guias por cliente</Link></p>
        </div>
      )}
      {aba === "acoes" && (
        <div className="card">
          <h2>Ferramentas permitidas</h2>
          {a.ferramentas.length ? a.ferramentas.map((f) => <span key={f} className="tag">{f}</span>) : <p className="mut">Nenhuma ferramenta: este agente coordena e consolida.</p>}
        </div>
      )}
      {aba === "historico" && (
        <div className="card">
          <h2>Últimas entregas</h2>
          {!hist?.length && <p className="vazio">Sem entregas registradas.</p>}
          {hist?.map((e) => (
            <details key={e.id}><summary>{rotuloTarefa(e.task_name || "")} <span className="mut" style={{ fontWeight: 400 }}>· {fmt(e.recebido_em)}</span></summary><pre className="doc">{e.output}</pre></details>
          ))}
        </div>
      )}
    </>
  );
}
