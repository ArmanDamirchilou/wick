# wick demo — a clean end-to-end run to screen-record.
#
# Usage (from the repo root, with the package installed):
#   .\demo.ps1 -Model .\models\gemma-3n-E2B-it-Q4_K_M.gguf
#
# Everything after the model loads is fully offline.

param(
    [string]$Model      = ".\models\gemma-3n-E2B-it-Q4_K_M.gguf",
    [string]$EmbedModel = "paraphrase-multilingual-MiniLM-L12-v2"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Wick = if (Test-Path ".\.venv\Scripts\wick.exe") { ".\.venv\Scripts\wick.exe" } else { "wick" }

if (-not (Test-Path $Model)) {
    Write-Host "Model not found: $Model" -ForegroundColor Red
    Write-Host "Download a GGUF model into .\models\ first (see docs/models.md)."
    exit 1
}

function Ask {
    param($Pdf, $Question, $Embed)
    Write-Host ""
    Write-Host "> $Question" -ForegroundColor Cyan
    if ($Embed) {
        & $Wick $Pdf $Question --model $Model --embed-model $Embed
    } else {
        & $Wick $Pdf $Question --model $Model
    }
    Start-Sleep -Seconds 1
}

Write-Host "wick - offline question answering over a local PDF" -ForegroundColor Green
Write-Host "Model: $Model"
Write-Host "From here on, no internet connection is used."

$eng = ".\examples\earthquake-safety.pdf"
Write-Host ""
Write-Host "== English: an earthquake-safety guide ==" -ForegroundColor Green
Ask $eng "What should I do the moment the shaking starts?"
Ask $eng "How much water should I store per person, and for how many days?"
Ask $eng "What should I do if I am trapped under rubble?"

Write-Host ""
Write-Host "When the answer isn't in the document, it declines instead of guessing:" -ForegroundColor Yellow
Ask $eng "What is the population of Tokyo?"

$fa = ".\examples\water-cycle-fa.pdf"
Write-Host ""
Write-Host "== Persian: same engine, a non-English document ==" -ForegroundColor Green
Write-Host "(the first Persian question downloads a multilingual retrieval model, once)"
Ask $fa "آب در چه دمایی به جوش می‌آید؟" $EmbedModel
Ask $fa "بیشتر آب کره زمین کجاست؟" $EmbedModel

Write-Host ""
Write-Host "Done - every answer produced locally, offline." -ForegroundColor Green
