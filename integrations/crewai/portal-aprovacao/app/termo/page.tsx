import Link from "next/link";
import Markdown from "@/components/Markdown";
import AvisoMinuta from "@/components/AvisoMinuta";
import { DOCUMENTOS } from "@/lib/documentos";

export const metadata = { title: "Termo de Conduta · Marketing Ops" };

export default function Termo() {
  const d = DOCUMENTOS.termo;
  return (
    <div className="doc">
      <AvisoMinuta md={d.md} versao={d.versao} />
      <article className="card doc-corpo"><Markdown texto={d.md} /></article>
      <p className="mut" style={{ textAlign: "center" }}>O aceite é registrado no primeiro acesso. Veja também o <Link href="/privacidade">Aviso de Privacidade</Link>.</p>
    </div>
  );
}
