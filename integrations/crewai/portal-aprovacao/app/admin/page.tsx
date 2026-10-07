import { notFound, redirect } from "next/navigation";
import { admin, ehAdmin, usuarioAtual } from "@/lib/supabase";
import { ajustesDosAgentes, estadoDaPlataforma, lerConfig } from "@/lib/admin";
import { AGENTES } from "@/lib/agentes";
import { listarExecucoes } from "@/lib/execucoes";
import { clientePorExecucao } from "@/lib/dados";
import Admin from "./Admin";

export const dynamic = "force-dynamic";

export default async function Administracao() {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  // Quem não é administrador não vê nem que a área existe: a rota responde 404, igual a um endereço inexistente.
  if (!ehAdmin(u)) notFound();
  const db = admin();
  const [{ data: perfis }, { data: convites }, ajustes, config, execs, clientes, { count: testes }] = await Promise.all([
    db.from("portal_perfis").select("user_id,nome,papel,portoes,criado_em").order("nome"),
    db.from("portal_convites").select("email,nome,cargo,papel,portoes,criado_em").order("nome"),
    ajustesDosAgentes(), lerConfig(), listarExecucoes(300), clientePorExecucao(),
    db.from("crewai_webhook_events").select("id", { count: "exact", head: true }).like("kickoff_id", "teste-%"),
  ]);
  const pendentes = execs.filter((e) => e.pendente).map((e) => ({ chave: e.chave, portao: e.portao, cliente: clientes.get(e.chave) || e.chave.slice(0, 8), desde: e.ultimo }));
  return (
    <>
      <div className="head"><div><h1>Administração do sistema</h1><p className="sub" style={{ margin: 0 }}>Controle de acessos, manutenção dos agentes, configuração de custos e ações de manutenção. Tudo fica na trilha de auditoria.</p></div></div>
      <Admin
        eu={u.id}
        perfis={(perfis || []) as never}
        convites={(convites || []) as never}
        agentes={AGENTES.map((a) => ({ chave: a.chave, papel: a.papel, objetivo: a.objetivo, tarefas: a.tarefas.map((t) => t.nome), ferramentas: a.ferramentas }))}
        ajustes={ajustes}
        config={config}
        plataforma={estadoDaPlataforma()}
        pendentes={pendentes}
        testes={testes ?? 0}
      />
    </>
  );
}
