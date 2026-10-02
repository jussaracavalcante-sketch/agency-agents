import { redirect } from "next/navigation";
import { admin, usuarioAtual } from "@/lib/supabase";
import { execucaoAtiva } from "@/lib/execucoes";
import Formulario from "./Formulario";

export const dynamic = "force-dynamic";

export default async function Disparar() {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  if (u.papel !== "aprovador") {
    return <div className="card"><h2 style={{ marginTop: 0 }}>Disparar campanha</h2><p className="mut">Apenas aprovadores disparam campanhas. Peça a um aprovador.</p></div>;
  }
  const { data: clientes } = await admin().from("portal_clientes").select("slug,nome,guia_completo").order("nome");
  const ativa = await execucaoAtiva();
  const { data: ultimos } = await admin().from("portal_disparos").select("id,cliente_slug,humano_nome,criado_em,enviado_ao_crewai,kickoff_id").order("criado_em", { ascending: false }).limit(5);
  return (
    <>
      <h2>Disparar campanha</h2>
      {ativa.ativa && <div className="card" style={{ borderColor: "var(--warn)" }}><strong>Há uma campanha rodando:</strong> {ativa.motivo}. O disparo fica bloqueado até ela terminar.</div>}
      <Formulario clientes={clientes || []} />
      <h3>Últimos disparos</h3>
      {!ultimos?.length && <p className="mut">Nenhum disparo pelo portal ainda.</p>}
      {ultimos?.map((d) => (
        <p key={d.id} className="mut">{new Date(d.criado_em).toLocaleString("pt-BR", { timeZone: "America/Manaus" })} · {d.cliente_slug} · {d.humano_nome} · {d.enviado_ao_crewai ? `enviado (${String(d.kickoff_id).slice(0, 8)})` : "não enviado"}</p>
      ))}
    </>
  );
}
