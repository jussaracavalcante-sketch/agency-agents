import Link from "next/link";
import Markdown from "@/components/Markdown";
import AvisoMinuta from "@/components/AvisoMinuta";
import { DOCUMENTOS } from "@/lib/documentos";

export const metadata = { title: "Aviso de Privacidade · Marketing Ops" };

/** Página pública (sem login): o aviso precisa estar acessível antes do primeiro acesso. */
export default function Privacidade() {
  const d = DOCUMENTOS.aviso;
  return (
    <div className="doc">
      <AvisoMinuta md={d.md} versao={d.versao} />
      <article className="card doc-corpo"><Markdown texto={d.md} /></article>
      <p className="mut" style={{ textAlign: "center" }}>Veja também o <Link href="/termo">Termo de Conduta</Link>.</p>
    </div>
  );
}
