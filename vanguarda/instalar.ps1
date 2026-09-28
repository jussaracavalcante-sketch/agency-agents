<#
.SYNOPSIS
  Instala os agentes da Vanguarda Martech no Claude Code (Windows / PowerShell 5.1+).

.DESCRIPTION
  Copia os agentes ja preparados em .claude\agents (com o bloco de contexto Vanguarda e sem lista
  fixa de ferramentas) para a pasta global do Claude Code e grava o caminho completo da base de
  conhecimento, para que os agentes a encontrem em qualquer projeto. Nao precisa de bash nem Git Bash.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File .\vanguarda\instalar.ps1
  powershell -ExecutionPolicy Bypass -File .\vanguarda\instalar.ps1 -Selecao
  powershell -ExecutionPolicy Bypass -File .\vanguarda\instalar.ps1 -Destino D:\agentes
#>
param(
  [string]$Destino = (Join-Path $HOME '.claude\agents'),
  # instala so o nucleo de marketing listado em vanguarda\agentes-vanguarda.txt
  [switch]$Selecao
)

$ErrorActionPreference = 'Stop'

$Root   = Split-Path -Parent $PSScriptRoot
$Origem = Join-Path $Root '.claude\agents'
$KB     = Join-Path $Root 'vanguarda\BASE-CONHECIMENTO.md'
$Utf8   = New-Object System.Text.UTF8Encoding($false)  # sem BOM: o frontmatter precisa comecar em '---'

if (-not (Test-Path $Origem)) { throw "Pasta de agentes nao encontrada: $Origem" }

$arquivos = Get-ChildItem -Path $Origem -Filter *.md

if ($Selecao) {
  $lista = Get-Content (Join-Path $Root 'vanguarda\agentes-vanguarda.txt') |
    ForEach-Object { $_.Trim() } | Where-Object { $_ -and -not $_.StartsWith('#') }
  # o slug do instalador e o campo 'name:' em minusculas, com nao-alfanumericos virando '-'
  $arquivos = $arquivos | Where-Object {
    $nome = (Select-String -Path $_.FullName -Pattern '^name:\s*(.+)$' | Select-Object -First 1).Matches.Groups[1].Value
    $slug = ($nome.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
    $lista -contains $slug
  }
}

New-Item -ItemType Directory -Force -Path $Destino | Out-Null

$n = 0
foreach ($f in $arquivos) {
  $texto = [System.IO.File]::ReadAllText($f.FullName, $Utf8)
  $texto = $texto.Replace('`vanguarda/BASE-CONHECIMENTO.md`', '`' + $KB + '`')
  [System.IO.File]::WriteAllText((Join-Path $Destino $f.Name), $texto, $Utf8)
  $n++
}

Write-Host "[OK] $n agentes com contexto Vanguarda instalados em $Destino" -ForegroundColor Green
Write-Host "     Base de conhecimento: $KB"
Write-Host "     Abra uma nova sessao do Claude Code para carregar os agentes."
