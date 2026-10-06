import { redirect } from "next/navigation";
import { ehAdmin, ehAprovador, usuarioAtual } from "@/lib/supabase";
import { ACOES, listar, mudancas, rotuloAcao } from "@/lib/auditoria";
import { fmt } from "@/lib/dados";

export const dynamic = "force-dynamic";
type Busca = { usuario?: string; acao?: string; entidade?: string; de?: string; ate?: string; q?: string };

export default async function Auditoria({ searchParams }: { searchParams: Busca }) {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  if (!ehAdmin(u) && !ehAprovador(u)) return <div className="card"><h1>Logs de auditoria</h1><p className="mut">Seu papel não acessa a auditoria. Peça ao administrador.</p></div>;
  const f = { usuario: searchParams.usuario, acao: searchParams.acao, entidade: searchParams.entidade, de: searchParams.de, ate: searchParams.ate, busca: searchParams.q };
  const linhas = await listar(f);
  const qs = new URLSearchParams(Object.entries(searchParams).filter(([, v]) => v) as [string, string][]).toString();
  const entidades = ["portal_decisoes", "portal_disparos", "portal_conhecimento", "portal_perfis", "portal_convites", "portal_agentes_ajustes", "portal_config", "crewai_webhook_events"];
  const hora = (s: string) => new Date(s).toLocaleTimeString("pt-BR", { timeZone: "America/Manaus", hour: "2-digit", minute: "2-digit", second: "2-digit" });
  const data = (s: string) => new Date(s).toLocaleDateString("pt-BR", { timeZone: "America/Manaus" });
  return (
    <>
      <div className="head">
        <div><h1>Logs de auditoria</h1><p className="sub" style={{ margin: 0 }}>Quem fez o quê, em qual sessão, quando e o que mudou. A trilha é só de leitura: ninguém edita nem apaga registros pelo portal.</p></div>
        <a className="btn" href={`/api/auditoria?${qs}`}>Exportar CSV</a>
      </div>
      <form className="card" method="get" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 10, alignItems: "end" }}>
        <label>Nome<input name="usuario" defaultValue={searchParams.usuario ?? ""} placeholder="parte do nome" /></label>
        <label>Ação<select name="acao" defaultValue={searchParams.acao ?? ""}><option value="">todas</option>{Object.entries(ACOES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></label>
        <label>Entidade<select name="entidade" defaultValue={searchParams.entidade ?? ""}><option value="">todas</option>{entidades.map((e) => <option key={e} value={e}>{e}</option>)}</select></label>
        <label>De<input type="date" name="de" defaultValue={searchParams.de ?? ""} /></label>
        <label>Até<input type="date" name="ate" defaultValue={searchParams.ate ?? ""} /></label>
        <label>Busca<input name="q" defaultValue={searchParams.q ?? ""} placeholder="detalhe, id, sessão" /></label>
        <div style={{ display: "flex", gap: 8 }}><button className="p" type="submit">Filtrar</button><a className="btn" href="/auditoria">Limpar</a></div>
      </form>
      <div className="card">
        <p className="mut">{linhas.length} registro(s){linhas.length >= 300 ? " (mostrando os 300 mais recentes; refine o filtro ou exporte o CSV)" : ""}.</p>
        {!linhas.length && <p className="vazio">Nenhum registro com esses filtros.</p>}
        {!!linhas.length && (
          <table className="tb"><thead><tr><th>Nome</th><th>Sessão</th><th>Data</th><th>Hora</th><th>Ação</th><th>O que foi alterado</th></tr></thead><tbody>
            {linhas.map((l) => {
              const m = mudancas(l.antes, l.depois);
              return (
                <tr key={l.id}>
                  <td>{l.usuario_nome}</td>
                  <td className="mut" title={l.sessao ?? ""}>{l.sessao ? l.sessao.slice(0, 8) : "—"}</td>
                  <td>{data(l.criado_em)}</td><td>{hora(l.criado_em)}</td>
                  <td><span className={`st ${l.acao.includes("reprovar") || l.acao.includes("excluir") ? "err" : l.acao.includes("devolver") ? "warn" : "ok"}`}>{rotuloAcao(l.acao)}</span><div className="mut" style={{ fontSize: 12 }}>{l.entidade}{l.entidade_id ? ` · ${l.entidade_id.slice(0, 12)}` : ""}</div></td>
                  <td style={{ maxWidth: 480 }}>
                    {l.detalhe && <div>{l.detalhe}</div>}
                    {m.length ? <ul style={{ margin: "4px 0 0 16px", padding: 0, fontSize: 13 }}>{m.slice(0, 6).map((x, i) => <li key={i}><code>{x}</code></li>)}{m.length > 6 && <li className="mut">+{m.length - 6} campo(s)</li>}</ul> : (!l.detalhe && <span className="mut">registro de evento, sem campos alterados</span>)}
                    {(l.antes || l.depois) ? <details style={{ marginTop: 4 }}><summary className="mut" style={{ cursor: "pointer", fontSize: 12 }}>ver antes/depois</summary><pre className="doc" style={{ fontSize: 12, maxHeight: 220, overflow: "auto" }}>{JSON.stringify({ antes: l.antes, depois: l.depois }, null, 2)}</pre></details> : null}
                  </td>
                </tr>
              );
            })}
          </tbody></table>
        )}
      </div>
      <p className="mut" style={{ fontSize: 12 }}>Horários em America/Manaus. A data em que o registro foi gravado é {fmt(new Date().toISOString()).split(",")[0]} para esta consulta.</p>
    </>
  );
}
