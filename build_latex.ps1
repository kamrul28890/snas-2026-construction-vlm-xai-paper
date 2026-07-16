$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$tempDir = Join-Path $root 'tmp\pdfs'
$outputDir = Join-Path $root 'output\pdf'

New-Item -ItemType Directory -Force -Path $tempDir, $outputDir | Out-Null

Push-Location $root
try {
    $sources = @(
        'SNAS_2026_abstract_draft.tex',
        'SNAS_2026_paper_draft.tex',
        'SNAS_2026_abstract_submission_candidate.tex',
        'SNAS_2026_paper_submission_candidate.tex'
    )

    foreach ($source in $sources) {
        1..2 | ForEach-Object {
            & xelatex -interaction=nonstopmode -halt-on-error "-output-directory=$tempDir" $source
            if ($LASTEXITCODE -ne 0) {
                throw "XeLaTeX failed for $source."
            }
        }

        $pdfName = [System.IO.Path]::ChangeExtension($source, '.pdf')
        Copy-Item -LiteralPath (Join-Path $tempDir $pdfName) -Destination (Join-Path $outputDir $pdfName) -Force
    }
}
finally {
    Pop-Location
}

Write-Host "Built PDFs in $outputDir"
