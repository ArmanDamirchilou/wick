# wick demo — a clean end-to-end run to screen-record.
#
# Usage (from the repo root, with the package installed):
#   .\demo.ps1
#   .\demo.ps1 -ModelName gemma-3n-e2b     # multilingual, ~3 GB
#
# Everything after the model loads is fully offline.

param(
    [ValidateSet("qwen2.5-0.5b", "qwen2.5-1.5b", "gemma-3n-e2b")]
    [string]$ModelName  = "qwen2.5-1.5b",
    [string]$EmbedModel = "paraphrase-multilingual-MiniLM-L12-v2"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Wick = if (Test-Path ".\.venv\Scripts\wick.exe") { ".\.venv\Scripts\wick.exe" } else { "wick" }

function Ask {
    param($Pdf, $Question, $Embed)
    Write-Host ""
    Write-Host "> $Question" -ForegroundColor Cyan
    if ($Embed) {
        & $Wick $Pdf $Question --model-name $ModelName --embed-model $Embed
    } else {
        & $Wick $Pdf $Question --model-name $ModelName
    }
    Start-Sleep -Seconds 1
}

Write-Host "wick - offline question answering over a local PDF" -ForegroundColor Green
Write-Host "Model: $ModelName (run 'wick --download-model' first if you haven't)"
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
Ask $fa "آب در چه دمایی به جوش می‌آید؟" $EmbedModel
Ask $fa "بیشتر آب کره زمین کجاست؟" $EmbedModel

Write-Host ""
Write-Host "Done - every answer produced locally, offline." -ForegroundColor Green
