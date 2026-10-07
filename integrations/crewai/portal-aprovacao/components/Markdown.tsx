import { Fragment } from "react";

/** Renderizador mínimo para os documentos do portal (títulos, parágrafos, listas, tabelas, citação, negrito). Sem HTML bruto: tudo vira texto. */

function inline(t: string, k: string) {
  return t.split(/(\*\*[^*]+\*\*)/).map((p, i) => {
    const negrito = p.startsWith("**") && p.endsWith("**");
    const corpo = negrito ? p.slice(2, -2) : p;
    const partes = corpo.split(/(\[[^\]]*\])/).map((q, j) => (/^\[[^\]]*\]$/.test(q) ? <mark key={j} className="pend">{q}</mark> : <Fragment key={j}>{q}</Fragment>));
    return negrito ? <b key={`${k}${i}`}>{partes}</b> : <Fragment key={`${k}${i}`}>{partes}</Fragment>;
  });
}

export default function Markdown({ texto }: { texto: string }) {
  const L = texto.split("\n");
  const out: React.ReactNode[] = [];
  let i = 0, n = 0;
  while (i < L.length) {
    const l = L[i].trimEnd();
    if (!l.trim()) { i++; continue; }
    const k = `b${n++}`;
    if (l.startsWith("# ")) { out.push(<h1 key={k}>{inline(l.slice(2), k)}</h1>); i++; }
    else if (l.startsWith("## ")) { out.push(<h2 key={k}>{inline(l.slice(3), k)}</h2>); i++; }
    else if (l.startsWith("### ")) { out.push(<h3 key={k}>{inline(l.slice(4), k)}</h3>); i++; }
    else if (l.startsWith("> ")) {
      const q: string[] = [];
      while (i < L.length && L[i].startsWith("> ")) q.push(L[i++].slice(2));
      out.push(<blockquote key={k}>{inline(q.join(" "), k)}</blockquote>);
    } else if (l.startsWith("|")) {
      const bloco: string[] = [];
      while (i < L.length && L[i].startsWith("|")) bloco.push(L[i++]);
      const linhas = bloco.filter((b) => !/^\|[\s\-|]+\|$/.test(b.trim())).map((b) => b.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
      out.push(
        <div className="tabw" key={k}><table><thead><tr>{linhas[0].map((c, j) => <th key={j}>{inline(c, `${k}h${j}`)}</th>)}</tr></thead>
          <tbody>{linhas.slice(1).map((r, a) => <tr key={a}>{r.map((c, j) => <td key={j}>{inline(c, `${k}${a}${j}`)}</td>)}</tr>)}</tbody></table></div>,
      );
    } else if (/^\d+\.\s/.test(l)) {
      const it: string[] = [];
      while (i < L.length && /^\d+\.\s/.test(L[i])) it.push(L[i++].replace(/^\d+\.\s/, ""));
      out.push(<ol key={k}>{it.map((x, j) => <li key={j}>{inline(x, `${k}${j}`)}</li>)}</ol>);
    } else if (l.startsWith("- ")) {
      const it: string[] = [];
      while (i < L.length && L[i].startsWith("- ")) it.push(L[i++].slice(2));
      out.push(<ul key={k}>{it.map((x, j) => <li key={j}>{inline(x, `${k}${j}`)}</li>)}</ul>);
    } else {
      const p: string[] = [l]; i++;
      while (i < L.length && L[i].trim() && !/^(#|>|\||- |\d+\.\s)/.test(L[i])) p.push(L[i++].trimEnd());
      out.push(<p key={k}>{p.map((x, j) => <Fragment key={j}>{j > 0 && <br />}{inline(x, `${k}${j}`)}</Fragment>)}</p>);
    }
  }
  return <>{out}</>;
}
