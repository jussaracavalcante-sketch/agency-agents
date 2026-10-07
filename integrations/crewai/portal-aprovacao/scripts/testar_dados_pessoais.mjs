// Teste do detector de dados pessoais do briefing. Rode:  node scripts/testar_dados_pessoais.mjs
import ts from "typescript";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const aqui = path.dirname(fileURLToPath(import.meta.url));
const src = fs.readFileSync(path.join(aqui, "../lib/dadosPessoais.ts"), "utf8");
const js = ts.transpileModule(src, { compilerOptions: { module: "ESNext", target: "ES2022" } }).outputText;
const m = await import("data:text/javascript;base64," + Buffer.from(js).toString("base64"));

const limpos = [
  "Campanha de captação de pacientes Hospital Santa Júlia Q4 2026",
  "Adultos 30-60 anos, classes A/B, beneficiários de planos de saúde e pacientes particulares que buscam especialistas e exames",
  "Gerar 400 contatos qualificados em 8 semanas (baseline: 863 conversões RD em 90 dias, 343 vindas de mídia paga)",
  "R$ 15.000 [VALIDAR] (run-rate Google Ads: R$ 11.654 em 90 dias) até 2026-09-30",
  "captação de paciente Hospital Santa Júlia",
  "campanha para pacientes Clínica São Lucas",
];
const sujos = ["a paciente Maria Souza voltou", "paciente João Pereira Lima", "paciente: Ana Costa", "CPF 529.982.247-25", "fale com maria@exemplo.com.br", "ligar (92) 99123-4567", "prontuário nº 4521"];

let falhas = 0;
for (const t of limpos) if (m.dadosPessoais(t).length) { falhas++; console.log("FALSO POSITIVO:", t); }
for (const t of sujos) if (!m.dadosPessoais(t).length) { falhas++; console.log("NÃO DETECTOU:", t); }
console.log(falhas ? `${falhas} falha(s)` : `ok: ${limpos.length} textos limpos e ${sujos.length} com dado pessoal`);
process.exit(falhas ? 1 : 0);
