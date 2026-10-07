import { DOCUMENTOS } from "./documentos";

/** Sem dependências de servidor: pode rodar no middleware (borda). */
export const COOKIE_ACEITE = "aceite_ok";
export const SELO_VIGENTE = Object.values(DOCUMENTOS).map((d) => d.hash).join("-");
