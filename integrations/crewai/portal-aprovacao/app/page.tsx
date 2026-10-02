import Link from "next/link";
import { redirect } from "next/navigation";
import { admin, usuarioAtual } from "@/lib/supabase";
import { listarExecucoes } from "@/lib/execucoes";
import { AGENTES, TAREFAS, rotuloTarefa } from "@/lib/agentes";
import { clientePorExecucao, entregasRecentes, haQuanto, hora } from "@/lib/dados";

const TOKENS_POR_CAMPANHA = 360_000; // estimativa medida nos pilotos

export default async function VisaoGeral() {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  const desde = new Date(Date.now() - 30 * 86_400_000).toISOString();
  const [execs, clientes, recentes, concl, disp, guias] = await Promise.all([
    listarExecucoes(),
    clientePorExecucao(),
    entregasRecentes(5),
    entregasRecentes(5000, desde),
    admin().from("portal_disparos").select("id", { count: "exact", head: true }).eq("enviado_ao_crewai", true).gt("criado_em", desde),
    admin().from("portal_clientes").select("nome").eq("guia_completo", false),
  ]);
  const pend = execs.filter((e) => e.pendente);
  const emAndamento = execs.filter((e) => !e.concluida && !e.pendente).length;
  const nome = (k: string) => clientes.get(k) || `Execução ${k.slice(0, 8)}`;
  const campanhas = disp.count ?? 0;

  return (
    <>
      <div className="head">
        <div><h1>Visão geral</h1><p className="sub" style={{ margin: 0 }}>Acompanhe a equipe de agentes e saiba onde agir.</p></div>
        {u.papel === "aprovador" && <Link className="btn p" href="/disparar">＋ Disparar campanha</Link>}
      </div>

      <div className="kpis">
        <div className="card"><span className="kic" style={{ background: "var(--ac-bg)", color: "var(--ac)" }}>👥</span><div><div className="kl">Agentes na equipe</div><div className="kn">{AGENTES.length}</div><div className="kl">{Object.keys(TAREFAS).length} tarefas por campanha</div></div></div>
        <div className="card"><span className="kic" style={{ background: "var(--ok-bg)", color: "var(--ok)" }}>✔</span><div><div className="kl">Tarefas concluídas</div><div className="kn">{concl.length.toLocaleString("pt-BR")}</div><div className="kl">Últimos 30 dias</div></div></div>
        <div className="card"><span className="kic" style={{ background: "var(--warn-bg)", color: "var(--warn)" }}>⏳</span><div><div className="kl">Portões aguardando</div><div className="kn">{pend.length}</div><div className="kl">{emAndamento} em andamento</div></div></div>
        <div className="card"><span className="kic" style={{ background: "var(--vio-bg)", color: "var(--vio)" }}>◔</span><div><div className="kl">Consumo estimado</div><div className="kn">{(campanhas * TOKENS_POR_CAMPANHA / 1000).toLocaleString("pt-BR")} mil</div><div className="kl">tokens, {campanhas} campanha(s) pelo portal em 30 dias (estimativa de ~360 mil por campanha)</div></div></div>
      </div>

      <div className="two">
        <div>
          <div className="card">
            <div className="row"><h2>Atividade recente</h2><Link href="/atividade">Ver atividade</Link></div>
            {!recentes.length && <p className="vazio">Nenhuma entrega registrada.</p>}
            {!!recentes.length && (
              <table className="tb"><thead><tr><th>Tarefa</th><th>Agente</th><th>Status</th><th>Horário</th></tr></thead><tbody>
                {recentes.map((t) => (
                  <tr key={t.id}><td>{rotuloTarefa(t.task_name || "")}</td><td>{TAREFAS[t.task_name || ""]?.papel ?? "agente"}</td><td><span className="st ok">Concluída</span></td><td>{hora(t.recebido_em)}</td></tr>
                ))}
              </tbody></table>
            )}
          </div>
          <div className="card">
            <div className="row"><h2>Seus agentes</h2><Link href="/agentes">Ver todos os {AGENTES.length} agentes</Link></div>
            {AGENTES.map((a) => (
              <Link key={a.chave} href={`/agentes/${a.chave}`} className="item" style={{ color: "var(--tx)" }}>
                <span className="bola">{a.papel.split(/\s+/).filter((w) => w.length > 2).slice(0, 2).map((w) => w[0]).join("").toUpperCase()}</span>
                <div className="grow"><strong>{a.papel}</strong><div className="mut">{a.tarefas.length} tarefa(s) no fluxo</div></div>
                <span className="st ok">Ativo</span>
              </Link>
            ))}
          </div>
        </div>
        <div>
          <div className="card">
            <h2>Precisa da sua atenção</h2>
            {!pend.length && !guias.data?.length && <p className="vazio">Nada pendente.</p>}
            {pend.map((e) => (
              <div key={e.chave} className="item">
                <span className="bola w">{e.portao ?? "?"}</span>
                <div className="grow"><strong>Portão {e.portao ?? "?"} aguarda decisão</strong><div className="mut">{nome(e.chave)} · {haQuanto(e.ultimo)}</div></div>
                <Link className="btn" href={`/execucao/${e.chave}`}>Revisar</Link>
              </div>
            ))}
            {!!guias.data?.length && (
              <div className="item">
                <span className="bola e">!</span>
                <div className="grow"><strong>{guias.data.length} guia(s) de marca incompleto(s)</strong><div className="mut">As decisões de marca saem como [VALIDAR].</div></div>
                <Link className="btn" href="/conhecimento?f=incompletos">Ver</Link>
              </div>
            )}
          </div>
          <div className="card">
            <h2>Como funciona</h2>
            <p className="mut">Cada campanha passa por três portões humanos: G1 (brief), G2 (peças) e G3 (publicação). Nada é publicado sem aprovação de uma pessoa.</p>
          </div>
        </div>
      </div>
    </>
  );
}
